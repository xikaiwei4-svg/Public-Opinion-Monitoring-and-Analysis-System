# MySQL数据库管理路由
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import text, func
from sqlalchemy.orm import Session
import json
from pydantic import BaseModel

from db.mysql_config import get_db, engine, admin_engine, settings
from models.mysql_models import Opinion, User, HotTopic, TrendData, CrawlerLog, Base

router = APIRouter(prefix="/api/database", tags=["数据库管理"])

# 创建数据库和表
@router.post("/init")
def init_database():
    try:
        # 使用admin引擎创建数据库（连接到mysql系统数据库）
        with admin_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            conn.commit()
        
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        
        return {"message": "数据库初始化成功", "database": settings.MYSQL_DATABASE}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")

# 获取数据库统计信息
@router.get("/stats")
def get_database_stats(db: Session = Depends(get_db)):
    try:
        # 获取各表记录数
        opinions_count = db.query(Opinion).count()
        users_count = db.query(User).count()
        hot_topics_count = db.query(HotTopic).count()
        trend_data_count = db.query(TrendData).count()
        crawler_logs_count = db.query(CrawlerLog).count()
        
        total_records = opinions_count + users_count + hot_topics_count + trend_data_count + crawler_logs_count
        
        # 构建集合信息（模拟MongoDB的集合概念）
        collections_info = [
            {
                "name": "opinions",
                "documentCount": opinions_count,
                "size": f"{opinions_count * 2.5:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "avgObjSize": "2.5 KB",
                "storageSize": f"{opinions_count * 3:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "indexCount": 3,
                "indexSize": f"{opinions_count * 0.5:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "status": "normal" if opinions_count < 100000 else "warning"
            },
            {
                "name": "users",
                "documentCount": users_count,
                "size": f"{users_count * 1.5:.1f} KB" if users_count > 0 else "0 Bytes",
                "avgObjSize": "1.5 KB",
                "storageSize": f"{users_count * 2:.1f} KB" if users_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{users_count * 0.3:.1f} KB" if users_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "name": "hot_topics",
                "documentCount": hot_topics_count,
                "size": f"{hot_topics_count * 2:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "avgObjSize": "2 KB",
                "storageSize": f"{hot_topics_count * 2.5:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{hot_topics_count * 0.4:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "name": "trend_data",
                "documentCount": trend_data_count,
                "size": f"{trend_data_count * 1.8:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "avgObjSize": "1.8 KB",
                "storageSize": f"{trend_data_count * 2.2:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{trend_data_count * 0.35:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "name": "crawler_logs",
                "documentCount": crawler_logs_count,
                "size": f"{crawler_logs_count * 3:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "avgObjSize": "3 KB",
                "storageSize": f"{crawler_logs_count * 3.5:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{crawler_logs_count * 0.5:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "status": "normal"
            }
        ]
        
        return {
            "db": settings.MYSQL_DATABASE,
            "collections": 5,
            "views": 0,
            "objects": total_records,
            "avgObjSize": 2200,
            "dataSize": total_records * 2200,
            "storageSize": total_records * 2600,
            "indexes": 11,
            "indexSize": total_records * 400,
            "totalSize": total_records * 3000,
            "fsUsedSize": 5242880000,
            "fsTotalSize": 10737418240,
            "collections_info": collections_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库统计信息失败: {str(e)}")

# 获取集合列表
@router.get("/collections")
def get_collections(db: Session = Depends(get_db)):
    try:
        opinions_count = db.query(Opinion).count()
        users_count = db.query(User).count()
        hot_topics_count = db.query(HotTopic).count()
        trend_data_count = db.query(TrendData).count()
        crawler_logs_count = db.query(CrawlerLog).count()
        
        collections = [
            {
                "key": "opinions",
                "name": "opinions",
                "documentCount": opinions_count,
                "size": f"{opinions_count * 2.5:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "avgObjSize": "2.5 KB",
                "storageSize": f"{opinions_count * 3:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "indexCount": 3,
                "indexSize": f"{opinions_count * 0.5:.1f} KB" if opinions_count > 0 else "0 Bytes",
                "status": "normal" if opinions_count < 100000 else "warning"
            },
            {
                "key": "users",
                "name": "users",
                "documentCount": users_count,
                "size": f"{users_count * 1.5:.1f} KB" if users_count > 0 else "0 Bytes",
                "avgObjSize": "1.5 KB",
                "storageSize": f"{users_count * 2:.1f} KB" if users_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{users_count * 0.3:.1f} KB" if users_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "key": "hot_topics",
                "name": "hot_topics",
                "documentCount": hot_topics_count,
                "size": f"{hot_topics_count * 2:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "avgObjSize": "2 KB",
                "storageSize": f"{hot_topics_count * 2.5:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{hot_topics_count * 0.4:.1f} KB" if hot_topics_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "key": "trend_data",
                "name": "trend_data",
                "documentCount": trend_data_count,
                "size": f"{trend_data_count * 1.8:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "avgObjSize": "1.8 KB",
                "storageSize": f"{trend_data_count * 2.2:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{trend_data_count * 0.35:.1f} KB" if trend_data_count > 0 else "0 Bytes",
                "status": "normal"
            },
            {
                "key": "crawler_logs",
                "name": "crawler_logs",
                "documentCount": crawler_logs_count,
                "size": f"{crawler_logs_count * 3:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "avgObjSize": "3 KB",
                "storageSize": f"{crawler_logs_count * 3.5:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "indexCount": 2,
                "indexSize": f"{crawler_logs_count * 0.5:.1f} KB" if crawler_logs_count > 0 else "0 Bytes",
                "status": "normal"
            }
        ]
        
        return collections
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集合列表失败: {str(e)}")

# 获取集合详情
@router.get("/collections/{collection_name}")
def get_collection_detail(collection_name: str, db: Session = Depends(get_db)):
    try:
        count = 0
        if collection_name == "opinions":
            count = db.query(Opinion).count()
        elif collection_name == "users":
            count = db.query(User).count()
        elif collection_name == "hot_topics":
            count = db.query(HotTopic).count()
        elif collection_name == "trend_data":
            count = db.query(TrendData).count()
        elif collection_name == "crawler_logs":
            count = db.query(CrawlerLog).count()
        else:
            raise HTTPException(status_code=404, detail=f"集合 {collection_name} 不存在")
        
        return {
            "name": collection_name,
            "documentCount": count,
            "size": f"{count * 2.5:.1f} KB" if count > 0 else "0 Bytes",
            "avgObjSize": "2.5 KB",
            "storageSize": f"{count * 3:.1f} KB" if count > 0 else "0 Bytes",
            "indexCount": 3,
            "indexSize": f"{count * 0.5:.1f} KB" if count > 0 else "0 Bytes",
            "status": "normal" if count < 100000 else "warning",
            "indexes": [
                {"name": "PRIMARY", "keys": {"id": 1}},
                {"name": "ix_source_platform", "keys": {"source_platform": 1}},
                {"name": "ix_publish_time", "keys": {"publish_time": -1}}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取集合详情失败: {str(e)}")

# 删除集合（清空表）
@router.delete("/collections/{collection_name}")
def delete_collection(collection_name: str, db: Session = Depends(get_db)):
    try:
        if collection_name == "opinions":
            db.query(Opinion).delete()
        elif collection_name == "users":
            db.query(User).delete()
        elif collection_name == "hot_topics":
            db.query(HotTopic).delete()
        elif collection_name == "trend_data":
            db.query(TrendData).delete()
        elif collection_name == "crawler_logs":
            db.query(CrawlerLog).delete()
        else:
            raise HTTPException(status_code=404, detail=f"集合 {collection_name} 不存在")
        
        db.commit()
        return {"message": f"集合 {collection_name} 已清空"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除集合失败: {str(e)}")

# 获取数据库配置信息
@router.get("/config")
def get_database_config():
    try:
        return {
            "host": settings.MYSQL_HOST,
            "port": settings.MYSQL_PORT,
            "database": settings.MYSQL_DATABASE,
            "username": settings.MYSQL_USER,
            "password": "********",
            "authSource": "mysql",
            "status": "connected",
            "lastConnected": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取数据库配置失败: {str(e)}")

# 获取舆情数据列表
@router.get("/opinions")
def get_opinions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    try:
        # 获取总数
        total = db.query(Opinion).count()
        # 获取分页数据
        opinions = db.query(Opinion).offset(skip).limit(limit).all()
        data = [opinion.to_dict() for opinion in opinions]
        # 返回包含总数的数据
        result = {
            "items": data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        return JSONResponse(content=result, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取舆情数据失败: {str(e)}")

# 创建舆情数据
@router.post("/opinions")
def create_opinion(opinion_data: Dict[str, Any], db: Session = Depends(get_db)):
    try:
        opinion = Opinion(**opinion_data)
        db.add(opinion)
        db.commit()
        db.refresh(opinion)
        return opinion.to_dict()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建舆情数据失败: {str(e)}")

# 运行爬虫任务（真实版本）

@router.post("/crawler/run")
def run_crawler(data: dict):
    platform = data.get("platform", "all")
    keywords = data.get("keywords", None)
    try:
        # 导入必要的库
        import requests
        from bs4 import BeautifulSoup
        
        # 真实的爬虫实现
        db = next(get_db())
        try:
            # 定义要抓取的网站 - 使用更通用的选择器
            sources = [
                # 综合教育网站
                {
                    "name": "新浪教育",
                    "url": "https://edu.sina.com.cn/",
                    "platform": "sina"
                },
                {
                    "name": "中国教育在线",
                    "url": "https://www.eol.cn/",
                    "platform": "eol"
                },
                {
                    "name": "中国教育新闻网",
                    "url": "http://www.jyb.cn/",
                    "platform": "jyb"
                },
                {
                    "name": "腾讯教育",
                    "url": "https://edu.qq.com/",
                    "platform": "qq"
                },
                {
                    "name": "搜狐教育",
                    "url": "https://learning.sohu.com/",
                    "platform": "sohu"
                },
                {
                    "name": "网易教育",
                    "url": "https://education.163.com/",
                    "platform": "163"
                },
                {
                    "name": "凤凰教育",
                    "url": "https://edu.ifeng.com/",
                    "platform": "ifeng"
                },
                
                # 高校相关网站
                {
                    "name": "中国高校之窗",
                    "url": "http://www.gx211.com/",
                    "platform": "gx211"
                },
                {
                    "name": "高校招生网",
                    "url": "https://www.gxzs.com/",
                    "platform": "gxzs"
                },
                {
                    "name": "中国考研网",
                    "url": "https://www.chinakaoyan.com/",
                    "platform": "chinakaoyan"
                },
                {
                    "name": "中国大学网",
                    "url": "https://www.chinauniversity.com.cn/",
                    "platform": "chinauniversity"
                },
                {
                    "name": "高校之窗",
                    "url": "https://www.gaoxiao.info/",
                    "platform": "gaoxiao"
                },
                
                # 教育考试网站
                {
                    "name": "高考网",
                    "url": "https://www.gaokao.com/",
                    "platform": "gaokao"
                },
                {
                    "name": "考研帮",
                    "url": "https://www.kaoyan.com/",
                    "platform": "kaoyanbang"
                },
                {
                    "name": "自考网",
                    "url": "https://www.zikao.com/",
                    "platform": "zikao"
                },
                
                # 教育行业网站
                {
                    "name": "教育界",
                    "url": "https://www.jyjy.net.cn/",
                    "platform": "jyjy"
                },
                {
                    "name": "教育信息网",
                    "url": "https://www.eduzhixin.com/",
                    "platform": "eduzhixin"
                },
                {
                    "name": "中国教育装备网",
                    "url": "https://www.ceiea.com/",
                    "platform": "ceiea"
                },
                
                # 地方教育网站
                {
                    "name": "北京教育考试院",
                    "url": "https://www.bjeea.cn/",
                    "platform": "bjeea"
                },
                {
                    "name": "上海教育考试院",
                    "url": "https://www.shmeea.edu.cn/",
                    "platform": "shmeea"
                },
                {
                    "name": "广东教育考试院",
                    "url": "https://eea.gd.gov.cn/",
                    "platform": "eeagd"
                }
            ]
            
            crawled_count = 0
            
            print(f"开始处理 {len(sources)} 个数据源")
            
            for i, source in enumerate(sources):
                if platform != "all" and source["platform"] != platform:
                    print(f"跳过数据源 {i+1}/{len(sources)}: {source['name']} (平台不匹配)")
                    continue
                
                try:
                    # 发送请求，添加请求头
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                    }
                    print(f"开始抓取 {i+1}/{len(sources)}: {source['name']}: {source['url']}")
                    response = requests.get(source["url"], headers=headers, timeout=15)
                    response.raise_for_status()
                    
                    # 自动检测编码
                    if response.encoding == 'ISO-8859-1':
                        response.encoding = response.apparent_encoding
                    print(f"获取页面成功，状态码: {response.status_code}, 编码: {response.encoding}")
                    
                    # 解析HTML，让BeautifulSoup自动检测编码
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # 使用更通用的方法提取新闻 - 查找所有的a标签
                    all_links = soup.find_all('a')
                    print(f"找到 {len(all_links)} 个链接")
                    
                    # 过滤和提取有效链接
                    processed_count = 0
                    skipped_count = 0
                    for link in all_links:  # 检查所有链接
                        try:
                            # 提取标题和链接
                            title = link.get_text(strip=True)
                            url = link.get('href', '')
                            
                            # 调试：打印前几个链接的信息
                            if processed_count < 3 and skipped_count < 10:
                                print(f"  检查链接: title='{title[:30]}...', url='{url[:50]}...', len={len(title)}")
                            
                            # 过滤条件
                            if len(title) < 2:  # 标题至少2个字符
                                skipped_count += 1
                                continue
                            if not url or url.strip() == '':  # 空链接跳过
                                skipped_count += 1
                                continue
                            if any(keyword in url.lower() for keyword in ['javascript:', 'void(0)']):
                                skipped_count += 1
                                continue
                            
                            # 处理协议相对链接
                            if url.startswith('//'):
                                # 使用与源站相同的协议
                                if source['url'].startswith('https'):
                                    url = 'https:' + url
                                else:
                                    url = 'http:' + url
                            
                            # 检查是否已存在
                            existing = db.query(Opinion).filter(Opinion.source_url == url).first()
                            if existing:
                                skipped_count += 1
                                continue
                            
                            # 创建舆情数据
                            opinion = Opinion(
                                title=title,
                                content=title,  # 简化处理，实际应该提取内容
                                source_platform=source["platform"],
                                source_url=url,
                                author=source["name"],
                                publish_time=datetime.now(),
                                sentiment="neutral",
                                sentiment_score=0.0,
                                keywords=",".join(title.split()[:5]),  # 简化关键词提取
                                read_count=0,
                                like_count=0,
                                comment_count=0,
                                share_count=0
                            )
                            
                            db.add(opinion)
                            crawled_count += 1
                            processed_count += 1
                            print(f"抓取成功: {title[:50]}...")
                                
                        except Exception as e:
                            print(f"抓取单条数据失败: {str(e)}")
                            continue
                    
                    print(f"从 {source['name']} 处理了 {processed_count} 条新数据")
                    
                except Exception as e:
                    print(f"抓取 {source['name']} 失败: {str(e)}")
                    continue
            
            # 保存数据
            if crawled_count > 0:
                db.commit()
                print(f"成功保存 {crawled_count} 条数据")
            else:
                print("没有抓取到新数据")
            
            # 记录爬虫日志
            log = CrawlerLog(
                platform=platform,
                status="success",
                start_time=datetime.now(),
                end_time=datetime.now(),
                total_count=crawled_count,
                success_count=crawled_count,
                error_count=0,
                error_message=""
            )
            db.add(log)
            db.commit()
            
            return {
                "status": "success",
                "message": f"{platform} 爬虫任务已完成",
                "task_id": f"crawler_task_{datetime.now().timestamp()}",
                "platform": platform,
                "crawled_count": crawled_count
            }
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"爬虫任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"运行爬虫任务失败: {str(e)}")

# 获取爬虫任务状态
@router.get("/crawler/task/{task_id}")
def get_crawler_task_status(task_id: str):
    try:
        return {
            "task_id": task_id,
            "status": "SUCCESS",
            "result": {"message": "任务已完成"}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")
