# 检查数据库连接状态
import sys
from db.mysql_config import engine, admin_engine, create_tables
from sqlalchemy import text

def check_mysql_connection():
    print("正在检查MySQL数据库连接...")
    try:
        # 测试连接到MySQL系统数据库
        with admin_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 成功连接到MySQL系统数据库")
    except Exception as e:
        print(f"✗ 连接MySQL系统数据库失败: {e}")
        return False
    
    try:
        # 测试连接到目标数据库
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ 成功连接到目标数据库")
    except Exception as e:
        print(f"✗ 连接目标数据库失败: {e}")
        # 尝试创建数据库
        try:
            with admin_engine.connect() as conn:
                conn.execute(text("CREATE DATABASE IF NOT EXISTS campus_opinion"))
                conn.commit()
                print("✓ 成功创建数据库")
                # 再次测试连接
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1"))
                    print("✓ 成功连接到目标数据库")
        except Exception as e:
            print(f"✗ 创建数据库失败: {e}")
            return False
    
    # 尝试创建表
    try:
        create_tables()
        print("✓ 成功创建表结构")
    except Exception as e:
        print(f"✗ 创建表结构失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = check_mysql_connection()
    if success:
        print("\n🎉 数据库连接检查通过！")
        sys.exit(0)
    else:
        print("\n❌ 数据库连接检查失败！")
        sys.exit(1)
