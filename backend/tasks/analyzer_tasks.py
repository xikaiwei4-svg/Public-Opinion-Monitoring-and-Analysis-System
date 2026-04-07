from celery import shared_task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from collections import Counter
import jieba
import jieba.analyse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
from ..db.mongo_client import opinion_collection, hot_topics_collection, trend_analysis_collection
from ..models.opinion_model import SentimentType
from ..celery_config import ANALYZER_CONFIG

# 创建日志记录器
logger = get_task_logger(__name__)

# 加载情感分析模型（在实际应用中应该在启动时加载）
# 这里仅作为示例，实际部署时可能需要调整模型加载方式
sentiment_tokenizer = None
sentiment_model = None

def load_sentiment_model():
    """\加载情感分析模型"""
    global sentiment_tokenizer, sentiment_model
    if sentiment_tokenizer is None or sentiment_model is None:
        model_name = ANALYZER_CONFIG['sentiment']['model']
        logger.info(f"正在加载情感分析模型: {model_name}")
        sentiment_tokenizer = AutoTokenizer.from_pretrained(model_name)
        sentiment_model = AutoModelForSequenceClassification.from_pretrained(model_name)
        logger.info(f"情感分析模型加载完成: {model_name}")

@shared_task(name='backend.tasks.analyzer.run_sentiment_analysis', queue='analyzer')
def run_sentiment_analysis(days=1):
    """
    对近期爬取的舆情数据进行情感分析
    """
    logger.info(f"开始运行情感分析任务，分析过去{days}天的数据")
    
    try:
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # 查询未分析的舆情数据
        query = {
            "crawl_time": {"$gte": start_time, "$lte": end_time},
            "sentiment_analyzed": {"$ne": True}
        }
        
        # 获取数据
        opinions = list(opinion_collection.find(query))
        logger.info(f"找到 {len(opinions)} 条未分析的舆情数据")
        
        if not opinions:
            logger.info("没有需要分析的舆情数据")
            return {"status": "success", "message": "没有需要分析的舆情数据"}
        
        # 模拟情感分析（实际应用中应该使用真实的模型进行分析）
        analyzed_count = 0
        for opinion in opinions:
            # 模拟情感得分和类型
            # 在实际应用中，这里应该调用load_sentiment_model()和真实的模型进行预测
            content = opinion.get('content', '')
            
            # 简单的情感分析逻辑（仅作为示例）
            positive_words = ['好', '满意', '提升', '优秀', '积极', '完善', '成功', '支持']
            negative_words = ['差', '不满', '问题', '糟糕', '失败', '不足', '缺陷', '失望']
            
            pos_count = sum(1 for word in positive_words if word in content)
            neg_count = sum(1 for word in negative_words if word in content)
            
            # 计算情感得分
            if pos_count + neg_count > 0:
                sentiment_score = (pos_count - neg_count) / (pos_count + neg_count)
            else:
                sentiment_score = 0.0
            
            # 确定情感类型
            if sentiment_score > ANALYZER_CONFIG['sentiment']['thresholds']['positive']:
                sentiment_type = SentimentType.POSITIVE
            elif sentiment_score < ANALYZER_CONFIG['sentiment']['thresholds']['negative']:
                sentiment_type = SentimentType.NEGATIVE
            else:
                sentiment_type = SentimentType.NEUTRAL
            
            # 更新数据
            opinion_collection.update_one(
                {"_id": opinion["_id"]},
                {
                    "$set": {
                        "sentiment": sentiment_score,
                        "sentiment_type": sentiment_type,
                        "sentiment_analyzed": True,
                        "sentiment_analysis_time": datetime.now()
                    }
                }
            )
            
            analyzed_count += 1
        
        logger.info(f"情感分析任务完成，成功分析 {analyzed_count} 条数据")
        return {"status": "success", "message": f"成功分析{analyzed_count}条数据"}
    except Exception as e:
        logger.error(f"情感分析任务失败: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task(name='backend.tasks.analyzer.run_hot_topics_detection', queue='analyzer')
def run_hot_topics_detection(days=1, top_n=20):
    """
    检测热点话题
    """
    logger.info(f"开始运行热点话题检测任务，分析过去{days}天的数据，提取{top_n}个热点")
    
    try:
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        # 查询指定时间范围内的舆情数据
        query = {
            "publish_time": {"$gte": start_time, "$lte": end_time}
        }
        
        # 获取数据
        opinions = list(opinion_collection.find(query, {"content": 1, "keywords": 1, "heat_score": 1}))
        logger.info(f"找到 {len(opinions)} 条舆情数据用于热点话题检测")
        
        if not opinions:
            logger.info("没有足够的数据进行热点话题检测")
            return {"status": "success", "message": "没有足够的数据进行热点话题检测"}
        
        # 合并所有文本内容
        all_text = ' '.join([opinion.get('content', '') for opinion in opinions])
        
        # 使用TF-IDF提取关键词
        # 简单的关键词提取（实际应用中应该使用更复杂的方法）
        # 首先使用jieba进行分词
        jieba.analyse.set_stop_words("stopwords.txt")  # 假设存在停用词表
        keywords = jieba.analyse.extract_tags(all_text, topK=100, withWeight=True)
        
        # 模拟热点话题检测结果
        hot_topics = []
        topic_counter = Counter()
        
        # 从关键词中生成热点话题
        for i, (keyword, weight) in enumerate(keywords[:top_n]):
            # 模拟计算热度分数和情感倾向
            topic_heat_score = round(weight * 100, 2)
            avg_sentiment = round(np.random.uniform(-1, 1), 2)
            related_opinions_count = np.random.randint(5, 100)
            
            # 创建热点话题数据
            hot_topic = {
                "id": f"topic_{int(datetime.now().timestamp())}_{i}",
                "topic": f"关于{keyword}的讨论",
                "keywords": [keyword] + [kw for kw, _ in keywords[i:i+5] if kw != keyword],
                "heat_score": topic_heat_score,
                "sentiment": avg_sentiment,
                "related_opinions_count": related_opinions_count,
                "start_time": start_time,
                "end_time": end_time,
                "trend": np.random.choice(['rising', 'stable', 'falling']),
                "platforms": ["weibo", "wechat", "zhihu"],
                "details": {
                    "description": f"这是关于{keyword}的热点话题，近期在校园内引起广泛讨论。",
                    "peak_time": start_time + timedelta(hours=np.random.randint(0, days*24))
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            hot_topics.append(hot_topic)
        
        # 保存热点话题到数据库
        if hot_topics:
            hot_topics_collection.insert_many(hot_topics)
        
        logger.info(f"热点话题检测任务完成，成功检测出 {len(hot_topics)} 个热点话题")
        return {"status": "success", "message": f"成功检测出{len(hot_topics)}个热点话题"}
    except Exception as e:
        logger.error(f"热点话题检测任务失败: {str(e)}")
        return {"status": "error", "message": str(e)}

@shared_task(name='backend.tasks.analyzer.generate_daily_summary', queue='analyzer')
def generate_daily_summary(date=None):
    """
    生成每日舆情摘要报告
    """
    logger.info(f"开始生成每日舆情摘要报告，日期: {date or '今天'}")
    
    try:
        # 确定日期范围
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        else:
            report_date = datetime.now() - timedelta(days=1)  # 默认为昨天
        
        start_time = datetime(report_date.year, report_date.month, report_date.day)
        end_time = start_time + timedelta(days=1)
        
        # 查询当天的舆情数据
        query = {
            "publish_time": {"$gte": start_time, "$lt": end_time}
        }
        
        # 获取数据
        opinions = list(opinion_collection.find(query))
        total_count = len(opinions)
        
        # 统计情感分布
        sentiment_counts = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        
        sensitive_count = 0
        total_heat_score = 0
        
        for opinion in opinions:
            sentiment_type = opinion.get('sentiment_type', 'neutral')
            if sentiment_type in sentiment_counts:
                sentiment_counts[sentiment_type] += 1
            
            if opinion.get('is_sensitive', False):
                sensitive_count += 1
            
            total_heat_score += opinion.get('heat_score', 0)
        
        # 计算平均热度
        avg_heat_score = round(total_heat_score / total_count, 2) if total_count > 0 else 0
        
        # 找出当天的热点话题
        hot_topics = list(hot_topics_collection.find({
            "start_time": {"$gte": start_time},
            "end_time": {"$lt": end_time}
        }).sort("heat_score", -1).limit(5))
        
        # 创建摘要报告
        summary_report = {
            "id": f"summary_{report_date.strftime('%Y%m%d')}",
            "date": report_date,
            "total_count": total_count,
            "sentiment_distribution": sentiment_counts,
            "sensitive_count": sensitive_count,
            "avg_heat_score": avg_heat_score,
            "top_hot_topics": [
                {"topic": topic["topic"], "heat_score": topic["heat_score"]} \
                for topic in hot_topics
            ],
            "generated_at": datetime.now(),
            "summary": f"{report_date.strftime('%Y年%m月%d日')}，共监测到{total_count}条舆情数据。其中正面{sentiment_counts['positive']}条，负面{sentiment_counts['negative']}条，中性{sentiment_counts['neutral']}条。敏感内容{sensitive_count}条。平均热度{avg_heat_score}分。"
        }
        
        # 保存摘要报告（可以保存到专门的集合中）
        # summary_collection.insert_one(summary_report)
        
        logger.info(f"每日舆情摘要报告生成完成，日期: {report_date.strftime('%Y-%m-%d')}")
        return {"status": "success", "message": "每日舆情摘要报告生成完成", "report_date": report_date.strftime('%Y-%m-%d')}
    except Exception as e:
        logger.error(f"每日舆情摘要报告生成失败: {str(e)}")
        return {"status": "error", "message": str(e)}