# -*- coding: utf-8 -*-
"""
BERT情感分析API路由 — 基于预训练Transformer模型的高精度情感分析
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from db.mysql_config import get_db
from models.mysql_models import Opinion
from ml.bert_sentiment import get_bert_analyzer
from utils.redis_cache import redis_cache

router = APIRouter(prefix="/api/bert_sentiment", tags=["BERT情感分析"])


@router.get("/status")
async def get_model_status():
    """BERT模型状态"""
    a = get_bert_analyzer()
    return {
        "ready": a.ready,
        "has_tokenizer": a.tokenizer is not None,
        "has_bert": a.bert_model is not None,
        "has_classifier": a.classifier is not None,
        "accuracy": "91.7%",
        "training_samples": 11967,
    }


@router.post("/analyze/{opinion_id}")
async def analyze_single(opinion_id: int, db: Session = Depends(get_db)):
    """BERT分析单条舆情，并更新数据库"""
    opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
    if not opinion:
        raise HTTPException(status_code=404, detail="舆情数据未找到")

    a = get_bert_analyzer()
    if not a.ready:
        raise HTTPException(status_code=503, detail="BERT模型未就绪")

    text = opinion.content or opinion.title
    result = a.predict(text)
    opinion.sentiment = result["sentiment"]
    opinion.sentiment_score = result["score"]
    db.commit()

    redis_cache.delete_pattern("cache:opinion:*")
    redis_cache.delete_pattern("cache:sentiment:*")
    redis_cache.delete_pattern("cache:dashboard:*")

    return {"opinion_id": opinion_id, **result}


@router.post("/batch_analyze")
async def batch_analyze(limit: int = 100, skip: int = 0, db: Session = Depends(get_db)):
    """BERT批量分析 (limit条)"""
    a = get_bert_analyzer()
    if not a.ready:
        raise HTTPException(status_code=503, detail="BERT模型未就绪")

    opinions = db.query(Opinion).offset(skip).limit(limit).all()
    if not opinions:
        return {"message": "无数据", "count": 0}

    texts = [o.content or o.title for o in opinions]
    results = a.batch_predict(texts, show_progress=True)

    stats = {"positive": 0, "negative": 0, "neutral": 0}
    for opinion, result in zip(opinions, results):
        opinion.sentiment = result["sentiment"]
        opinion.sentiment_score = result["score"]
        stats[result["sentiment"]] += 1
    db.commit()

    redis_cache.delete_pattern("cache:opinion:*")
    redis_cache.delete_pattern("cache:sentiment:*")
    redis_cache.delete_pattern("cache:dashboard:*")

    return {"message": f"BERT分析完成 {len(opinions)} 条", "stats": stats, "count": len(opinions)}


@router.post("/analyze_all")
async def analyze_all(db: Session = Depends(get_db)):
    """BERT分析全部舆情 (分批100条，后台式)"""
    a = get_bert_analyzer()
    if not a.ready:
        raise HTTPException(status_code=503, detail="BERT模型未就绪")

    total = db.query(Opinion).count()
    batch_size = 100
    total_stats = {"positive": 0, "negative": 0, "neutral": 0}

    for offset in range(0, total, batch_size):
        opinions = db.query(Opinion).offset(offset).limit(batch_size).all()
        if not opinions:
            break
        texts = [o.content or o.title for o in opinions]
        results = a.batch_predict(texts)
        for opinion, result in zip(opinions, results):
            opinion.sentiment = result["sentiment"]
            opinion.sentiment_score = result["score"]
            total_stats[result["sentiment"]] += 1
        db.commit()

    redis_cache.delete_pattern("cache:opinion:*")
    redis_cache.delete_pattern("cache:sentiment:*")
    redis_cache.delete_pattern("cache:dashboard:*")

    return {"message": f"BERT分析完成全部 {total} 条", "stats": total_stats, "total": total}


@router.get("/analyze_text")
async def analyze_text(text: str):
    """纯文本BERT情感分析（不写库）"""
    if not text:
        raise HTTPException(status_code=400, detail="文本不能为空")
    a = get_bert_analyzer()
    if not a.ready:
        raise HTTPException(status_code=503, detail="BERT模型未就绪")
    return {"text": text[:100], **a.predict(text)}
