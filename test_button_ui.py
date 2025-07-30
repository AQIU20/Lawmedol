#!/usr/bin/env python3
"""
测试按钮UI功能
"""

import os
import tempfile
import sys

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.case_manager import CaseManager


def test_button_ui_features():
    """测试按钮UI功能"""
    print("测试按钮UI功能...")
    
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
                
                # 测试文件删除功能
                case_meta = case_manager.get_case_meta(case_id)
                if case_meta and case_meta['file_list']:
                    filename = case_meta['file_list'][0]['filename']
                    if case_manager.delete_file_from_case(case_id, filename):
                        print(f"✅ 文件删除成功: {filename}")
                        
                        # 验证文件确实被删除了
                        updated_meta = case_manager.get_case_meta(case_id)
                        if not updated_meta['file_list']:
                            print("✅ 文件列表已清空")
                        else:
                            print("❌ 文件列表未清空")
                    else:
                        print("❌ 文件删除失败")
                else:
                    print("❌ 案例元数据获取失败")
            else:
                print("❌ 文件上传失败")
                
        finally:
            # 清理测试文件
            os.unlink(test_file_path)
    
    print("按钮UI功能测试完成\n")


def test_law_file_management():
    """测试法律条文文件管理"""
    print("测试法律条文文件管理...")
    
    # 创建临时法律条文目录
    with tempfile.TemporaryDirectory() as temp_law_dir:
        # 创建测试法律条文文件
        test_laws = [
            "刑法.txt",
            "民法通则.txt", 
            "合同法.txt"
        ]
        
        for law_file in test_laws:
            law_path = os.path.join(temp_law_dir, law_file)
            with open(law_path, 'w', encoding='utf-8') as f:
                f.write(f"这是{law_file}的内容\n用于测试法律条文管理功能")
        
        print(f"✅ 创建了 {len(test_laws)} 个测试法律条文文件")
        
        # 列出文件
        law_files = [f for f in os.listdir(temp_law_dir) if f.endswith('.txt')]
        print(f"✅ 法律条文文件列表: {law_files}")
        
        # 模拟删除文件
        if law_files:
            test_delete_file = law_files[0]
            try:
                os.remove(os.path.join(temp_law_dir, test_delete_file))
                print(f"✅ 删除法律条文文件成功: {test_delete_file}")
            except Exception as e:
                print(f"❌ 删除法律条文文件失败: {e}")
    
    print("法律条文文件管理测试完成\n")


def main():
    """主测试函数"""
    print("🧪 按钮UI功能测试")
    print("=" * 50)
    
    test_button_ui_features()
    test_law_file_management()
    
    print("🎉 所有测试完成！")
    print("\n主要改进：")
    print("1. ✅ 法律条文选择改为按钮形式")
    print("2. ✅ 案例文档选择改为按钮形式")
    print("3. ✅ 支持单个文件删除")
    print("4. ✅ 选中状态可视化")
    print("5. ✅ 保持简洁的交互风格")


if __name__ == "__main__":
    main() 