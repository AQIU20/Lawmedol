#!/usr/bin/env python3
"""
Legal Analyzer 前端启动脚本
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_node_installed():
    """检查 Node.js 是否安装"""
    try:
        result = subprocess.run(['node', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Node.js 已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js 未安装，请先安装 Node.js")
        print("下载地址: https://nodejs.org/")
        return False

def check_npm_installed():
    """检查 npm 是否安装"""
    try:
        result = subprocess.run(['npm', '--version'], 
                              capture_output=True, text=True, check=True)
        print(f"✅ npm 已安装: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm 未安装")
        return False

def install_dependencies():
    """安装前端依赖"""
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ frontend 目录不存在")
        return False
    
    os.chdir(frontend_dir)
    
    # 检查 package.json 是否存在
    if not Path("package.json").exists():
        print("❌ package.json 不存在")
        return False
    
    # 检查 node_modules 是否存在
    if not Path("node_modules").exists():
        print("📦 安装前端依赖...")
        try:
            subprocess.run(['npm', 'install'], check=True)
            print("✅ 前端依赖安装完成")
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    else:
        print("✅ 前端依赖已安装")
    
    return True

def check_backend_service():
    """检查后端服务是否运行"""
    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正在运行")
            return True
        else:
            print("❌ 后端服务响应异常")
            return False
    except requests.exceptions.RequestException:
        print("❌ 后端服务未运行，请先启动后端服务")
        print("运行: python start_backend.py")
        return False

def start_electron():
    """启动 Electron 应用"""
    print("🚀 启动 Electron 前端应用...")
    
    frontend_dir = Path("frontend")
    os.chdir(frontend_dir)
    
    try:
        # 启动 Electron
        process = subprocess.Popen(['npm', 'start'])
        
        print("⏳ 等待应用启动...")
        time.sleep(3)
        
        print("✅ Electron 应用启动成功！")
        print("🖥️  应用窗口应该已经打开")
        
        print("\n按 Ctrl+C 停止应用")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止应用...")
            process.terminate()
            process.wait()
            print("✅ 应用已停止")
        
        return True
        
    except Exception as e:
        print(f"❌ 启动应用失败: {e}")
        return False

def main():
    """主函数"""
    print("⚖️  Legal Analyzer - 前端启动脚本")
    print("=" * 50)
    
    # 检查 Node.js
    if not check_node_installed():
        return
    
    # 检查 npm
    if not check_npm_installed():
        return
    
    # 安装依赖
    if not install_dependencies():
        return
    
    # 检查后端服务
    if not check_backend_service():
        return
    
    # 启动应用
    if start_electron():
        print("✅ 前端应用启动完成")
    else:
        print("❌ 前端应用启动失败")

if __name__ == "__main__":
    main() 