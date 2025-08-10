from __future__ import annotations
import os
import re
import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Iterable, Dict

import faiss
import numpy as np

# --- 全局参数 ---
DEFAULT_CORPUS_DIR = Path(__file__).resolve().parents[1] / "legal_corpus"
# 为了简单，把索引也放在 legal_corpus 下；如需放 storage，改成 parents[1]/"storage"
DEFAULT_INDEX_DIR = DEFAULT_CORPUS_DIR

INDEX_FILE = "law_faiss.index"
META_FILE = "law_meta.pkl"

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBED_DIM = 384
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


# -------- 工具 --------
def _read_text(fp: Path) -> str:
    try:
        return fp.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return fp.read_text(encoding="gb18030", errors="ignore")


def _split_paragraph_chunks(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> Iterable[str]:
    """先按空行分段，再做长度控制 + overlap。"""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    buf = ""
    for p in paragraphs:
        if not buf:
            buf = p
            continue
        if len(buf) + 1 + len(p) <= size:
            buf = buf + "\n" + p
        else:
            # 切块
            start = 0
            cur = buf
            while len(cur) > size:
                yield cur[:size]
                start = size - overlap
                cur = cur[start:]
            if cur:
                yield cur
            buf = p
    if buf:
        # 最后一块也按 size/overlap 切一遍
        cur = buf
        while len(cur) > size:
            yield cur[:size]
            cur = cur[size - overlap :]
        if cur:
            yield cur


def _norm(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v, axis=1, keepdims=True) + 1e-12
    return v / n


def _paths(index_dir: Path) -> Tuple[Path, Path]:
    return index_dir / INDEX_FILE, index_dir / META_FILE


# 延迟加载模型，避免模块导入就耗时
_model = None
def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


# -------- 数据结构 --------
@dataclass
class RetrievedChunk:
    text: str
    source: str
    score: float


# -------- 类实现（与你现有代码兼容） --------
class RAGSystem:
    """法条 RAG 系统：构建索引 + 检索。"""

    def __init__(self, corpus_dir: str = "legal_corpus", index_dir: str = "storage"):
        self.corpus_dir = Path(corpus_dir)
        self.index_dir = Path(index_dir)
        self.index_path, self.meta_path = _paths(self.index_dir)

        self.index: faiss.Index | None = None
        self.metadata: List[Dict] = []

        self.corpus_dir.mkdir(parents=True, exist_ok=True)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    # ---- 内部 ----
    def _load_corpus(self) -> List[Tuple[str, str]]:
        """加载语料库中的 .txt / .md 文件，返回 (文件名, 全文) 列表。"""
        out: List[Tuple[str, str]] = []
        if not self.corpus_dir.exists():
            return out

        # 逐类收集，使用 list 相加，而不是 |
        files = list(sorted(self.corpus_dir.glob("*.txt")))
        files += list(sorted(self.corpus_dir.glob("*.md")))

        for f in files:
            try:
                text = _read_text(f)
            except Exception:
                # 回退：避免个别文件解码失败中断全流程
                try:
                    text = f.read_text(encoding="gb18030", errors="ignore")
                except Exception:
                    continue
            out.append((f.name, text))
        return out


    # ---- 构建 ----
    def build_index(self) -> bool:
        try:
            files = self._load_corpus()
            if not files:
                return False

            texts: List[str] = []
            meta: List[Dict] = []

            for fname, content in files:
                for i, chunk in enumerate(_split_paragraph_chunks(content)):
                    texts.append(chunk)
                    # 保存完整 chunk 以便回答引用
                    meta.append({"source": fname, "chunk_id": i, "text": chunk})

            if not texts:
                return False

            model = _get_model()
            emb = model.encode(texts, convert_to_numpy=True, batch_size=64, show_progress_bar=True).astype("float32")
            emb = _norm(emb)

            index = faiss.IndexFlatIP(EMBED_DIM)
            index.add(emb)

            faiss.write_index(index, str(self.index_path))
            with open(self.meta_path, "wb") as f:
                pickle.dump(meta, f)

            self.index = index
            self.metadata = meta
            return True
        except Exception as e:
            print("[RAG] build_index failed:", e)
            return False

    # ---- 加载 ----
    def load_index(self) -> bool:
        try:
            if not self.index_path.exists() or not self.meta_path.exists():
                return False
            self.index = faiss.read_index(str(self.index_path))
            with open(self.meta_path, "rb") as f:
                self.metadata = pickle.load(f)
            return True
        except Exception as e:
            print("[RAG] load_index failed:", e)
            return False

    # ---- 检索 ----
    def retrieve_law_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        if self.index is None:
            if not self.load_index():
                return []

        try:
            model = _get_model()
            q = model.encode([query], convert_to_numpy=True).astype("float32")
            q = _norm(q)
            scores, ids = self.index.search(q, top_k)
            results: List[Dict] = []
            for s, idx in zip(scores[0], ids[0]):
                if 0 <= idx < len(self.metadata):
                    m = self.metadata[idx]
                    results.append(
                        {
                            "text": m["text"], 
                            "source": m["source"], 
                            "score": float(s), 
                            "chunk_id": m["chunk_id"],
                            "full_text": m.get("full_text", m["text"]),  # 添加完整文本
                            "chunk_index": idx  # 添加chunk索引
                        }
                    )
            return results
        except Exception as e:
            print("[RAG] retrieve failed:", e)
            return []

    def format_retrieved_chunks_for_display(self, chunks: List[Dict]) -> List[Dict]:
        """
        格式化检索到的chunks用于前端显示
        
        Args:
            chunks: 检索到的chunks列表
            
        Returns:
            格式化后的chunks列表
        """
        formatted_chunks = []
        for i, chunk in enumerate(chunks):
            formatted_chunk = {
                "id": i + 1,
                "text": chunk["text"],
                "source": chunk["source"],
                "score": chunk["score"],
                "full_text": chunk.get("full_text", chunk["text"]),
                "preview": chunk["text"][:100] + "..." if len(chunk["text"]) > 100 else chunk["text"]
            }
            formatted_chunks.append(formatted_chunk)
        return formatted_chunks

    def is_index_available(self) -> bool:
        return self.index_path.exists() and self.meta_path.exists()


# -------- 模块级便捷函数（供脚本/按钮/just 调用） --------
def build_index(corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
                 index_dir:  str | Path = DEFAULT_INDEX_DIR) -> None:
    rag = RAGSystem(str(corpus_dir), str(index_dir))
    ok = rag.build_index()
    if not ok:
        raise RuntimeError("未找到语料或构建失败")
    print(f"[RAG] 索引构建完成：{rag.index_path}  元数据：{rag.meta_path}")


def index_exists(corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
                 index_dir:  str | Path = DEFAULT_INDEX_DIR) -> bool:
    idx, meta = _paths(Path(index_dir))
    return Path(corpus_dir).exists() and idx.exists() and meta.exists()


@dataclass
class SimpleChunk:
    text: str
    source: str
    score: float


def retrieve_law_chunks(query: str, top_k: int = 5,
                        corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
                        index_dir:  str | Path = DEFAULT_INDEX_DIR) -> List[SimpleChunk]:
    rag = RAGSystem(str(corpus_dir), str(index_dir))
    if not rag.load_index():
        return []
    items = rag.retrieve_law_chunks(query, top_k=top_k)
    return [SimpleChunk(text=i["text"], source=i["source"], score=i["score"]) for i in items]


def chunks_to_prompt(chunks: List[SimpleChunk]) -> str:
    lines = []
    for i, c in enumerate(chunks, 1):
        lines.append(f"[{i}] 来源: {c.source}  相似度: {c.score:.3f}\n{c.text}\n")
    return "\n".join(lines)


# -------- CLI --------
def _cli():
    import argparse, sys, textwrap
    p = argparse.ArgumentParser(
        prog="python -m utils.rag_system",
        formatter_class=argparse.RawTextHelpFormatter,
        description=textwrap.dedent("""\
        法条 RAG 工具：
          build                         构建索引
          query  '问题'  --topk 5       检索法条段落
        """),
    )
    p.add_argument("cmd", choices=["build", "query"])
    p.add_argument("--corpus", default=str(DEFAULT_CORPUS_DIR))
    p.add_argument("--index", default=str(DEFAULT_INDEX_DIR))
    p.add_argument("--topk", type=int, default=5)
    p.add_argument("rest", nargs="*")
    args = p.parse_args()

    if args.cmd == "build":
        build_index(args.corpus, args.index)
        return

    if args.cmd == "query":
        if not args.rest:
            print("请提供查询内容，如：python -m utils.rag_system query 合同解除的条件")
            sys.exit(1)
        q = " ".join(args.rest)
        chunks = retrieve_law_chunks(q, top_k=args.topk, corpus_dir=args.corpus, index_dir=args.index)
        print(chunks_to_prompt(chunks))
        return


if __name__ == "__main__":
    _cli()
