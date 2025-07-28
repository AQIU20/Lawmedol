"""
案例管理器模块
用于管理案例的创建、存储和检索
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict, Optional
import logging
from .file_processor import FileProcessor

logger = logging.getLogger(__name__)


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
            uploaded_file: Streamlit 上传的文件对象
            
        Returns:
            上传是否成功
        """
        try:
            case_dir = os.path.join(self.cases_dir, f"case_{case_id}")
            if not os.path.exists(case_dir):
                logger.error(f"案例不存在: {case_id}")
                return False
            
            # 保存原始文件
            files_dir = os.path.join(case_dir, "files")
            file_path = os.path.join(files_dir, uploaded_file.name)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # 提取文本
            file_processor = FileProcessor()
            extracted_text = file_processor.extract_text_from_file(file_path)
            
            if extracted_text is None:
                logger.error(f"文件文本提取失败: {uploaded_file.name}")
                return False
            
            # 追加到案例文本
            current_text = self.get_case_text(case_id)
            new_text = current_text + "\n\n" + extracted_text if current_text else extracted_text
            
            # 更新案例文本
            self._save_case_text(case_id, new_text)
            
            # 更新元数据
            case_meta = self.get_case_meta(case_id)
            if case_meta:
                case_meta['file_list'].append(uploaded_file.name)
                case_meta['total_chars'] = len(new_text)
                case_meta['updated_at'] = datetime.now().isoformat()
                self._save_case_meta(case_id, case_meta)
            
            logger.info(f"文件上传成功: {uploaded_file.name} -> case_{case_id}")
            return True
            
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            return False
    
    def add_dialog(self, case_id: str, question: str, answer: str, citations: List[Dict] = None) -> bool:
        """
        添加对话记录
        
        Args:
            case_id: 案例 ID
            question: 用户问题
            answer: AI 回答
            citations: 引用依据
            
        Returns:
            添加是否成功
        """
        try:
            dialog_log = self._load_dialog_log(case_id)
            
            dialog_entry = {
                'timestamp': datetime.now().isoformat(),
                'question': question,
                'answer': answer,
                'citations': citations or []
            }
            
            dialog_log.append(dialog_entry)
            self._save_dialog_log(case_id, dialog_log)
            
            logger.info(f"对话记录添加成功: case_{case_id}")
            return True
            
        except Exception as e:
            logger.error(f"添加对话记录失败: {str(e)}")
            return False
    
    def get_dialog_history(self, case_id: str) -> List[Dict]:
        """
        获取对话历史
        
        Args:
            case_id: 案例 ID
            
        Returns:
            对话历史列表
        """
        return self._load_dialog_log(case_id)
    
    def delete_case(self, case_id: str) -> bool:
        """
        删除案例
        
        Args:
            case_id: 案例 ID
            
        Returns:
            删除是否成功
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
    
    def _generate_case_id(self) -> str:
        """
        生成唯一的案例 ID
        
        Returns:
            案例 ID
        """
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
        """保存对话日志"""
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
    import shutil
    
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
        
        # 测试获取案例文本
        text = manager.get_case_text(case_id)
        assert text == ""
        
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
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    test_case_manager() 