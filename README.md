# 智能新闻分析系统

一个自动化的七步流程新闻分析系统，能够从新闻获取、筛选、内容提取到深度分析的完整链路，最终生成结构化的分析报告。

## 功能特点

- 🔍 **自动新闻获取**: 从SearXNG API获取多页新闻数据
- 🌐 **连通性筛选**: 异步检查URL可访问性，提高效率
- 🤖 **AI相关性筛选**: 使用GLM-4.5-flash模型智能筛选相关新闻
- 📄 **内容提取**: 智能解析HTML，提取新闻正文
- 🧠 **AI深度分析**: 使用Gemini-2.0-flash-exp模型进行专业分析
- 📊 **汇总报告**: 生成综合性的分析报告
- 🌍 **多语言支持**: 支持中文、英文、日文、韩文等多种语言

## 系统架构

系统采用七步流程设计：

1. **步骤1**: 获取新闻列表与预清理
2. **步骤2**: 连通性筛选
3. **步骤3**: AI相关性筛选
4. **步骤4**: 获取原始HTML
5. **步骤5**: 提取正文
6. **步骤6**: AI深度分析
7. **步骤7**: 生成最终汇总报告

## 安装和配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 环境配置

⚠️ **安全提醒**: 本项目包含真实的API密钥，请注意保护！

如果您是从GitHub克隆的项目：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置您自己的API密钥：

- `GLM_API_KEY`: GLM模型的API密钥
- `GEMINI_API_KEY`: Gemini模型的API密钥
- `SEARXNG_API_URL`: SearXNG搜索API地址

**注意**: 如果您要提交到公开仓库，请确保移除真实的API密钥！

## 使用方法

### 命令行运行

```bash
# 方式1: 直接传入搜索关键词
python main.py "英伟达"

# 方式2: 运行后输入关键词
python main.py
```

### 单独运行各步骤

每个步骤都可以独立运行进行测试：

```bash
# 测试步骤1
python step1_fetch_news.py

# 测试步骤2
python step2_filter_accessible.py

# ... 其他步骤类似
```

## 输出结构

所有处理结果都保存在 `processed_data/` 目录下：

```
processed_data/
├── 01_raw_search_results/      # 原始搜索结果
├── 02_filtered_accessible_urls/ # 可访问URL筛选结果
├── 03_ai_relevance_filtered/   # AI相关性筛选结果
├── 04_raw_html_pages/          # 原始HTML页面
├── 05_extracted_article_content/ # 提取的正文内容
├── 06_ai_processed_data/       # AI分析结果
└── 07_final_summary_reports/   # 最终汇总报告
```

## 示例输出

最终报告包含以下信息：

- 搜索主题和生成时间
- 工作流统计数据
- 综合性分析报告
- 数据来源统计

## 技术栈

- **Python 3.7+**
- **requests**: HTTP请求处理
- **aiohttp**: 异步HTTP请求
- **BeautifulSoup4**: HTML解析
- **python-dotenv**: 环境变量管理

## API集成

- **SearXNG**: 新闻搜索
- **GLM-4.5-flash**: 相关性判断
- **Gemini-2.0-flash-exp**: 深度分析和汇总

## 注意事项

1. **API密钥安全**: 请妥善保管您的API密钥，不要提交到公开仓库
2. 确保网络连接稳定，系统需要访问多个外部API
3. API调用有频率限制，系统已内置延迟机制
4. 大量新闻处理可能需要较长时间，请耐心等待
5. 建议在稳定的网络环境下运行

## 安全说明

请查看 [SECURITY.md](SECURITY.md) 了解API密钥安全相关的重要信息。

## 故障排除

### 常见问题

1. **API密钥错误**: 检查 `.env` 文件中的API密钥配置
2. **网络连接问题**: 确保能够访问相关API服务
3. **依赖包缺失**: 运行 `pip install -r requirements.txt` 安装依赖

### 日志和调试

系统会在控制台输出详细的执行日志，包括：
- 每个步骤的进度信息
- 成功/失败统计
- 错误信息和堆栈跟踪

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 免责声明

本项目仅供学习和研究使用。请遵守相关网站的robots.txt和使用条款。
