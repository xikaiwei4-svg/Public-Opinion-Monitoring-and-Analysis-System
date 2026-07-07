# -*- coding: utf-8 -*-
"""爬虫调度 API"""

from fastapi import APIRouter
from services.crawler_service import scheduler, fetch_all_real_news, push_to_stream, consume_stream

router = APIRouter(prefix="/api/crawler", tags=["爬虫调度"])


@router.get("/status")
async def crawler_status():
    return {
        "running": scheduler._running,
        "stats": scheduler.stats,
    }


@router.post("/start")
async def crawler_start():
    if scheduler._running:
        return {"message": "爬虫已在运行中", "running": True}
    scheduler.start()
    return {"message": "爬虫已启动", "running": True}


@router.post("/stop")
async def crawler_stop():
    scheduler.stop()
    return {"message": "爬虫已停止", "running": False}


@router.post("/trigger")
async def crawler_trigger():
    """手动触发一轮真实新闻采集"""
    items = await fetch_all_real_news()
    pushed = push_to_stream(items) if items else 0
    consumed = consume_stream(batch_size=50)
    return {
        "pushed": pushed,
        "consumed": consumed,
        "scraped": len(items) if items else 0,
        "message": f"采集 {len(items) if items else 0} 条，推送 {pushed} 条，入库 {consumed} 条",
    }
