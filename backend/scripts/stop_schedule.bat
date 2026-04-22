@echo off

REM 停止定时爬虫任务脚本

cd /d "%~dp0.."

echo 正在停止定时爬虫任务...

REM 查找并终止运行中的定时爬虫任务进程
for /f "tokens=2 delims=," %%a in ('tasklist /fi "imagename eq python.exe" /fo csv /nh') do (
    taskkill /pid %%~a /f /t 2>nul
)

echo 定时爬虫任务已停止

pause
