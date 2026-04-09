"""Kafka消费者服务"""
import json
import logging
import threading
import time
from typing import Dict, Any, List, Callable
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from .kafka_config import kafka_config
from ..utils.db_utils import db_utils

logger = logging.getLogger(__name__)

class KafkaConsumerService:
    """Kafka消费者服务"""
    
    def __init__(self):
        """初始化Kafka消费者"""
        self.consumers = {}
        self.running = False
        self.threads = []
    
    def create_consumer(self, topics: List[str], group_id: str = None) -> KafkaConsumer:
        """创建消费者"""
        consumer_config = kafka_config.CONSUMER_CONFIG.copy()
        if group_id:
            consumer_config['group_id'] = group_id
        
        try:
            consumer = KafkaConsumer(
                *topics,
                **consumer_config
            )
            logger.info(f"创建消费者成功，订阅主题: {topics}")
            return consumer
        except Exception as e:
            logger.error(f"创建消费者失败: {e}")
            return None
    
    def start_consuming(self, topic: str, callback: Callable[[Dict[str, Any]], None], 
                       group_id: str = None):
        """开始消费消息
        
        Args:
            topic: 主题名称
            callback: 消息处理回调函数
            group_id: 消费者组ID
        """
        if topic in self.consumers:
            logger.warning(f"消费者已存在: {topic}")
            return
        
        consumer = self.create_consumer([topic], group_id)
        if not consumer:
            return
        
        self.consumers[topic] = consumer
        self.running = True
        
        # 创建线程运行消费者
        thread = threading.Thread(
            target=self._consume_loop,
            args=(consumer, callback),
            daemon=True
        )
        self.threads.append(thread)
        thread.start()
        
        logger.info(f"开始消费主题: {topic}")
    
    def _consume_loop(self, consumer: KafkaConsumer, callback: Callable[[Dict[str, Any]], None]):
        """消费循环"""
        try:
            while self.running:
                for message in consumer:
                    if not self.running:
                        break
                    
                    try:
                        # 解析消息
                        message_value = message.value
                        if message_value:
                            message_data = json.loads(message_value)
                            
                            # 调用回调函数处理消息
                            callback(message_data)
                            
                            logger.info(f"处理消息成功: {message.topic}, offset={message.offset}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"解析消息失败: {e}")
                    except Exception as e:
                        logger.error(f"处理消息失败: {e}")
                        
                # 短暂休眠，避免CPU占用过高
                time.sleep(0.1)
                
        except KafkaError as e:
            logger.error(f"消费者错误: {e}")
        except Exception as e:
            logger.error(f"消费循环异常: {e}")
    
    def stop_consuming(self, topic: str = None):
        """停止消费
        
        Args:
            topic: 主题名称，如果为None则停止所有消费
        """
        if topic:
            # 停止特定主题的消费
            if topic in self.consumers:
                consumer = self.consumers[topic]
                consumer.close()
                del self.consumers[topic]
                logger.info(f"停止消费主题: {topic}")
        else:
            # 停止所有消费
            self.running = False
            
            # 关闭所有消费者
            for topic_name, consumer in self.consumers.items():
                consumer.close()
            
            self.consumers.clear()
            
            # 等待线程结束
            for thread in self.threads:
                thread.join(timeout=5)
            
            self.threads.clear()
            logger.info("停止所有消费")

# 创建全局消费者实例
kafka_consumer = KafkaConsumerService()

# 消息处理函数
async def process_opinion_message(message_data: Dict[str, Any]):
    """处理舆情消息"""
    try:
        # 这里可以添加情感分析、热点检测等处理逻辑
        logger.info(f"处理舆情消息: {message_data.get('id')}")
        
        # 示例：将数据保存到数据库
        # 注意：这里应该是异步处理
        # await db_utils.save_opinion(message_data)
        
    except Exception as e:
        logger.error(f"处理舆情消息失败: {e}")

async def process_sentiment_message(message_data: Dict[str, Any]):
    """处理情感分析结果消息"""
    try:
        logger.info(f"处理情感分析结果: {message_data.get('opinion_id')}")
        
    except Exception as e:
        logger.error(f"处理情感分析结果失败: {e}")

async def process_hot_topic_message(message_data: Dict[str, Any]):
    """处理热点话题消息"""
    try:
        logger.info(f"处理热点话题: {message_data.get('id')}")
        
    except Exception as e:
        logger.error(f"处理热点话题失败: {e}")

async def process_trend_message(message_data: Dict[str, Any]):
    """处理趋势数据消息"""
    try:
        logger.info(f"处理趋势数据: {message_data.get('date')}")
        
    except Exception as e:
        logger.error(f"处理趋势数据失败: {e}")
