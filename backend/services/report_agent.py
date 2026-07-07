# -*- coding: utf-8 -*-
"""舆情报告 Agent —— DeepSeek 函数调用驱动，自主查询数据并生成报告"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from db.mysql_config import SessionLocal
from models.mysql_models import Opinion, HotTopic
from models.report_model import Report, ReportType

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

MAX_TOOL_TURNS = 10

# ── System Prompt ──
SYSTEM_PROMPT = """# 角色

你是一位高校网络舆情监测中心的高级分析师。你的任务是：自主查询系统数据，经过多轮信息收集后，撰写一份专业、客观、数据充分的周度舆情分析报告。

# 核心原则

- 你拥有完整的工具调用能力，可以自主决定查询哪些数据。
- 你必须在收集到足够数据之后才生成最终报告。
- 在最终报告输出前，不输出任何分析结论，只执行工具调用和记录中间发现。
- 报告的每个数据结论必须来源于实际查询返回的数值，不得编造。
- 若某个维度的数据查询失败或为空，生成报告时应在对应小节如实说明。
- 所有工具调用的参数值必须是真实日期和数字。
- 不得在最终报告中使用未从工具返回中获取的数据。
- 不得在生成报告前向用户输出任何分析过程或中间结果。
- 如果你发现某个维度的数据对完整报告至关重要但查询失败，在报告中注明"本期该维度数据缺失"。

# 工作流程

你必须严格按照以下流程执行：

## 第一步：规划查询策略

在首次收到"生成周报"指令后，先思考需要收集哪些维度的数据。必查维度包括：

1. 舆情统计数据（总量、情感分布、平台分布）
2. 热点话题列表（按热度排序，取 Top 5-10）
3. 趋势分析数据（每日舆情量、情感趋势）
4. 平台分布数据（各平台来源占比）
5. 情感分析统计数据（正/负/中性占比、平均情感分）
6. 关键词云数据（高频关键词）
7. 高热度舆情条目（热度最高的 3-5 条）

## 第二步：执行数据查询

调用工具查询数据。允许并行调用的应同时发起。

## 第三步：生成报告

当你认为已收集到足够的数据后，调用 generate_report 工具输出最终报告。

报告必须包含完整的数据引用，输出格式为 Markdown。

---

# 输出模板

调用 generate_report 时，报告正文必须按以下结构撰写：

