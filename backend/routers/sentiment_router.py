# -*- coding: utf-8 -*-
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Dict, Any
import jieba
import jieba.analyse
import re

from db.mysql_config import get_db
from models.mysql_models import Opinion, SentimentType
from utils.redis_cache import redis_cache, make_cache_key

router = APIRouter(prefix="/api/sentiment", tags=["情感分析"])

# ── 否定词 ──
NEGATION_WORDS = {"不", "没", "无", "未", "别", "勿", "毋", "莫", "非",
                  "不要", "没有", "不是", "不能", "不会", "不可", "不必",
                  "难以", "从未", "并非", "从不", "绝不", "毫不", "并未",
                  "不太", "不怎么", "不用", "不许", "不准", "禁止", "严禁"}

# ── 程度副词（值越大越强）──
DEGREE_WORDS = {
    "极其": 2.0, "极度": 2.0, "万分": 2.0, "绝顶": 2.0, "无比": 2.0,
    "超": 1.9, "超级": 1.9, "特别": 1.8, "非常": 1.8, "十分": 1.7,
    "相当": 1.6, "很": 1.5, "太": 1.5, "真": 1.4, "挺": 1.3,
    "比较": 1.2, "较为": 1.2, "颇": 1.2,
    "稍微": 0.5, "有点": 0.5, "略微": 0.5, "些许": 0.5,
    "多": 1.3, "更加": 1.4, "更": 1.3, "越": 1.3,
}

# ── 正面情感词（按场景分组）──
POSITIVE_WORDS = set([
    # 赞扬肯定
    "好", "优秀", "出色", "杰出", "卓越", "优异", "优良", "良好", "佳", "极佳",
    "赞", "称赞", "赞扬", "赞美", "赞赏", "赞叹", "夸奖",
    "棒", "很棒", "真棒", "太棒了", "厉害", "真厉害",
    "完美", "完善", "漂亮", "精彩", "辉煌", "灿烂",
    "成功", "胜利", "成就", "成果", "成效",
    "骄傲", "自豪", "光荣", "荣耀", "荣幸",
    # 认可信任
    "认可", "肯定", "赞同", "支持", "拥护", "赞成",
    "信任", "信赖", "可靠", "靠谱", "放心",
    "满意", "如意", "中意", "合意",
    "推荐", "力荐", "安利", "首推",
    # 喜悦幸福
    "喜欢", "爱", "热爱", "喜爱", "钟情", "欣赏",
    "快乐", "开心", "高兴", "喜悦", "愉快", "欢乐", "欢快",
    "幸福", "美满", "甜蜜", "温馨",
    "激动", "兴奋", "惊喜", "欣喜", "狂喜",
    "轻松", "舒心", "舒畅", "舒服", "痛快",
    "羡慕", "向往", "憧憬",
    # 希望期待
    "希望", "期望", "期待", "期盼", "盼望", "渴望", "祈望",
    "信心", "自信", "坚信", "确信",
    "相信", "信赖", "信念",
    "加油", "努力", "奋斗", "拼搏",
    # 进步发展
    "进步", "提升", "提高", "增长", "增加", "上升", "上涨",
    "发展", "繁荣", "兴盛", "兴旺",
    "创新", "突破", "超越", "飞跃", "腾飞",
    "领先", "优势", "前沿", "先进", "发达",
    "改善", "改进", "优化", "升级", "更新",
    "复苏", "回升", "回暖", "反弹",
    # 教育正面（校园舆情相关）
    "扩招", "减负", "奖学金", "助学金", "保研", "推免",
    "重点", "双一流", "985", "211",
    "就业好", "高薪", "师资", "名师", "教授", "博导",
    "实力", "排名", "优秀毕业生", "优秀学生",
    "开放", "改革", "现代化", "国际化",
    "校园文化", "社团", "活动", "比赛", "竞赛", "获奖",
    "录取", "上岸", "考取", "通过", "毕业", "学位",
    "学术", "科研", "论文", "专利", "项目",
    "勤工俭学", "助学", "减免", "补贴",
    "新校区", "扩建", "智慧校园", "信息化",
    "招生", "生源", "报考", "志愿",
    # 情绪正面
    "感动", "感激", "感谢", "感恩", "致谢",
    "致敬", "敬佩", "佩服", "崇拜",
    "温暖", "暖心", "贴心", "用心", "细心",
    "热情", "积极", "主动", "乐观",
    "真诚", "真实", "实在", "踏实",
    "团结", "友爱", "互助", "和谐",
    "文明", "礼貌", "谦逊", "虚心",
    # 正面短语
    "越来越好", "蒸蒸日上", "突飞猛进", "日新月异",
    "名列前茅", "首屈一指", "数一数二", "有目共睹",
    "来之不易", "难能可贵",
    # 表情
    "👍", "❤️", "🎉", "🌟", "✨", "👏", "😊", "😄", "😁",
    "🥰", "😍", "🤗", "🙏", "💪", "🎊", "🏆", "🥇",
])

