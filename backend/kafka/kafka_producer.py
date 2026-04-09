"""Kafka生产者服务"""
import json
import logging
from typing import Dict, Any, Optional
from kafka import KafkaProducer, KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import KafkaError

from .kafka_config import kafka_config

logger = logging.getLogger(__name__)

class KafkaProducerService:
    """Kafka生产者服务"""
    
    def __init__(self):
        """初始化Kafka生产者"""
        try:
            # 创建生产者
            self.producer = KafkaProducer(**kafka_config.PRODUCER_CONFIG)
            logger.info("Kafka生产者初始化成功")
            
            # 创建主题（如果不存在）
            self._create_topics()
            
        except Exception as e:
            logger.error(f"Kafka生产者初始化失败: {e}")
            self.producer = None
    
    def _create_topics(self):
        """创建主题"""
        try:
            admin_client = KafkaAdminClient(bootstrap_servers=kafka_config.BOOTSTRAP_SERVERS)
            
            # 获取现有主题
            existing_topics = admin_client.list_topics()
            
            # 创建不存在的主题
            topics_to_create = []
            for topic_name in kafka_config.TOPICS.values():
                if topic_name not in existing_topics:
                    topics_to_create.append(NewTopic(
                        name=topic_name,
                        num_partitions=3,
                        replication_factor=1
                    ))
            
            if topics_to_create:
                admin_client.create_topics(topics_to_create)
                logger.info(f"创建主题: {[topic.name for topic in topics_to_create]}")
            
            admin_client.close()
            
        except Exception as e:
            logger.error(f"创建主题失败: {e}")
    
    def send_message(self, topic: str, message: Dict[str, Any], key: Optional[str] = None) -> bool:
        """发送消息到Kafka
        
        Args:
            topic: 主题名称
            message: 消息内容
            key: 消息键（可选）
            
        Returns:
            bool: 是否发送成功
        """
        if not self.producer:
            logger.error("Kafka生产者未初始化")
            return False
        
        try:
            # 序列化消息
            message_json = json.dumps(message, ensure_ascii=False)
            
            # 发送消息
            future = self.producer.send(
                topic=topic,
                key=key,
                value=message_json
            )
            
            # 等待发送完成
            record_metadata = future.get(timeout=10)
            logger.info(f"消息发送成功: {topic}, partition={record_metadata.partition}, offset={record_metadata.offset}")
            
            return True
            
        except KafkaError as e:
            logger.error(f"发送消息失败: {e}")
            return False
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return False
    
    def send_opinion(self, opinion_data: Dict[str, Any]) -> bool:
        """发送舆情数据"""
        return self.send_message(
            topic=kafka_config.TOPICS['opinions'],
            message=opinion_data,
            key=f"opinion_{opinion_data.get('id', 'unknown')}"
        )
    
    def send_sentiment_result(self, sentiment_data: Dict[str, Any]) -> bool:
        """发送情感分析结果"""
        return self.send_message(
            topic=kafka_config.TOPICS['sentiment_results'],
            message=sentiment_data,
            key=f"sentiment_{sentiment_data.get('opinion_id', 'unknown')}"
        )
    
    def send_hot_topic(self, hot_topic_data: Dict[str, Any]) -> bool:
        """发送热点话题数据"""
        return self.send_message(
            topic=kafka_config.TOPICS['hot_topics'],
            message=hot_topic_data,
            key=f"hot_topic_{hot_topic_data.get('id', 'unknown')}"
        )
    
    def send_trend_data(self, trend_data: Dict[str, Any]) -> bool:
        """发送趋势数据"""
        return self.send_message(
            topic=kafka_config.TOPICS['trend_data'],
            message=trend_data,
            key=f"trend_{trend_data.get('date', 'unknown')}"
        )
    
    def flush(self):
        """刷新缓冲区，确保所有消息都发送出去"""
        if self.producer:
            self.producer.flush()
    
    def close(self):
        """关闭生产者"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka生产者已关闭")

# 创建全局生产者实例
kafka_producer = KafkaProducerService()
