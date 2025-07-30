"""
文件处理工具模块
用于解析 PDF 和 Word 文档，提取文本内容
"""

import os
import PyPDF2
from docx import Document
from typing import Optional, List
import logging

# 尝试导入 docx2txt 来处理 .doc 文件
try:
    import docx2txt
    HAS_DOCX2TXT = True
except ImportError:
    HAS_DOCX2TXT = False

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
    def extract_text_from_doc(file_path: str) -> Optional[str]:
        """
        从旧版 Word 文档(.doc)中提取文本
        
        Args:
            file_path: Word 文档路径
            
        Returns:
            提取的文本内容，失败时返回 None
        """
        try:
            if HAS_DOCX2TXT:
                # 使用 docx2txt 处理 .doc 文件
                text = docx2txt.process(file_path)
                return text.strip() if text else None
            else:
                # 如果没有安装 docx2txt，返回提示信息
                logger.warning(f"未安装 docx2txt，无法处理 .doc 格式: {file_path}")
                return f"[注意：此文件为 .doc 格式，需要安装 docx2txt 库才能正确解析文本内容]"
        except Exception as e:
            logger.error(f"Word 文档解析失败: {file_path}, 错误: {str(e)}")
            return None
    
    @staticmethod
    def extract_text_from_txt(file_path: str) -> Optional[str]:
        """
        从文本文件中提取文本
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            提取的文本内容，失败时返回 None
        """
        try:
            # 尝试多种编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        return f.read().strip()
                except UnicodeDecodeError:
                    continue
            logger.error(f"无法解码文本文件: {file_path}")
            return None
        except Exception as e:
            logger.error(f"文本文件解析失败: {file_path}, 错误: {str(e)}")
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
        elif file_ext == '.docx':
            return FileProcessor.extract_text_from_docx(file_path)
        elif file_ext == '.doc':
            return FileProcessor.extract_text_from_doc(file_path)
        elif file_ext in ['.txt', '.md']:
            return FileProcessor.extract_text_from_txt(file_path)
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
        return ['.pdf', '.docx', '.doc', '.txt', '.md']


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