# ── 负面情感词 ──
NEGATIVE_WORDS = set([
    # 批评否定
    "差", "差劲", "恶劣", "糟糕", "太差", "很差",
    "失败", "败笔", "失误", "错误", "出错",
    "不足", "缺陷", "缺点", "短板", "毛病",
    "问题", "漏洞", "隐患", "风险",
    "批评", "谴责", "指责", "斥责", "痛斥",
    "质疑", "争议", "非议", "异议",
    "否定", "否认", "拒绝", "抵制",
    # 愤怒不满
    "愤怒", "生气", "恼火", "气愤", "怒", "震怒",
    "不满", "不满", "反感", "厌恶", "憎恨", "痛恨",
    "投诉", "举报", "上访", "抗议",
    "鄙视", "轻视", "蔑视", "唾弃",
    "嚣张", "猖獗", "无耻", "可恶",
    "过分", "太过分", "离谱", "荒谬",
    # 悲伤失望
    "失望", "绝望", "灰心", "沮丧", "消沉",
    "悲伤", "难过", "伤心", "悲痛", "哀伤", "心碎",
    "痛苦", "痛心", "痛", "疼",
    "遗憾", "惋惜", "可惜",
    "孤独", "寂寞", "失落", "空虚",
    "后悔", "内疚", "羞愧", "惭愧", "自责",
    "丢脸", "丢人", "羞耻", "可耻",
    "哭", "泪", "哭泣", "流泪", "😭", "😢",
    # 担忧恐惧
    "担心", "担忧", "忧虑", "焦虑", "不安", "慌张",
    "害怕", "恐惧", "恐慌", "畏惧", "胆怯", "心虚",
    "紧张", "着急", "焦急", "急躁", "心烦",
    "压力", "负担", "包袱", "重担",
    "危机", "危险", "威胁",
    "😡", "😠", "😤", "😞", "😰", "😨", "😱",
    # 困难压力（校园相关）
    "困难", "艰难", "艰辛", "艰苦", "吃力",
    "挑战", "障碍", "阻碍", "阻力",
    "限制", "约束", "束缚", "禁锢",
    "内卷", "卷", "躺平", "摆烂",
    "应试", "刷题", "填鸭", "高压",
    "降薪", "裁员", "失业", "就业难", "找工作",
    "熬夜", "失眠", "脱发", "焦虑症", "抑郁症",
    # 下降衰退
    "下降", "下滑", "下跌", "降低", "减少", "减弱",
    "衰退", "萎缩", "萧条", "低迷",
    "恶化", "倒退", "退步", "落后",
    "崩溃", "断裂", "瘫痪", "停机",
    "关闭", "取消", "暂停", "停止",
    # 教育负面
    "减招", "停招", "缩招", "停办", "倒闭",
    "落榜", "退学", "肄业", "休学", "劝退",
    "作弊", "抄袭", "代考", "替考", "舞弊",
    "处分", "警告", "记过", "开除", "留校察看",
    "降分", "预警", "通报", "黑名单",
    "校园贷", "套路贷", "诈骗", "被骗",
    "霸凌", "欺凌", "校园暴力", "斗殴", "打架",
    "性侵", "骚扰", "猥亵",
    "跳楼", "自杀", "自残", "轻生",
    "食品安全", "中毒", "食物中毒",
    "漏水", "停电", "断网", "停水",
    "甲醛", "危房", "塌陷", "事故",
    "高收费", "乱收费", "天价", "暴利",
    "挂科", "重修", "补考", "清考",
    # 违规负面
    "违规", "违法", "违纪", "违章",
    "事故", "灾难", "灾害", "伤亡", "死亡",
    "腐败", "贪污", "受贿", "滥用",
    "造假", "虚假", "伪造", "谎报",
    "侵犯", "侵占", "霸占", "抢占",
    "迟延", "拖延", "推诿", "扯皮",
    # 负面短语
    "一塌糊涂", "不堪入目", "惨不忍睹", "触目惊心",
    "雪上加霜", "火上浇油", "变本加厉",
    "无人问津", "门可罗雀", "每况愈下",
    "不可理喻", "无法忍受", "忍无可忍",
    # 程度负面
    "严重", "严峻", "恶劣", "险恶",
    "可怕", "恐怖", "惊人",
])

