"""
Legal Analyzer - Streamlit 主应用
法律案例分析工具的主界面
"""

import streamlit as st
import os
import sys
from datetime import datetime
import logging

# 添加当前目录到 Python 路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.case_manager import CaseManager
from utils.rag_system import RAGSystem
from utils.ai_client import AIClient
from utils.file_processor import FileProcessor

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 页面配置
st.set_page_config(
    page_title="Legal Analyzer - 法律案例分析工具",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .case-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .dialog-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .citation-box {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin-top: 0.5rem;
        border-left: 3px solid #1f77b4;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """初始化会话状态"""
    if 'selected_case_id' not in st.session_state:
        st.session_state.selected_case_id = None
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'ai_client' not in st.session_state:
        st.session_state.ai_client = None
    if 'case_manager' not in st.session_state:
        st.session_state.case_manager = None


def initialize_components():
    """初始化组件"""
    try:
        # 初始化案例管理器
        if st.session_state.case_manager is None:
            st.session_state.case_manager = CaseManager()
        
        # 初始化 RAG 系统
        if st.session_state.rag_system is None:
            st.session_state.rag_system = RAGSystem()
            # 尝试加载索引
            if not st.session_state.rag_system.load_index():
                st.warning("法条向量库未构建，请先构建索引")
        
        # 初始化 AI 客户端
        if st.session_state.ai_client is None:
            try:
                st.session_state.ai_client = AIClient()
            except ValueError as e:
                st.error(f"AI 客户端初始化失败: {str(e)}")
                st.session_state.ai_client = None
                
    except Exception as e:
        st.error(f"组件初始化失败: {str(e)}")


def render_header():
    """渲染页面头部"""
    st.markdown('<h1 class="main-header">⚖️ Legal Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">法律案例分析工具</p>', unsafe_allow_html=True)


def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("📁 案例管理")
    
    # 新建案例
    st.sidebar.subheader("新建案例")
    new_case_title = st.sidebar.text_input("案例标题", placeholder="请输入案例标题")
    if st.sidebar.button("➕ 创建新案例", type="primary"):
        if new_case_title.strip():
            try:
                case_meta = st.session_state.case_manager.create_case(new_case_title.strip())
                st.success(f"案例 '{new_case_title}' 创建成功！")
                st.rerun()
            except Exception as e:
                st.error(f"创建案例失败: {str(e)}")
        else:
            st.warning("请输入案例标题")
    
    st.sidebar.divider()
    
    # 案例列表
    st.sidebar.subheader("案例列表")
    cases = st.session_state.case_manager.get_all_cases()
    
    if not cases:
        st.sidebar.info("暂无案例，请先创建案例")
    else:
        for case in cases:
            case_id = case['id']
            title = case['title']
            created_at = datetime.fromisoformat(case['created_at']).strftime("%Y-%m-%d %H:%M")
            file_count = len(case['file_list'])
            
            # 创建案例卡片
            with st.sidebar.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"📄 {title}", key=f"case_{case_id}"):
                        st.session_state.selected_case_id = case_id
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"delete_{case_id}"):
                        if st.session_state.case_manager.delete_case(case_id):
                            st.success("案例删除成功")
                            if st.session_state.selected_case_id == case_id:
                                st.session_state.selected_case_id = None
                            st.rerun()
                        else:
                            st.error("删除失败")
                
                st.caption(f"📅 {created_at} | 📎 {file_count} 个文件")
    
    st.sidebar.divider()
    
    # 重建法条向量库
    st.sidebar.subheader("🔧 系统设置")
    if st.sidebar.button("🔨 重建法条向量库"):
        with st.spinner("正在重建法条向量库..."):
            try:
                if st.session_state.rag_system.build_index():
                    st.success("法条向量库重建成功！")
                else:
                    st.error("法条向量库重建失败")
            except Exception as e:
                st.error(f"重建失败: {str(e)}")


def render_main_content():
    """渲染主要内容区域"""
    if st.session_state.selected_case_id is None:
        render_welcome_page()
    else:
        render_case_page()


def render_welcome_page():
    """渲染欢迎页面"""
    st.markdown("""
    ## 🎯 欢迎使用 Legal Analyzer
    
    ### 主要功能
    - **📁 案例管理**: 创建和管理法律案例
    - **📄 文档解析**: 支持 PDF 和 Word 文档自动解析
    - **🤖 智能问答**: 基于案例内容和相关法条的 AI 问答
    - **📚 法条检索**: 本地 RAG 向量库，快速检索相关法律条文
    
    ### 使用步骤
    1. **创建案例**: 在左侧输入案例标题并创建
    2. **上传文件**: 选择案例后上传判决书等文档
    3. **智能问答**: 在右侧输入问题，获得基于材料的专业回答
    
    ### 系统状态
    """)
    
    # 显示系统状态
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("案例数量", len(st.session_state.case_manager.get_all_cases()))
    
    with col2:
        rag_status = "✅ 已构建" if st.session_state.rag_system.is_index_available() else "❌ 未构建"
        st.metric("法条向量库", rag_status)
    
    with col3:
        ai_status = "✅ 已连接" if st.session_state.ai_client else "❌ 未连接"
        st.metric("AI 服务", ai_status)


