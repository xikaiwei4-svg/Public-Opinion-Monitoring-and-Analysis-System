# -*- coding: utf-8 -*-
"""
持续运行的爬虫脚本
"""
import time
import requests
import json

def run_continuous_crawler():
    """持续运行爬虫"""
    print("开始持续运行爬虫...")
    print("按 Ctrl+C 停止爬虫")
    
    try:
        while True:
            print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] 开始新一轮爬虫任务...")
            
            # 发送请求到爬虫API
            url = "http://localhost:8000/api/database/crawler/run"
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "platform": "all",
                "keywords": ["校园", "学生", "教育", "高校"]
            }
            
            try:
                response = requests.post(url, json=data, headers=headers, timeout=120)
                response.raise_for_status()
                
                result = response.json()
                print(f"爬虫任务完成: {result['message']}")
                print(f"抓取数据数量: {result.get('crawled_count', 0)}")
                print(f"任务ID: {result.get('task_id', 'N/A')}")
                
            except Exception as e:
                print(f"爬虫任务失败: {str(e)}")
            
            # 等待一段时间后再次运行
            wait_time = 20  # 20秒
            print(f"等待 {wait_time} 秒后开始下一轮...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print("\n爬虫已停止")

if __name__ == "__main__":
    run_continuous_crawler()
