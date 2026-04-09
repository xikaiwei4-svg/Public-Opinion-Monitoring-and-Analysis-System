"""启动Kafka实时数据流处理系统"""
import subprocess
import time
import logging
import os
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def start_kafka():
    """启动Kafka服务"""
    logger.info("正在启动Kafka服务...")
    
    # 检查Kafka是否已安装
    try:
        result = subprocess.run(['kafka-server-start.sh'], capture_output=True, text=True)
        if result.returncode != 0 and "command not found" in result.stderr:
            logger.warning("未检测到Kafka，将使用模拟模式")
            return False
    except FileNotFoundError:
        logger.warning("未检测到Kafka，将使用模拟模式")
        return False
    
    # 启动Kafka
    try:
        # 启动ZooKeeper
        zk_process = subprocess.Popen([
            'zookeeper-server-start.sh', 
            '/usr/local/etc/kafka/zookeeper.properties'
        ])
        
        # 等待ZooKeeper启动
        time.sleep(5)
        
        # 启动Kafka
        kafka_process = subprocess.Popen([
            'kafka-server-start.sh', 
            '/usr/local/etc/kafka/server.properties'
        ])
        
        # 等待Kafka启动
        time.sleep(10)
        
        logger.info("Kafka服务启动成功")
        return True
        
    except Exception as e:
        logger.error(f"启动Kafka失败: {e}")
        return False

def start_backend():
    """启动后端服务"""
    logger.info("正在启动后端服务...")
    
    try:
        backend_process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'backend.main:app', 
            '--host', '0.0.0.0', '--port', '8001', '--reload'
        ], cwd='backend')
        
        logger.info("后端服务启动成功")
        return backend_process
        
    except Exception as e:
        logger.error(f"启动后端服务失败: {e}")
        return None

def start_kafka_consumers():
    """启动Kafka消费者"""
    logger.info("正在启动Kafka消费者...")
    
    try:
        consumer_process = subprocess.Popen([
            sys.executable, 'kafka/start_consumers.py'
        ], cwd='backend')
        
        logger.info("Kafka消费者启动成功")
        return consumer_process
        
    except Exception as e:
        logger.error(f"启动Kafka消费者失败: {e}")
        return None

def start_frontend():
    """启动前端服务"""
    logger.info("正在启动前端服务...")
    
    try:
        frontend_process = subprocess.Popen([
            'npm', 'run', 'dev'
        ], cwd='frontend')
        
        logger.info("前端服务启动成功")
        return frontend_process
        
    except Exception as e:
        logger.error(f"启动前端服务失败: {e}")
        return None

def main():
    """主函数"""
    logger.info("启动校园舆情检测与热点话题分析系统")
    
    processes = []
    
    try:
        # 启动Kafka（可选）
        kafka_started = start_kafka()
        
        if not kafka_started:
            logger.warning("Kafka未启动，系统将使用模拟模式")
        
        # 启动后端服务
        backend_process = start_backend()
        if backend_process:
            processes.append(backend_process)
        
        # 启动Kafka消费者
        consumer_process = start_kafka_consumers()
        if consumer_process:
            processes.append(consumer_process)
        
        # 启动前端服务
        frontend_process = start_frontend()
        if frontend_process:
            processes.append(frontend_process)
        
        logger.info("系统启动完成！")
        logger.info("后端API: http://localhost:8001")
        logger.info("前端界面: http://localhost:3003")
        
        # 保持系统运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止系统...")
        
        # 停止所有进程
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()
        
        logger.info("系统已停止")

if __name__ == "__main__":
    main()
