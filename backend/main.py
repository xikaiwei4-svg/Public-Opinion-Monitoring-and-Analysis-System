# -*- coding: utf-8 -*-

"""

鏍″洯鑸嗘儏妫娴嬩笌鐑偣璇濋鍒嗘瀽绯荤粺鍚庣

"""

from fastapi import FastAPI, Request

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, HTMLResponse

from fastapi.staticfiles import StaticFiles

from starlette.types import Scope

import mimetypes



# 闈欐佹枃浠剁紦瀛樺ご涓棿浠?

class CachedStaticFiles(StaticFiles):

    async def __call__(self, scope: Scope, receive, send):

        async def send_with_cache(event):

            if event["type"] == "http.response.start":

                headers = dict(event.get("headers", []))

                path = scope.get("path", "")

                if any(path.endswith(ext) for ext in (".js", ".css", ".woff2", ".png", ".jpg", ".svg", ".ico")):

                    headers[b"cache-control"] = b"public, max-age=31536000, immutable"

                elif path.endswith(".html"):

                    headers[b"cache-control"] = b"public, max-age=0, must-revalidate"

                event["headers"] = list(headers.items())

            await send(event)

        await super().__call__(scope, receive, send_with_cache)

from datetime import datetime

import uvicorn

import json

import logging

import random

import asyncio

import time

import os



_startup_start = 0.0



from routers.health_router import router as health_router

from routers.mysql_database_router import router as database_router

from routers.opinion_router import router as opinion_router

from routers.sentiment_router import router as sentiment_router

from routers.cnn_sentiment_router import router as cnn_sentiment_router

from routers.hot_topic_router import router as hot_topic_router

from routers.trend_router import router as trend_router
from routers.keyword_router import router as keyword_router
from routers.report_router import router as report_router



from utils.redis_cache import redis_cache



logging.basicConfig(

    level=logging.INFO,

    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'

)

logger = logging.getLogger(__name__)





class CustomJSONResponse(JSONResponse):

    def render(self, content) -> bytes:

        return json.dumps(content, ensure_ascii=False, allow_nan=False, indent=None, separators=(",", ":")).encode("utf-8")





app = FastAPI(

    title="鏍″洯鑸嗘儏妫娴嬩笌鐑偣璇濋鍒嗘瀽绯荤粺",

    description="鐢ㄤ簬瀹炴椂鐩戞帶銆佸垎鏋愬拰鍙鍖栨牎鍥浉鍏宠垎鎯呬俊鎭殑骞冲彴",

    version="2.0.0",

    default_response_class=CustomJSONResponse,

)



app.add_middleware(

    CORSMiddleware,

    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,

    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],

    allow_headers=["*"],

)



app.include_router(health_router)

app.include_router(database_router)

app.include_router(opinion_router)

app.include_router(sentiment_router)

app.include_router(cnn_sentiment_router)

app.include_router(hot_topic_router)

app.include_router(trend_router)
app.include_router(keyword_router)
app.include_router(report_router)


# 鈹鈹 闈欐佹枃浠讹紙鐢熶骇鍓嶇鏋勫缓浜х墿锛夆攢鈹

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend", "dist")

FRONTEND_DIST = os.path.abspath(FRONTEND_DIST)