def render_case_page():
    """渲染案例页面"""
    case_id = st.session_state.selected_case_id
    case_meta = st.session_state.case_manager.get_case_meta(case_id)
    
    if not case_meta:
        st.error("案例不存在")
        return
    
    # 页面标题
    st.title(f"📄 {case_meta['title']}")
    
    # 案例信息
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("文件数量", len(case_meta['file_list']))
    with col2:
        st.metric("文本字数", case_meta['total_chars'])
    with col3:
        created_at = datetime.fromisoformat(case_meta['created_at']).strftime("%Y-%m-%d")
        st.metric("创建时间", created_at)
    with col4:
        updated_at = datetime.fromisoformat(case_meta['updated_at']).strftime("%Y-%m-%d")
        st.metric("更新时间", updated_at)
    
    # 主要内容区域
    col1, col2 = st.columns([1, 2])
    
    with col1:
        render_file_upload_section(case_id)
        render_file_list_section(case_meta)
    
    with col2:
        render_qa_section(case_id)


def render_file_upload_section(case_id):
    """渲染文件上传区域"""
    st.subheader("📤 上传文件")
    
    uploaded_files = st.file_uploader(
        "选择 PDF 或 Word 文档",
        type=['pdf', 'docx', 'doc'],
        accept_multiple_files=True,
        key=f"upload_{case_id}"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            if st.button(f"上传 {uploaded_file.name}", key=f"upload_btn_{uploaded_file.name}"):
                with st.spinner(f"正在处理 {uploaded_file.name}..."):
                    if st.session_state.case_manager.upload_file_to_case(case_id, uploaded_file):
                        st.success(f"文件 {uploaded_file.name} 上传成功！")
                        st.rerun()
                    else:
                        st.error(f"文件 {uploaded_file.name} 上传失败")


def render_file_list_section(case_meta):
    """渲染文件列表区域"""
    st.subheader("📎 文件列表")
    
    if not case_meta['file_list']:
        st.info("暂无文件")
    else:
        for i, filename in enumerate(case_meta['file_list']):
            st.write(f"{i+1}. {filename}")


def render_qa_section(case_id):
    """渲染问答区域"""
    st.subheader("🤖 智能问答")
    
    # 检查 AI 客户端
    if st.session_state.ai_client is None:
        st.error("AI 服务未连接，请检查 API 配置")
        return
    
    # 检查 RAG 系统
    if not st.session_state.rag_system.is_index_available():
        st.warning("法条向量库未构建，问答功能可能受限")
    
    # 问题输入
    user_question = st.text_area(
        "请输入您的问题：",
        placeholder="例如：这个案例的判决依据是什么？",
        height=100,
        key=f"question_{case_id}"
    )
    
    if st.button("🔍 提交问题", type="primary", key=f"submit_{case_id}"):
        if user_question.strip():
            process_question(case_id, user_question.strip())
        else:
            st.warning("请输入问题")
    
    # 显示对话历史
    render_dialog_history(case_id)


def process_question(case_id, question):
    """处理用户问题"""
    try:
        # 获取案例文本
        case_text = st.session_state.case_manager.get_case_text(case_id)
        
        if not case_text.strip():
            st.error("案例中没有文本内容，请先上传文件")
            return
        
        # 检索相关法条
        law_chunks = []
        if st.session_state.rag_system.is_index_available():
            law_chunks = st.session_state.rag_system.retrieve_law_chunks(question, top_k=5)
        
        # 生成 AI 回答
        with st.spinner("正在生成回答..."):
            result = st.session_state.ai_client.generate_answer(
                case_text, law_chunks, question
            )
        
        # 保存对话记录
        st.session_state.case_manager.add_dialog(
            case_id, question, result['answer'], result['citations']
        )
        
        # 显示回答
        st.success("回答生成完成！")
        st.rerun()
        
    except Exception as e:
        st.error(f"处理问题失败: {str(e)}")


def render_dialog_history(case_id):
    """渲染对话历史"""
    st.subheader("💬 对话历史")
    
    dialog_history = st.session_state.case_manager.get_dialog_history(case_id)
    
    if not dialog_history:
        st.info("暂无对话记录")
        return
    
    # 倒序显示对话历史
    for dialog in reversed(dialog_history):
        with st.container():
            st.markdown("---")
            
            # 时间戳
            timestamp = datetime.fromisoformat(dialog['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
            st.caption(f"📅 {timestamp}")
            
            # 问题
            st.markdown("**❓ 问题：**")
            st.markdown(f"<div class='dialog-box'>{dialog['question']}</div>", unsafe_allow_html=True)
            
            # 回答
            st.markdown("**🤖 回答：**")
            st.markdown(f"<div class='dialog-box'>{dialog['answer']}</div>", unsafe_allow_html=True)
            
            # 引用依据
            if dialog['citations']:
                st.markdown("**📚 引用依据：**")
                for citation in dialog['citations']:
                    st.markdown(f"""
                    <div class='citation-box'>
                        <strong>来源：</strong>{citation['source']}<br>
                        <strong>内容：</strong>{citation['text']}
                    </div>
                    """, unsafe_allow_html=True)


def main():
    """主函数"""
    # 初始化
    initialize_session_state()
    initialize_components()
    
    # 渲染页面
    render_header()
    render_sidebar()
    render_main_content()


if __name__ == "__main__":
    main() 