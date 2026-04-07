# -*- coding: utf-8 -*-
"""
运行爬虫任务
"""
import sys
import time
from tasks.crawler_tasks import run_weibo_crawler, run_wechat_crawler, run_zhihu_crawler


def main():
    """主函数"""
    print("开始运行爬虫任务...")
    
    # 运行微博爬虫
    print("\n运行微博爬虫...")
    try:
        result = run_weibo_crawler()
        print(f"微博爬虫结果: {result}")
    except Exception as e:
        print(f"微博爬虫失败: {str(e)}")
    
    # 等待一段时间
    time.sleep(2)
    
    # 运行微信爬虫
    print("\n运行微信爬虫...")
    try:
        result = run_wechat_crawler()
        print(f"微信爬虫结果: {result}")
    except Exception as e:
        print(f"微信爬虫失败: {str(e)}")
    
    # 等待一段时间
    time.sleep(2)
    
    # 运行知乎爬虫
    print("\n运行知乎爬虫...")
    try:
        result = run_zhihu_crawler()
        print(f"知乎爬虫结果: {result}")
    except Exception as e:
        print(f"知乎爬虫失败: {str(e)}")
    
    print("\n所有爬虫任务已完成！")


if __name__ == "__main__":
    main()
