# Legal Analyzer - 法律案例分析工具

一个基于 Streamlit 和 Electron 的桌面应用，用于法律案例管理和智能问答分析。

## 功能特性

- 📁 **案例管理**: 创建新案例，上传判决书 PDF/Word 文件
- 🔍 **智能问答**: 基于案例内容和相关法条进行智能问答
- 📚 **法条检索**: 本地 RAG 向量库，快速检索相关法律条文
- 💾 **本地存储**: 所有数据本地持久化，保护隐私
- 🖥️ **桌面应用**: 支持打包为 Windows/macOS 桌面应用

## 项目结构

```
legal-analyzer/
├── backend/                 # 后端服务
│   ├── app.py              # Streamlit 主应用
│   ├── legal_corpus/       # 法条语料库
│   ├── storage/            # 案例存储
│   ├── utils/              # 工具函数
│   └── .env               # 环境变量
├── frontend/               # Electron 前端
│   ├── main.js            # Electron 主进程
│   ├── package.json       # Node.js 配置
│   └── build/             # 打包输出
└── requirements.txt        # Python 依赖
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd legal-analyzer

# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Node.js 依赖
cd frontend
npm install
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp backend/.env.sample backend/.env

# 编辑 .env 文件，添加你的 DeepSeek API Key
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 本地运行

```bash
# 启动 Streamlit 后端
cd backend
streamlit run app.py

# 在另一个终端启动 Electron 前端
cd frontend
npm start
```

### 4. 构建桌面应用

```bash
# 构建 Electron 应用
cd frontend
npm run build

# 输出文件在 frontend/build/ 目录
```

## 使用说明

1. **创建案例**: 点击左侧"新建案例"按钮，输入标题
2. **上传文件**: 选择案例后，点击"上传文件"上传判决书
3. **智能问答**: 在右侧输入问题，系统会基于案例内容和相关法条回答
4. **查看历史**: 所有对话都会保存在案例中，可随时查看

## 技术栈

- **后端**: Streamlit, Python, FAISS, sentence-transformers
- **前端**: Electron, Node.js
- **AI**: DeepSeek API
- **存储**: 本地文件系统

## 开发说明

### 添加新的法条

将法条文本文件放入 `backend/legal_corpus/` 目录，然后点击"重建法条向量库"按钮。

### 自定义模型

可以在 `backend/utils/ai_client.py` 中修改 AI 模型配置。

## 许可证

MIT License 