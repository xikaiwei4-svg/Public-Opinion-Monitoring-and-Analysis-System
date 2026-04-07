# -*- coding: utf-8 -*-
"""
重新排序数据库ID，使其从1开始连续排列
"""
from sqlalchemy import text, create_engine
from db.mysql_config import settings, get_db
from models.mysql_models import Opinion, Base
import pymysql

def reorder_opinion_ids():
    """重新排序opinions表的ID"""
    try:
        # 创建连接
        connection_string = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        engine = create_engine(connection_string)
        
        with engine.connect() as conn:
            # 1. 创建临时表，复制原表数据
            print("创建临时表...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS opinions_temp LIKE opinions
            """))
            conn.commit()
            
            # 2. 将数据插入临时表，ID重新从1开始
            print("复制数据到临时表，重新排序ID...")
            conn.execute(text("""
                INSERT INTO opinions_temp (
                    title, content, source_platform, source_url, author, author_id,
                    publish_time, crawl_time, sentiment, sentiment_score, keywords,
                    read_count, like_count, comment_count, share_count, is_hot, hot_score
                )
                SELECT 
                    title, content, source_platform, source_url, author, author_id,
                    publish_time, crawl_time, sentiment, sentiment_score, keywords,
                    read_count, like_count, comment_count, share_count, is_hot, hot_score
                FROM opinions
                ORDER BY id ASC
            """))
            conn.commit()
            
            # 3. 删除原表
            print("删除原表...")
            conn.execute(text("DROP TABLE IF EXISTS opinions"))
            conn.commit()
            
            # 4. 重命名临时表为原表名
            print("重命名临时表...")
            conn.execute(text("RENAME TABLE opinions_temp TO opinions"))
            conn.commit()
            
            # 5. 重置自增计数器
            print("重置自增计数器...")
            conn.execute(text("ALTER TABLE opinions AUTO_INCREMENT = 1"))
            conn.commit()
            
            # 6. 获取新的记录数
            result = conn.execute(text("SELECT COUNT(*) FROM opinions"))
            count = result.fetchone()[0]
            
            print(f"✅ ID重新排序完成！")
            print(f"📊 当前记录数: {count}")
            print(f"🔢 ID范围: 1 - {count}")
            
            return True
            
    except Exception as e:
        print(f"❌ 重新排序失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔄 开始重新排序数据库ID...")
    success = reorder_opinion_ids()
    if success:
        print("\n✨ 操作完成！")
    else:
        print("\n💥 操作失败！")
