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
    检测热点话题 - 优化版本
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
        opinions = list(opinion_collection.find(query, {"content": 1, "keywords": 1, "heat_score": 1, "sentiment": 1, "platform": 1}))
        logger.info(f"找到 {len(opinions)} 条舆情数据用于热点话题检测")
        
        if not opinions:
            logger.info("没有足够的数据进行热点话题检测")
            return {"status": "success", "message": "没有足够的数据进行热点话题检测"}
        
        # 提取所有文本内容和关键词
        texts = [opinion.get('content', '') for opinion in opinions]
        all_keywords = []
        for opinion in opinions:
            if 'keywords' in opinion:
                if isinstance(opinion['keywords'], list):
                    all_keywords.extend(opinion['keywords'])
                else:
                    all_keywords.append(opinion['keywords'])
        
        # 使用TF-IDF提取关键词
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'  # 使用内置的英文停用词，中文停用词可以自定义
        )
        
        # 构建文档集合
        documents = texts + [' '.join(all_keywords)]
        tfidf_matrix = vectorizer.fit_transform(documents)
        
        # 获取关键词及其权重
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.sum(axis=0).A1
        keywords_with_scores = [(feature_names[i], tfidf_scores[i]) for i in range(len(feature_names))]
        
        # 按权重排序
        keywords_with_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 使用K-means聚类进行话题聚类
        if len(texts) > 10:  # 数据量足够时使用聚类
            # 准备聚类数据
            text_tfidf = vectorizer.transform(texts)
            
            # 使用肘部法则确定聚类数量
            from sklearn.cluster import KMeans
            from sklearn.metrics import silhouette_score
            
            best_k = 5
            best_score = -1
            
            for k in range(3, min(10, len(texts) // 2)):
                kmeans = KMeans(n_clusters=k, random_state=42)
                labels = kmeans.fit_predict(text_tfidf)
                
                if k > 1:
                    score = silhouette_score(text_tfidf, labels)
                    if score > best_score:
                        best_score = score
                        best_k = k
            
            # 使用最佳聚类数量
            kmeans = KMeans(n_clusters=best_k, random_state=42)
            labels = kmeans.fit_predict(text_tfidf)
            
            # 分析每个聚类的关键词
            cluster_keywords = {}
            for cluster_id in range(best_k):
                cluster_texts = [texts[i] for i, label in enumerate(labels) if label == cluster_id]
                if cluster_texts:
                    # 提取聚类的关键词
                    cluster_tfidf = vectorizer.transform(cluster_texts)
                    cluster_scores = cluster_tfidf.sum(axis=0).A1
                    cluster_keywords[cluster_id] = [(feature_names[i], cluster_scores[i]) for i in range(len(feature_names))]
                    cluster_keywords[cluster_id].sort(key=lambda x: x[1], reverse=True)
        else:
            # 数据量不足时，直接使用关键词频率
            cluster_keywords = {0: keywords_with_scores[:50]}
        
        # 生成热点话题
        hot_topics = []
        
        # 从聚类结果生成热点话题
        for cluster_id, cluster_keywords_list in cluster_keywords.items():
            if not cluster_keywords_list:
                continue
            
            # 获取聚类的主要关键词
            main_keywords = [kw for kw, _ in cluster_keywords_list[:5]]
            if not main_keywords:
                continue
            
            # 构建话题名称
            topic_name = "关于" + "、".join(main_keywords[:3]) + "的讨论"
            
            # 计算该话题的相关舆情
            related_opinions = []
            total_heat = 0
            total_sentiment = 0
            platforms = set()
            
            for opinion in opinions:
                content = opinion.get('content', '')
                if any(keyword in content for keyword in main_keywords):
                    related_opinions.append(opinion)
                    total_heat += opinion.get('heat_score', 0)
                    total_sentiment += opinion.get('sentiment', 0)
                    platforms.add(opinion.get('platform', 'unknown'))
            
            if not related_opinions:
                continue
            
            # 计算统计数据
            avg_heat = round(total_heat / len(related_opinions), 2)
            avg_sentiment = round(total_sentiment / len(related_opinions), 2)
            
            # 计算趋势
            # 简单的趋势判断：基于最近24小时的热度变化
            recent_opinions = [o for o in related_opinions if o.get('publish_time', datetime.now()) > end_time - timedelta(hours=24)]
            older_opinions = [o for o in related_opinions if o.get('publish_time', datetime.now()) <= end_time - timedelta(hours=24)]
            
            if recent_opinions and older_opinions:
                recent_heat = sum(o.get('heat_score', 0) for o in recent_opinions) / len(recent_opinions)
                older_heat = sum(o.get('heat_score', 0) for o in older_opinions) / len(older_opinions)
                
                if recent_heat > older_heat * 1.2:
                    trend = 'rising'
                elif recent_heat< older_heat * 0.8:
                    trend = 'falling'
                else:
                    trend = 'stable'
            else:
                trend = 'stable'
            
            # 创建热点话题数据
            hot_topic = {
                "id": f"topic_{int(datetime.now().timestamp())}_{cluster_id}",
                "topic": topic_name,
                "keywords": main_keywords,
                "heat_score": avg_heat,
                "sentiment": avg_sentiment,
                "related_opinions_count": len(related_opinions),
                "start_time": start_time,
                "end_time": end_time,
                "trend": trend,
                "platforms": list(platforms),
                "details": {
                    "description": f"这是关于{topic_name}的热点话题，近期在校园内引起广泛讨论。",
                    "peak_time": max([o.get('publish_time', start_time) for o in related_opinions])
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            hot_topics.append(hot_topic)
        
        # 如果聚类结果不足，添加基于关键词的热点话题
        if len(hot_topics) < top_n:
            for i, (keyword, weight) in enumerate(keywords_with_scores[:top_n - len(hot_topics)]):
                # 检查是否已存在类似话题
                if any(keyword in topic['topic'] for topic in hot_topics):
                    continue
                
                # 计算相关舆情
                related_opinions = [o for o in opinions if keyword in o.get('content', '')]
                if not related_opinions:
                    continue
                
                total_heat = sum(o.get('heat_score', 0) for o in related_opinions)
                total_sentiment = sum(o.get('sentiment', 0) for o in related_opinions)
                platforms = set(o.get('platform', 'unknown') for o in related_opinions)
                
                hot_topic = {
                    "id": f"topic_{int(datetime.now().timestamp())}_kw_{i}",
                    "topic": f"关于{keyword}的讨论",
                    "keywords": [keyword],
                    "heat_score": round(total_heat / len(related_opinions), 2),
                    "sentiment": round(total_sentiment / len(related_opinions), 2),
                    "related_opinions_count": len(related_opinions),
                    "start_time": start_time,
                    "end_time": end_time,
                    "trend": 'stable',
                    "platforms": list(platforms),
                    "details": {
                        "description": f"这是关于{keyword}的热点话题，近期在校园内引起广泛讨论。",
                        "peak_time": max([o.get('publish_time', start_time) for o in related_opinions])
                    },
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                hot_topics.append(hot_topic)
        
        # 按热度排序并限制数量
        hot_topics.sort(key=lambda x: x['heat_score'], reverse=True)
        hot_topics = hot_topics[:top_n]
        
        # 保存热点话题到数据库
        if hot_topics:
            # 删除旧的热点话题
            hot_topics_collection.delete_many({
                "start_time": {"$gte": start_time},
                "end_time": {"$lte": end_time}
            })
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