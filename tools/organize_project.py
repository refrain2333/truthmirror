#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import glob

def organize_project():
    """整理项目目录结构"""
    
    print("🔧 开始整理项目目录结构...")
    
    # 创建目录
    directories = ['src', 'tests', 'tools']
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✓ 创建目录: {dir_name}/")
    
    # 定义文件移动规则
    move_rules = {
        'src': [
            'step1_fetch_news.py',
            'step2_filter_accessible.py', 
            'step3_ai_relevance_filter.py',
            'step4_fetch_html.py',
            'step5_extract_content.py',
            'step6_ai_analysis.py',
            'step7_final_summary.py'
        ],
        'tests': [
            'test_glm.py',
            'test_glm_relevance.py',
            'test_large_content.py',
            'test_max_tokens.py',
            'test_step7.py',
            'test_system.py',
            'test_text_length.py',
            'verify_limit.py',
            'simple_glm_test.py'
        ],
        'tools': [
            'check_deps.py',
            'install_dependencies.py',
            'install_with_mirror.py',
            'simple_main.py',
            'organize_project.py'  # 这个脚本本身也移动到tools
        ]
    }
    
    # 移动文件
    for target_dir, files in move_rules.items():
        for file_name in files:
            if os.path.exists(file_name):
                source = file_name
                destination = os.path.join(target_dir, file_name)
                try:
                    shutil.move(source, destination)
                    print(f"✓ 移动: {source} -> {destination}")
                except Exception as e:
                    print(f"✗ 移动失败: {source} -> {destination}, 错误: {e}")
    
    # 移动批处理文件到tools
    bat_files = ['check_deps.bat', 'run_analysis.bat', 'run_test.bat']
    for bat_file in bat_files:
        if os.path.exists(bat_file):
            try:
                shutil.move(bat_file, os.path.join('tools', bat_file))
                print(f"✓ 移动: {bat_file} -> tools/{bat_file}")
            except Exception as e:
                print(f"✗ 移动失败: {bat_file}, 错误: {e}")
    
    print("\n📁 整理后的目录结构:")
    print("├── main.py                    # 主程序")
    print("├── requirements.txt           # 依赖配置")
    print("├── .env                       # 环境变量")
    print("├── README.md                  # 项目说明")
    print("├── 开发指南.md                # 开发指南")
    print("├── src/                       # 源代码模块")
    print("│   ├── step1_fetch_news.py")
    print("│   ├── step2_filter_accessible.py")
    print("│   ├── step3_ai_relevance_filter.py")
    print("│   ├── step4_fetch_html.py")
    print("│   ├── step5_extract_content.py")
    print("│   ├── step6_ai_analysis.py")
    print("│   └── step7_final_summary.py")
    print("├── tests/                     # 测试文件")
    print("│   ├── test_*.py")
    print("│   └── verify_*.py")
    print("├── tools/                     # 工具脚本")
    print("│   ├── check_deps.py")
    print("│   ├── install_*.py")
    print("│   ├── simple_main.py")
    print("│   └── *.bat")
    print("└── processed_data/            # 数据输出")
    
    print("\n⚠️  需要手动更新的文件:")
    print("1. main.py - 更新import路径")
    print("2. 其他引用step文件的脚本")

if __name__ == "__main__":
    organize_project()
