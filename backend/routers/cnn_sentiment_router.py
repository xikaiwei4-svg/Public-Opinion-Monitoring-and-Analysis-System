# -*- coding: utf-8 -*-
"""
基于CNN的情感分析API路由
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from db.mysql_config import get_db
from models.mysql_models import Opinion
from models.cnn_sentiment_model import CNNSentimentModel

router = APIRouter(prefix="/api/cnn_sentiment", tags=["CNN情感分析"])

# 全局模型实例
cnn_model = None

def get_cnn_model():
    """获取CNN模型实例"""
    global cnn_model
    if cnn_model is None:
        cnn_model = CNNSentimentModel()
    return cnn_model

@router.get("/analyze/{opinion_id}")
async def analyze_opinion_sentiment(
    opinion_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """分析单条舆情的情感（使用CNN模型）"""
    try:
        # 获取舆情数据
        opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
        if not opinion:
            raise HTTPException(status_code=404, detail="舆情数据不存在")
        
        # 分析情感
        model = get_cnn_model()
        text = f"{opinion.title or ''} {opinion.content or ''}"
        sentiment_type, sentiment_score = model.predict(text)
        
        # 更新数据库
        opinion.sentiment = sentiment_type
        opinion.sentiment_score = sentiment_score
        db.commit()
        
        return {
            "id": opinion.id,
            "title": opinion.title,
            "content": opinion.content,
            "sentiment": sentiment_type,
            "sentiment_score": sentiment_score,
            "message": "情感分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"情感分析失败: {str(e)}")

@router.post("/batch_analyze")
async def batch_analyze_sentiment(
    opinion_ids: List[int],
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """批量分析情感（使用CNN模型）"""
    try:
        model = get_cnn_model()
        results = []
        
        for opinion_id in opinion_ids:
            opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
            if opinion:
                text = f"{opinion.title or ''} {opinion.content or ''}"
                sentiment_type, sentiment_score = model.predict(text)
                
                # 更新数据库
                opinion.sentiment = sentiment_type
                opinion.sentiment_score = sentiment_score
                
                results.append({
                    "id": opinion.id,
                    "sentiment": sentiment_type,
                    "sentiment_score": sentiment_score
                })
        
        db.commit()
        
        return {
            "total_analyzed": len(results),
            "results": results,
            "message": "批量情感分析完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量情感分析失败: {str(e)}")

@router.get("/analyze_text")
async def analyze_text_sentiment(
    text: str
) -> Dict[str, Any]:
    """分析文本情感（使用CNN模型）"""
    try:
        if not text:
            raise HTTPException(status_code=400, detail="文本不能为空")
        
        model = get_cnn_model()
        sentiment_type, sentiment_score = model.predict(text)
        
        return {
            "text": text,
            "sentiment": sentiment_type,
            "sentiment_score": sentiment_score,
            "message": "文本情感分析完成"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文本情感分析失败: {str(e)}")

@router.get("/statistics")
async def get_sentiment_statistics(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """获取情感分析统计（使用CNN模型分析所有数据）"""
    try:
        # 获取所有未分析的舆情数据
        opinions = db.query(Opinion).filter(
            (Opinion.sentiment.is_(None)) | 
            (Opinion.sentiment == "")
        ).all()
        
        if not opinions:
            # 所有数据都已分析
            total = db.query(Opinion).count()
            positive = db.query(Opinion).filter(Opinion.sentiment == "positive").count()
            negative = db.query(Opinion).filter(Opinion.sentiment == "negative").count()
            neutral = db.query(Opinion).filter(Opinion.sentiment == "neutral").count()
            
            return {
                "total": total,
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "positive_percentage": round(positive/total*100, 2) if total > 0 else 0,
                "negative_percentage": round(negative/total*100, 2) if total > 0 else 0,
                "neutral_percentage": round(neutral/total*100, 2) if total > 0 else 0,
                "message": "所有数据已分析"
            }
        
        # 分析未分析的数据
        model = get_cnn_model()
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for opinion in opinions:
            text = f"{opinion.title or ''} {opinion.content or ''}"
            sentiment_type, sentiment_score = model.predict(text)
            
            # 更新数据库
            opinion.sentiment = sentiment_type
            opinion.sentiment_score = sentiment_score
            
            if sentiment_type == "positive":
                positive_count += 1
            elif sentiment_type == "negative":
                negative_count += 1
            else:
                neutral_count += 1
        
        db.commit()
        
        # 计算总数
        total = db.query(Opinion).count()
        total_positive = db.query(Opinion).filter(Opinion.sentiment == "positive").count()
        total_negative = db.query(Opinion).filter(Opinion.sentiment == "negative").count()
        total_neutral = db.query(Opinion).filter(Opinion.sentiment == "neutral").count()
        
        return {
            "total": total,
            "positive": total_positive,
            "negative": total_negative,
            "neutral": total_neutral,
            "positive_percentage": round(total_positive/total*100, 2) if total > 0 else 0,
            "negative_percentage": round(total_negative/total*100, 2) if total > 0 else 0,
            "neutral_percentage": round(total_neutral/total*100, 2) if total > 0 else 0,
            "newly_analyzed": len(opinions),
            "message": "情感分析统计完成"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情感统计失败: {str(e)}")
