# -*- coding: utf-8 -*-
from fastapi import APIRouter, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from db.mysql_config import get_db
from models.mysql_models import Opinion
from utils.redis_cache import redis_cache, make_cache_key

import jieba
import jieba.analyse
import re
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/keywords", tags=["词云关键词"])

# ── 停用词（常见中文虚词 + 无语义高频词）──
STOP_WORDS = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
    "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
    "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
    "所", "为", "所以", "因为", "但是", "然而", "而且", "虽然", "如果",
    "可以", "这个", "那个", "什么", "怎么", "怎样", "哪", "哪里",
    "还", "被", "把", "从", "让", "给", "向", "对", "与", "及", "或",
    "之", "其", "以", "而", "等", "能", "能够", "应该", "需要", "已经",
    "将", "正在", "一直", "还是", "只是", "之后", "然后", "接着",
    "啊", "吧", "吗", "呢", "嘛", "哦", "嗯", "呀", "哈", "呵",
    "太", "更", "最", "很", "非常", "比较", "真", "特别",
    "觉得", "感觉", "认为", "以为", "知道", "想", "希望",
    "今天", "昨天", "明天", "现在", "以前", "以后", "时候",
    "一个", "一种", "一些", "很多", "没有", "可能", "一定",
    "进行", "使用", "通过", "根据", "关于", "对于", "有关",
    "相关", "各种", "不同", "主要", "重要", "需要", "目前",
    "该", "已", "未", "无", "非", "仅", "只", "整个",
    "大量", "部分", "全部", "所有", "其他", "另外",
    "大家", "有人", "别人", "本人", "同学", "老师",
    "真的", "确实", "居然", "竟然", "简直", "到底",
    "?,", "!","？","！","，","。","：","、","；","""",
    ""","「","」","『","』","（","）","【","】","《","》",
    "…","—","～","~","#","@","￥","$","%","&","*",
}

# ── 自定义校园词库 ──
CAMPUS_WORDS = [
    "食堂", "图书馆", "宿舍", "教室", "实验室", "操场", "体育馆",
    "校园网", "校园卡", "校园", "学校", "大学", "学院",
    "期末考", "期中考", "考试", "成绩", "学分", "绩点", "选课", "课程",
    "奖学金", "助学金", "助学贷款", "学费", "住宿费",
    "考研", "保研", "就业", "实习", "毕业", "论文", "答辩",
    "社团", "学生会", "志愿者", "运动会", "比赛", "讲座",
    "新生", "报到", "军训", "校招", "招聘", "面试",
    "安全", "卫生", "后勤", "食堂涨价", "空调", "热水",
    "辅导员", "导师", "教授", "院长", "校长",
    "校庆", "文化节", "艺术节", "科技节",
    "四六级", "托福", "雅思", "GRE", "考公", "考编",
    "双学位", "辅修", "交换生", "留学生", "外教",
    "在线课程", "网课", "MOOC", "学习氛围", "自习",
    "转专业", "休学", "退学", "复学",
]
for w in CAMPUS_WORDS:
    jieba.add_word(w)

CACHE_TTL = 300  # 5分钟


def extract_keywords_from_texts(texts: list[str], topk: int = 120) -> list[dict]:
    """用 jieba TF-IDF 从文本列表中提取关键词及权重"""
    if not texts:
        return []

    combined = " ".join(texts)
    # 用 jieba TF-IDF 提取，比纯频率统计更准确
    tags = jieba.analyse.extract_tags(combined, topK=topk, withWeight=True)

    words = []
    for word, weight in tags:
        word = word.strip()
        # 过滤停用词、单字、纯数字、纯标点
        if len(word) < 2:
            continue
        if word in STOP_WORDS:
            continue
        if re.match(r'^[\d\.\+\-\*/%=]+$', word):
            continue
        if re.match(r'^[a-zA-Z]{1,2}$', word):
            continue
        # 权重归一化到 100-2000 区间，让词云更好看
        normalized = int(weight * 1000)
        words.append({"name": word, "value": max(normalized, 50)})

    return words


@router.get("/cloud")
async def get_keyword_cloud(
    days: int = Query(7, ge=1, le=90, description="统计过去天数"),
    platform: Optional[str] = Query(None, description="平台筛选"),
    db: Session = Depends(get_db),
):
    """基于真实舆情内容 + jieba TF-IDF 提取词云关键词"""
    cache_key = make_cache_key("cache:keywords:cloud", days=days, platform=platform)

    def query_db():
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        query = db.query(Opinion.content).filter(
            Opinion.content.isnot(None),
            Opinion.content != "",
            Opinion.publish_time >= start_date,
            Opinion.publish_time <= end_date,
        )
        if platform:
            query = query.filter(Opinion.source_platform == platform)

        # 取最近的数据，限制 2000 条避免内存爆炸
        rows = query.order_by(Opinion.publish_time.desc()).limit(2000).all()
        texts = [r[0] for r in rows if r[0] and len(r[0]) > 10]

        if not texts:
            return []

        words = extract_keywords_from_texts(texts, topk=120)

        # 如果提取出的词太少，用词频统计补足
        if len(words) < 40:
            # 对所有文本分词后统计词频作为补充
            freq_map = {}
            for t in texts:
                seg = jieba.cut(t)
                for w in seg:
                    w = w.strip()
                    if len(w) < 2 or w in STOP_WORDS:
                        continue
                    if re.match(r'^[\d\.\+\-\*/%=]+$', w) or re.match(r'^[a-zA-Z]{1,2}$', w):
                        continue
                    freq_map[w] = freq_map.get(w, 0) + 1

            for w, cnt in sorted(freq_map.items(), key=lambda x: x[1], reverse=True)[:120]:
                name = w.strip()
                exists = any(item["name"] == name for item in words)
                if not exists and len(name) <= 10:
                    words.append({"name": name, "value": min(cnt * 10, 500)})

        return sorted(words, key=lambda x: x["value"], reverse=True)[:100]

    try:
        data = redis_cache.cache_aside(cache_key, query_db, expire=CACHE_TTL)
        return {"words": data, "count": len(data)}
    except Exception as e:
        logger.error(f"词云数据查询失败: {e}")
        return {"words": [], "count": 0, "error": str(e)}
