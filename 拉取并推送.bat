@echo off
chcp 65001 >nul
title 拉取远程更改并推送
echo 正在拉取远程更改并推送您的现代化改进...
echo.

cd /d "%~dp0"

echo [1/4] 拉取远程更改...
"C:\Program Files\Git\bin\git.exe" pull origin master

echo [2/4] 添加所有文件...
"C:\Program Files\Git\bin\git.exe" add .

echo [3/4] 提交改动...
"C:\Program Files\Git\bin\git.exe" commit -m "feat: 现代化界面升级 - 渐变背景和毛玻璃卡片效果"

echo [4/4] 推送到GitHub...
"C:\Program Files\Git\bin\git.exe" push origin master

echo.
echo 完成！请刷新GitHub页面查看。
pause