# ── 感叹词/增强器 ──
INTENSIFIER_PUNCT = {"！", "!", "？", "?"}


def analyze_sentiment(text: str) -> Dict[str, Any]:
    """
    增强版情感分析：
    - 上下文否定词反转
    - 程度副词加权
    - 重复字符/感叹号增强
    - 对照词表确保准确
    """
    if not text:
        return {"sentiment_type": SentimentType.NEUTRAL, "sentiment_score": 0.0}

    words = jieba.lcut(text)
    total_score = 0.0
    matched_count = 0
    pos_strength = 0.0
    neg_strength = 0.0

    # 检查是否有感叹号/问号（情感增强器）
    has_exclamation = any(ch in text for ch in {"！", "!"})
    has_question = any(ch in text for ch in {"？", "?"})

    for i, word in enumerate(words):
        factor = 1.0
        is_negated = False

        # 程度副词
        if word in DEGREE_WORDS:
            continue  # 程度词本身不计分，影响下一个情感词

        # 检查前面是否有程度副词
        if i > 0 and words[i - 1] in DEGREE_WORDS:
            factor *= DEGREE_WORDS[words[i - 1]]
        elif i > 1 and words[i - 2] in DEGREE_WORDS:
            factor *= DEGREE_WORDS[words[i - 2]]

        # 检查前面是否有否定词（窗口2）
        if i > 0 and words[i - 1] in NEGATION_WORDS:
            is_negated = True
        elif i > 1 and words[i - 2] in NEGATION_WORDS:
            is_negated = True
        elif i > 2 and words[i - 2] in NEGATION_WORDS and words[i - 1] in DEGREE_WORDS:
            # "不是很满意" → 前面有否定+程度
            is_negated = True

        # 重复字符增强（好好好 → 更强）
        repeat_bonus = 1.0
        if len(word) >= 2:
            # 检测 AA / AAA 重复模式
            if len(set(word)) == 1:
                repeat_bonus = min(1.0 + (len(word) - 1) * 0.3, 2.0)
            # 检测 AABB 模式（高高兴兴 → 略强）
            elif len(word) >= 4 and word[:2] == word[2:]:
                repeat_bonus = 1.2

        if word in POSITIVE_WORDS:
            score = 1.0 * factor * repeat_bonus
            if is_negated:
                score = -score * 0.8  # 否定反转（力度稍弱）
                neg_strength += abs(score)
            else:
                pos_strength += score
            total_score += score
            matched_count += 1

        elif word in NEGATIVE_WORDS:
            score = 1.0 * factor * repeat_bonus
            if is_negated:
                score = abs(score) * 0.8  # 否定反转
                pos_strength += score
            else:
                neg_strength += abs(score)
            total_score += -score  # 注意这里是负分
            matched_count += 1

    # 感叹号增强：如果匹配到情感词且有感叹号，加强强度
    if matched_count > 0 and has_exclamation:
        if total_score > 0:
            total_score *= 1.3
            pos_strength *= 1.3
        elif total_score < 0:
            total_score *= 1.3
            neg_strength *= 1.3

    # 最终归一化到 [-1, 1]
    if matched_count > 0:
        # 用正负强度比来计算分数，更稳定
        combined = pos_strength + neg_strength
        if combined > 0:
            sentiment_score = (pos_strength - neg_strength) / combined
        else:
            sentiment_score = 0.0
    else:
        sentiment_score = 0.0

    # 阈值判定（含中性缓冲区）
    if sentiment_score > 0.15:
        sentiment_type = SentimentType.POSITIVE
    elif sentiment_score < -0.15:
        sentiment_type = SentimentType.NEGATIVE
    else:
        sentiment_type = SentimentType.NEUTRAL

    return {
        "sentiment_type": sentiment_type,
        "sentiment_score": round(sentiment_score, 4),
    }

