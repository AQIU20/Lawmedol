set shell := ["bash", "-cu"]

ENV        := "lawmedol"
PYTHON_VER := "3.11"
CUDA_FLAG  := "cpuonly"

PY        := "conda run -n {{ENV}} python"
PIP       := "conda run -n {{ENV}} python -m pip"
STREAMLIT := "conda run -n {{ENV}} streamlit"
NPM       := "conda run -n {{ENV}} npm"

default:
    just --list

help:
    @echo "just setup           # 创建环境并安装依赖"
    @echo "just install         # 仅安装依赖"
    @echo "just check           # 自检 FAISS / 嵌入 / DeepSeek"
    @echo "just build-index     # 构建法条向量库"
    @echo "just backend         # 启动 Streamlit"
    @echo "just frontend        # 启动 Electron"
    @echo "just dev             # 一键同时启动（Unix/Git-Bash）"
    @echo "just dev-win         # Windows 双窗口启动"
    @echo "just dist            # 打包 Electron"
    @echo "just clean           # 清理构建产物"

create-env:
    conda create -y -n {{ENV}} python={{PYTHON_VER}} -c conda-forge
    conda config --add channels conda-forge
    conda config --set channel_priority strict
    conda install -y -n {{ENV}} -c conda-forge faiss-cpu nodejs
    conda install -y -n {{ENV}} -c pytorch pytorch torchvision torchaudio {{CUDA_FLAG}}

install:
    {{PIP}} install --upgrade pip
    {{PIP}} install -r requirements.txt
    cd frontend && {{NPM}} install

setup: create-env install

check:
    {{PY}} scripts/check_faiss.py
    {{PY}} scripts/check_embed.py
    {{PY}} scripts/check_deepseek.py

build-index:
    cd backend && {{PY}} -c "from utils.rag_system import build_index; build_index(corpus_dir='legal_corpus')"

backend:
    cd backend && {{STREAMLIT}} run app.py

frontend:
    cd frontend && {{NPM}} start

dev:
    (cd backend && {{STREAMLIT}} run app.py) & \
    (cd frontend && {{NPM}} start) & \
    wait

dev-win:
    powershell -NoProfile
