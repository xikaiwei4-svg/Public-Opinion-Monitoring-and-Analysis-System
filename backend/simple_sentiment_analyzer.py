# -*- coding: utf-8 -*-
import pymysql
import jieba

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'database': 'campus_opinion',
    'charset': 'utf8mb4'
}

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
        return "neutral", 0.0
    
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
        sentiment_type = "positive"
    elif sentiment_score < -0.2:
        sentiment_type = "negative"
    else:
        sentiment_type = "neutral"
    
    return sentiment_type, round(sentiment_score, 4)

def main():
    """主函数：重新分析所有舆情数据的情感倾向"""
    print("开始重新分析所有数据的情感倾向...")
    
    # 连接数据库
    connection = pymysql.connect(**DB_CONFIG)
    cursor = connection.cursor()
    
    try:
        # 获取所有需要分析的舆情数据
        cursor.execute("SELECT id, title, content FROM opinions")
        opinions = cursor.fetchall()
        total_count = len(opinions)
        
        if total_count == 0:
            print("没有需要分析的数据")
            return
        
        print(f"找到 {total_count} 条舆情数据需要分析")
        
        analyzed_count = 0
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for opinion_id, title, content in opinions:
            # 分析标题和内容的情感
            text = f"{title or ''} {content or ''}"
            sentiment_type, sentiment_score = analyze_sentiment(text)
            
            # 更新情感分析结果
            update_sql = """
                UPDATE opinions 
                SET sentiment = %s, sentiment_score = %s 
                WHERE id = %s
            """
            cursor.execute(update_sql, (sentiment_type, sentiment_score, opinion_id))
            
            # 统计情感类型
            if sentiment_type == "positive":
                positive_count += 1
            elif sentiment_type == "negative":
                negative_count += 1
            else:
                neutral_count += 1
            
            analyzed_count += 1
            
            # 每100条提交一次
            if analyzed_count % 100 == 0:
                connection.commit()
                print(f"已分析 {analyzed_count}/{total_count} 条数据")
        
        # 提交剩余的更改
        connection.commit()
        
        print(f"\n情感分析完成！")
        print(f"总数据量: {total_count}")
        print(f"正面情感: {positive_count} ({positive_count/total_count*100:.2f}%)")
        print(f"负面情感: {negative_count} ({negative_count/total_count*100:.2f}%)")
        print(f"中性情感: {neutral_count} ({neutral_count/total_count*100:.2f}%)")
        
    except Exception as e:
        connection.rollback()
        print(f"情感分析失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    main()
