"""
文件处理工具模块
用于解析 PDF 和 Word 文档，提取文本内容
"""

import os
import PyPDF2
from docx import Document
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class FileProcessor:
    """文件处理器，支持 PDF 和 Word 文档解析"""
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> Optional[str]:
        """
        从 PDF 文件中提取文本
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            提取的文本内容，失败时返回 None
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text.strip()
        except Exception as e:
            logger.error(f"PDF 解析失败: {file_path}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_docx(file_path: str) -> Optional[str]:
        """
        从 Word 文档中提取文本
        
        Args:
            file_path: Word 文档路径
            
        Returns:
            提取的文本内容，失败时返回 None
        """
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Word 文档解析失败: {file_path}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_file(file_path: str) -> Optional[str]:
        """
        根据文件扩展名自动选择解析方法
        
        Args:
            file_path: 文件路径
            
        Returns:
            提取的文本内容，失败时返回 None
        """
        if not os.path.exists(file_path):
            logger.error(f"文件不存在: {file_path}")
            return None
        
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            return FileProcessor.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            return FileProcessor.extract_text_from_docx(file_path)
        else:
            logger.error(f"不支持的文件格式: {file_ext}")
            return None
    
    @staticmethod
    def get_supported_extensions() -> List[str]:
        """
        获取支持的文件扩展名
        
        Returns:
            支持的文件扩展名列表
        """
        return ['.pdf', '.docx', '.doc']


def test_file_processor():
    """测试文件处理器功能"""
    processor = FileProcessor()
    
    # 测试支持的文件格式
    supported_exts = processor.get_supported_extensions()
    assert '.pdf' in supported_exts
    assert '.docx' in supported_exts
    
    print("文件处理器测试通过")


if __name__ == "__main__":
    test_file_processor() 