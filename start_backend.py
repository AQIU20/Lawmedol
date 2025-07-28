#!/usr/bin/env python3
"""
Legal Analyzer 后端启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import openai
        import faiss
        import sentence_transformers
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def check_env_file():
    """检查环境变量文件"""
    env_file = Path("backend/env.sample")
    if not env_file.exists():
        print("❌ 环境变量模板文件不存在")
        return False
    
    # 检查是否已复制为 .env
    env_path = Path("backend/.env")
    if not env_path.exists():
        print("⚠️  环境变量文件不存在，正在复制模板...")
        try:
            import shutil
            shutil.copy(env_file, env_path)
            print("✅ 已创建 .env 文件，请编辑 backend/.env 添加您的 API Key")
        except Exception as e:
            print(f"❌ 创建 .env 文件失败: {e}")
            return False
    
    return True

def start_streamlit():
    """启动 Streamlit 服务"""
    print("🚀 启动 Streamlit 后端服务...")
    
    # 切换到 backend 目录
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ backend 目录不存在")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # 启动 Streamlit
        process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
        print("⏳ 等待服务启动...")
        time.sleep(5)
        
        # 检查服务是否启动成功
        try:
            import requests
            response = requests.get("http://localhost:8501", timeout=10)
            if response.status_code == 200:
                print("✅ Streamlit 服务启动成功！")
                print("🌐 访问地址: http://localhost:8501")
                
                # 自动打开浏览器
                webbrowser.open("http://localhost:8501")
                
                print("\n按 Ctrl+C 停止服务")
                
                try:
                    process.wait()
                except KeyboardInterrupt:
                    print("\n🛑 正在停止服务...")
                    process.terminate()
                    process.wait()
                    print("✅ 服务已停止")
                
                return True
            else:
                print(f"❌ 服务响应异常: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException:
            print("❌ 无法连接到 Streamlit 服务")
            return False
            
    except Exception as e:
        print(f"❌ 启动服务失败: {e}")
        return False

def main():
    """主函数"""
    print("⚖️  Legal Analyzer - 后端启动脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查环境变量
    if not check_env_file():
        return
    
    # 启动服务
    if start_streamlit():
        print("✅ 后端服务启动完成")
    else:
        print("❌ 后端服务启动失败")

if __name__ == "__main__":
    main() 