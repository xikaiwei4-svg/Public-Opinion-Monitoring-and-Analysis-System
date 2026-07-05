#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""

init_db.py  独立建表脚本



从环境变量 / .env 文件读取数据库连接信息，使用 SQLAlchemy ORM 创建全部表。



用法：

    python init_db.py                          # 正常建表

    python init_db.py --drop                   # 先删后建

    python init_db.py --verbose                # 打印 SQL 语句

    python init_db.py --env-file /path/to/.env  # 指定 .env 路径



依赖：

    pip install pymysql sqlalchemy pydantic-settings python-dotenv

"""



import argparse

import sys

import os

import logging



# 将项目根目录加入 sys.path（使 backend 内部的 import 可用）

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))



logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s [%(levelname)s] %(message)s",

)

logger = logging.getLogger("init_db")





def parse_args():

    parser = argparse.ArgumentParser(

        description="校园舆情系统  独立数据库建表脚本",

        formatter_class=argparse.RawDescriptionHelpFormatter,

        epilog="""

示例：

  python init_db.py

  python init_db.py --drop

  python init_db.py --verbose

  python init_db.py --env-file /etc/campus/.env

        """,

    )

    parser.add_argument(

        "--drop",

        action="store_true",

        help="先 DROP 所有表再重新创建（ 会丢失数据）",

    )

    parser.add_argument(

        "--verbose",

        action="store_true",

        help="打印建表的 SQL 语句",

    )

    parser.add_argument(

        "--env-file",

        default=None,

        help=".env 文件路径（默认从环境变量读取）",

    )

    return parser.parse_args()





def load_env(env_file: str | None):

    """加载 .env 文件（如果指定且存在）"""

    if env_file:

        if os.path.exists(env_file):

            from dotenv import load_dotenv



            load_dotenv(env_file)

            logger.info(f"已加载环境变量文件: {env_file}")

        else:

            logger.warning(f".env 文件不存在: {env_file}，将仅使用环境变量")

    else:

        # 尝试在项目根目录寻找 .env

        candidates = [

            os.path.join(os.path.dirname(__file__), "..", ".env"),

            os.path.join(os.path.dirname(__file__), "..", "..", ".env"),

        ]

        for p in candidates:

            p = os.path.abspath(p)

            if os.path.exists(p):

                from dotenv import load_dotenv



                load_dotenv(p)

                logger.info(f"已自动加载: {p}")

                return

        logger.info("未找到 .env 文件，仅使用系统环境变量")





def build_engine():

    """从环境变量构建 SQLAlchemy 引擎"""

    host = os.getenv("MYSQL_HOST", "localhost")

    port = os.getenv("MYSQL_PORT", "3306")

    user = os.getenv("MYSQL_USER", "root")

    password = os.getenv("MYSQL_PASSWORD", "")

    database = os.getenv("MYSQL_DATABASE", "campus_opinion")



    if not password:

        logger.warning("  MYSQL_PASSWORD 未设置，尝试空密码连接")



    from sqlalchemy import create_engine



    url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"

    logger.info(f"连接数据库: {host}:{port}/{database} (用户: {user})")

    engine = create_engine(url, pool_pre_ping=True)

    return engine, database





def ensure_database(engine, database: str):

    """确保目标数据库存在（若不存在则创建）"""

    from sqlalchemy import text



    try:

        with engine.connect() as conn:

            result = conn.execute(text(f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db"), {"db": database})

            if not result.fetchone():

                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))

                conn.commit()

                logger.info(f" 数据库 `{database}` 已创建")

            else:

                logger.info(f"数据库 `{database}` 已存在")

    except Exception as e:

        logger.warning(f"建库检查失败（权限不足或连接异常）: {e}")

        logger.warning("跳过建库步骤，假设数据库已存在")





def create_all_tables(engine, drop_first: bool = False, verbose: bool = False):

    """创建 / 重建全部表"""

    from db.mysql_config import Base



    if verbose:

        # 打印所有 CREATE TABLE 语句（不执行）

        from sqlalchemy.schema import CreateTable



        logger.info("=" * 50)

        logger.info("将创建的 SQL 语句:")

        logger.info("=" * 50)

        for table in Base.metadata.sorted_tables:

            stmt = str(CreateTable(table).compile(engine)).strip()

            logger.info(f"\n{stmt};\n")



    if drop_first:

        logger.warning("  正在删除所有表（数据将丢失）...")

        Base.metadata.drop_all(bind=engine)

        logger.info(" 旧表已全部删除")



    logger.info("正在创建表...")

    Base.metadata.create_all(bind=engine)

    logger.info(" 全部表创建完成")



    # 打印表清单

    tables = list(Base.metadata.sorted_tables)

    logger.info(f"共创建 {len(tables)} 张表:")

    for t in tables:

        col_count = len(t.columns)

        logger.info(f"  - {t.name}: {col_count} 列")





def main():

    args = parse_args()



    # 加载环境变量

    load_env(args.env_file)



    # 确保目标数据库存在

    engine, database = build_engine()

    ensure_database(engine, database)



    # 重新构建引擎（连到具体数据库）

    engine.close()

    engine, _ = build_engine()



    # 创建表

    create_all_tables(engine, drop_first=args.drop, verbose=args.verbose)



    logger.info(" init_db.py 执行完毕")





if __name__ == "__main__":

    main()