@router.get("/analyze")
def get_sentiment_analysis(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取舆情数据的情感分析结果
    """
    try:
        opinions = db.query(Opinion).offset(skip).limit(limit).all()
        data = [opinion.to_dict() for opinion in opinions]
        return {
            "status": "success",
            "data": data,
            "total": len(data),
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情感分析结果失败: {str(e)}")

@router.post("/reanalyze")
def reanalyze_all_sentiments(db: Session = Depends(get_db)):
    """
    重新分析所有舆情数据的情感倾向
    """
    try:
        # 获取所有需要分析的舆情数据
        opinions = db.query(Opinion).all()
        total_count = len(opinions)
        
        if total_count == 0:
            return {
                "status": "success",
                "message": "没有需要分析的数据",
                "analyzed_count": 0,
                "total_count": 0
            }
        
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
        
        return {
            "status": "success",
            "message": f"成功重新分析 {analyzed_count} 条数据",
            "analyzed_count": analyzed_count,
            "total_count": total_count,
            "statistics": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"重新分析情感倾向失败: {str(e)}")

@router.get("/statistics")
def get_sentiment_statistics(db: Session = Depends(get_db)):
    """
    获取情感分析统计数据 (缓存优先)
    """
    cache_key = "cache:sentiment:stats"

    def query_db():
        positive_count = db.query(Opinion).filter(Opinion.sentiment == SentimentType.POSITIVE).count()
        negative_count = db.query(Opinion).filter(Opinion.sentiment == SentimentType.NEGATIVE).count()
        neutral_count = db.query(Opinion).filter(Opinion.sentiment == SentimentType.NEUTRAL).count()
        total_count = positive_count + negative_count + neutral_count
        avg_sentiment_score = db.query(func.avg(Opinion.sentiment_score)).scalar() or 0.0

        from sqlalchemy import case
        platform_stats = db.query(
            Opinion.source_platform,
            func.count(Opinion.id).label('total'),
            func.sum(case((Opinion.sentiment == SentimentType.POSITIVE, 1), else_=0)).label('positive'),
            func.sum(case((Opinion.sentiment == SentimentType.NEGATIVE, 1), else_=0)).label('negative'),
            func.sum(case((Opinion.sentiment == SentimentType.NEUTRAL, 1), else_=0)).label('neutral')
        ).group_by(Opinion.source_platform).all()

        platform_distribution = []
        for platform, total, pos, neg, neu in platform_stats:
            platform_distribution.append({
                "platform": platform or "unknown", "total": total,
                "positive": pos or 0, "negative": neg or 0, "neutral": neu or 0
            })

        return {
            "status": "success",
            "statistics": {
                "total_count": total_count, "positive_count": positive_count,
                "negative_count": negative_count, "neutral_count": neutral_count,
                "positive_percentage": round(positive_count / total_count * 100, 2) if total_count > 0 else 0,
                "negative_percentage": round(negative_count / total_count * 100, 2) if total_count > 0 else 0,
                "neutral_percentage": round(neutral_count / total_count * 100, 2) if total_count > 0 else 0,
                "avg_sentiment_score": round(avg_sentiment_score, 4)
            },
            "platform_distribution": platform_distribution
        }

    try:
        return redis_cache.cache_aside(cache_key, query_db, expire=120)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情感统计失败: {str(e)}")

@router.post("/analyze/{opinion_id}")
def analyze_single_opinion(opinion_id: int, db: Session = Depends(get_db)):
    """
    分析单条舆情的情感倾向
    """
    try:
        opinion = db.query(Opinion).filter(Opinion.id == opinion_id).first()
        if not opinion:
            raise HTTPException(status_code=404, detail=f"未找到ID为{opinion_id}的舆情数据")
        
        # 分析情感
        text = f"{opinion.title or ''} {opinion.content or ''}"
        result = analyze_sentiment(text)
        
        # 更新数据库
        opinion.sentiment = result["sentiment_type"]
        opinion.sentiment_score = result["sentiment_score"]
        db.commit()
        
        return {
            "status": "success",
            "message": "情感分析完成",
            "opinion_id": opinion_id,
            "sentiment_type": result["sentiment_type"],
            "sentiment_score": result["sentiment_score"]
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"分析单条舆情情感失败: {str(e)}")
