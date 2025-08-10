"""
案例管理器模块
用于管理案例的创建、存储和检索
"""

from __future__ import annotations
import os
import json
import shutil
import re
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from io import BytesIO, BufferedReader
import logging

from .file_processor import FileProcessor

logger = logging.getLogger(__name__)

# -----------------------------
# 上传健壮性工具
# -----------------------------

_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')

def _safe_filename(name: str) -> str:
    """清洗文件名，避免非法字符/路径注入"""
    name = (name or "file").strip()
    name = _ILLEGAL.sub("_", name)
    return name or "file"

def _write_uploaded(target: Path, uploaded_file) -> int:
    """
    将上传内容写入到 target。
    兼容多种 Streamlit / file-like 对象：
    - 有 getbuffer()：直接写入
    - 有 read()：分块写入
    - bytes / bytearray：直接写
    返回写入字节数（<=0 表示失败）
    """
    target.parent.mkdir(parents=True, exist_ok=True)
    size = 0

    # bytes / bytearray
    if isinstance(uploaded_file, (bytes, bytearray)):
        with open(target, "wb") as f:
            f.write(uploaded_file)
        return len(uploaded_file)

    # Streamlit UploadedFile 常见：getbuffer()
    try:
        buf = uploaded_file.getbuffer()
        with open(target, "wb") as f:
            f.write(buf)
        return len(buf)
    except Exception:
        pass

    # 退回到 read() 流式写入
    try:
        with open(target, "wb") as f:
            while True:
                chunk = uploaded_file.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                size += len(chunk)
        return size
    except Exception:
        return 0


