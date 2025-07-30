#!/usr/bin/env python3
"""
测试修复后的功能
"""

import os
import tempfile
import sys

# 添加后端路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.file_processor import FileProcessor
from utils.case_manager import CaseManager
from utils.rag_system import RAGSystem


def test_file_processor_fixes():
    """测试文件处理器的修复"""
    print("测试文件处理器修复...")
    
    processor = FileProcessor()
    
    # 测试支持的文件格式
    supported_exts = processor.get_supported_extensions()
    print(f"支持的文件格式: {supported_exts}")
    
    # 创建测试文本文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("这是测试法律条文\n包含刑法条文\n用于测试文件处理")
        test_txt_path = f.name
    
    # 创建测试Markdown文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
        f.write("# 民法条文\n\n## 第一条\n这是民法条文内容")
        test_md_path = f.name
    
    try:
        # 测试文本文件提取
        txt_text = processor.extract_text_from_file(test_txt_path)
        if txt_text:
            print(f"✅ 文本文件提取成功: {len(txt_text)} 字符")
        else:
            print("❌ 文本文件提取失败")
        
        # 测试Markdown文件提取
        md_text = processor.extract_text_from_file(test_md_path)
        if md_text:
            print(f"✅ Markdown文件提取成功: {len(md_text)} 字符")
        else:
            print("❌ Markdown文件提取失败")
            
    finally:
        # 清理测试文件
        os.unlink(test_txt_path)
        os.unlink(test_md_path)
    
    print("文件处理器修复测试完成\n")


def test_case_manager_fixes():
    """测试案例管理器的修复"""
    print("测试案例管理器修复...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        case_manager = CaseManager(storage_dir=temp_dir)
        
        # 创建测试案例
        case_meta = case_manager.create_case("修复测试案例")
        case_id = case_meta['id']
        print(f"✅ 创建案例成功: {case_id}")
        
        # 创建测试文本文件
        test_content = "这是测试案例文件内容\n包含法律条文\n用于测试上传功能"
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
    
    print("案例管理器修复测试完成\n")


def test_rag_system_fixes():
    """测试RAG系统的修复"""
    print("测试RAG系统修复...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建法律条文目录
        corpus_dir = os.path.join(temp_dir, "legal_corpus")
        os.makedirs(corpus_dir, exist_ok=True)
        
        # 创建测试法律条文文件
        law_content = """
        中华人民共和国刑法
        
        第一条 为了惩罚犯罪，保护人民，根据宪法，结合我国同犯罪作斗争的具体经验及实际情况，制定本法。
        
        第二条 中华人民共和国刑法的任务，是用刑罚同一切犯罪行为作斗争，以保卫国家安全，保卫人民民主专政的政权和社会主义制度，保护国有财产和劳动群众集体所有的财产，保护公民私人所有的财产，保护公民的人身权利、民主权利和其他权利，维护社会秩序、经济秩序，保障社会主义建设事业的顺利进行。
        """
        
        with open(os.path.join(corpus_dir, "刑法.txt"), 'w', encoding='utf-8') as f:
            f.write(law_content)
        
        # 测试RAG系统
        rag_system = RAGSystem(corpus_dir=corpus_dir, index_dir=temp_dir)
        
        # 测试构建索引
        success = rag_system.build_index()
        if success:
            print("✅ 索引构建成功")
            
            # 测试检索
            results = rag_system.retrieve_law_chunks("犯罪", top_k=2)
            if results:
                print(f"✅ 检索成功: 找到 {len(results)} 个相关片段")
            else:
                print("❌ 检索失败")
        else:
            print("❌ 索引构建失败")
    
    print("RAG系统修复测试完成\n")


def main():
    """主测试函数"""
    print("🧪 修复功能测试")
    print("=" * 50)
    
    test_file_processor_fixes()
    test_case_manager_fixes()
    test_rag_system_fixes()
    
    print("🎉 所有修复测试完成！")
    print("\n主要修复：")
    print("1. ✅ 支持文本文件(.txt)和Markdown文件(.md)")
    print("2. ✅ 改进文件编码处理")
    print("3. ✅ 确保目录存在")
    print("4. ✅ 添加法律条文上传功能")
    print("5. ✅ 改进错误处理和用户反馈")


if __name__ == "__main__":
    main() 