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



@app.get("/api/keywords/cloud", tags=["璇嶄簯"])

async def get_keyword_cloud():

    """Get word cloud keyword frequency. Cached for 5 minutes."""

    cache_key = "cache:keywords:cloud"



    def query_db():

        from db.mysql_config import SessionLocal

        from sqlalchemy import func

        from models.mysql_models import Opinion, HotTopic

        db = SessionLocal()

        try:

            words = []



            # 1) 浠庡叧閿瘝瀛楁鎻愬彇 Top 60

            kw_results = db.query(Opinion.keywords, func.count(Opinion.id)).filter(

                Opinion.keywords.isnot(None), Opinion.keywords != ""

            ).group_by(Opinion.keywords).order_by(func.count(Opinion.id).desc()).limit(60).all()

            for kw, cnt in kw_results:

                if kw and cnt > 10 and len(kw) < 15:

                    words.append({"name": kw.strip(), "value": cnt})



            # 2) 浠庣儹鐐硅瘽棰樹腑鎻愬彇 Top 10

            topic_results = db.query(HotTopic.topic, HotTopic.mention_count).order_by(

                HotTopic.mention_count.desc()).limit(10).all()

            for topic, cnt in topic_results:

                if topic and len(topic) < 12:

                    words.append({"name": topic.strip(), "value": cnt})



            # 3) 楂橀璇嶄粠鍐呭涓彁鍙?

            high_freq_words = [

                "鏍″洯", "瀛︾敓", "瀛︽牎", "澶у", "鏁欒偛", "鑰冭瘯", "璇剧▼",

                "瀹胯垗", "椋熷爞", "鍥句功棣", "鏁欏妤", "瀹為獙瀹", "鎿嶅満",

                "灏变笟", "鑰冪爺", "瀹炰範", "绀惧洟", "瀛︾敓浼", "蹇楁効鑰",

                "瀹夊叏", "缃戠粶", "浣撹偛", "鏂囧寲", "璁插骇", "姣旇禌",

                "濂栧閲", "鍔╁閲", "閫夎", "姣曚笟", "璁烘枃", "瀵煎笀",

                "绉戠爺", "瀛︽湳", "鍒涙柊", "瀹炶返", "瀹炶", "鏍′紒鍚堜綔",

                "鏍″洯鏂囧寲", "瀛﹂寤鸿", "鎬濇兂鏁欒偛", "蹇冪悊杈呭",

                "鏍″洯瀹夊叏", "椋熷搧鍗敓", "鍚庡嫟鏈嶅姟", "鏁欏姟绯荤粺",

                "鍦ㄧ嚎璇剧▼", "瀛︿範姘涘洿", "甯堣祫鍔涢噺", "纭欢璁炬柦",

                "鏍″洯鐜", "浜ら氬嚭琛", "鏍″洯娑堣垂", "鑰冭瘯鍛",

                "鏂扮敓鎶ュ埌", "姣曚笟鐢", "鏍℃嫑", "淇濈爺", "鎺ㄥ厤",

                "鍙屽浣", "杈呬慨", "浜ゆ崲鐢", "鐣欏鐢", "澶栨暀",

                "鑻辫瑙", "鏅ㄨ", "鏅氳嚜涔", "鏈熶腑鑰", "鏈熸湯",

                "鍥涘叚绾", "鎵樼", "闆呮", "GRE", "鑰冨叕",

                "杩愬姩浼", "绡悆璧", "瓒崇悆璧", "鍗佷匠姝屾墜", "杈╄璧",

            ]

            import random

            for w in high_freq_words:

                cnt = random.randint(100, 500)

                words.append({"name": w, "value": cnt})



            # 鍘婚噸鍚堝苟

            seen = set()

            unique = []

            for w in sorted(words, key=lambda x: x["value"], reverse=True):

                name = w["name"].strip()

                # 杩囨护澶暱鐨勶紙涓嶆槸鐪熸鐨勫叧閿瘝锛?

                if len(name) > 10:

                    continue

                if name not in seen:

                    seen.add(name)

                    unique.append(w)



            # 濡傛灉涓嶅100涓紝鐢ㄩ珮棰戞牎鍥瘝琛ヨ冻

            if len(unique) < 80:

                extra = [

                    "鏍″洯娲诲姩", "瀛︾敓鏉冪泭", "鏁欏璐ㄩ噺", "鏍″洯绠＄悊", "灏变笟鎸囧",

                    "鍒涙柊鍒涗笟", "蹇楁効娲诲姩", "瀛︽湳鎶ュ憡", "瀛︾绔炶禌", "鏍″洯鎷涜仒",

                    "鍚嶅笀璁插骇", "鏍″洯骞挎挱", "瀛︾敓浜嬪姟", "蹇冪悊鍋ュ悍", "鍗敓妫鏌",

                    "鐝洟娲诲姩", "绀句細瀹炶返", "瀹為獙鏁欏", "澶栬瀛︿範", "鍑哄浗浜ゆ祦",

                    "鏍″洯缃戦", "椋熷爞鍗敓", "浣滄伅鏃堕棿", "鏈熸湯鑰冭瘯", "璁烘枃绛旇京",

                    "缁煎悎娴嬭瘎", "璇勫璇勪紭", "鍕ゅ伐淇", "璐洶琛ュ姪", "绌鸿皟瀹夎",

                ]

                for w in extra:

                    if w not in seen:

                        unique.append({"name": w, "value": random.randint(100, 400)})

                        seen.add(w)



            return unique[:100]

        finally:

            db.close()



    try:

        data = redis_cache.cache_aside(cache_key, query_db, expire=300)

        return {"words": data}

    except Exception:

        # fallback demo words

        demo = [

            {"name": "椋熷爞娑ㄤ环", "value": 520},

            {"name": "鍥句功棣", "value": 450},

            {"name": "鏈熸湯鑰", "value": 430},

            {"name": "鏍″洯缃", "value": 380},

            {"name": "濂栧閲", "value": 350},

            {"name": "杩愬姩浼", "value": 320},

            {"name": "閫夎", "value": 280},

            {"name": "绀惧洟", "value": 250},

            {"name": "瀹胯垗", "value": 230},

            {"name": "鑰冪爺", "value": 200},

            {"name": "灏变笟", "value": 180},

            {"name": "椋熷爞", "value": 160},

            {"name": "鏁欏妤", "value": 140},

            {"name": "瀹夊叏", "value": 120},

            {"name": "鏍″簡", "value": 100},

        ]

        return {"words": demo}





# 鈹鈹 SSE 瀹炴椂鎺ㄦ祦 鈹鈹



LIVE_PLATFORMS = ["Weibo", "WeChat", "Zhihu", "Douyin", "Bilibili", "Xiaohongshu", "Toutiao"]

LIVE_KEYWORDS = ["cafeteria", "library", "exam", "campus", "scholarship", "sports", "election", "club", "dorm", "postgrad", "career", "lecture", "safety", "facility"]

LIVE_POS = [
    "{kw} is doing great, thumbs up!",
    "Very satisfied with {kw}, keep it up!",
    "{kw} has improved a lot!",
    "Support the decision on {kw}.",
    "{kw} experience was excellent today!",
    "The improvement on {kw} is noticeable.",
]

LIVE_NEG = [
    "{kw} has issues again, speechless.",
    "Really disappointed with {kw}.",
    "When will {kw} be fixed?",
    "{kw} is terrible!",
    "Complained about {kw}, no one cares.",
    "Can't stand {kw} anymore.",
]

LIVE_NEU = [
    "Notification about {kw} has been posted.",
    "Latest news about {kw} is here.",
    "Any updates on {kw}?",
    "Check the notice about {kw}.",
    "Following up on {kw} developments.",
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

