"""
文件处理器的单元测试
"""

import pytest
import tempfile
import os
import sys

# 添加项目根目录到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.file_processor import FileProcessor


class TestFileProcessor:
    """文件处理器测试类"""
    
    def test_get_supported_extensions(self):
        """测试获取支持的文件扩展名"""
        processor = FileProcessor()
        extensions = processor.get_supported_extensions()
        
        assert '.pdf' in extensions
        assert '.docx' in extensions
        assert '.doc' in extensions
        assert len(extensions) == 3
    
    def test_extract_text_from_nonexistent_file(self):
        """测试从不存在文件提取文本"""
        processor = FileProcessor()
        result = processor.extract_text_from_file("nonexistent.pdf")
        
        assert result is None
    
    def test_extract_text_from_unsupported_format(self):
        """测试不支持的文件格式"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b"test content")
            temp_file = f.name
        
        try:
            processor = FileProcessor()
            result = processor.extract_text_from_file(temp_file)
            
            assert result is None
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__]) 