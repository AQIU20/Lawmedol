#!/usr/bin/env python3
"""
Legal Analyzer 应用构建脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_prerequisites():
    """检查构建前提条件"""
    print("🔍 检查构建前提条件...")
    
    # 检查 Node.js
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Node.js: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js 未安装")
        return False
    
    # 检查 npm
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ npm: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm 未安装")
        return False
    
    # 检查 Python 依赖
    try:
        import streamlit
        import openai
        import faiss
        print("✅ Python 依赖已安装")
    except ImportError as e:
        print(f"❌ Python 依赖未安装: {e}")
        return False
    
    return True

def build_frontend():
    """构建前端应用"""
    print("🔨 构建前端应用...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend 目录不存在")
        return False
    
    os.chdir(frontend_dir)
    
    # 安装依赖
    print("📦 安装前端依赖...")
    try:
        subprocess.run(['npm', 'install'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False
    
    # 构建应用
    print("🔨 构建 Electron 应用...")
    try:
        # 根据操作系统选择构建目标
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            subprocess.run(['npm', 'run', 'build:win'], check=True)
        elif system == "darwin":  # macOS
            subprocess.run(['npm', 'run', 'build:mac'], check=True)
        else:  # Linux
            subprocess.run(['npm', 'run', 'build:linux'], check=True)
        
        print("✅ 前端应用构建完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return False

def create_distribution():
    """创建分发包"""
    print("📦 创建分发包...")
    
    # 创建 dist 目录
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    # 复制构建文件
    frontend_build_dir = Path("frontend/build")
    if frontend_build_dir.exists():
        for item in frontend_build_dir.iterdir():
            if item.is_file():
                shutil.copy2(item, dist_dir)
            elif item.is_dir():
                shutil.copytree(item, dist_dir / item.name)
    
    # 复制后端文件
    backend_dir = Path("backend")
    if backend_dir.exists():
        backend_dist = dist_dir / "backend"
        shutil.copytree(backend_dir, backend_dist, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.env', 'storage/*'
        ))
    
    # 复制启动脚本
    scripts = ["start_backend.py", "start_frontend.py"]
    for script in scripts:
        if Path(script).exists():
            shutil.copy2(script, dist_dir)
    
    # 复制 requirements.txt
    if Path("requirements.txt").exists():
        shutil.copy2("requirements.txt", dist_dir)
    
    # 复制 README
    if Path("README.md").exists():
        shutil.copy2("README.md", dist_dir)
    
    print("✅ 分发包创建完成")
    return True

def create_installer():
    """创建安装包"""
    print("📦 创建安装包...")
    
    # 这里可以添加创建安装包的逻辑
    # 例如使用 Inno Setup (Windows) 或 DMG Creator (macOS)
    
    print("ℹ️  安装包创建功能待实现")
    return True

def main():
    """主函数"""
    print("⚖️  Legal Analyzer - 应用构建脚本")
    print("=" * 50)
    
    # 检查前提条件
    if not check_prerequisites():
        print("❌ 构建前提条件不满足")
        return
    
    # 构建前端
    if not build_frontend():
        print("❌ 前端构建失败")
        return
    
    # 创建分发包
    if not create_distribution():
        print("❌ 分发包创建失败")
        return
    
    # 创建安装包
    if not create_installer():
        print("❌ 安装包创建失败")
        return
    
    print("🎉 应用构建完成！")
    print("📁 构建文件位于: dist/ 目录")
    print("📁 前端构建文件位于: frontend/build/ 目录")

if __name__ == "__main__":
    main() 