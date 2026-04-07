# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict, Any
import jieba
import jieba.analyse
import numpy as np

from db.mysql_config import get_db, engine
from models.mysql_models import Opinion, SentimentType

router = APIRouter(prefix="/api/sentiment", tags=["情感分析"])

# 情感分析关键词库
POSITIVE_WORDS = [
    '好', '优秀', '满意', '提升', '积极', '完善', '成功', '支持', '赞同', 
    '认可', '喜欢', '爱', '赞扬', '表扬', '鼓励', '进步', '发展',
    '创新', '突破', '领先', '优势', '强', '优', '佳', '美',
    '棒', '赞', '👍', '❤️', '🎉', '🌟', '✨', '👏',
    '值得', '推荐', '优秀', '出色', '杰出', '卓越', '辉煌', '精彩',
    '完美', '理想', '美好', '幸福', '快乐', '开心', '高兴', '喜悦',
    '激动', '兴奋', '热情', '积极', '正面', '肯定', '认可',
    '希望', '期待', '期待', '盼望', '信心', '相信', '信任',
    '感谢', '感激', '谢谢', '致谢', '荣幸', '骄傲', '自豪'
]

NEGATIVE_WORDS = [
    '差', '不满', '问题', '糟糕', '失败', '不足', '缺陷', '失望',
    '反对', '批评', '指责', '谴责', '愤怒', '生气', '恼火',
    '讨厌', '厌恶', '反感', '痛恨', '憎恨', '鄙视', '轻视',
    '质疑', '怀疑', '不信任', '担心', '忧虑', '焦虑', '恐惧',
    '悲伤', '难过', '痛苦', '痛苦', '痛苦', '痛苦', '痛苦',
    '遗憾', '后悔', '内疚', '羞愧', '羞耻', '丢脸', '丢人',
    '差劲', '糟糕', '恶劣', '恶劣', '恶劣', '恶劣', '恶劣',
    '👎', '❌', '😡', '😠', '😤', '😞', '😢', '😭',
    '不行', '不可以', '不能', '拒绝', '否认', '否定', '反对',
    '担忧', '忧虑', '担心', '害怕', '恐惧', '恐慌', '紧张',
    '压力', '困难', '挑战', '障碍', '阻碍', '限制', '约束',
    '下降', '下滑', '衰退', '萎缩', '减少', '降低', '减弱'
]

