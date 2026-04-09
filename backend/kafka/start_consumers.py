"""启动Kafka消费者服务"""
import logging
import asyncio
from kafka.kafka_consumer import kafka_consumer, process_opinion_message, process_sentiment_message
from kafka.kafka_config import kafka_config

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def start_kafka_consumers():
    """启动Kafka消费者"""
    logger.info("正在启动Kafka消费者服务...")
    
    try:
        # 启动舆情消息消费者
        kafka_consumer.start_consuming(
            topic=kafka_config.TOPICS['opinions'],
            callback=process_opinion_message,
            group_id='opinion-consumers'
        )
        
        # 启动情感分析结果消费者
        kafka_consumer.start_consuming(
            topic=kafka_config.TOPICS['sentiment_results'],
            callback=process_sentiment_message,
            group_id='sentiment-consumers'
        )
        
        logger.info("Kafka消费者服务启动成功")
        
        # 保持程序运行
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止Kafka消费者服务...")
    except Exception as e:
        logger.error(f"启动Kafka消费者服务失败: {e}")
    finally:
        kafka_consumer.stop_consuming()
        logger.info("Kafka消费者服务已停止")

if __name__ == "__main__":
    asyncio.run(start_kafka_consumers())
