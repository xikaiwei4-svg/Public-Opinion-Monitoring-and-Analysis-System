# -*- coding: utf-8 -*-
"""舆情采集引擎 — Redis Stream 缓冲 + 多数据源 + 定时调度"""

import os
import json
import random
import hashlib
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

import redis
import httpx

from db.mysql_config import SessionLocal
from models.mysql_models import Opinion

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
STREAM_KEY = "campus:crawler:stream"
CONSUMER_GROUP = "crawler-consumers"
CONSUMER_NAME = f"consumer-{os.uname().nodename if hasattr(os, 'uname') else '1'}"

# ── 舆情模板库 ──

PLATFORMS = ["weibo", "wechat", "zhihu", "douyin", "xiaohongshu", "bilibili", "toutiao"]

CAMPUS_TOPICS = {
    "食堂": {
        "positive": ["食堂新开的窗口味道太赞了，价格实惠", "食堂卫生检查结果优秀", "食堂推出了新菜品很受欢迎", "食堂延长了供餐时间方便学生"],
        "negative": ["食堂排队太长了等了半小时", "食堂又涨价了性价比低", "食堂某窗口卫生状况令人担忧", "食堂菜品太咸了口味不合适"],
        "neutral": ["食堂供应时间调整通知", "食堂菜品价格变动公告", "食堂暑期营业安排", "食堂新窗口招标结果公示"],
    },
    "图书馆": {
        "positive": ["图书馆延长开放时间了非常方便", "图书馆新增了自习座位", "图书馆线上预约系统很好用", "图书馆空调终于修好了"],
        "negative": ["图书馆自习室占座现象严重", "图书馆闭馆时间太早了", "图书馆某个区域太吵影响学习", "图书馆预约系统经常崩溃"],
        "neutral": ["图书馆暑期开放时间调整", "图书馆新书上架通知", "图书馆入馆须知更新", "图书馆座位预约规则变更"],
    },
    "宿舍": {
        "positive": ["宿舍新装的空调效果很好", "宿舍网络升级了网速快多了", "宿舍楼新加了洗衣机", "宿舍管理员服务态度很好"],
        "negative": ["宿舍热水供应不稳定老断", "宿舍隔音太差影响休息", "宿舍门禁太早不方便", "宿舍电费收费不合理"],
        "neutral": ["宿舍楼停水通知", "宿舍安全检查安排", "宿舍搬迁通知", "宿舍报修流程说明"],
    },
    "课程": {
        "positive": ["某老师的课讲得太好了受益匪浅", "新开的选修课内容丰富实用", "实验课设备更新了体验很好", "课程考核方式很合理"],
        "negative": ["某课程考试太难了挂科率高", "课程安排不合理时间冲突", "某老师上课只会念PPT", "实验课设备老旧经常故障"],
        "neutral": ["选课系统开放通知", "课程调课安排公告", "考试时间安排表发布", "补考报名通知"],
    },
    "校园网": {
        "positive": ["校园网提速了下载很快", "校园网覆盖范围扩大了", "校园网稳定性有所改善"],
        "negative": ["校园网又断了没法上网课", "校园网网速太慢看不了视频", "校园网收费太高不合理"],
        "neutral": ["校园网维护通知", "校园网升级改造公告", "校园网上网指南更新"],
    },
    "就业": {
        "positive": ["学校就业指导中心服务很专业", "校招企业质量很高", "某专业就业率创新高", "学校新增了实习基地"],
        "negative": ["就业形势严峻工作难找", "校招企业数量比往年少", "某专业就业前景堪忧"],
        "neutral": ["校园招聘会安排通知", "就业指导讲座公告", "毕业生就业手续办理指南"],
    },
    "奖学金": {
        "positive": ["奖学金评选结果公示公平公正", "学校增加了奖学金名额", "某同学获得国家级奖学金"],
        "negative": ["奖学金评选标准不透明", "奖学金金额太少了不够用", "奖学金申请流程太复杂"],
        "neutral": ["奖学金申请通知", "奖学金评选办法修订", "助学金发放安排"],
    },
    "社团": {
        "positive": ["某社团活动办得很成功", "社团招新现场气氛热烈", "社团文化节丰富多彩"],
        "negative": ["社团活动经费不足", "社团场地不够用", "社团管理太松散"],
        "neutral": ["社团招新通知", "社团换届公告", "社团活动审批流程"],
    },
}

AUTHORS = ["校园观察员", "学生小助手", "校园之声", "学子心声", "教育前沿",
           "大学生活指南", "高校资讯站", "学习达人", "校园热点追踪", "考试资讯通"]


def generate_opinion() -> dict:
    """生成一条仿真实时舆情"""
    topic_name = random.choice(list(CAMPUS_TOPICS.keys()))
    topic = CAMPUS_TOPICS[topic_name]
    sentiment = random.choices(["positive", "negative", "neutral"], weights=[35, 30, 35])[0]
    content = random.choice(topic[sentiment])

    platform = random.choice(PLATFORMS)
    now = datetime.now()
    # 随机几分钟到几小时内的时间
    publish_time = now - timedelta(minutes=random.randint(1, 180))

    return {
        "content": content,
        "source_platform": platform,
        "sentiment": sentiment,
        "sentiment_score": round(random.uniform(0.65, 0.95), 3) if sentiment == "positive"
        else round(random.uniform(0.05, 0.35), 3) if sentiment == "negative"
        else round(random.uniform(0.40, 0.60), 3),
        "keywords": topic_name,
        "source_url": f"https://{platform}.com/post/{random.randint(1000000, 9999999)}",
        "author": random.choice(AUTHORS),
        "read_count": random.randint(50, 500),
        "like_count": random.randint(0, 30),
        "comment_count": random.randint(0, 15),
        "share_count": random.randint(0, 10),
        "publish_time": publish_time.strftime("%Y-%m-%d %H:%M:%S"),
        "crawl_time": now.strftime("%Y-%m-%d %H:%M:%S"),
    }