def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    分析文本的情感倾向
    
    Args:
        text: 要分析的文本内容
    
    Returns:
        包含情感类型和分数的字典
    """
    if not text:
        return {
            "sentiment_type": SentimentType.NEUTRAL,
            "sentiment_score": 0.0
        }
    
    # 使用jieba进行分词
    words = jieba.lcut(text)
    
    # 统计正面和负面词汇
    pos_count = sum(1 for word in words if word in POSITIVE_WORDS)
    neg_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    # 计算情感得分
    total_sentiment_words = pos_count + neg_count
    if total_sentiment_words > 0:
        sentiment_score = (pos_count - neg_count) / total_sentiment_words
    else:
        sentiment_score = 0.0
    
    # 确定情感类型
    if sentiment_score > 0.2:
        sentiment_type = SentimentType.POSITIVE
    elif sentiment_score < -0.2:
        sentiment_type = SentimentType.NEGATIVE
    else:
        sentiment_type = SentimentType.NEUTRAL
    
    return {
        "sentiment_type": sentiment_type,
        "sentiment_score": round(sentiment_score, 4)
    }

@router.get("/analyze")
def get_sentiment_analysis(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取舆情数据的情感分析结果
    """
    try:
        opinions = db.query(Opinion).offset(skip).limit(limit).all()
        data = [opinion.to_dict() for opinion in opinions]
        return {
            "status": "success",
            "data": data,
            "total": len(data),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情感分析结果失败: {str(e)}")

@router.post("/reanalyze")
def reanalyze_all_sentiments(db: Session = Depends(get_db)):
    """
    重新分析所有舆情数据的情感倾向
    """
    try:
        # 获取所有需要分析的舆情数据
        opinions = db.query(Opinion).all()
        total_count = len(opinions)
        
        if total_count == 0:
            return {
                "status": "success",
                "message": "没有需要分析的数据",
                "analyzed_count": 0,
                "total_count": 0
            }
        
        analyzed_count = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for opinion in opinions:
            # 分析标题和内容的情感
            text = f"{opinion.title or ''} {opinion.content or ''}"
            result = analyze_sentiment(text)
            
            # 更新情感分析结果
            opinion.sentiment = result["sentiment_type"]
            opinion.sentiment_score = result["sentiment_score"]
            
            # 统计情感类型
            if result["sentiment_type"] == SentimentType.POSITIVE:
                positive_count += 1
            elif result["sentiment_type"] == SentimentType.NEGATIVE:
                negative_count += 1
            else:
                neutral_count += 1
            
            analyzed_count += 1
            
            # 每100条提交一次
            if analyzed_count % 100 == 0:
                db.commit()
                print(f"已分析 {analyzed_count}/{total_count} 条数据")
        
        # 提交剩余的更改
        db.commit()
        
        return {
            "status": "success",
            "message": f"成功重新分析 {analyzed_count} 条数据",
            "analyzed_count": analyzed_count,
            "total_count": total_count,
            "statistics": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"重新分析情感倾向失败: {str(e)}")

@router.get("/statistics")
def get_sentiment_statistics(db: Session = Depends(get_db)):
    """
    获取情感分析统计数据
    """
    try:
        # 统计各情感类型的数量
        positive_count = db.query(Opinion).filter(Opinion.sentiment == SentimentType.POSITIVE).count()
        negative_count = db.query(Opinion).filter(Opinion.sentiment == SentimentType.NEGATIVE).count()
        neutral_count = db.query(Opinion).filter(Opinion.sentiment == SentimentType.NEUTRAL).count()
        total_count = positive_count + negative_count + neutral_count
        
        # 计算平均情感分数
        avg_sentiment_score = db.query(func.avg(Opinion.sentiment_score)).scalar() or 0.0
        
        # 按平台统计情感分布
        platform_stats = db.query(
            Opinion.source_platform,
            func.count(Opinion.id).label('total'),
            func.sum(func.case((Opinion.sentiment == SentimentType.POSITIVE, 1), else_=0)).label('positive'),
            func.sum(func.case((Opinion.sentiment == SentimentType.NEGATIVE, 1), else_=0)).label('negative'),
            func.sum(func.case((Opinion.sentiment == SentimentType.NEUTRAL, 1), else_=0)).label('neutral')
        ).group_by(Opinion.source_platform).all()
        
        platform_distribution = []
        for platform, total, pos, neg, neu in platform_stats:
            platform_distribution.append({
                "platform": platform or "unknown",
                "total": total,
                "positive": pos or 0,
                "negative": neg or 0,
                "neutral": neu or 0
            })
        
        return {
            "status": "success",
            "statistics": {
                "total_count": total_count,
                "positive_count": positive_count,
                "negative_count": negative_count,
                "neutral_count": neutral_count,
                "positive_percentage": round(positive_count / total_count * 100, 2) if total_count > 0 else 0,
                "negative_percentage": round(negative_count / total_count * 100, 2) if total_count > 0 else 0,
                "neutral_percentage": round(neutral_count / total_count * 100, 2) if total_count > 0 else 0,
                "avg_sentiment_score": round(avg_sentiment_score, 4)
            },
            "platform_distribution": platform_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情感统计失败: {str(e)}")

@router.post("/analyze/{opinion_id}")
def analyze_single_opinion(opinion_id: int, db: Session = Depends(get_db)):
    """
    分析单条舆情的情感倾向
    """
    try:
        opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
        if not opinion:
            raise HTTPException(status_code=404, detail=f"未找到ID为{opinion_id}的舆情数据")
        
        # 分析情感
        text = f"{opinion.title or ''} {opinion.content or ''}"
        result = analyze_sentiment(text)
        
        # 更新数据库
        opinion.sentiment = result["sentiment_type"]
        opinion.sentiment_score = result["sentiment_score"]
        db.commit()
        
        return {
            "status": "success",
            "message": "情感分析完成",
            "opinion_id": opinion_id,
            "sentiment_type": result["sentiment_type"],
            "sentiment_score": result["sentiment_score"]
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"分析单条舆情情感失败: {str(e)}")
