#!/usr/bin/env python3
"""
测试RAG检索和文档显示功能
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from utils.rag_system import RAGSystem, retrieve_law_chunks

def test_rag_retrieval():
    """测试RAG检索功能"""
    print("=== 测试RAG检索功能 ===")
    
    # 检查索引是否存在
    rag = RAGSystem()
    if not rag.is_index_available():
        print("❌ 法条向量库未构建，请先运行 build_index")
        return False
    
    # 测试检索
    query = "合同解除的条件"
    print(f"查询: {query}")
    
    chunks = rag.retrieve_law_chunks(query, top_k=3)
    print(f"检索到 {len(chunks)} 个相关文档")
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- 文档 {i+1} ---")
        print(f"来源: {chunk['source']}")
        print(f"相似度: {chunk['score']:.3f}")
        print(f"内容: {chunk['text'][:100]}...")
    
    # 测试格式化显示
    formatted_chunks = rag.format_retrieved_chunks_for_display(chunks)
    print(f"\n=== 格式化后的文档 ===")
    for chunk in formatted_chunks:
        print(f"ID: {chunk['id']}")
        print(f"来源: {chunk['source']}")
        print(f"相似度: {chunk['score']:.3f}")
        print(f"预览: {chunk['preview']}")
        print("---")
    
    return True

def test_module_functions():
    """测试模块级函数"""
    print("\n=== 测试模块级函数 ===")
    
    query = "盗窃罪的处罚"
    print(f"查询: {query}")
    
    chunks = retrieve_law_chunks(query, top_k=2)
    print(f"检索到 {len(chunks)} 个相关文档")
    
    for chunk in chunks:
        print(f"来源: {chunk.source}")
        print(f"相似度: {chunk.score:.3f}")
        print(f"内容: {chunk.text[:80]}...")
        print("---")

if __name__ == "__main__":
    try:
        success = test_rag_retrieval()
        if success:
            test_module_functions()
            print("\n✅ 所有测试通过！")
        else:
            print("\n❌ 测试失败")
    except Exception as e:
        print(f"\n❌ 测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
