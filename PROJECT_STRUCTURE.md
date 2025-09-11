# 项目目录结构

## 📁 整理后的目录结构

```
TruthNews/
├── main.py                    # 🚀 主程序入口
├── requirements.txt           # 📦 Python依赖配置
├── .env                       # 🔐 环境变量配置
├── README.md                  # 📖 项目说明文档
├── 开发指南.md                # 📋 开发指南
├── PROJECT_STRUCTURE.md       # 📁 项目结构说明
│
├── src/                       # 📂 源代码模块
│   ├── __init__.py
│   ├── step1_fetch_news.py           # 步骤1: 获取新闻
│   ├── step2_filter_accessible.py   # 步骤2: 连通性筛选
│   ├── step3_ai_relevance_filter.py # 步骤3: 智能关键词筛选
│   ├── step4_fetch_html.py          # 步骤4: 获取HTML内容
│   ├── step5_extract_content.py     # 步骤5: 提取正文
│   ├── step6_ai_analysis.py         # 步骤6: AI深度分析
│   └── step7_final_summary.py       # 步骤7: 生成汇总报告
│
├── tests/                     # 🧪 测试文件
│   ├── __init__.py
│   ├── test_glm.py                  # GLM API测试
│   ├── test_glm_relevance.py        # GLM相关性测试
│   ├── test_large_content.py        # 大内容测试
│   ├── test_max_tokens.py           # Token限制测试
│   ├── test_step7.py                # 步骤7测试
│   ├── test_system.py               # 系统测试
│   ├── test_text_length.py          # 文本长度测试
│   ├── verify_limit.py              # 限制验证
│   └── simple_glm_test.py           # 简单GLM测试
│
├── tools/                     # 🔧 工具脚本
│   ├── __init__.py
│   ├── check_deps.py                # 依赖检查
│   ├── check_deps.bat               # 依赖检查(批处理)
│   ├── install_dependencies.py      # 依赖安装
│   ├── install_with_mirror.py       # 镜像源安装
│   ├── simple_main.py               # 简化版主程序
│   ├── organize_project.py          # 项目整理脚本
│   ├── run_analysis.bat             # 运行分析(批处理)
│   └── run_test.bat                 # 运行测试(批处理)
│
└── processed_data/            # 📊 数据输出目录
    ├── 01_raw_search_results/       # 原始搜索结果
    ├── 02_filtered_accessible_urls/ # 可访问URL筛选结果
    ├── 03_ai_relevance_filtered/    # 相关性筛选结果
    ├── 04_raw_html_pages/           # 原始HTML页面
    ├── 05_extracted_article_content/# 提取的文章正文
    ├── 06_ai_processed_data/        # AI分析结果
    ├── 07_final_summary_reports/    # 最终汇总报告
    └── simple_results/              # 简化版结果
```

## 🚀 使用方法

### 主程序运行
```bash
python main.py "搜索关键词"
```

### 简化版运行
```bash
python tools/simple_main.py "搜索关键词"
```

### 依赖检查
```bash
python tools/check_deps.py
```

### 运行测试
```bash
python tests/test_system.py
```

## 📝 文件说明

### 核心文件
- **main.py**: 主程序，协调7个步骤的执行
- **requirements.txt**: Python依赖包列表
- **.env**: 环境变量配置（API密钥等）

### 源代码模块 (src/)
- **step1_fetch_news.py**: 从SearXNG API获取新闻数据
- **step2_filter_accessible.py**: 检查URL可访问性
- **step3_ai_relevance_filter.py**: 智能关键词相关性筛选
- **step4_fetch_html.py**: 获取网页HTML内容
- **step5_extract_content.py**: 提取文章正文
- **step6_ai_analysis.py**: GLM AI深度分析
- **step7_final_summary.py**: 生成最终汇总报告

### 测试文件 (tests/)
- **test_*.py**: 各种功能测试脚本
- **verify_*.py**: 验证脚本

### 工具脚本 (tools/)
- **check_deps.py**: 检查依赖包安装状态
- **install_*.py**: 依赖包安装脚本
- **simple_main.py**: 仅使用Python标准库的简化版
- **organize_project.py**: 项目目录整理脚本

## 🔧 开发说明

### 导入路径
由于文件重新组织，导入语句需要使用相对路径：
```python
from src.step1_fetch_news import step1_fetch_and_clean_news
from src.step2_filter_accessible import run_step2
# ... 其他导入
```

### 添加新功能
1. 核心功能模块放在 `src/` 目录
2. 测试文件放在 `tests/` 目录
3. 工具脚本放在 `tools/` 目录

### 数据输出
所有处理结果都保存在 `processed_data/` 目录的相应子目录中，按步骤编号组织。
