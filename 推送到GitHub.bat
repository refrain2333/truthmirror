@echo off
chcp 65001 >nul
title 推送到GitHub
echo 正在推送现代化界面改进到GitHub...
echo.

cd /d "%~dp0"

echo [1/3] 添加所有文件...
"C:\Program Files\Git\bin\git.exe" add .

echo [2/3] 提交改动...
"C:\Program Files\Git\bin\git.exe" commit -m "feat: 现代化界面升级 - 渐变背景和毛玻璃卡片效果"

echo [3/3] 推送到GitHub...
"C:\Program Files\Git\bin\git.exe" push origin master --force

echo.
echo 推送完成！请刷新GitHub页面查看。
pause
