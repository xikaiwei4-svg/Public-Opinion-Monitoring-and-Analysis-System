# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'C:\\Users\\wei\\Desktop\\project1\\backend')

from db.mysql_config import SessionLocal, engine
from models.mysql_models import Opinion, SentimentType
import jieba

# 情感分析关键词库
POSITIVE_WORDS = [
    '好', '优秀', '满意', '提升', '积极', '完善', '成功', '支持', '赞同', 
    '认可', '喜欢', '爱', '赞扬', '表扬', '鼓励', '进步', '发展',
    '创新', '突破', '领先', '优势', '强', '优', '佳', '美',
    '棒', '赞', '👍', '❤️', '🎉', '🌟', '✨', '👏',
    '值得', '推荐', '优秀', '出色', '杰出', '卓越', '辉煌', '精彩',
    '完美', '理想', '美好', '幸福', '快乐', '开心', '高兴', '喜悦',
    '激动', '兴奋', '热情', '积极', '正面', '肯定', '认可',
    '希望', '期待', '期待', '盼望', '信心', '相信', '信任',
    '感谢', '感激', '谢谢', '致谢', '荣幸', '骄傲', '自豪'
]

NEGATIVE_WORDS = [
    '差', '不满', '问题', '糟糕', '失败', '不足', '缺陷', '失望',
    '反对', '批评', '指责', '谴责', '愤怒', '生气', '恼火',
    '讨厌', '厌恶', '反感', '痛恨', '憎恨', '鄙视', '轻视',
    '质疑', '怀疑', '不信任', '担心', '忧虑', '焦虑', '恐惧',
    '悲伤', '难过', '痛苦', '痛苦', '痛苦', '痛苦', '痛苦',
    '遗憾', '后悔', '内疚', '羞愧', '羞耻', '丢脸', '丢人',
    '差劲', '糟糕', '恶劣', '恶劣', '恶劣', '恶劣', '恶劣',
    '👎', '❌', '😡', '😠', '😤', '😞', '😢', '😭',
    '不行', '不可以', '不能', '拒绝', '否认', '否定', '反对',
    '担忧', '忧虑', '担心', '害怕', '恐惧', '恐慌', '紧张',
    '压力', '困难', '挑战', '障碍', '阻碍', '限制', '约束',
    '下降', '下滑', '衰退', '萎缩', '减少', '降低', '减弱'
]

def analyze_sentiment(text):
    """分析文本的情感倾向"""
    if not text:
        return {
            "sentiment_type": SentimentType.NEUTRAL,
            "sentiment_score": 0.0
        }
    
    # 使用jieba进行分词
    words = jieba.lcut(text)
    
    # 统计正面和负面词汇
    pos_count = sum(1 for word in words if word in POSITIVE_WORDS)
    neg_count = sum(1 for word in words if word in NEGATIVE_WORDS)
    
    # 计算情感得分
    total_sentiment_words = pos_count + neg_count
    if total_sentiment_words > 0:
        sentiment_score = (pos_count - neg_count) / total_sentiment_words
    else:
        sentiment_score = 0.0
    
    # 确定情感类型
    if sentiment_score > 0.2:
        sentiment_type = SentimentType.POSITIVE
    elif sentiment_score < -0.2:
        sentiment_type = SentimentType.NEGATIVE
    else:
        sentiment_type = SentimentType.NEUTRAL
    
    return {
        "sentiment_type": sentiment_type,
        "sentiment_score": round(sentiment_score, 4)
    }

def main():
    """主函数：重新分析所有舆情数据的情感倾向"""
    print("开始重新分析所有数据的情感倾向...")
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 获取所有需要分析的舆情数据
        opinions = db.query(Opinion).all()
        total_count = len(opinions)
        
        if total_count == 0:
            print("没有需要分析的数据")
            return
        
        print(f"找到 {total_count} 条舆情数据需要分析")
        
        analyzed_count = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for opinion in opinions:
            # 分析标题和内容的情感
            text = f"{opinion.title or ''} {opinion.content or ''}"
            result = analyze_sentiment(text)
            
            # 更新情感分析结果
            opinion.sentiment = result["sentiment_type"]
            opinion.sentiment_score = result["sentiment_score"]
            
            # 统计情感类型
            if result["sentiment_type"] == SentimentType.POSITIVE:
                positive_count += 1
            elif result["sentiment_type"] == SentimentType.NEGATIVE:
                negative_count += 1
            else:
                neutral_count += 1
            
            analyzed_count += 1
            
            # 每100条提交一次
            if analyzed_count % 100 == 0:
                db.commit()
                print(f"已分析 {analyzed_count}/{total_count} 条数据")
        
        # 提交剩余的更改
        db.commit()
        
        print(f"\n情感分析完成！")
        print(f"总数据量: {total_count}")
        print(f"正面情感: {positive_count} ({positive_count/total_count*100:.2f}%)")
        print(f"负面情感: {negative_count} ({negative_count/total_count*100:.2f}%)")
        print(f"中性情感: {neutral_count} ({neutral_count/total_count*100:.2f}%)")
        
    except Exception as e:
        db.rollback()
        print(f"情感分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
