# -*- coding: utf-8 -*-
"""
检查数据库中的数据
"""
from db.mysql_config import get_db, engine
from models.mysql_models import Opinion
from sqlalchemy import text

def check_database_data():
    """检查数据库中的数据"""
    try:
        db = next(get_db())
        
        # 获取总记录数
        total = db.query(Opinion).count()
        print(f"总记录数: {total}")
        
        # 获取前5条记录
        opinions = db.query(Opinion).limit(5).all()
        
        print("\n前5条记录:")
        for i, opinion in enumerate(opinions, 1):
            print(f"\n记录 {i}:")
            print(f"  ID: {opinion.id}")
            print(f"  标题: {opinion.title}")
            print(f"  内容: {opinion.content[:100]}..." if opinion.content and len(opinion.content) > 100 else f"  内容: {opinion.content}")
            print(f"  平台: {opinion.source_platform}")
            print(f"  作者: {opinion.author}")
            print(f"  情感: {opinion.sentiment}")
            
            # 检查to_dict方法
            opinion_dict = opinion.to_dict()
            print(f"  to_dict标题: {opinion_dict.get('title')}")
            
    except Exception as e:
        print(f"检查数据失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("检查数据库数据...")
    check_database_data()
