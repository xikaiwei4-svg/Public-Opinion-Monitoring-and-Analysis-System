# -*- coding: utf-8 -*-
"""
训练CNN情感分析模型
"""
import os
import numpy as np
import pandas as pd
import random
from datetime import datetime
from models.cnn_sentiment_model import CNNSentimentModel
import pymysql

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': 'campus_opinion',
    'charset': 'utf8mb4'
}

def generate_campus_data(count=7000):
    """生成校园舆情数据"""
    print(f"正在生成{count}条校园舆情数据...")
    
    # 关键词库
    keywords = [
        '校园', '学生', '大学', '高校', '教育', '学习', '考试', '课程',
        '宿舍', '食堂', '图书馆', '操场', '活动', '社团', '学生会', '志愿者',
        '就业', '实习', '考研', '出国', '奖学金', '助学金', '校园安全', '网络',
        '体育', '艺术', '科技', '文化', '讲座', '比赛', '演出', '展览'
    ]
    
    # 内容模板
    templates = [
        "关于{keyword}的情况，{opinion}。",
        "{keyword}真的很{adjective}，{detail}。",
        "大家对{keyword}有什么看法？{question}？",
        "今天在{location}看到{keyword}，{description}。",
        "{keyword}的问题需要重视，{issue}。",
        "分享一下关于{keyword}的经验，{experience}。",
        "{keyword}的政策有变化，{change}。",
        "对{keyword}的建议，{suggestion}。"
    ]
    
    # 情感表达
    positive_opinions = [
        '感觉很好', '非常满意', '值得推荐', '体验很棒', '服务周到',
        '环境优美', '设施完善', '管理规范', '氛围和谐', '质量很高'
    ]
    
    negative_opinions = [
        '不太满意', '需要改进', '问题很多', '体验很差', '服务态度差',
        '环境糟糕', '设施陈旧', '管理混乱', '氛围压抑', '质量低下'
    ]
    
    neutral_opinions = [
        '一般般', '还可以', '有待观察', '因人而异', '有好有坏',
        '中规中矩', '符合预期', '需要时间', '保持中立', '不置可否'
    ]
    
    # 地点
    locations = [
        '图书馆', '教学楼', '食堂', '宿舍', '操场', '体育馆',
        '实验室', '行政楼', '校门', '停车场', '校园周边'
    ]
    
    # 生成数据
    texts = []
    labels = []
    
    for i in range(count):
        keyword = random.choice(keywords)
        template = random.choice(templates)
        
        # 随机情感
        sentiment_rand = random.random()
        if sentiment_rand > 0.66:
            sentiment = "positive"
            opinion = random.choice(positive_opinions)
            label = 2
        elif sentiment_rand < 0.33:
            sentiment = "negative"
            opinion = random.choice(negative_opinions)
            label = 0
        else:
            sentiment = "neutral"
            opinion = random.choice(neutral_opinions)
            label = 1
        
        # 生成内容
        adjective = random.choice(['好', '棒', '赞', '差', '糟', '一般'])
        location = random.choice(locations)
        detail = random.choice([
            '希望能够持续改进', '大家都很关注', '确实需要解决',
            '体验非常不错', '还有很大提升空间', '值得大家关注'
        ])
        question = random.choice(['大家怎么看', '有什么好的建议', '是否有类似经历'])
        description = random.choice(['情况很特殊', '场面很热闹', '秩序很好', '需要注意'])
        issue = random.choice(['影响很广泛', '需要及时处理', '希望引起重视'])
        experience = random.choice(['希望对大家有帮助', '仅供参考', '欢迎交流'])
        change = random.choice(['大家要注意', '影响很大', '需要适应'])
        suggestion = random.choice(['希望能采纳', '仅供参考', '大家一起讨论'])
        
        content = template.format(
            keyword=keyword,
            opinion=opinion,
            adjective=adjective,
            detail=detail,
            location=location,
            question=question,
            description=description,
            issue=issue,
            experience=experience,
            change=change,
            suggestion=suggestion
        )
        
        texts.append(content)
        labels.append(label)
    
    print(f"生成 {len(texts)} 条数据")
    print(f"正面: {labels.count(2)}, 中性: {labels.count(1)}, 负面: {labels.count(0)}")
    return texts, labels

