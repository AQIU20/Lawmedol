"""
RAG (Retrieval-Augmented Generation) 系统
用于构建法条向量库和检索相关法条
"""

import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
import logging
import re

logger = logging.getLogger(__name__)


class RAGSystem:
    """RAG 系统，用于法条向量化和检索"""
    
    def __init__(self, corpus_dir: str = "legal_corpus", index_dir: str = "storage"):
        """
        初始化 RAG 系统
        
        Args:
            corpus_dir: 法条语料库目录
            index_dir: 索引存储目录
        """
        self.corpus_dir = corpus_dir
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "law_faiss.index")
        self.metadata_path = os.path.join(index_dir, "metadata.pkl")
        
        # 使用多语言模型
        self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        
        # 初始化索引和元数据
        self.index = None
        self.metadata = []
        
        # 确保目录存在
        os.makedirs(corpus_dir, exist_ok=True)
        os.makedirs(index_dir, exist_ok=True)
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 400) -> List[str]:
        """
        将文本分割成固定大小的块
        
        Args:
            text: 输入文本
            chunk_size: 块大小（字符数）
            
        Returns:
            文本块列表
        """
        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # 如果当前块加上新段落超过限制，保存当前块
            if len(current_chunk) + len(paragraph) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = paragraph
            else:
                current_chunk += "\n" + paragraph if current_chunk else paragraph
        
        # 添加最后一个块
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _load_corpus_files(self) -> List[Tuple[str, str]]:
        """
        加载语料库文件
        
        Returns:
            (文件名, 文件内容) 的列表
        """
        corpus_files = []
        
        if not os.path.exists(self.corpus_dir):
            logger.warning(f"语料库目录不存在: {self.corpus_dir}")
            return corpus_files
        
        for filename in os.listdir(self.corpus_dir):
            if filename.endswith(('.txt', '.md')):
                file_path = os.path.join(self.corpus_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    corpus_files.append((filename, content))
                except Exception as e:
                    logger.error(f"读取文件失败: {file_path}, 错误: {str(e)}")
        
        return corpus_files
    
    def build_index(self) -> bool:
        """
        构建法条向量索引
        
        Returns:
            构建是否成功
        """
        try:
            # 加载语料库文件
            corpus_files = self._load_corpus_files()
            
            if not corpus_files:
                logger.warning("没有找到语料库文件")
                return False
            
            # 分割文本并准备数据
            chunks = []
            metadata = []
            
            for filename, content in corpus_files:
                file_chunks = self._split_text_into_chunks(content)
                
                for i, chunk in enumerate(file_chunks):
                    chunks.append(chunk)
                    metadata.append({
                        'source': filename,
                        'chunk_id': i,
                        'text': chunk[:100] + "..." if len(chunk) > 100 else chunk
                    })
            
            if not chunks:
                logger.warning("没有有效的文本块")
                return False
            
            # 生成嵌入向量
            logger.info(f"正在生成 {len(chunks)} 个文本块的嵌入向量...")
            embeddings = self.model.encode(chunks, show_progress_bar=True)
            
            # 创建 FAISS 索引
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # 使用内积相似度
            self.index.add(embeddings.astype('float32'))
            
            # 保存索引和元数据
            faiss.write_index(self.index, self.index_path)
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            self.metadata = metadata
            logger.info(f"索引构建完成，共 {len(chunks)} 个文本块")
            return True
            
        except Exception as e:
            logger.error(f"构建索引失败: {str(e)}")
            return False
    
    def load_index(self) -> bool:
        """
        加载已存在的索引
        
        Returns:
            加载是否成功
        """
        try:
            if not os.path.exists(self.index_path) or not os.path.exists(self.metadata_path):
                logger.warning("索引文件不存在，需要先构建索引")
                return False
            
            # 加载索引
            self.index = faiss.read_index(self.index_path)
            
            # 加载元数据
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            
            logger.info(f"索引加载成功，共 {len(self.metadata)} 个文本块")
            return True
            
        except Exception as e:
            logger.error(f"加载索引失败: {str(e)}")
            return False
    
    def retrieve_law_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索相关的法条片段
        
        Args:
            query: 查询文本
            top_k: 返回的片段数量
            
        Returns:
            相关法条片段列表，每个包含 text 和 source
        """
        if self.index is None:
            logger.warning("索引未加载，尝试加载...")
            if not self.load_index():
                return []
        
        try:
            # 生成查询向量
            query_embedding = self.model.encode([query])
            
            # 检索相似向量
            scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
            
            # 构建结果
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata):
                    metadata = self.metadata[idx]
                    results.append({
                        'text': metadata['text'],
                        'source': metadata['source'],
                        'score': float(score)
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"检索失败: {str(e)}")
            return []
    
    def is_index_available(self) -> bool:
        """
        检查索引是否可用
        
        Returns:
            索引是否可用
        """
        return (os.path.exists(self.index_path) and 
                os.path.exists(self.metadata_path) and 
                self.index is not None)


def test_rag_system():
    """测试 RAG 系统功能"""
    # 创建测试语料库
    test_corpus_dir = "test_corpus"
    os.makedirs(test_corpus_dir, exist_ok=True)
    
    # 创建测试文件
    test_content = """
    中华人民共和国刑法
    
    第一条 为了惩罚犯罪，保护人民，根据宪法，结合我国同犯罪作斗争的具体经验及实际情况，制定本法。
    
    第二条 中华人民共和国刑法的任务，是用刑罚同一切犯罪行为作斗争，以保卫国家安全，保卫人民民主专政的政权和社会主义制度，保护国有财产和劳动群众集体所有的财产，保护公民私人所有的财产，保护公民的人身权利、民主权利和其他权利，维护社会秩序、经济秩序，保障社会主义建设事业的顺利进行。
    """
    
    with open(os.path.join(test_corpus_dir, "刑法.txt"), 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # 测试 RAG 系统
    rag = RAGSystem(corpus_dir=test_corpus_dir, index_dir="test_index")
    
    # 构建索引
    success = rag.build_index()
    assert success, "索引构建失败"
    
    # 测试检索
    results = rag.retrieve_law_chunks("犯罪", top_k=2)
    assert len(results) > 0, "检索结果为空"
    
    print("RAG 系统测试通过")
    
    # 清理测试文件
    import shutil
    shutil.rmtree(test_corpus_dir)
    shutil.rmtree("test_index")


if __name__ == "__main__":
    test_rag_system() 