# ── 教育新闻采集（真实数据源）──

EDU_RSS_FEEDS = [
    "https://www.eol.cn/web/api/feeds/news?page=1&size=10",
]

EDU_NEWS_URLS = [
    "https://news.baidu.com/ns?word=%E9%AB%98%E6%A0%A1%E6%95%99%E8%82%B2&pn=0&rn=5",
]


async def fetch_real_edu_news() -> list[dict]:
    """从真实教育新闻源采集舆情"""
    items = []
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for url in EDU_RSS_FEEDS:
            try:
                resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
                if resp.status_code == 200:
                    data = resp.json()
                    news_list = data.get("data", {}).get("list", data.get("data", []))
                    for article in news_list[:5]:
                        title = article.get("title", "")
                        if title and len(title) > 5:
                            items.append({
                                "content": title,
                                "source_platform": "eol",
                                "source_url": article.get("url", ""),
                                "author": article.get("source", "教育在线"),
                                "sentiment": "neutral",
                                "sentiment_score": 0.5,
                                "keywords": "教育新闻",
                                "read_count": random.randint(100, 1000),
                                "like_count": random.randint(0, 50),
                                "comment_count": random.randint(0, 20),
                                "share_count": random.randint(0, 15),
                                "publish_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            })
            except Exception as e:
                logger.warning("Real news fetch failed: %s", e)
    return items


# ── Redis Stream 操作 ──

def get_redis() -> Optional[redis.Redis]:
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)
        r.ping()
        return r
    except Exception as e:
        logger.warning("Redis unavailable: %s", e)
        return None


def push_to_stream(items: list[dict]) -> int:
    """推送舆情条目到 Redis Stream"""
    r = get_redis()
    if not r:
        return 0
    count = 0
    for item in items:
        item["_id"] = hashlib.md5(item["content"].encode()).hexdigest()[:12]
        r.xadd(STREAM_KEY, item, maxlen=10000)
        count += 1
    return count


def consume_stream(batch_size: int = 20) -> int:
    """从 Redis Stream 消费舆情并写入 MySQL"""
    r = get_redis()
    if not r:
        return 0

    # 创建消费者组
    try:
        r.xgroup_create(STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True)
    except Exception:
        pass

    db = SessionLocal()
    inserted = 0
    try:
        messages = r.xreadgroup(CONSUMER_GROUP, CONSUMER_NAME, {STREAM_KEY: ">"}, count=batch_size, block=2000)
        for stream_name, entries in messages:
            for msg_id, fields in entries:
                try:
                    opinion = Opinion(
                        content=fields.get("content", ""),
                        source_platform=fields.get("source_platform", "other"),
                        source_url=fields.get("source_url", ""),
                        author=fields.get("author", ""),
                        sentiment=fields.get("sentiment", "neutral"),
                        sentiment_score=float(fields.get("sentiment_score", 0.5)),
                        keywords=fields.get("keywords", ""),
                        read_count=int(fields.get("read_count", 0)),
                        like_count=int(fields.get("like_count", 0)),
                        comment_count=int(fields.get("comment_count", 0)),
                        share_count=int(fields.get("share_count", 0)),
                        publish_time=datetime.strptime(fields.get("publish_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")), "%Y-%m-%d %H:%M:%S"),
                        crawl_time=datetime.now(),
                    )
                    db.add(opinion)
                    inserted += 1
                except Exception as e:
                    logger.error("Insert opinion failed: %s", e)
                # 确认消息
                r.xack(STREAM_KEY, CONSUMER_GROUP, msg_id)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Consume stream failed: %s", e)
    finally:
        db.close()

    return inserted


# ── 爬虫调度 ──

class CrawlerScheduler:
    """轻量调度器 — 后台线程定时触发采集"""

    def __init__(self):
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._stats = {"crawled": 0, "consumed": 0, "last_run": None, "errors": 0}

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        logger.info("Crawler scheduler started")

    def stop(self):
        self._running = False
        logger.info("Crawler scheduler stopped")

    def _loop(self):
        """主循环：每 5-10 分钟生成一批舆情 + 消费流"""
        while self._running:
            try:
                # 1. 生成一批校园舆情（8-15 条/次）
                batch = [generate_opinion() for _ in range(random.randint(8, 15))]
                pushed = push_to_stream(batch)
                self._stats["crawled"] += pushed
                logger.info("Crawled %d opinions (total: %d)", pushed, self._stats["crawled"])

                # 2. 消费流入库
                consumed = consume_stream(batch_size=20)
                self._stats["consumed"] += consumed
                if consumed > 0:
                    logger.info("Consumed %d opinions into DB (total: %d)", consumed, self._stats["consumed"])

                # 3. 失效相关缓存
                r = get_redis()
                if r:
                    for pattern in ["cache:opinion:*", "cache:dashboard:*", "cache:trend:*", "cache:keywords:*", "cache:hot:*"]:
                        keys = r.keys(pattern)
                        if keys:
                            r.delete(*keys)

                self._stats["last_run"] = datetime.now().isoformat()

            except Exception as e:
                self._stats["errors"] += 1
                logger.error("Crawler loop error: %s", e)

            # 休眠 5-10 分钟再跑下一轮
            sleep_sec = random.randint(300, 600)
            time.sleep(sleep_sec)


# 全局实例
scheduler = CrawlerScheduler()
