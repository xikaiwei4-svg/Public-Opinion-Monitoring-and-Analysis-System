@echo off

REM 启动定时爬虫任务脚本

cd /d "%~dp0.."

echo 正在启动定时爬虫任务...
echo 日志将输出到 logs/crawler_schedule.log

REM 启动定时爬虫任务脚本
python scripts/schedule_crawler.py

pause
