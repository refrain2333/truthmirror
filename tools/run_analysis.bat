@echo off
echo 智能新闻分析系统
echo ==================
echo.
set /p query="请输入搜索关键词: "
echo.
echo 开始分析主题: %query%
echo.
python main.py "%query%"
echo.
pause
