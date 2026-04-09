# Kafka实时数据流处理系统部署指南

## 系统架构

本系统采用Kafka作为消息中间件，实现校园舆情数据的实时处理。系统架构如下：

```
爬虫系统 → Kafka生产者 → Kafka集群 → Kafka消费者 → 数据处理服务 → 数据库/前端展示
```

## 组件说明

### 1. Kafka配置模块 (`kafka/kafka_config.py`)
- 管理Kafka服务器地址和主题配置
- 提供生产者和消费者配置

### 2. Kafka生产者服务 (`kafka/kafka_producer.py`)
- 负责将爬虫数据发送到Kafka主题
- 支持自动创建主题
- 提供消息发送接口

### 3. Kafka消费者服务 (`kafka/kafka_consumer.py`)
- 订阅Kafka主题，实时消费数据
- 支持多线程并发处理
- 提供消息处理回调机制

### 4. 爬虫集成
- 爬虫任务自动将数据发送到Kafka
- 支持批量处理和实时发送

## 部署步骤

### 1. 安装Kafka (可选)

#### 方式一：使用Docker (推荐)
```bash
# 启动ZooKeeper和Kafka
docker-compose up -d

# 或者单独启动
docker run -d --name zookeeper -p 2181:2181 zookeeper:3.8
docker run -d --name kafka -p 9092:9092 \
    --link zookeeper:zookeeper \
    -e KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181 \
    -e KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
    -e KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1 \
    confluentinc/cp-kafka:7.4.0
```

#### 方式二：本地安装
```bash
# 下载Kafka
wget https://downloads.apache.org/kafka/3.6.1/kafka_2.13-3.6.1.tgz
tar -xzf kafka_2.13-3.6.1.tgz
cd kafka_2.13-3.6.1

# 启动ZooKeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# 启动Kafka
bin/kafka-server-start.sh config/server.properties
```

### 2. 安装依赖
```bash
cd backend
pip install kafka-python
```

### 3. 配置环境变量
```bash
# 设置Kafka服务器地址（如果不是默认地址）
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092
```

### 4. 启动系统

#### 方式一：使用启动脚本
```bash
# 在项目根目录运行
python start_kafka_system.py
```

#### 方式二：手动启动各组件
```bash
# 1. 启动后端服务
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# 2. 启动Kafka消费者
cd backend
python kafka/start_consumers.py

# 3. 启动前端服务
cd frontend
npm run dev
```

## 使用说明

### 1. 运行爬虫任务
```bash
cd backend
python run_crawlers.py
```

爬虫会自动将数据发送到Kafka主题 `campus_opinions`。

### 2. 监控Kafka主题
```bash
# 查看所有主题
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# 消费消息
bin/kafka-console-consumer.sh --topic campus_opinions --from-beginning --bootstrap-server localhost:9092
```

### 3. 测试Kafka集成
```bash
cd backend
python test_kafka_integration.py
```

## 系统特性

### 1. 容错机制
- 当Kafka不可用时，系统自动切换到模拟模式
- 支持消息重试和错误处理

### 2. 实时处理
- 爬虫数据实时发送到Kafka
- 消费者实时处理数据
- 支持批量处理和微批处理

### 3. 扩展性
- 支持多消费者并行处理
- 支持水平扩展
- 支持动态添加新的处理逻辑

### 4. 监控
- 详细的日志记录
- 消息处理统计
- 错误监控和报警

## 主题说明

系统使用以下Kafka主题：

| 主题名称 | 用途 | 数据内容 |
|---------|------|---------|
| campus_opinions | 舆情数据 | 爬虫采集的原始舆情数据 |
| sentiment_results | 情感分析结果 | 情感分析处理结果 |
| hot_topics | 热点话题 | 热点话题识别结果 |
| trend_data | 趋势数据 | 趋势分析结果 |

## 故障排查

### 常见问题

1. **Kafka连接失败**
   - 检查Kafka服务是否运行
   - 检查网络连接和端口配置

2. **消息发送失败**
   - 检查Kafka主题是否存在
   - 检查权限配置

3. **消费者无法接收消息**
   - 检查消费者组配置
   - 检查主题订阅是否正确

### 日志位置
- 后端日志：控制台输出
- Kafka日志：`/tmp/kafka-logs/`
- 消费者日志：控制台输出

## 性能优化

### 1. 生产者优化
- 调整批量大小和延迟时间
- 使用异步发送
- 配置适当的重试策略

### 2. 消费者优化
- 增加消费者数量
- 调整批处理大小
- 使用多线程处理

### 3. Kafka配置优化
- 调整分区数量
- 优化副本配置
- 调整日志保留策略

## 安全建议

1. 配置Kafka认证和授权
2. 启用SSL加密
3. 设置适当的访问控制
4. 定期监控和审计

## 扩展功能

未来可扩展的功能：

1. 集成机器学习模型进行实时情感分析
2. 添加数据可视化仪表盘
3. 实现实时预警机制
4. 支持更多数据源接入
