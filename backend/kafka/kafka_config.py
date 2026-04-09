"""Kafka配置模块"""
import os
from typing import Dict, Any

class KafkaConfig:
    """Kafka配置类"""
    
    # Kafka服务器地址
    BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    
    # 主题配置
    TOPICS = {
        'opinions': 'campus_opinions',
        'sentiment_results': 'sentiment_results',
        'hot_topics': 'hot_topics',
        'trend_data': 'trend_data'
    }
    
    # 生产者配置
    PRODUCER_CONFIG: Dict[str, Any] = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'acks': 'all',
        'retries': 3,
        'batch_size': 16384,
        'linger_ms': 5,
        'buffer_memory': 33554432,
        'key_serializer': lambda x: x.encode('utf-8'),
        'value_serializer': lambda x: x.encode('utf-8')
    }
    
    # 消费者配置
    CONSUMER_CONFIG: Dict[str, Any] = {
        'bootstrap_servers': BOOTSTRAP_SERVERS,
        'group_id': 'campus_opinion_group',
        'auto_offset_reset': 'earliest',
        'enable_auto_commit': True,
        'auto_commit_interval_ms': 1000,
        'key_deserializer': lambda x: x.decode('utf-8') if x else None,
        'value_deserializer': lambda x: x.decode('utf-8') if x else None
    }

# 创建全局配置实例
kafka_config = KafkaConfig()