def load_training_data():
    """从数据库加载训练数据"""
    print("正在加载训练数据...")
    
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # 检查数据库中是否已有数据
        cursor.execute("SELECT COUNT(*) FROM opinions")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print("数据库中无数据，开始生成数据...")
            # 生成7000条数据
            texts, labels = generate_campus_data(7000)
            
            # 保存到数据库
            print("正在保存数据到数据库...")
            for i, (text, label) in enumerate(zip(texts, labels)):
                sentiment = "positive" if label == 2 else "negative" if label == 0 else "neutral"
                cursor.execute(
                    "INSERT INTO opinions (title, content, sentiment, sentiment_score, source, publish_time, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (f"校园舆情{i+1}", text, sentiment, random.uniform(-1, 1), "generated", datetime.now(), datetime.now())
                )
                if (i + 1) % 1000 == 0:
                    connection.commit()
                    print(f"已保存 {i+1} 条数据")
            connection.commit()
            print("数据保存完成！")
            return texts, labels
        else:
            # 获取所有舆情数据
            cursor.execute("SELECT id, title, content, sentiment FROM opinions")
            data = cursor.fetchall()
            
            print(f"找到 {len(data)} 条数据")
            
            # 预处理数据
            texts = []
            labels = []
            
            for _, title, content, sentiment in data:
                text = f"{title or ''} {content or ''}"
                if not text.strip():
                    continue
                
                texts.append(text)
                
                # 映射情感标签到数字
                if sentiment == "positive":
                    labels.append(2)
                elif sentiment == "negative":
                    labels.append(0)
                else:
                    labels.append(1)  # neutral
            
            print(f"预处理后得到 {len(texts)} 条有效数据")
            print(f"正面: {labels.count(2)}, 中性: {labels.count(1)}, 负面: {labels.count(0)}")
            
            return texts, labels
            
    except Exception as e:
        print(f"加载数据失败: {str(e)}")
        return [], []
    finally:
        cursor.close()
        connection.close()

def generate_synthetic_data():
    """生成合成训练数据"""
    print("生成合成训练数据...")
    
    # 正面情感数据
    positive_texts = [
        "学校环境很好，老师很负责",
        "课程内容丰富，学习氛围浓厚",
        "图书馆资源丰富，自习室环境舒适",
        "校园活动丰富多彩，社团活动很有趣",
        "老师教学水平高，课堂互动性强",
        "学校设施完善，生活便利",
        "同学关系融洽，校园氛围和谐",
        "学校管理规范，服务周到",
        "就业前景好，学校就业率高",
        "校园风景优美，环境整洁"
    ]
    
    # 负面情感数据
    negative_texts = [
        "课程安排不合理，作业太多",
        "食堂饭菜不好吃，价格还贵",
        "宿舍条件差，卫生状况不好",
        "学校管理混乱，服务态度差",
        "教学质量差，老师不负责任",
        "校园安全问题严重，治安不好",
        "学费昂贵，负担很重",
        "学校设施陈旧，设备老化",
        "校园网络差，经常断网",
        "学校办事效率低，流程复杂"
    ]
    
    # 中性情感数据
    neutral_texts = [
        "学校位于城市中心，交通便利",
        "学校有多个食堂，品种齐全",
        "校园面积很大，环境优美",
        "学校有图书馆，藏书丰富",
        "学校有体育馆，设施齐全",
        "学校有多个专业，选择多样",
        "学校有很多社团，活动丰富",
        "学校有国际交流项目，机会很多",
        "学校有奖学金制度，奖励优秀学生",
        "学校有就业指导中心，提供就业服务"
    ]
    
    # 扩展数据
    texts = []
    labels = []
    
    # 复制数据以增加样本量
    for _ in range(5):
        for text in positive_texts:
            texts.append(text)
            labels.append(2)
        for text in negative_texts:
            texts.append(text)
            labels.append(0)
        for text in neutral_texts:
            texts.append(text)
            labels.append(1)
    
    print(f"生成 {len(texts)} 条合成数据")
    return texts, labels

def main():
    """主函数"""
    print("开始训练CNN情感分析模型...")
    
    # 加载数据（使用数据库数据）
    texts, labels = load_training_data()
    
    print(f"总训练数据: {len(texts)} 条")
    
    # 创建模型
    model = CNNSentimentModel()
    
    # 训练模型
    print("开始训练模型...")
    history = model.train(
        texts=texts,
        labels=labels,
        epochs=20,
        batch_size=32
    )
    
    # 打印训练结果
    print("\n训练完成!")
    print(f"训练准确率: {history.history['accuracy'][-1]:.4f}")
    print(f"验证准确率: {history.history['val_accuracy'][-1]:.4f}")
    
    # 测试模型
    print("\n测试模型:")
    test_texts = [
        "学校环境很好，老师很负责，学习氛围浓厚",
        "课程安排不合理，作业太多，压力很大",
        "校园活动丰富多彩，社团活动很有趣",
        "食堂饭菜不好吃，价格还贵",
        "图书馆资源丰富，自习室环境舒适"
    ]
    
    for text in test_texts:
        sentiment, score = model.predict(text)
        print(f"文本: {text}")
        print(f"情感: {sentiment}, 得分: {score}")
        print("-" * 50)

if __name__ == "__main__":
    main()
