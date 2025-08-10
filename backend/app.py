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
    /* 全局样式 */
    .main-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
        padding: 20px;
    }
    .card {
        background: #ffffff;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(52, 152, 219, 0.1);
        transition: all 0.3s ease;
    }
    .card-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 20px;
        border-bottom: 3px solid #3498db;
        padding-bottom: 12px;
        position: relative;
    }
    .card-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: #3498db;
        border-radius: 2px;
    }
    .case-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #3498db;
        transition: all 0.3s ease;
    }
    .case-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    .dialog-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #e74c3c;
    }
    .citation-box {
        background: #ecf0f1;
        border-radius: 8px;
        padding: 12px;
        margin-top: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #3498db;
    }
    .retrieved-docs-box {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 16px;
        margin: 16px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #27ae60;
    }
    .doc-chunk-box {
        background: #ffffff;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid #e9ecef;
    }
    .metric-container {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-container:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 4px;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-success {
        background: #27ae60;
        box-shadow: 0 0 8px rgba(39, 174, 96, 0.3);
    }
    .status-warning {
        background: #f39c12;
        box-shadow: 0 0 8px rgba(243, 156, 18, 0.3);
    }
    .status-error {
        background: #e74c3c;
        box-shadow: 0 0 8px rgba(231, 76, 60, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(52, 152, 219, 0.4);
    }
    .stSidebar {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(52, 152, 219, 0.1);
    }
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid rgba(52, 152, 219, 0.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .stTextInput > div > div > input:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    .stFileUploader > div {
        border-radius: 12px;
        border: 2px dashed rgba(52, 152, 219, 0.3);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    .stFileUploader > div:hover {
        border-color: #3498db;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }
    .stTextArea > div > div > textarea {
        border-radius: 8px;
        border: 2px solid rgba(52, 152, 219, 0.1);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .stTextArea > div > div > textarea:focus {
        border-color: #3498db;
        box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    }
    .stDivider {
        margin: 24px 0;
    }
    .stAlert {
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    .file-button {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 6px 12px;
        margin: 2px 0;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    .file-button:hover {
        background: #e9ecef;
        border-color: #adb5bd;
    }
    .file-button.selected {
        background: #d1ecf1;
        border-color: #17a2b8;
        color: #0c5460;
    }
    .law-button {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 6px 12px;
        margin: 2px 0;
        font-size: 0.85rem;
        transition: all 0.2s ease;
    }
    .law-button:hover {
        background: #e9ecef;
        border-color: #adb5bd;
    }
    .law-button.selected {
        background: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    
    /* 检索文档卡片样式 */
    .retrieved-doc-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin: 12px 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .retrieved-doc-card:hover {
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
        transform: translateY(-2px);
    }
    
    .retrieved-doc-card.history {
        background: #f8f9fa;
        border-color: #dee2e6;
    }
    
    .doc-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        flex-wrap: wrap;
    }
    
    .doc-number {
        background: #3498db;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .doc-source {
        font-weight: 600;
        color: #2c3e50;
        font-size: 0.9rem;
        flex: 1;
    }
    
    .doc-score {
        background: #e8f5e8;
        color: #27ae60;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .doc-content {
        color: #555;
        line-height: 1.6;
        margin-bottom: 12px;
        font-size: 0.9rem;
    }
    
    .doc-footer {
        text-align: center;
    }
    
    .view-full-btn {
        background: #3498db;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        cursor: pointer;
        transition: background 0.2s ease;
    }
    
    .view-full-btn:hover {
        background: #2980b9;
    }
    
    /* 改进expander样式 */
    .streamlit-expanderHeader {
        background: #f8f9fa !important;
        border-radius: 8px !important;
        border: 1px solid #dee2e6 !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
        transition: all 0.2s ease !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #e9ecef !important;
        border-color: #adb5bd !important;
    }
    
    .streamlit-expanderContent {
        padding: 16px !important;
        background: #ffffff !important;
        border-radius: 0 0 8px 8px !important;
        border: 1px solid #dee2e6 !important;
        border-top: none !important;
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
    if 'show_latest_dialog' not in st.session_state:
        st.session_state.show_latest_dialog = False
    if 'latest_dialog_result' not in st.session_state:
        st.session_state.latest_dialog_result = None


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
    st.markdown('<h1 class="main-header">Legal Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">法律案例分析工具</p>', unsafe_allow_html=True)


def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("案例管理")
    
    # 新建案例
    st.sidebar.subheader("新建案例")
    new_case_title = st.sidebar.text_input("案例标题", placeholder="请输入案例标题")
    if st.sidebar.button("创建新案例", type="primary"):
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
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(f"{title}", key=f"case_{case_id}"):
                        st.session_state.selected_case_id = case_id
                        st.rerun()
                with col2:
                    if st.button("删除", key=f"delete_{case_id}", help="删除案例"):
                        if st.session_state.case_manager.delete_case(case_id):
                            st.success("案例删除成功")
                            if st.session_state.selected_case_id == case_id:
                                st.session_state.selected_case_id = None
                            st.rerun()
                        else:
                            st.error("删除失败")
                
                st.caption(f"{created_at} | {file_count} 个文件")
    
    st.sidebar.divider()
    
    # 法律条文管理
    st.sidebar.subheader("法律条文管理")
    
    # 初始化选中状态
    if 'selected_laws' not in st.session_state:
        st.session_state.selected_laws = []
    if 'show_delete_confirm' not in st.session_state:
        st.session_state.show_delete_confirm = None
    
    # 显示当前法律条文文件
    law_files = []
    if os.path.exists("legal_corpus"):
        law_files = [f for f in os.listdir("legal_corpus") if f.endswith(('.txt', '.md', '.pdf', '.docx'))]
    
    if law_files:
        st.sidebar.write(f"当前有 {len(law_files)} 个法律条文文件")
        
        # 显示法律条文按钮
        for i, filename in enumerate(law_files):
            is_selected = filename in st.session_state.selected_laws
            
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                button_style = "primary" if is_selected else "secondary"
                if st.button(f"{filename}", key=f"law_{i}", type=button_style):
                    if filename not in st.session_state.selected_laws:
                        st.session_state.selected_laws.append(filename)
                    else:
                        st.session_state.selected_laws.remove(filename)
                    st.rerun()
            with col2:
                if st.button("删除", key=f"delete_law_{i}", help="删除此条文"):
                    st.session_state.show_delete_confirm = filename
                    st.rerun()
        
        # 删除确认弹窗
        if st.session_state.show_delete_confirm:
            filename = st.session_state.show_delete_confirm
            st.sidebar.warning(f"确认删除法律条文：{filename}")
            col1, col2 = st.sidebar.columns(2)
            with col1:
                if st.button("确认删除", key="confirm_delete", type="primary"):
                    try:
                        law_file_path = os.path.join("legal_corpus", filename)
                        os.remove(law_file_path)
                        # 从选中列表中移除
                        if filename in st.session_state.selected_laws:
                            st.session_state.selected_laws.remove(filename)
                        st.sidebar.success(f"删除成功: {filename}")
                        st.session_state.show_delete_confirm = None
                        st.rerun()
                    except Exception as e:
                        st.sidebar.error(f"删除失败: {filename}")
            with col2:
                if st.button("取消", key="cancel_delete"):
                    st.session_state.show_delete_confirm = None
                    st.rerun()
    else:
        st.sidebar.info("暂无法律条文文件")
    
    # 上传法律条文（集成在已上传条文模块内）
    st.sidebar.markdown("**上传新条文：**")
    uploaded_laws = st.sidebar.file_uploader(
        "选择法律条文文件",
        type=['txt', 'md', 'pdf', 'docx'],
        accept_multiple_files=True,
        key="upload_laws"
    )
    
    if uploaded_laws:
        st.sidebar.write(f"已选择 {len(uploaded_laws)} 个法律条文文件")
        if st.sidebar.button("保存法律条文", key="save_laws"):
            with st.spinner("正在保存法律条文..."):
                success_count = 0
                for uploaded_file in uploaded_laws:
                    try:
                        # 确保目录存在
                        os.makedirs("legal_corpus", exist_ok=True)
                        # 保存到法律条文目录
                        law_file_path = os.path.join("legal_corpus", uploaded_file.name)
                        with open(law_file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        success_count += 1
                    except Exception as e:
                        st.sidebar.error(f"保存失败: {uploaded_file.name}")
                
                if success_count > 0:
                    st.sidebar.success(f"成功保存 {success_count} 个法律条文文件")
                    st.rerun()
    
    # 显示选中的法律条文（在上传模块之后）
    st.sidebar.markdown("**已选中的条文：**")
    if st.session_state.selected_laws:
        for i, filename in enumerate(st.session_state.selected_laws):
            col1, col2 = st.sidebar.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div style="padding: 4px 8px; margin: 2px 0; background: rgba(52, 152, 219, 0.2); border-radius: 4px; font-size: 0.8rem; border-left: 3px solid #3498db;">
                    {filename}
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if st.button("移除", key=f"remove_law_{i}", help="从选中列表中移除"):
                    st.session_state.selected_laws.remove(filename)
                    st.rerun()
    else:
        st.sidebar.markdown("""
        <div style="padding: 8px 12px; margin: 4px 0; background: rgba(248, 249, 250, 0.8); border-radius: 4px; font-size: 0.8rem; border: 1px dashed #dee2e6; color: #6c757d; text-align: center;">
            请选择条文构建向量库
        </div>
        """, unsafe_allow_html=True)
    
    # 重建法条向量库
    if st.sidebar.button("重建法条向量库", type="primary"):
        with st.spinner("正在重建法条向量库..."):
            try:
                if st.session_state.rag_system.build_index():
                    st.success("法条向量库重建成功！")
                else:
                    st.error("法条向量库重建失败，请确保已上传法律条文文件")
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
    ## 欢迎使用 Legal Analyzer
    
    ### 主要功能
    - **案例管理**: 创建和管理法律案例
    - **文档解析**: 支持 PDF 和 Word 文档自动解析
    - **智能问答**: 基于案例内容和相关法条的 AI 问答
    - **法条检索**: 本地 RAG 向量库，快速检索相关法律条文
    
    ### 使用步骤
    1. **创建案例**: 在左侧输入案例标题并创建
    2. **上传文件**: 选择案例后上传判决书等文档
    3. **智能问答**: 在右侧输入问题，获得基于材料的专业回答
    
    ### 系统状态
    """)
    
    # 显示系统状态
    col1, col2, col3 = st.columns(3)
    
    with col1:
        case_count = len(st.session_state.case_manager.get_all_cases())
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{case_count}</div>
            <div class="metric-label">案例数量</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        rag_available = st.session_state.rag_system.is_index_available()
        rag_status = "已构建" if rag_available else "未构建"
        rag_class = "status-success" if rag_available else "status-warning"
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">
                <span class="status-indicator {rag_class}"></span>{rag_status}
            </div>
            <div class="metric-label">法条向量库</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        ai_available = st.session_state.ai_client is not None
        ai_status = "已连接" if ai_available else "未连接"
        ai_class = "status-success" if ai_available else "status-error"
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">
                <span class="status-indicator {ai_class}"></span>{ai_status}
            </div>
            <div class="metric-label">AI 服务</div>
        </div>
        """, unsafe_allow_html=True)


def render_case_page():
    """渲染案例页面"""
    case_id = st.session_state.selected_case_id
    case_meta = st.session_state.case_manager.get_case_meta(case_id)
    
    if not case_meta:
        st.error("案例不存在")
        return
    
    # 案例标题 - 单独列出
    st.markdown(f"""
    <div class="card" style="margin-bottom: 16px;">
        <div class="card-header" style="font-size: 1.8rem; text-align: center; border-bottom: none;">
            {case_meta['title']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 案例信息 - 简化显示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-container" style="padding: 12px;">
            <div class="metric-value" style="font-size: 1.5rem;">{len(case_meta['file_list'])}</div>
            <div class="metric-label">文件数量</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-container" style="padding: 12px;">
            <div class="metric-value" style="font-size: 1.5rem;">{case_meta['total_chars']}</div>
            <div class="metric-label">文本字数</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        updated_at = datetime.fromisoformat(case_meta['updated_at']).strftime("%Y-%m-%d")
        st.markdown(f"""
        <div class="metric-container" style="padding: 12px;">
            <div class="metric-value" style="font-size: 1.5rem;">{updated_at}</div>
            <div class="metric-label">更新时间</div>
        </div>
        """, unsafe_allow_html=True)
    
    # 文件管理模块 - 缩小并列
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="card" style="padding: 16px; margin-bottom: 16px;">
            <div class="card-header" style="font-size: 1.2rem; margin-bottom: 12px;">文件上传</div>
        """, unsafe_allow_html=True)
        render_file_upload_section(case_id)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card" style="padding: 16px; margin-bottom: 16px;">
            <div class="card-header" style="font-size: 1.2rem; margin-bottom: 12px;">文件列表</div>
        """, unsafe_allow_html=True)
        render_file_list_section(case_meta)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # AI问答模块 - 加大模块化
    st.markdown("""
    <div class="card" style="margin-bottom: 16px;">
        <div class="card-header" style="font-size: 1.4rem;">智能问答</div>
    """, unsafe_allow_html=True)
    render_qa_section(case_id)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 历史记录 - 无感展示在底部
    render_dialog_history_simple(case_id)


def render_file_upload_section(case_id):
    """渲染文件上传区域"""
    st.markdown("**文件上传**")
    uploaded_files = st.file_uploader(
        "选择文档文件",
        type=['pdf', 'docx', 'doc', 'txt', 'md'],
        accept_multiple_files=True,
        key=f"upload_{case_id}"
    )
    
    if uploaded_files:
        st.write(f"已选择 {len(uploaded_files)} 个文件")
        for uploaded_file in uploaded_files:
            st.markdown(f"""
            <div style="padding: 6px 8px; margin-bottom: 4px; background: rgba(52, 152, 219, 0.1); border-radius: 4px; font-size: 0.8rem;">
                {uploaded_file.name}
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("解析并上传所有文件", key=f"upload_all_{case_id}"):
            with st.spinner("正在处理文件..."):
                success_count = 0
                for uploaded_file in uploaded_files:
                    if st.session_state.case_manager.upload_file_to_case(case_id, uploaded_file):
                        success_count += 1
                
                if success_count > 0:
                    st.success(f"成功上传 {success_count} 个文件")
                    st.rerun()
                else:
                    st.error("文件上传失败")


def render_file_list_section(case_meta):
    """渲染文件列表区域"""
    st.markdown("**文件列表**")
    if not case_meta['file_list']:
        st.info("暂无文件")
    else:
        # 获取当前案例ID
        case_id = st.session_state.selected_case_id
        
        # 初始化选中的文件列表
        if f'selected_files_{case_id}' not in st.session_state:
            st.session_state[f'selected_files_{case_id}'] = []
        
        # 初始化删除确认状态
        if f'show_delete_confirm_{case_id}' not in st.session_state:
            st.session_state[f'show_delete_confirm_{case_id}'] = None
        
        # 显示文件按钮
        for i, file_info in enumerate(case_meta['file_list']):
            if isinstance(file_info, dict):
                filename = file_info.get('filename', '未知文件')
                chars = file_info.get('chars', 0)
            else:
                filename = str(file_info)
                chars = 0
            
            col1, col2 = st.columns([3, 1])
            with col1:
                # 根据是否被选中显示不同样式
                is_selected = filename in st.session_state[f'selected_files_{case_id}']
                button_style = "primary" if is_selected else "secondary"
                
                if st.button(f"{filename} ({chars} 字符)", key=f"file_{case_id}_{i}", type=button_style):
                    if filename in st.session_state[f'selected_files_{case_id}']:
                        st.session_state[f'selected_files_{case_id}'].remove(filename)
                    else:
                        st.session_state[f'selected_files_{case_id}'].append(filename)
                    st.rerun()
            
            with col2:
                if st.button("删除", key=f"delete_file_{case_id}_{i}", help="删除此文件"):
                    st.session_state[f'show_delete_confirm_{case_id}'] = filename
                    st.rerun()
        
        # 删除确认弹窗
        if st.session_state[f'show_delete_confirm_{case_id}']:
            filename = st.session_state[f'show_delete_confirm_{case_id}']
            st.warning(f"确认删除文件：{filename}")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("确认删除", key=f"confirm_delete_file_{case_id}", type="primary"):
                    if st.session_state.case_manager.delete_file_from_case(case_id, filename):
                        # 从选中列表中移除
                        if filename in st.session_state[f'selected_files_{case_id}']:
                            st.session_state[f'selected_files_{case_id}'].remove(filename)
                        st.success(f"删除成功: {filename}")
                        st.session_state[f'show_delete_confirm_{case_id}'] = None
                        st.rerun()
                    else:
                        st.error(f"删除失败: {filename}")
            with col2:
                if st.button("取消", key=f"cancel_delete_file_{case_id}"):
                    st.session_state[f'show_delete_confirm_{case_id}'] = None
                    st.rerun()
        
        # 显示选中的文件
        st.markdown("**已选中的文件：**")
        if st.session_state[f'selected_files_{case_id}']:
            for i, filename in enumerate(st.session_state[f'selected_files_{case_id}']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div style="padding: 4px 8px; margin: 2px 0; background: rgba(39, 174, 96, 0.2); border-radius: 4px; font-size: 0.8rem; border-left: 3px solid #27ae60;">
                        {filename}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("移除", key=f"remove_file_{case_id}_{i}", help="从选中列表中移除"):
                        st.session_state[f'selected_files_{case_id}'].remove(filename)
                        st.rerun()
        else:
            st.markdown("""
            <div style="padding: 8px 12px; margin: 4px 0; background: rgba(248, 249, 250, 0.8); border-radius: 4px; font-size: 0.8rem; border: 1px dashed #dee2e6; color: #6c757d; text-align: center;">
                请选择文件用于AI对话
            </div>
            """, unsafe_allow_html=True)


def render_qa_section(case_id):
    """渲染问答区域"""
    # 检查 AI 客户端
    if st.session_state.ai_client is None:
        st.error("AI 服务未连接，请检查 API 配置")
        return
    
    # 检查 RAG 系统
    if not st.session_state.rag_system.is_index_available():
        st.warning("法条向量库未构建，问答功能可能受限")
    
    # 问题输入区域
    user_question = st.text_area(
        "请输入您的问题：",
        placeholder="例如：这个案例的判决依据是什么？这个案例涉及哪些法律条文？",
        height=150,
        key=f"question_{case_id}"
    )
    
    # 按钮区域
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("提交问题", type="primary", key=f"submit_{case_id}"):
            if user_question.strip():
                # 处理问题但不在这里渲染
                process_question(case_id, user_question.strip())
                # 设置标志，表示需要显示最新对话
                st.session_state.show_latest_dialog = True
                st.rerun()
            else:
                st.warning("请输入问题")
    
    with col2:
        if st.button("清空问题", key=f"clear_{case_id}"):
            st.session_state.show_latest_dialog = False
            st.rerun()
    
    with col3:
        if st.button("查看历史", key=f"view_history_{case_id}"):
            st.session_state.show_full_history = not st.session_state.get('show_full_history', False)
            st.rerun()
    
    # 显示最新对话（如果用户提交了问题）
    if st.session_state.get('show_latest_dialog', False):
        render_latest_dialog(case_id)
    
    # 显示完整历史记录（如果用户点击了查看历史）
    if st.session_state.get('show_full_history', False):
        render_dialog_history(case_id)


def process_question(case_id, question):
    """处理用户问题"""
    try:
        # 获取案例文本
        case_text = st.session_state.case_manager.get_case_text(case_id)
        
        if not case_text.strip():
            st.error("案例中没有文本内容，请先上传文件")
            # 显示调试信息
            case_meta = st.session_state.case_manager.get_case_meta(case_id)
            if case_meta and case_meta.get('file_list'):
                st.info(f"已上传 {len(case_meta['file_list'])} 个文件，但文本提取可能失败")
                for i, file_info in enumerate(case_meta['file_list']):
                    if isinstance(file_info, dict):
                        filename = file_info.get('filename', '未知文件')
                        chars = file_info.get('chars', 0)
                        st.write(f"文件 {i+1}: {filename} (提取字符数: {chars})")
            return
        
        # 检索相关法条
        law_chunks = []
        if st.session_state.rag_system.is_index_available():
            raw_chunks = st.session_state.rag_system.retrieve_law_chunks(question, top_k=5)
            # 格式化检索结果用于显示
            law_chunks = st.session_state.rag_system.format_retrieved_chunks_for_display(raw_chunks)
        
        # 生成 AI 回答
        with st.spinner("正在生成回答..."):
            result = st.session_state.ai_client.generate_answer(
                case_text, law_chunks, question
            )
        
                # 保存对话记录（包含检索到的文档信息）
        st.session_state.case_manager.add_dialog(
            case_id, question, result['answer'], result['citations'], result.get('retrieved_chunks', [])
        )
        
        # 将结果存储到session state中，供render_latest_dialog使用
        st.session_state.latest_dialog_result = {
            'question': question,
            'answer': result['answer'],
            'citations': result.get('citations', []),
            'retrieved_chunks': result.get('retrieved_chunks', [])
        }
        
        # 显示回答
        st.success("回答生成完成！")
        
    except Exception as e:
        st.error(f"处理问题失败: {str(e)}")


def render_latest_dialog(case_id):
    """渲染最新对话"""
    if not st.session_state.get('latest_dialog_result'):
        return
    
    result = st.session_state.latest_dialog_result
    
    st.markdown("### 最新对话")
    
    # 使用两列布局：左半边显示对话，右半边显示检索文档
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("**问题：**")
        st.markdown(f"<div class='dialog-box'>{result['question']}</div>", unsafe_allow_html=True)
        
        st.markdown("**回答：**")
        st.markdown(f"<div class='dialog-box'>{result['answer']}</div>", unsafe_allow_html=True)
        
        # 显示引用依据
        if result['citations']:
            st.markdown("**引用依据：**")
            for citation in result['citations']:
                st.markdown(f"""
                <div class='citation-box'>
                    <strong>来源：</strong>{citation['source']}<br>
                    <strong>内容：</strong>{citation['text']}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # 显示检索到的相关文档（在右半边）
        if result.get('retrieved_chunks'):
            st.markdown("**检索到的相关文档**")
            for i, chunk in enumerate(result['retrieved_chunks']):
                # 使用改进的expander样式
                with st.expander(f" {chunk['source']} (相似度: {chunk['score']:.3f})", expanded=False):
                    st.markdown(f"""
                    <div class='retrieved-doc-card'>
                        <div class='doc-header'>
                            <span class='doc-number'>#{i+1}</span>
                            <span class='doc-source'>{chunk['source']}</span>
                            <span class='doc-score'>相似度: {chunk['score']:.3f}</span>
                        </div>
                        <div class='doc-content'>
                            {chunk['text']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("未检索到相关文档")


def render_dialog_history(case_id):
    """渲染对话历史"""
    st.subheader("对话历史")
    
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
            st.caption(f"{timestamp}")
            
            # 问题
            st.markdown("**问题：**")
            st.markdown(f"<div class='dialog-box'>{dialog['question']}</div>", unsafe_allow_html=True)
            
            # 回答
            st.markdown("**回答：**")
            st.markdown(f"<div class='dialog-box'>{dialog['answer']}</div>", unsafe_allow_html=True)
            
            # 引用依据
            if dialog.get('citations'):
                st.markdown("**引用依据：**")
                for citation in dialog['citations']:
                    st.markdown(f"""
                    <div class='citation-box'>
                        <strong>来源：</strong>{citation['source']}<br>
                        <strong>内容：</strong>{citation['text']}
                    </div>
                    """, unsafe_allow_html=True)
            
            # 显示检索到的相关文档（在对话下方）
            if dialog.get('retrieved_chunks'):
                st.markdown("---")
                st.markdown("**📚 检索文档：**")
                for i, chunk in enumerate(dialog['retrieved_chunks']):
                    # 使用改进的expander样式
                    with st.expander(f"📄 {chunk['source']}", expanded=False):
                        st.markdown(f"""
                        <div class='retrieved-doc-card history'>
                            <div class='doc-header'>
                                <span class='doc-number'>#{i+1}</span>
                                <span class='doc-source'>{chunk['source']}</span>
                                {f'<span class="doc-score">相似度: {chunk["score"]:.3f}</span>' if 'score' in chunk else ''}
                            </div>
                            <div class='doc-content'>
                                {chunk['text']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("---")
                st.info("无检索文档")


def render_dialog_history_simple(case_id):
    """渲染简化的对话历史 - 无感展示"""
    dialog_history = st.session_state.case_manager.get_dialog_history(case_id)
    
    if not dialog_history:
        return
    
    # 只显示最新的3条对话
    recent_dialogs = dialog_history[-3:]
    
    st.markdown("""
    <div style="margin-top: 20px; padding: 16px; background: rgba(248, 249, 250, 0.5); border-radius: 8px; border-left: 3px solid #3498db;">
        <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 12px;">最近对话</div>
    """, unsafe_allow_html=True)
    
    for dialog in reversed(recent_dialogs):
        timestamp = datetime.fromisoformat(dialog['timestamp']).strftime("%m-%d %H:%M")
        question = dialog['question'][:40] + '...' if len(dialog['question']) > 40 else dialog['question']
        answer = dialog['answer'][:60] + '...' if len(dialog['answer']) > 60 else dialog['answer']
        
        st.markdown(f"""
        <div style="margin-bottom: 12px; padding: 8px; background: rgba(255, 255, 255, 0.7); border-radius: 6px; font-size: 0.85rem;">
            <div style="color: #7f8c8d; font-size: 0.75rem;">{timestamp}</div>
            <div style="font-weight: 500; margin: 4px 0; color: #2c3e50;">问：{question}</div>
            <div style="margin: 4px 0; color: #7f8c8d; font-size: 0.8rem;">答：{answer}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


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