```markdown
## 舆情周报（第 XX 周）

**报告周期**：YYYY-MM-DD 至 YYYY-MM-DD
**数据来源**：校园舆情监测系统
**生成时间**：YYYY-MM-DD HH:mm

### 一、本周舆情概览

一段总结性概述，包含本周舆情总量、热点话题数、阅读量、情感分布占比，以及一句话定性结论。

### 二、情感分析

正面/负面/中性占比、平均情感评分、情感趋势的简要解读（如"负面情绪在周中出现峰值"）。

### 三、热点话题分析

以列表形式列出热度前 5 的话题，每个话题包含：名称、提及次数、情感分布、变化趋势、一句话定性。

### 四、平台分布

主要信息来源平台及占比，各平台情感倾向差异解读。

### 五、风险预警

负面倾向显著上升的议题、敏感话题、建议重点关注的事项。

### 六、趋势与研判

舆情总量及热度走势判断，可能的发展方向。

### 七、总结与建议

3-5 条可操作的管理建议。
```"""

# ── Tool Definitions ──
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_opinion_statistics",
            "description": "查询舆情整体统计数据，包含总量、热点话题数、阅读量、情感分布、平台分布",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_time": {"type": "string", "description": "起始日期，格式 YYYY-MM-DD"},
                    "end_time": {"type": "string", "description": "结束日期，格式 YYYY-MM-DD"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hot_topics",
            "description": "查询热点话题列表，按热度排序",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "统计天数，默认7，范围1-30"},
                    "pageSize": {"type": "integer", "description": "返回条数，默认10"},
                    "platform": {"type": "string", "description": "按平台筛选"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_trend_analysis",
            "description": "查询舆情趋势分析数据，返回每日情感分布",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "开始日期，格式 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期，格式 YYYY-MM-DD"},
                    "keyword": {"type": "string", "description": "按关键词筛选"},
                    "source": {"type": "string", "description": "按来源平台筛选"},
                    "sentiment_type": {"type": "string", "description": "按情感类型筛选"},
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_platform_distribution",
            "description": "查询各平台舆情分布数据，返回各平台占比",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "开始日期，格式 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期，格式 YYYY-MM-DD"},
                    "keyword": {"type": "string", "description": "按关键词筛选"},
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sentiment_statistics",
            "description": "查询情感分析统计数据，返回正/负/中性占比、平均情感分、各平台情感分布",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_keyword_cloud",
            "description": "查询关键词云数据，返回高频关键词列表及权重",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "统计天数，默认7"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_opinions",
            "description": "查询高热度舆情条目，按热度排序",
            "parameters": {
                "type": "object",
                "properties": {
                    "pageSize": {"type": "integer", "description": "返回条数，默认5"},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_report",
            "description": "生成最终的舆情分析报告。仅在数据收集完毕且确认充分后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_content": {
                        "type": "string",
                        "description": "完整的 Markdown 格式报告正文",
                    },
                },
                "required": ["report_content"],
            },
        },
    },
]


# ── Tool Handlers ──

def _make_db() -> Session:
    return SessionLocal()


PLATFORM_MAP = {
    "weibo": "微博", "wechat": "微信", "zhihu": "知乎",
    "douyin": "抖音", "xiaohongshu": "小红书", "bilibili": "B站",
    "toutiao": "头条",
}


def handle_get_opinion_statistics(args: dict) -> dict:
    db = _make_db()
    try:
        q = db.query(Opinion)
        if args.get("start_time"):
            q = q.filter(Opinion.publish_time >= datetime.strptime(args["start_time"], "%Y-%m-%d"))
        if args.get("end_time"):
            q = q.filter(Opinion.publish_time <= datetime.strptime(args["end_time"], "%Y-%m-%d"))

        total = q.count()
        hot_count = db.query(HotTopic).count()

        sentiments = q.with_entities(Opinion.sentiment, func.count(Opinion.id)).group_by(Opinion.sentiment).all()
        dist = {"positive": 0, "negative": 0, "neutral": 0}
        for s, c in sentiments:
            if s in dist:
                dist[s] = c

        platforms = q.with_entities(Opinion.source_platform, func.count(Opinion.id)).group_by(
            Opinion.source_platform).order_by(desc(func.count(Opinion.id))).all()
        plat_list = []
        for p, c in platforms:
            pct = round(c / total * 100, 1) if total > 0 else 0
            plat_list.append({"platform": PLATFORM_MAP.get(p, p), "count": c, "percentage": pct})

        views = q.with_entities(func.sum(Opinion.read_count)).scalar() or 0

        return {
            "total_count": total,
            "hot_topics_count": hot_count,
            "views_count": int(views),
            "sentiment_distribution": dist,
            "platform_distribution": plat_list,
        }
    finally:
        db.close()


def handle_get_hot_topics(args: dict) -> dict:
    db = _make_db()
    try:
        days = args.get("days", 7)
        limit = args.get("pageSize", 10)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        q = db.query(HotTopic).filter(HotTopic.last_seen >= start_date)
        if args.get("platform"):
            q = q.filter(HotTopic.topic.like(f"%{args['platform']}%"))
        topics = q.order_by(desc(HotTopic.mention_count)).limit(limit).all()

        return {
            "items": [
                {
                    "topic": t.topic,
                    "keyword": t.keyword,
                    "mention_count": t.mention_count,
                    "sentiment_distribution": t.sentiment_distribution,
                    "trend": t.trend,
                    "first_seen": t.first_seen.isoformat() if t.first_seen else None,
                    "last_seen": t.last_seen.isoformat() if t.last_seen else None,
                }
                for t in topics
            ],
            "total": len(topics),
        }
    finally:
        db.close()


def handle_get_trend_analysis(args: dict) -> dict:
    db = _make_db()
    try:
        start = datetime.strptime(args["start_date"], "%Y-%m-%d")
        end = datetime.strptime(args["end_date"], "%Y-%m-%d")

        q = db.query(
            func.date(Opinion.publish_time).label("date"),
            Opinion.sentiment,
            func.count(Opinion.id).label("count"),
        ).filter(Opinion.publish_time >= start, Opinion.publish_time <= end)

        if args.get("keyword"):
            q = q.filter(Opinion.content.like(f"%{args['keyword']}%"))
        if args.get("source"):
            q = q.filter(Opinion.source_platform == args["source"])
        if args.get("sentiment_type"):
            q = q.filter(Opinion.sentiment == args["sentiment_type"])

        rows = q.group_by(func.date(Opinion.publish_time), Opinion.sentiment).all()
        import pandas as pd
        df = pd.DataFrame([{"date": str(r.date), "sentiment": r.sentiment, "count": r.count} for r in rows])

        trend_data = []
        if not df.empty:
            for date in sorted(df["date"].unique()):
                pos = int(df[(df["date"] == date) & (df["sentiment"] == "positive")]["count"].sum())
                neg = int(df[(df["date"] == date) & (df["sentiment"] == "negative")]["count"].sum())
                neu = int(df[(df["date"] == date) & (df["sentiment"] == "neutral")]["count"].sum())
                trend_data.append({
                    "date": date, "positive_count": pos, "negative_count": neg,
                    "neutral_count": neu, "total_count": pos + neg + neu,
                })

        total = sum(d["total_count"] for d in trend_data)
        return {"trend_data": trend_data, "total_count": total, "time_range": f"{args['start_date']} 至 {args['end_date']}"}
    finally:
        db.close()


def handle_get_platform_distribution(args: dict) -> dict:
    db = _make_db()
    try:
        start = datetime.strptime(args["start_date"], "%Y-%m-%d")
        end = datetime.strptime(args["end_date"], "%Y-%m-%d")

        q = db.query(
            Opinion.source_platform, func.count(Opinion.id).label("count")
        ).filter(Opinion.publish_time >= start, Opinion.publish_time <= end)

        if args.get("keyword"):
            q = q.filter(Opinion.content.like(f"%{args['keyword']}%"))

        rows = q.group_by(Opinion.source_platform).all()
        total = sum(r.count for r in rows)
        dist = []
        for plat, cnt in rows:
            dist.append({"platform": PLATFORM_MAP.get(plat, plat), "count": cnt, "percentage": round(cnt / total * 100, 1) if total else 0})

        # Also add sentiment distribution per platform
        for item in dist:
            platform_en = next((k for k, v in PLATFORM_MAP.items() if v == item["platform"]), None)
            if platform_en:
                sent_rows = db.query(Opinion.sentiment, func.count(Opinion.id)).filter(
                    Opinion.publish_time >= start, Opinion.publish_time <= end,
                    Opinion.source_platform == platform_en,
                ).group_by(Opinion.sentiment).all()
                for s, c in sent_rows:
                    item[f"{s}_count"] = c

        return {"distribution_data": dist, "total_count": total}
    finally:
        db.close()


def handle_get_sentiment_statistics(args: dict) -> dict:
    db = _make_db()
    try:
        total = db.query(Opinion).count()
        rows = db.query(Opinion.sentiment, func.count(Opinion.id)).group_by(Opinion.sentiment).all()
        dist = {"positive": 0, "negative": 0, "neutral": 0}
        for s, c in rows:
            if s in dist:
                dist[s] = c

        avg_score = db.query(func.avg(Opinion.sentiment_score)).filter(Opinion.sentiment_score.isnot(None)).scalar() or 0

        # Per-platform sentiment
        plat_sent = {}
        plat_rows = db.query(Opinion.source_platform, Opinion.sentiment, func.count(Opinion.id)).group_by(
            Opinion.source_platform, Opinion.sentiment).all()
        for plat, sent, cnt in plat_rows:
            plat_name = PLATFORM_MAP.get(plat, plat)
            if plat_name not in plat_sent:
                plat_sent[plat_name] = {}
            plat_sent[plat_name][sent] = cnt

        return {
            "total_count": total,
            "sentiment_distribution": dist,
            "positive_pct": round(dist["positive"] / total * 100, 1) if total else 0,
            "negative_pct": round(dist["negative"] / total * 100, 1) if total else 0,
            "neutral_pct": round(dist["neutral"] / total * 100, 1) if total else 0,
            "average_sentiment_score": round(float(avg_score), 3),
            "platform_sentiment": plat_sent,
        }
    finally:
        db.close()


def handle_get_keyword_cloud(args: dict) -> dict:
    db = _make_db()
    try:
        days = args.get("days", 7)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        rows = db.query(Opinion.content).filter(
            Opinion.content.isnot(None), Opinion.content != "",
            Opinion.publish_time >= start_date,
        ).order_by(desc(Opinion.publish_time)).limit(2000).all()

        texts = [r[0] for r in rows if r[0] and len(r[0]) > 10]
        if not texts:
            return {"words": [], "count": 0}

        import jieba
        import jieba.analyse
        combined = " ".join(texts)
        tags = jieba.analyse.extract_tags(combined, topK=60, withWeight=True)

        words = []
        for word, weight in tags:
            word = word.strip()
            if len(word) < 2:
                continue
            words.append({"name": word, "value": int(weight * 1000)})

        return {"words": words, "count": len(words)}
    finally:
        db.close()


def handle_get_top_opinions(args: dict) -> dict:
    db = _make_db()
    try:
        limit = args.get("pageSize", 5)
        rows = db.query(Opinion).order_by(desc(Opinion.read_count)).limit(limit).all()
        return {
            "items": [
                {
                    "id": o.id, "title": o.title or o.content[:40],
                    "content": o.content, "source_platform": PLATFORM_MAP.get(o.source_platform, o.source_platform),
                    "sentiment": o.sentiment, "hot_score": o.hot_score or 0,
                    "read_count": o.read_count, "like_count": o.like_count,
                    "comment_count": o.comment_count, "publish_time": o.publish_time.isoformat() if o.publish_time else None,
                }
                for o in rows
            ],
            "total": len(rows),
        }
    finally:
        db.close()


TOOL_HANDLERS = {
    "get_opinion_statistics": handle_get_opinion_statistics,
    "get_hot_topics": handle_get_hot_topics,
    "get_trend_analysis": handle_get_trend_analysis,
    "get_platform_distribution": handle_get_platform_distribution,
    "get_sentiment_statistics": handle_get_sentiment_statistics,
    "get_keyword_cloud": handle_get_keyword_cloud,
    "get_top_opinions": handle_get_top_opinions,
}


# ── Agent Loop ──

async def run_report_agent(report_type: str = "weekly") -> Optional[dict]:
    """Run the report agent. Returns the saved report dict or None on failure."""
    if not DEEPSEEK_API_KEY:
        logger.error("DEEPSEEK_API_KEY not set")
        return None

    now = datetime.now()
    if report_type == "weekly":
        period_start = now - timedelta(days=7)
        title = f"舆情周报（{period_start.strftime('%m.%d')} - {now.strftime('%m.%d')}）"
        user_msg = f"请生成本周舆情分析报告。报告周期：{period_start.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}。"
    elif report_type == "monthly":
        period_start = now - timedelta(days=30)
        title = f"舆情月报（{period_start.strftime('%m.%d')} - {now.strftime('%m.%d')}）"
        user_msg = f"请生成本月舆情分析报告。报告周期：{period_start.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}。"
    else:
        period_start = now - timedelta(days=7)
        title = f"舆情报告（{now.strftime('%Y-%m-%d')}）"
        user_msg = f"请生成舆情分析报告。报告周期：{period_start.strftime('%Y-%m-%d')} 至 {now.strftime('%Y-%m-%d')}。"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    report_content = None

    async with httpx.AsyncClient(timeout=120) as client:
        for turn in range(MAX_TOOL_TURNS):
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": DEEPSEEK_MODEL,
                    "messages": messages,
                    "tools": TOOLS,
                    "temperature": 0.3,
                },
            )
            resp.raise_for_status()
            body = resp.json()
            choice = body["choices"][0]
            msg = choice["message"]

            if choice["finish_reason"] == "stop" and not msg.get("tool_calls"):
                # Agent decided to stop without calling generate_report
                if msg.get("content"):
                    report_content = msg["content"]
                break

            if not msg.get("tool_calls"):
                # No tool calls and no content - add the message and continue
                messages.append(msg)
                continue

            # Execute tool calls
            tool_msgs = []
            for tc in msg["tool_calls"]:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])

                if func_name == "generate_report":
                    report_content = func_args.get("report_content", "")
                    tool_msgs.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": "报告已生成。",
                    })
                    break

                handler = TOOL_HANDLERS.get(func_name)
                if handler:
                    try:
                        result = handler(func_args)
                        tool_msgs.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": json.dumps(result, ensure_ascii=False, default=str),
                        })
                    except Exception as e:
                        logger.error(f"Tool {func_name} error: {e}")
                        tool_msgs.append({
                            "role": "tool",
                            "tool_call_id": tc["id"],
                            "content": json.dumps({"error": str(e)}, ensure_ascii=False),
                        })

            messages.append(msg)
            messages.extend(tool_msgs)

            if report_content:
                break

    if not report_content:
        logger.warning("Agent did not generate a report")
        return None

    # Save report to database
    db = _make_db()
    try:
        report = Report(
            title=title,
            content=report_content,
            report_type=report_type,
            period_start=period_start,
            period_end=now,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        result = report.to_dict()

        # ── 推送到微信（Server酱）──
        sct_key = os.getenv("SCT_KEY", "")
        if sct_key:
            try:
                type_label = {"weekly": "周报", "monthly": "月报", "daily": "日报"}.get(report_type, "报告")
                async with httpx.AsyncClient(timeout=15) as push_client:
                    await push_client.post(
                        "https://sctapi.ftqq.com/%s.send" % sct_key,
                        data={
                            "title": "校园舆情%s｜%s" % (type_label, now.strftime("%m.%d")),
                            "desp": report_content[:8000],
                        },
                    )
                logger.info("微信推送成功")
            except Exception as e:
                logger.warning("微信推送失败: %s", e)

        return result
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save report: {e}")
        return None
    finally:
        db.close()