class CaseManager:
    """案例管理器，负责案例的 CRUD 操作"""
    
    def __init__(self, storage_dir: str = "storage"):
        """
        初始化案例管理器
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        self.cases_dir = os.path.join(storage_dir, "cases")
        os.makedirs(self.cases_dir, exist_ok=True)
    
    def create_case(self, title: str) -> Dict:
        """
        创建新案例
        
        Args:
            title: 案例标题
            
        Returns:
            创建的案例信息
        """
        try:
            # 生成案例 ID
            case_id = self._generate_case_id()
            case_dir = os.path.join(self.cases_dir, f"case_{case_id}")
            
            # 创建案例目录
            os.makedirs(case_dir, exist_ok=True)
            os.makedirs(os.path.join(case_dir, "files"), exist_ok=True)
            
            # 创建案例元数据
            case_meta = {
                'id': case_id,
                'title': title,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'file_list': [],
                'total_chars': 0
            }
            
            # 保存元数据
            self._save_case_meta(case_id, case_meta)
            
            # 创建空文件
            self._save_case_text(case_id, "")
            self._save_dialog_log(case_id, [])
            
            logger.info(f"创建案例成功: {title} (ID: {case_id})")
            return case_meta
            
        except Exception as e:
            logger.error(f"创建案例失败: {str(e)}")
            raise
    
    def get_all_cases(self) -> List[Dict]:
        """
        获取所有案例列表
        
        Returns:
            案例列表，按创建时间倒序
        """
        cases = []
        
        try:
            if not os.path.exists(self.cases_dir):
                return cases
            
            for case_dir in os.listdir(self.cases_dir):
                if case_dir.startswith("case_"):
                    case_id = case_dir.replace("case_", "")
                    case_meta = self.get_case_meta(case_id)
                    if case_meta:
                        cases.append(case_meta)
            
            # 按创建时间倒序排序
            cases.sort(key=lambda x: x['created_at'], reverse=True)
            return cases
            
        except Exception as e:
            logger.error(f"获取案例列表失败: {str(e)}")
            return []
    
    def get_case_meta(self, case_id: str) -> Optional[Dict]:
        """
        获取案例元数据
        
        Args:
            case_id: 案例 ID
            
        Returns:
            案例元数据，不存在时返回 None
        """
        try:
            meta_path = os.path.join(self.cases_dir, f"case_{case_id}", "meta.json")
            if not os.path.exists(meta_path):
                return None
            
            with open(meta_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"获取案例元数据失败: {case_id}, 错误: {str(e)}")
            return None
    
    def get_case_text(self, case_id: str) -> str:
        """
        获取案例完整文本
        
        Args:
            case_id: 案例 ID
            
        Returns:
            案例文本内容
        """
        try:
            text_path = os.path.join(self.cases_dir, f"case_{case_id}", "full_text.txt")
            if not os.path.exists(text_path):
                return ""
            
            with open(text_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"获取案例文本失败: {case_id}, 错误: {str(e)}")
            return ""
    
    def upload_file_to_case(self, case_id: str, uploaded_file) -> bool:
        """
        上传文件到案例
        
        Args:
            case_id: 案例 ID
            uploaded_file: Streamlit 上传的文件对象 / file-like / bytes
            
        Returns:
            上传是否成功
        """
        try:
            case_dir = os.path.join(self.cases_dir, f"case_{case_id}")
            if not os.path.exists(case_dir):
                logger.error(f"案例不存在: {case_id}")
                return False
            
            # 保存原始文件目录
            files_dir = os.path.join(case_dir, "files")
            os.makedirs(files_dir, exist_ok=True)

            # 安全文件名 + 去重
            raw_name = getattr(uploaded_file, "name", "file")
            safe_name = _safe_filename(raw_name)
            base, ext = os.path.splitext(safe_name)
            target = Path(files_dir) / safe_name
            n = 1
            while target.exists():
                target = Path(files_dir) / f"{base}({n}){ext}"
                n += 1

            # 写入文件（兼容多种上传对象）
            bytes_written = _write_uploaded(target, uploaded_file)
            if bytes_written <= 0:
                logger.error(f"写入上传文件失败: {safe_name}")
                return False
            
            # 提取文本
            extracted_text = ""
            try:
                file_processor = FileProcessor()
                extracted_text = file_processor.extract_text_from_file(str(target)) or ""
                logger.info(f"文本提取结果: {target.name} -> {len(extracted_text)} 字符")
            except Exception as e:
                logger.error(f"文件文本提取失败: {target.name} -> {e}")
                extracted_text = ""

            # 追加到案例文本
            current_text = self.get_case_text(case_id)
            if extracted_text:
                new_text = current_text + "\n\n" + extracted_text if current_text else extracted_text
                self._save_case_text(case_id, new_text)
                total_chars = len(new_text)
            else:
                total_chars = len(current_text)

            # 更新元数据
            case_meta = self.get_case_meta(case_id) or {}
            file_list = case_meta.get('file_list', [])
            file_list.append({
                'filename': target.name,
                'path': str(target),
                'size': bytes_written,
                'added_at': datetime.now().isoformat(),
                'chars': len(extracted_text),
            })
            case_meta['file_list'] = file_list
            case_meta['total_chars'] = total_chars
            case_meta['updated_at'] = datetime.now().isoformat()
            self._save_case_meta(case_id, case_meta)
            
            logger.info(f"文件上传成功: {target.name} ({bytes_written} bytes) -> case_{case_id}")
            return True
            
        except Exception as e:
            logger.exception(f"文件上传失败: {str(e)}")
            return False
    
    def add_dialog(self, case_id: str, question: str, answer: str, citations: List[Dict] = None, retrieved_chunks: List[Dict] = None) -> bool:
        """
        添加对话记录
        
        Args:
            case_id: 案例ID
            question: 用户问题
            answer: AI回答
            citations: 引用依据
            retrieved_chunks: 检索到的相关文档chunks
        """
        try:
            dialog_log = self._load_dialog_log(case_id)
            
            dialog_entry = {
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'answer': answer,
                'citations': citations or [],
                'retrieved_chunks': retrieved_chunks or []  # 添加检索到的文档chunks
            }
            
            dialog_log.append(dialog_entry)
            self._save_dialog_log(case_id, dialog_log)
            
            logger.info(f"对话记录添加成功: case_{case_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加对话记录失败: {str(e)}")
            return False
    
    def get_dialog_history(self, case_id: str) -> List[Dict]:
        """获取对话历史"""
        return self._load_dialog_log(case_id)
    
    def delete_case(self, case_id: str) -> bool:
        """
        删除案例
        """
        try:
            case_dir = os.path.join(self.cases_dir, f"case_{case_id}")
            if os.path.exists(case_dir):
                shutil.rmtree(case_dir)
                logger.info(f"案例删除成功: case_{case_id}")
                return True
            else:
                logger.warning(f"案例不存在: case_{case_id}")
                return False
                
        except Exception as e:
            logger.error(f"删除案例失败: {str(e)}")
            return False
    
    def delete_file_from_case(self, case_id: str, filename: str) -> bool:
        """
        从案例中删除指定文件
        
        Args:
            case_id: 案例 ID
            filename: 文件名
            
        Returns:
            删除是否成功
        """
        try:
            case_dir = os.path.join(self.cases_dir, f"case_{case_id}")
            if not os.path.exists(case_dir):
                logger.error(f"案例不存在: {case_id}")
                return False
            
            # 找到要删除的文件
            files_dir = os.path.join(case_dir, "files")
            file_path = os.path.join(files_dir, filename)
            
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {filename}")
                return False
            
            # 删除文件
            os.remove(file_path)
            
            # 重新构建案例文本（排除已删除的文件）
            case_meta = self.get_case_meta(case_id)
            if case_meta:
                file_list = case_meta.get('file_list', [])
                # 移除被删除的文件
                file_list = [f for f in file_list if f.get('filename') != filename]
                case_meta['file_list'] = file_list
                
                # 重新构建文本内容
                new_text = ""
                for file_info in file_list:
                    file_path = file_info.get('path')
                    if file_path and os.path.exists(file_path):
                        try:
                            file_processor = FileProcessor()
                            extracted_text = file_processor.extract_text_from_file(file_path) or ""
                            if extracted_text:
                                new_text += "\n\n" + extracted_text if new_text else extracted_text
                        except Exception as e:
                            logger.warning(f"重新提取文件文本失败: {file_path} -> {e}")
                
                # 更新案例文本和元数据
                self._save_case_text(case_id, new_text)
                case_meta['total_chars'] = len(new_text)
                case_meta['updated_at'] = datetime.now().isoformat()
                self._save_case_meta(case_id, case_meta)
            
            logger.info(f"文件删除成功: {filename} -> case_{case_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除文件失败: {str(e)}")
            return False
    
    def _generate_case_id(self) -> str:
        """生成唯一的案例 ID"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _save_case_meta(self, case_id: str, meta: Dict):
        """保存案例元数据"""
        meta_path = os.path.join(self.cases_dir, f"case_{case_id}", "meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
    
    def _save_case_text(self, case_id: str, text: str):
        """保存案例文本"""
        text_path = os.path.join(self.cases_dir, f"case_{case_id}", "full_text.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
    
    def _save_dialog_log(self, case_id: str, dialog_log: List[Dict]):
        """保存对话日志（整写）"""
        log_path = os.path.join(self.cases_dir, f"case_{case_id}", "dialog.jsonl")
        with open(log_path, 'w', encoding='utf-8') as f:
            for entry in dialog_log:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    
    def _load_dialog_log(self, case_id: str) -> List[Dict]:
        """加载对话日志"""
        log_path = os.path.join(self.cases_dir, f"case_{case_id}", "dialog.jsonl")
        if not os.path.exists(log_path):
            return []
        
        dialog_log = []
        try:
            with open(log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        dialog_log.append(json.loads(line))
        except Exception as e:
            logger.error(f"加载对话日志失败: {str(e)}")
        
        return dialog_log


def test_case_manager():
    """测试案例管理器功能"""
    import tempfile
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        manager = CaseManager(storage_dir=temp_dir)
        
        # 测试创建案例
        case_meta = manager.create_case("测试案例")
        assert case_meta['title'] == "测试案例"
        assert 'id' in case_meta
        
        case_id = case_meta['id']
        
        # 测试获取案例列表
        cases = manager.get_all_cases()
        assert len(cases) == 1
        assert cases[0]['id'] == case_id
        
        # 测试获取/初始文本
        text = manager.get_case_text(case_id)
        assert text == ""
        
        # 构造一个伪上传对象
        from io import BytesIO
        content = "第一条 为了……这是测试文本。".encode("utf-8")
        fake = BytesIO(content)
        fake.name = "测试.txt"
        ok = manager.upload_file_to_case(case_id, fake)
        assert ok
        
        # 校验文本已合入
        text2 = manager.get_case_text(case_id)
        assert "第一条" in text2
        
        # 测试添加对话
        success = manager.add_dialog(case_id, "测试问题", "测试回答")
        assert success
        
        # 测试获取对话历史
        history = manager.get_dialog_history(case_id)
        assert len(history) == 1
        assert history[0]['question'] == "测试问题"
        
        # 测试删除案例
        success = manager.delete_case(case_id)
        assert success
        
        cases = manager.get_all_cases()
        assert len(cases) == 0
        
        print("案例管理器测试通过")
        
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    test_case_manager()
