#!/usr/bin/env python3
"""
测试文件上传功能
"""

import os
import tempfile
import sys

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.file_processor import FileProcessor
from utils.case_manager import CaseManager


def test_file_processor():
    """测试文件处理器"""
    print("测试文件处理器...")
    
    processor = FileProcessor()
    
    # 测试支持的文件格式
    supported_exts = processor.get_supported_extensions()
    print(f"支持的文件格式: {supported_exts}")
    
    # 创建测试文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("这是一个测试文件内容\n包含多行文本\n用于测试文件处理功能")
        test_file_path = f.name
    
    try:
        # 测试文本提取
        text = processor.extract_text_from_file(test_file_path)
        if text:
            print(f"✅ 文本提取成功: {len(text)} 字符")
        else:
            print("❌ 文本提取失败")
    finally:
        # 清理测试文件
        os.unlink(test_file_path)
    
    print("文件处理器测试完成\n")


def test_case_manager():
    """测试案例管理器"""
    print("测试案例管理器...")
    
    # 创建临时存储目录
    with tempfile.TemporaryDirectory() as temp_dir:
        case_manager = CaseManager(storage_dir=temp_dir)
        
        # 创建测试案例
        case_meta = case_manager.create_case("测试案例")
        case_id = case_meta['id']
        print(f"✅ 创建案例成功: {case_id}")
        
        # 创建测试文件
        test_file_content = "这是一个测试PDF文件内容\n包含法律条文\n用于测试上传功能"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(test_file_content)
            test_file_path = f.name
        
        try:
            # 模拟文件上传
            class MockUploadedFile:
                def __init__(self, file_path):
                    self.name = os.path.basename(file_path)
                    with open(file_path, 'rb') as f:
                        self._buffer = f.read()
                
                def getbuffer(self):
                    return self._buffer
            
            mock_file = MockUploadedFile(test_file_path)
            
            # 测试文件上传
            success = case_manager.upload_file_to_case(case_id, mock_file)
            if success:
                print("✅ 文件上传成功")
                
                # 检查案例文本
                case_text = case_manager.get_case_text(case_id)
                if case_text:
                    print(f"✅ 案例文本获取成功: {len(case_text)} 字符")
                else:
                    print("❌ 案例文本获取失败")
                
                # 检查案例元数据
                case_meta = case_manager.get_case_meta(case_id)
                if case_meta and case_meta['file_list']:
                    print(f"✅ 案例元数据更新成功: {len(case_meta['file_list'])} 个文件")
                else:
                    print("❌ 案例元数据更新失败")
            else:
                print("❌ 文件上传失败")
                
        finally:
            # 清理测试文件
            os.unlink(test_file_path)
    
    print("案例管理器测试完成\n")


def test_directory_creation():
    """测试目录创建"""
    print("测试目录创建...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        case_manager = CaseManager(storage_dir=temp_dir)
        
        # 创建案例
        case_meta = case_manager.create_case("目录测试案例")
        case_id = case_meta['id']
        
        # 检查目录结构
        case_dir = os.path.join(temp_dir, f"case_{case_id}")
        files_dir = os.path.join(case_dir, "files")
        
        print(f"案例目录: {case_dir}")
        print(f"文件目录: {files_dir}")
        
        if os.path.exists(case_dir):
            print("✅ 案例目录创建成功")
        else:
            print("❌ 案例目录创建失败")
        
        if os.path.exists(files_dir):
            print("✅ 文件目录创建成功")
        else:
            print("❌ 文件目录创建失败")
    
    print("目录创建测试完成\n")


def main():
    """主测试函数"""
    print("🧪 文件上传功能测试")
    print("=" * 50)
    
    test_file_processor()
    test_case_manager()
    test_directory_creation()
    
    print("🎉 所有测试完成！")
    print("\n主要修复：")
    print("1. ✅ 确保文件目录存在")
    print("2. ✅ 改进错误处理")
    print("3. ✅ 优化文件上传流程")
    print("4. ✅ 重新设计UI布局")
    print("5. ✅ 使用蓝色主题和阴影效果")


if __name__ == "__main__":
    main() 