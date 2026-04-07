# -*- coding: utf-8 -*-
"""
检查API响应
"""
import requests
import json

def check_api_response():
    """检查API响应"""
    try:
        response = requests.get('http://localhost:8001/api/database/opinions?skip=0&limit=5')
        print(f"状态码: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"编码: {response.encoding}")
        
        data = response.json()
        print(f"\n总记录数: {data.get('total')}")
        print(f"返回记录数: {len(data.get('items', []))}")
        
        print("\n前3条记录:")
        for i, item in enumerate(data.get('items', [])[:3], 1):
            print(f"\n记录 {i}:")
            print(f"  ID: {item.get('id')}")
            print(f"  标题: {item.get('title')}")
            print(f"  内容: {item.get('content', '')[:50]}...")
            print(f"  平台: {item.get('source_platform')}")
            
    except Exception as e:
        print(f"检查API失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("检查API响应...")
    check_api_response()
