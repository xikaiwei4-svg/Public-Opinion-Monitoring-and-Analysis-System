# -*- coding: utf-8 -*-
"""
批量生成校园舆情数据
"""
import time
import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from models.opinion_model import SourcePlatform, SentimentType

# MongoDB连接
client = MongoClient('mongodb://localhost:27017')
db = client['campus_opinion']
opinion_collection = db['opinions']

# 配置
TOTAL_COUNT = 7000  # 目标数据量
BATCH_SIZE = 100    # 每批次生成数量

# 关键词库
CAMPUS_KEYWORDS = [
    '校园', '学生', '大学', '高校', '教育', '学习', '考试', '课程',
    '宿舍', '食堂', '图书馆', '操场', '活动', '社团', '学生会', '志愿者',
    '就业', '实习', '考研', '出国', '奖学金', '助学金', '校园安全', '网络',
    '体育', '艺术', '科技', '文化', '讲座', '比赛', '演出', '展览'
]

# 内容模板
CONTENT_TEMPLATES = [
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
POSITIVE_OPINIONS = [
    '感觉很好', '非常满意', '值得推荐', '体验很棒', '服务周到',
    '环境优美', '设施完善', '管理规范', '氛围和谐', '质量很高'
]

NEGATIVE_OPINIONS = [
    '不太满意', '需要改进', '问题很多', '体验很差', '服务态度差',
    '环境糟糕', '设施陈旧', '管理混乱', '氛围压抑', '质量低下'
]

NEUTRAL_OPINIONS = [
    '一般般', '还可以', '有待观察', '因人而异', '有好有坏',
    '中规中矩', '符合预期', '需要时间', '保持中立', '不置可否'
]

# 地点
LOCATIONS = [
    '图书馆', '教学楼', '食堂', '宿舍', '操场', '体育馆',
    '实验室', '行政楼', '校门', '停车场', '校园周边'
]

# 平台
PLATFORMS = [
    ('微博', SourcePlatform.WEIBO),
    ('微信', SourcePlatform.WECHAT),
    ('知乎', SourcePlatform.ZHIHU),
    ('贴吧', SourcePlatform.FORUM),
    ('小红书', SourcePlatform.OTHER)
]

def generate_opinion():
    """生成单条舆情数据"""
    platform_name, platform = random.choice(PLATFORMS)
    keyword = random.choice(CAMPUS_KEYWORDS)
    template = random.choice(CONTENT_TEMPLATES)
    
    # 随机情感
    sentiment_rand = random.random()
    if sentiment_rand > 0.66:
        sentiment_type = SentimentType.POSITIVE
        sentiment = round(random.uniform(0.3, 1.0), 2)
        opinion = random.choice(POSITIVE_OPINIONS)
    elif sentiment_rand < 0.33:
        sentiment_type = SentimentType.NEGATIVE
        sentiment = round(random.uniform(-1.0, -0.3), 2)
        opinion = random.choice(NEGATIVE_OPINIONS)
    else:
        sentiment_type = SentimentType.NEUTRAL
        sentiment = round(random.uniform(-0.2, 0.2), 2)
        opinion = random.choice(NEUTRAL_OPINIONS)
    
    # 生成内容
    adjective = random.choice(['好', '棒', '赞', '差', '糟', '一般'])
    location = random.choice(LOCATIONS)
    
    # 生成详细内容
    detail_options = [
        '希望能够持续改进', '大家都很关注', '确实需要解决',
        '体验非常不错', '还有很大提升空间', '值得大家关注'
    ]
    detail = random.choice(detail_options)
    
    question_options = [
        '大家怎么看', '有什么好的建议', '是否有类似经历'
    ]
    question = random.choice(question_options)
    
    description_options = [
        '情况很特殊', '场面很热闹', '秩序很好', '需要注意'
    ]
    description = random.choice(description_options)
    
    issue_options = [
        '影响很广泛', '需要及时处理', '希望引起重视'
    ]
    issue = random.choice(issue_options)
    
    experience_options = [
        '希望对大家有帮助', '仅供参考', '欢迎交流'
    ]
    experience = random.choice(experience_options)
    
    change_options = [
        '大家要注意', '影响很大', '需要适应'
    ]
    change = random.choice(change_options)
    
    suggestion_options = [
        '希望能采纳', '仅供参考', '大家一起讨论'
    ]
    suggestion = random.choice(suggestion_options)
    
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
    
    # 生成数据
    data = {
        'id': f'{platform_name}_{int(time.time() * 1000)}_{random.randint(1000, 9999)}',
        'content': content,
        'source': platform_name,
        'source_platform': platform,
        'publish_time': datetime.now() - timedelta(hours=random.randint(1, 168)),
        'crawl_time': datetime.now(),
        'sentiment': sentiment,
        'sentiment_type': sentiment_type,
        'keywords': [keyword] + random.sample(CAMPUS_KEYWORDS, min(2, len(CAMPUS_KEYWORDS) - 1)),
        'url': f'https://{platform_name}.com/{random.randint(1000000, 9999999)}',
        'views': random.randint(100, 50000),
        'likes': random.randint(0, 5000),
        'comments': random.randint(0, 1000),
        'shares': random.randint(0, 500),
        'heat_score': round(random.uniform(10, 90), 2),
        'is_sensitive': random.random() < 0.05,
        'sensitive_level': random.randint(1, 3) if random.random() < 0.05 else 0,
        'location': f'某大学{location}',
        'user_info': {
            'username': f'{platform_name}用户{random.randint(1000, 9999)}',
            'user_id': f'{platform_name[0]}_{random.randint(1000000, 9999999)}'
        },
        'raw_data': {'status': 'generated_data'}
    }
    
    return data

def main():
    """主函数"""
    print(f"开始生成{7000}条校园舆情数据...")
    
    generated_count = 0
    attempts = 0
    max_attempts = TOTAL_COUNT * 2  # 最大尝试次数
    
    while generated_count < TOTAL_COUNT and attempts < max_attempts:
        # 批量生成
        batch_data = []
        for _ in range(BATCH_SIZE):
            data = generate_opinion()
            # 检查是否重复
            existing = opinion_collection.find_one({'content': data['content']})
            if not existing:
                batch_data.append(data)
            attempts += 1
        
        # 批量插入
        if batch_data:
            opinion_collection.insert_many(batch_data)
            generated_count += len(batch_data)
            print(f"已生成 {generated_count}/{TOTAL_COUNT} 条数据")
        
        # 避免过快
        time.sleep(0.1)
    
    if generated_count >= TOTAL_COUNT:
        print(f"成功生成 {generated_count} 条数据！")
    else:
        print(f"在{max_attempts}次尝试后，仅生成了{generated_count}条数据")
    
    # 统计数据分布
    total = opinion_collection.count_documents({})
    positive = opinion_collection.count_documents({'sentiment_type': 'positive'})
    negative = opinion_collection.count_documents({'sentiment_type': 'negative'})
    neutral = opinion_collection.count_documents({'sentiment_type': 'neutral'})
    
    print(f"\n数据分布:")
    print(f"总数: {total}")
    print(f"正面: {positive} ({positive/total*100:.2f}%)")
    print(f"负面: {negative} ({negative/total*100:.2f}%)")
    print(f"中性: {neutral} ({neutral/total*100:.2f}%)")

if __name__ == "__main__":
    main()