if os.path.exists(FRONTEND_DIST):

    app.mount("/assets", CachedStaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    logger.info(f"鍓嶇闈欐佹枃浠舵湇鍔″凡鍚敤: {FRONTEND_DIST}")

else:

    logger.warning(f"鍓嶇鏋勫缓浜х墿涓嶅瓨鍦? {FRONTEND_DIST}锛屼粎鎻愪緵API鏈嶅姟")





@app.on_event("startup")

async def startup_event():

    global _startup_start

    _startup_start = time.time()



    # ── 自动创建数据库表（首次启动时） ──

    from models.report_model import Report  # noqa: F811  ensure table is registered
    from db.mysql_config import create_tables

    try:

        create_tables()

        logger.info("数据库表已就绪")

    except Exception as e:

        logger.warning(f"建表失败（可能已存在）: {e}")



    logger.info("绯荤粺鍚姩涓?..")



    # 鈹鈹 缂撳瓨棰勭儹锛堜粎鍏抽敭鏁版嵁锛屼笉鍔犺浇BERT锛夆攢鈹

    logger.info("寮濮婻edis缂撳瓨棰勭儹锛堣交閲忔ā寮忥級...")



    from db.mysql_config import SessionLocal

    from models.mysql_models import Opinion, HotTopic, TrendData

    from sqlalchemy import func



    def warmup_dashboard_stats():

        db = SessionLocal()

        try:

            total = db.query(Opinion).count()

            hot = db.query(HotTopic).count()

            views = db.query(func.sum(Opinion.read_count)).scalar() or 0

            sentiment_stats = db.query(Opinion.sentiment, func.count(Opinion.id)).group_by(Opinion.sentiment).all()

            dist = {"positive": 0, "negative": 0, "neutral": 0}

            for s, c in sentiment_stats:

                if s in dist:

                    dist[s] = c

            return {"total_count": total, "hot_topics_count": hot, "views_count": views, "sentiment_distribution": dist}

        finally:

            db.close()



    def warmup_hot_topics():

        db = SessionLocal()

        try:

            topics = db.query(HotTopic).order_by(HotTopic.mention_count.desc()).limit(50).all()

            return [{"id": t.id, "topic": t.topic, "keyword": t.keyword, "mention_count": t.mention_count,

                     "trend": t.trend, "first_seen": t.first_seen.isoformat() if t.first_seen else None,

                     "last_seen": t.last_seen.isoformat() if t.last_seen else None} for t in topics]

        finally:

            db.close()



    warmup_map = {

        "cache:dashboard:stats": warmup_dashboard_stats,

        "cache:hot:top50": warmup_hot_topics,

    }



    for key, warmup_fn in warmup_map.items():

        try:

            data = warmup_fn()

            if data:

                redis_cache.set(key, data, expire=600)

                logger.info(f"缂撳瓨棰勭儹瀹屾垚: {key}")

        except Exception as e:

            logger.warning(f"缂撳瓨棰勭儹澶辫触 [{key}]: {e}")



    logger.info(f"绯荤粺鍚姩瀹屾垚 ({time.time() - _startup_start:.1f}s) - Redis: {'鍙敤' if redis_cache.available else '鍐呭瓨妯″紡'} | BERT: 寤惰繜鍔犺浇")





@app.on_event("shutdown")

async def shutdown_event():

    logger.info("绯荤粺鍏抽棴涓?..")





@app.get("/", tags=["鍓嶇"])

async def serve_root():

    """Frontend index page. Port 80 maps here."""

    index_path = os.path.join(FRONTEND_DIST, "index.html")

    if os.path.exists(index_path):

        return FileResponse(index_path)

    return HTMLResponse("<h1>API Server Running</h1>")





@app.get("/api/ping", tags=["鍩虹鎺ュ彛"])

async def ping():

    return {"status": "ok", "message": "鏈嶅姟杩愯姝ｅ父", "timestamp": datetime.now().isoformat()}





@app.get("/api/cache/status", tags=["鍩虹鎺ュ彛"])

async def cache_status():

    """View cache status. Checks Redis availability."""

    return {

        "redis_available": redis_cache.available,

        "mode": "Redis" if redis_cache.available else "鍐呭瓨",

        "timestamp": datetime.now().isoformat(),

    }





@app.post("/api/cache/refresh", tags=["鍩虹鎺ュ彛"])

async def refresh_cache():

    """Manually refresh all cached data."""

    redis_cache.delete_pattern("cache:*")

    # 閲嶆柊棰勭儹

    from db.mysql_config import SessionLocal

    from models.mysql_models import Opinion, HotTopic

    from sqlalchemy import func

    db = SessionLocal()

    try:

        total = db.query(Opinion).count()

        hot = db.query(HotTopic).count()

        redis_cache.set("cache:dashboard:stats", {"total_count": total, "hot_topics_count": hot}, expire=600)

    finally:

        db.close()

    return {"message": "Cache refreshed", "timestamp": datetime.now().isoformat()}





# 鈹鈹 璇嶄簯鍏抽敭璇?API 鈹鈹



# 词云关键词 API 已迁移至 routers/keyword_router.py


# SSE 实时推送数据
LIVE_PLATFORMS = ["微博", "微信", "知乎", "抖音", "B站", "小红书", "头条"]
LIVE_KEYWORDS = ["食堂", "图书馆", "期末考试", "校园网", "奖学金", "运动会", "选修课", "社团", "宿舍", "考研", "就业", "讲座", "校庆", "安全"]
LIVE_POS = [
    "今天{kw}体验太好了，给学校点赞！",
    "对{kw}非常满意，继续保持！",
    "{kw}越来越好了，真开心！",
    "支持学校关于{kw}的决定！",
    "{kw}改进很明显，棒！",
    "这次{kw}做得不错！",
]
LIVE_NEG = [
    "{kw}又出问题了，无语",
    "对{kw}真的很失望",
    "{kw}什么时候能解决？",
    "{kw}实在太差了！",
    "投诉了{kw}没人管",
    "忍不了{kw}了",
]
LIVE_NEU = [
    "关于{kw}的通知已发布",
    "{kw}最新消息来了",
    "有了解{kw}情况的吗？",
    "{kw}相关通知请查收",
    "{kw}后续发展关注中",
]

@app.get("/api/live/stream")

async def live_stream(request: Request):

    """SSE real-time opinion stream"""



    async def event_generator():

        while True:

            if await request.is_disconnected():

                break



            kw = random.choice(LIVE_KEYWORDS)

            plat = random.choice(LIVE_PLATFORMS)

            r = random.random()

            if r < 0.25:

                content = random.choice(LIVE_POS).format(kw=kw)

                sentiment = "positive"

                score = random.uniform(0.7, 1.0)

            elif r < 0.50:

                content = random.choice(LIVE_NEG).format(kw=kw)

                sentiment = "negative"

                score = random.uniform(0.7, 1.0)

            else:

                content = random.choice(LIVE_NEU).format(kw=kw)

                sentiment = "neutral"

                score = random.uniform(0.5, 0.8)



            data = {

                "id": f"live_{int(time.time()*1000)}",

                "content": content,

                "source_platform": plat,

                "publish_time": datetime.now().isoformat(),

                "sentiment": sentiment,

                "sentiment_score": round(score, 3),

                "keywords": [kw],

            }



            yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

            await asyncio.sleep(random.randint(2, 5))



    return StreamingResponse(

        event_generator(),

        media_type="text/event-stream",

        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},

    )





# 鈹鈹 SPA fallback 鈥?蹇呴』鏀惧湪鎵鏈夎矾鐢辨渶鍚?鈹鈹

@app.get("/{full_path:path}")

async def serve_frontend(full_path: str):

    """SPA fallback - serve index.html for non-API routes"""

    if full_path.startswith("api/"):

        return JSONResponse({"detail": "Not Found"}, status_code=404)

    if FRONTEND_DIST and os.path.exists(FRONTEND_DIST):

        file_path = os.path.join(FRONTEND_DIST, full_path)

        if os.path.isfile(file_path) and not full_path.startswith("api"):

            return FileResponse(file_path)

        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

    return HTMLResponse("<h1>API Server Running</h1>")





if __name__ == "__main__":

    import sys

    port = 8001

    if len(sys.argv) > 2 and sys.argv[1] == "--port":

        port = int(sys.argv[2])

    uvicorn.run(app, host="0.0.0.0", port=port, workers=4)

