"""
AI 客户端模块
用于调用 DeepSeek API 进行智能问答
"""

import os
import openai
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)


class AIClient:
    """AI 客户端，用于调用 DeepSeek API"""
    
    def __init__(self):
        """初始化 AI 客户端"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("DEEPSEEK_API_KEY 环境变量未设置")
        
        # 配置 OpenAI 客户端（兼容 DeepSeek）
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
    
    def generate_answer(self, 
                       case_text: str, 
                       law_chunks: List[Dict], 
                       user_question: str) -> Dict:
        """
        生成基于案例和法条的智能回答
        
        Args:
            case_text: 案例文本
            law_chunks: 相关法条片段
            user_question: 用户问题
            
        Returns:
            包含回答和引用依据的字典
        """
        try:
            # 构建上下文
            context = self._build_context(case_text, law_chunks)
            
            # 构建提示词
            prompt = self._build_prompt(context, user_question)
            
            # 调用 API
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            answer = response.choices[0].message.content
            
            # 解析回答和引用依据
            parsed_result = self._parse_answer(answer, law_chunks)
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"AI 回答生成失败: {str(e)}")
            return {
                'answer': f"抱歉，生成回答时出现错误: {str(e)}",
                'citations': [],
                'has_citations': False
            }
    
    def _build_context(self, case_text: str, law_chunks: List[Dict]) -> str:
        """
        构建上下文信息
        
        Args:
            case_text: 案例文本
            law_chunks: 相关法条片段
            
        Returns:
            格式化的上下文文本
        """
        context_parts = []
        
        # 添加案例文本
        if case_text:
            context_parts.append("【案例内容】")
            context_parts.append(case_text[:3000] + "..." if len(case_text) > 3000 else case_text)
        
        # 添加相关法条
        if law_chunks:
            context_parts.append("\n【相关法条】")
            for i, chunk in enumerate(law_chunks, 1):
                context_parts.append(f"{i}. {chunk['text']}")
                context_parts.append(f"   来源: {chunk['source']}")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, context: str, user_question: str) -> str:
        """
        构建完整的提示词
        
        Args:
            context: 上下文信息
            user_question: 用户问题
            
        Returns:
            完整的提示词
        """
        prompt = f"""
基于以下材料回答用户问题：

{context}

用户问题：{user_question}

请基于上述材料提供准确、详细的回答。如果材料中有相关信息，请在回答末尾列出"引用依据"，包含具体的法条或案例片段。如果材料中没有相关信息，请明确说明"未在材料中找到依据"。
"""
        return prompt.strip()
    
    def _get_system_prompt(self) -> str:
        """
        获取系统提示词
        
        Returns:
            系统提示词
        """
        return """你是一个专业的法律分析助手。你的任务是：

1. 基于提供的案例内容和相关法条，准确回答用户的法律问题
2. 回答必须基于提供的材料，不得编造信息
3. 在回答末尾列出"引用依据"，包含具体的法条条文或案例片段
4. 如果材料中没有相关信息，明确说明"未在材料中找到依据"
5. 使用专业、准确的法律术语
6. 保持客观、中立的分析态度"""
    
    def _parse_answer(self, answer: str, law_chunks: List[Dict]) -> Dict:
        """
        解析 AI 回答，提取引用依据
        
        Args:
            answer: AI 回答
            law_chunks: 相关法条片段
            
        Returns:
            解析后的结果
        """
        # 检查是否包含引用依据
        if "引用依据" in answer or "依据" in answer:
            # 简单提取引用部分
            citations = []
            for chunk in law_chunks:
                if chunk['text'][:50] in answer:  # 简单匹配
                    citations.append({
                        'text': chunk['text'][:200] + "..." if len(chunk['text']) > 200 else chunk['text'],
                        'source': chunk['source']
                    })
            
            return {
                'answer': answer,
                'citations': citations,
                'has_citations': len(citations) > 0
            }
        else:
            return {
                'answer': answer,
                'citations': [],
                'has_citations': False
            }


def test_ai_client():
    """测试 AI 客户端功能"""
    try:
        # 检查环境变量
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            print("跳过 AI 客户端测试：DEEPSEEK_API_KEY 未设置")
            return
        
        client = AIClient()
        
        # 测试数据
        case_text = "被告人张三因盗窃罪被判处有期徒刑三年。"
        law_chunks = [
            {
                'text': '第二百六十四条 盗窃公私财物，数额较大的，处三年以下有期徒刑、拘役或者管制，并处或者单处罚金。',
                'source': '刑法.txt'
            }
        ]
        user_question = "张三的判决是否合理？"
        
        # 测试生成回答
        result = client.generate_answer(case_text, law_chunks, user_question)
        
        assert 'answer' in result
        assert 'citations' in result
        assert 'has_citations' in result
        
        print("AI 客户端测试通过")
        
    except Exception as e:
        print(f"AI 客户端测试失败: {str(e)}")


if __name__ == "__main__":
    test_ai_client() 