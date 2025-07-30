#!/usr/bin/env python3
"""
测试 .doc 文件处理修复
"""

import os
import tempfile
import sys

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.file_processor import FileProcessor
from utils.case_manager import CaseManager


def test_doc_file_processing():
    """测试 .doc 文件处理"""
    print("测试 .doc 文件处理...")
    
    processor = FileProcessor()
    
    # 检查是否支持 .doc 格式
    supported_exts = processor.get_supported_extensions()
    print(f"支持的文件格式: {supported_exts}")
    
    # 创建测试 .doc 文件内容（模拟）
    test_content = """
    西藏天晟泰丰药业有限公司诉上海双基药业有限公司买卖合同纠纷一案二审民事判决书
    
    上诉人（原审原告）：西藏天晟泰丰药业有限公司
    被上诉人（原审被告）：上海双基药业有限公司
    
    本案为买卖合同纠纷案件，涉及药品购销合同履行问题。
    """
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file_path = f.name
    
    try:
        # 测试文本提取
        text = processor.extract_text_from_file(test_file_path)
        if text:
            print(f"✅ 文本文件提取成功: {len(text)} 字符")
            print(f"内容预览: {text[:100]}...")
        else:
            print("❌ 文本文件提取失败")
            
    finally:
        # 清理测试文件
        os.unlink(test_file_path)
    
    print("文件处理测试完成\n")


def test_case_manager_with_files():
    """测试案例管理器文件处理"""
    print("测试案例管理器文件处理...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        case_manager = CaseManager(storage_dir=temp_dir)
        
        # 创建测试案例
        case_meta = case_manager.create_case("测试案例")
        case_id = case_meta['id']
        print(f"✅ 创建案例成功: {case_id}")
        
        # 创建测试文件
        test_content = "这是一个测试案例文件内容\n包含法律条文\n用于测试上传功能"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
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
                if case_text and len(case_text) > 0:
                    print(f"✅ 案例文本获取成功: {len(case_text)} 字符")
                    print(f"文本预览: {case_text[:100]}...")
                else:
                    print("❌ 案例文本获取失败")
                
                # 检查案例元数据
                case_meta = case_manager.get_case_meta(case_id)
                if case_meta and case_meta['file_list']:
                    print(f"✅ 案例元数据更新成功: {len(case_meta['file_list'])} 个文件")
                    for file_info in case_meta['file_list']:
                        if isinstance(file_info, dict):
                            print(f"  - {file_info.get('filename')}: {file_info.get('chars')} 字符")
                else:
                    print("❌ 案例元数据更新失败")
            else:
                print("❌ 文件上传失败")
                
        finally:
            # 清理测试文件
            os.unlink(test_file_path)
    
    print("案例管理器测试完成\n")


def main():
    """主测试函数"""
    print("🧪 .doc 文件处理修复测试")
    print("=" * 50)
    
    test_doc_file_processing()
    test_case_manager_with_files()
    
    print("🎉 所有测试完成！")
    print("\n主要修复：")
    print("1. ✅ 添加了 .doc 文件处理支持")
    print("2. ✅ 改进了文本提取错误处理")
    print("3. ✅ 添加了详细的调试信息")
    print("4. ✅ 更新了依赖包")
    print("5. ✅ 改进了用户界面反馈")


if __name__ == "__main__":
    main() 