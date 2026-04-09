# MySQL数据库配置
from pydantic_settings import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

class MySQLSettings(BaseSettings):
    MYSQL_HOST: str = "localhost"  # 数据库主机
    MYSQL_PORT: int = 3306  # 数据库端口
    MYSQL_USER: str = "root"  # 数据库用户
    MYSQL_PASSWORD: str = ""  # 强烈建议通过环境变量或.env文件配置
    MYSQL_DATABASE: str = "campus_opinion"  # 数据库名称
    
    class Config:
        env_file = ".env"

# 获取配置
settings = MySQLSettings()

# 构建数据库URL（先连接到mysql数据库来创建目标数据库）
# 添加charset=utf8mb4确保中文正确存储
DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}?charset=utf8mb4"

# 用于创建数据库的引擎（连接到mysql系统数据库）
ADMIN_DATABASE_URL = f"mysql+pymysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/mysql?charset=utf8mb4"
admin_engine = create_engine(ADMIN_DATABASE_URL, pool_pre_ping=True)

# 创建目标数据库的引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

# 获取数据库会话
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 创建所有表
def create_tables():
    Base.metadata.create_all(bind=engine)
