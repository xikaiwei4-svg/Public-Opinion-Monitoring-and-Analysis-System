# -*- coding: utf-8 -*-
"""
检查API响应
"""
import requests
import json
import logging

logger = logging.getLogger(__name__)

def check_api_response(timeout=10):
    """检查API响应"""
    try:
        response = requests.get('http://localhost:8001/api/database/opinions?skip=0&limit=5', timeout=timeout)
        logger.info(f"状态码: {response.status_code}")
        logger.info(f"Content-Type: {response.headers.get('content-type')}")
        logger.info(f"编码: {response.encoding}")
        
        try:
            data = response.json()
        except ValueError:
            logger.error("响应不是有效的 JSON")
            return

        logger.info(f"\n总记录数: {data.get('total')}")
        logger.info(f"返回记录数: {len(data.get('items', []))}")
        
        logger.info("\n前3条记录:")
        for i, item in enumerate(data.get('items', [])[:3], 1):
            logger.info(f"\n记录 {i}:")
            logger.info(f"  ID: {item.get('id')}")
            logger.info(f"  标题: {item.get('title')}")
            logger.info(f"  内容: {item.get('content', '')[:50]}...")
            logger.info(f"  平台: {item.get('source_platform')}")
            
    except requests.RequestException as e:
        logger.exception(f"检查API失败: {e}")
    except Exception as e:
        logger.exception(f"检查API失败: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(name)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.info("检查API响应...")
    check_api_response()
