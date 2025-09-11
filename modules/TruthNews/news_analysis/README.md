# 智能新闻分析模块

Truth Mirror平台的AI分析核心模块，提供7步自动化新闻分析流程。

## 🔧 功能概述

| 步骤 | 功能 | 说明 |
|------|------|------|
| Step 1 | 新闻获取 | 从SearXNG API获取多源新闻数据 |
| Step 2 | 连通性筛选 | 异步检查URL可访问性 |
| Step 3 | AI相关性筛选 | 使用GLM-4.5模型智能筛选 |
| Step 4 | 内容获取 | 获取新闻页面完整HTML |
| Step 5 | 正文提取 | 智能解析HTML，提取新闻正文 |
| Step 6 | AI深度分析 | 使用Gemini/DeepSeek进行专业分析 |
| Step 7 | 汇总报告 | 生成综合性分析报告 |

## ⚙️ 配置要求

### API密钥配置（.env文件）
```bash
# 主要AI模型
GLM_API_KEY=your_glm_api_key
GLM_MODEL_ID=glm-4.5-flash

# 深度分析模型  
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL_ID=gemini-2.0-flash-exp

# 备选模型（推荐配置）
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_MODEL_ID=deepseek-chat

# 搜索引擎
SEARXNG_API_URL=http://your-searxng-instance/search
```

## 🚀 使用方法

### 作为模块调用
```python
from main import run_news_analysis_pipeline

# 执行完整分析流程
result_file = run_news_analysis_pipeline("事件关键词")
```

### 独立运行
```bash
cd modules/TruthNews/news_analysis
python main.py
```

## 📊 输出格式

分析结果保存在 `processed_data/07_final_summary_reports/` 目录，包含：

- **final_summary**: 综合分析报告
- **analysis_statistics**: 分析统计信息
- **workflow_summary**: 工作流程摘要
- **source_count**: 信息源数量统计

## 🔄 容错机制

- **多模型备选**: GLM失败时自动切换到DeepSeek
- **异步处理**: 提高URL检查效率
- **错误重试**: 网络请求自动重试机制
- **日志记录**: 完整的处理日志便于调试

## 📝 集成说明

本模块已集成到Truth Mirror主平台：
- 通过 `backend/app/services/analysis_service.py` 调用
- 支持事件ID关联
- 自动触发机制（10人关注）
- 结果展示在前端事件详情页

更多详情请参考主项目README。