#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖包安装脚本
"""

import subprocess
import sys

def install_package(package):
    """安装单个包"""
    try:
        print(f"正在安装 {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 安装失败: {e}")
        return False

def check_package(package):
    """检查包是否已安装"""
    try:
        __import__(package)
        print(f"✅ {package} 已安装")
        return True
    except ImportError:
        print(f"❌ {package} 未安装")
        return False

def main():
    """主函数"""
    print("智能新闻分析系统 - 依赖包安装")
    print("=" * 40)
    
    # 需要安装的包
    packages = [
        'requests',
        'beautifulsoup4', 
        'lxml',
        'python-dotenv'
    ]
    
    # 检查已安装的包
    print("\n检查已安装的包:")
    installed = []
    for package in packages:
        if package == 'beautifulsoup4':
            # beautifulsoup4导入时使用bs4
            if check_package('bs4'):
                installed.append(package)
        elif package == 'python-dotenv':
            # python-dotenv导入时使用dotenv
            if check_package('dotenv'):
                installed.append(package)
        else:
            if check_package(package):
                installed.append(package)
    
    # 安装缺失的包
    to_install = [p for p in packages if p not in installed]
    
    if not to_install:
        print("\n🎉 所有依赖包都已安装！")
        return
    
    print(f"\n需要安装的包: {to_install}")
    
    success_count = 0
    for package in to_install:
        if install_package(package):
            success_count += 1
    
    print(f"\n安装完成: {success_count}/{len(to_install)} 个包安装成功")
    
    if success_count == len(to_install):
        print("🎉 所有依赖包安装完成！")
        print("现在可以运行: python main.py \"英伟达\"")
    else:
        print("⚠️ 部分包安装失败，可以尝试手动安装")

if __name__ == "__main__":
    main()
