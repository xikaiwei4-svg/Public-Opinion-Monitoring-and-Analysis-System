# -*- coding: utf-8 -*-
"""
检查数据库中的数据
"""
import pymysql

# MySQL数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'campus_opinion',
    'charset': 'utf8mb4'
}

def check_database():
    """检查数据库中的数据"""
    print("开始检查数据库...")
    
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES LIKE 'campus_opinion'")
        if cursor.fetchone() is None:
            print("错误: 数据库 'campus_opinion' 不存在")
            return
        
        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'opinions'")
        if cursor.fetchone() is None:
            print("错误: 表 'opinions' 不存在")
            return
        
        # 检查表结构
        print("表结构:")
        cursor.execute("DESCRIBE opinions")
        for row in cursor.fetchall():
            print(row)
        
        # 检查数据数量
        cursor.execute("SELECT COUNT(*) FROM opinions")
        count = cursor.fetchone()[0]
        print(f"\n数据库中的数据条数: {count}")
        
        # 检查前10条数据
        if count > 0:
            print("\n前10条数据:")
            cursor.execute("SELECT id, title, content, sentiment, sentiment_score, publish_time, crawl_time FROM opinions LIMIT 10")
            for row in cursor.fetchall():
                print(f"ID: {row[0]}")
                print(f"标题: {row[1]}")
                print(f"内容: {row[2][:100]}...")
                print(f"情感: {row[3]}")
                print(f"情感分数: {row[4]}")
                print(f"发布时间: {row[5]}")
                print(f"爬取时间: {row[6]}")
                print("-" * 50)
        else:
            print("数据库中没有数据")
            
    except Exception as e:
        print(f"检查数据库失败: {str(e)}")
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    check_database()
