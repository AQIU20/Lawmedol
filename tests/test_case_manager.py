"""
案例管理器的单元测试
"""

import pytest
import tempfile
import shutil
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.case_manager import CaseManager


class TestCaseManager:
    """案例管理器测试类"""
    
    @pytest.fixture
    def temp_storage_dir(self):
        """创建临时存储目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def case_manager(self, temp_storage_dir):
        """创建案例管理器实例"""
        return CaseManager(storage_dir=temp_storage_dir)
    
    def test_create_case(self, case_manager):
        """测试创建案例"""
        case_meta = case_manager.create_case("测试案例")
        
        assert case_meta['title'] == "测试案例"
        assert 'id' in case_meta
        assert 'created_at' in case_meta
        assert 'file_list' in case_meta
        assert case_meta['file_list'] == []
        assert case_meta['total_chars'] == 0
    
    def test_get_all_cases_empty(self, case_manager):
        """测试获取空案例列表"""
        cases = case_manager.get_all_cases()
        
        assert cases == []
    
    def test_get_all_cases_with_data(self, case_manager):
        """测试获取有数据的案例列表"""
        # 创建多个案例
        case1 = case_manager.create_case("案例1")
        case2 = case_manager.create_case("案例2")
        
        cases = case_manager.get_all_cases()
        
        assert len(cases) == 2
        # 应该按创建时间倒序
        assert cases[0]['id'] == case2['id']
        assert cases[1]['id'] == case1['id']
    
    def test_get_case_meta(self, case_manager):
        """测试获取案例元数据"""
        case_meta = case_manager.create_case("测试案例")
        case_id = case_meta['id']
        
        retrieved_meta = case_manager.get_case_meta(case_id)
        
        assert retrieved_meta is not None
        assert retrieved_meta['title'] == "测试案例"
    
    def test_get_case_meta_nonexistent(self, case_manager):
        """测试获取不存在的案例元数据"""
        result = case_manager.get_case_meta("nonexistent")
        
        assert result is None
    
    def test_get_case_text_empty(self, case_manager):
        """测试获取空案例文本"""
        case_meta = case_manager.create_case("测试案例")
        case_id = case_meta['id']
        
        text = case_manager.get_case_text(case_id)
        
        assert text == ""
    
    def test_delete_case(self, case_manager):
        """测试删除案例"""
        case_meta = case_manager.create_case("测试案例")
        case_id = case_meta['id']
        
        # 验证案例存在
        assert case_manager.get_case_meta(case_id) is not None
        
        # 删除案例
        success = case_manager.delete_case(case_id)
        
        assert success is True
        assert case_manager.get_case_meta(case_id) is None
    
    def test_delete_nonexistent_case(self, case_manager):
        """测试删除不存在的案例"""
        success = case_manager.delete_case("nonexistent")
        
        assert success is False
    
    def test_add_dialog(self, case_manager):
        """测试添加对话记录"""
        case_meta = case_manager.create_case("测试案例")
        case_id = case_meta['id']
        
        success = case_manager.add_dialog(
            case_id, 
            "测试问题", 
            "测试回答", 
            [{"text": "引用1", "source": "来源1"}]
        )
        
        assert success is True
        
        # 验证对话历史
        history = case_manager.get_dialog_history(case_id)
        assert len(history) == 1
        assert history[0]['question'] == "测试问题"
        assert history[0]['answer'] == "测试回答"
        assert len(history[0]['citations']) == 1


if __name__ == "__main__":
    pytest.main([__file__]) 