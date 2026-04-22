@echo off

REM 运行多线程爬虫任务脚本

cd /d "%~dp0.."

echo 正在运行多线程爬虫任务...
echo 日志将输出到 logs/multi_thread_crawler.log

REM 运行多线程爬虫任务脚本
python tasks/multi_thread_crawler.py

pause
