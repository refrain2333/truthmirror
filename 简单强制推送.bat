@echo off
chcp 65001 >nul
title 简单强制推送
echo 直接强制推送现代化改进到GitHub...
echo 注意：这会覆盖远程的所有内容！
echo.

cd /d "%~dp0"

echo [1/3] 添加所有文件...
"C:\Program Files\Git\bin\git.exe" add .

echo [2/3] 提交改动...
"C:\Program Files\Git\bin\git.exe" commit -m "feat: 现代化界面升级 - 渐变背景和毛玻璃卡片效果"

echo [3/3] 强制推送到GitHub...
"C:\Program Files\Git\bin\git.exe" push origin master --force

echo.
echo 强制推送完成！请刷新GitHub页面查看。
pause
