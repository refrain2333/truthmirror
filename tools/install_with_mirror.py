#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用国内镜像源安装依赖包
"""

import subprocess
import sys
import os

def install_with_mirror(package, mirror_url):
    """使用指定镜像源安装包"""
    try:
        print(f"正在从 {mirror_url} 安装 {package}...")
        cmd = [sys.executable, "-m", "pip", "install", "-i", mirror_url, package]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print(f"✅ {package} 安装成功")
            return True
        else:
            print(f"❌ {package} 安装失败")
            print(f"错误信息: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {package} 安装超时")
        return False
    except Exception as e:
        print(f"❌ {package} 安装异常: {e}")
        return False

def check_package_installed(package_name, import_name=None):
    """检查包是否已安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name} 已安装")
        return True
    except ImportError:
        print(f"❌ {package_name} 未安装")
        return False

def main():
    """主函数"""
    print("智能新闻分析系统 - 使用国内镜像安装依赖")
    print("=" * 50)
    
    # 国内镜像源列表
    mirrors = [
        "https://pypi.douban.com/simple/",
        "https://pypi.tuna.tsinghua.edu.cn/simple/",
        "https://mirrors.aliyun.com/pypi/simple/",
        "https://pypi.mirrors.ustc.edu.cn/simple/"
    ]
    
    # 需要安装的包 (包名, 导入名)
    packages = [
        ("requests", "requests"),
        ("beautifulsoup4", "bs4"),
        ("lxml", "lxml"),
        ("python-dotenv", "dotenv")
    ]
    
    print("\n1. 检查当前已安装的包:")
    print("-" * 30)
    
    installed_packages = []
    for package_name, import_name in packages:
        if check_package_installed(package_name, import_name):
            installed_packages.append(package_name)
    
    # 需要安装的包
    to_install = [pkg for pkg, _ in packages if pkg not in installed_packages]
    
    if not to_install:
        print("\n🎉 所有依赖包都已安装！")
        print("现在可以运行: python main.py \"英伟达\"")
        return
    
    print(f"\n2. 需要安装的包: {to_install}")
    print("-" * 30)
    
    # 尝试使用不同的镜像源安装
    success_count = 0
    
    for package_name in to_install:
        installed = False
        
        for i, mirror in enumerate(mirrors, 1):
            print(f"\n尝试镜像源 {i}: {mirror}")
            
            if install_with_mirror(package_name, mirror):
                success_count += 1
                installed = True
                break
            else:
                print(f"镜像源 {i} 安装失败，尝试下一个...")
        
        if not installed:
            print(f"❌ {package_name} 所有镜像源都安装失败")
    
    print(f"\n3. 安装结果:")
    print("-" * 30)
    print(f"成功安装: {success_count}/{len(to_install)} 个包")
    
    if success_count == len(to_install):
        print("🎉 所有依赖包安装完成！")
        print("\n现在可以运行:")
        print("  python main.py \"英伟达\"")
        print("  或")
        print("  python test_system.py")
    else:
        print("⚠️ 部分包安装失败")
        print("\n可以尝试手动安装失败的包:")
        failed_packages = [pkg for pkg in to_install]
        for pkg in failed_packages:
            print(f"  pip install -i https://pypi.douban.com/simple/ {pkg}")
    
    # 最终检查
    print(f"\n4. 最终检查:")
    print("-" * 30)
    all_installed = True
    for package_name, import_name in packages:
        if not check_package_installed(package_name, import_name):
            all_installed = False
    
    if all_installed:
        print("\n✅ 所有依赖包验证通过！")
    else:
        print("\n❌ 仍有包未正确安装")

if __name__ == "__main__":
    main()
