# -*- coding: utf-8 -*-
"""事件脉络追踪 Agent —— DeepSeek 驱动，追溯话题生命周期"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from db.mysql_config import SessionLocal
from models.mysql_models import Opinion
from models.report_model import Report

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
MAX_TOOL_TURNS = 12

PLATFORM_MAP = {
    "weibo": "微博", "wechat": "微信", "zhihu": "知乎",
    "douyin": "抖音", "xiaohongshu": "小红书", "bilibili": "B站",
    "toutiao": "头条", "people_edu": "人民网教育", "sina_edu": "新浪教育",
    "eol": "中国教育在线",
}

SYSTEM_PROMPT = """你是一名高校网络舆情事件分析专家。你的任务是：**给定一个话题关键词，自动追溯该话题的完整生命周期，识别关键转折点，输出结构化的事件脉络报告**。

# 核心原则

- 你有完整的数据查询工具，可以自主决定分多轮查询不同时间段的数据。
- 每个事件脉络必须包含：潜伏期 → 爆发期 → 高峰期 → 衰退期（如有二次爆发则追加）。
- 每个阶段必须对应真实的数据证据（时间范围、舆论数量、情感分布），不得编造。
- 如果数据不足以划分某个阶段，在报告中如实说明"本阶段数据不完整"。
- 不得输出任何推测性结论，所有判断必须基于工具返回的数据。

# 阶段划分标准

| 阶段 | 判定条件 |
|------|---------|
| 潜伏期 | 关键词日均提及量 < 峰值的 10%，情感分散，无集中讨论 |
| 爆发期 | 单日提及量环比增长 > 200%，或有单条高互动内容（评论 + 转发 > 过去均值 × 5） |
| 高峰期 | 连续 2-3 天提及量维持在高位（峰值的 80% 以上），情感倾向趋于一致 |
| 衰退期 | 连续 3 天环比下降 > 30%，新增内容减少，互动率下降 |
| 二次爆发 | 衰退后再次出现单日环比增长 > 150%，且有新的话题切入点 |

# 工作流程

## 第一步：确定时间窗口

以关键词首次出现的时间为起点，当前时间为终点，划定完整检索范围。

## 第二步：分段扫描数据

按天粒度查询该关键词的提及量、情感分布、高热度内容，识别数据突变点。

## 第三步：划分阶段

根据突变点和阶段判定标准，将时间轴切割为若干阶段。

## 第四步：提取每个阶段的关键内容

在每个阶段内，提取热度最高的 3-5 条代表性内容，记录其平台、情感、互动数据。

## 第五步：输出事件脉络报告

调用 `generate_trace_report` 工具输出最终报告。

# 输出模板

调用 `generate_trace_report` 时，报告正文必须按以下结构撰写：

## 事件脉络追踪报告

**事件关键词**：xxx
**追踪时间范围**：YYYY-MM-DD 至 YYYY-MM-DD
**覆盖数据量**：共 xxx 条相关舆论
**涉及平台**：平台A、平台B、……

### 一、事件总览
一句话概述事件性质，包含生命周期总天数、峰值日提及量、峰值日情感占比、整体情感倾向。

### 二、生命周期时间线
| 阶段 | 起止时间 | 持续天数 | 提及量 | 情感倾向 | 关键触发点 |
|------|---------|---------|--------|---------|-----------|
| ... | ... | ... | ... | ... | ... |

### 三、各阶段详析
（每个阶段包含：阶段特征、代表性内容列表）

### 四、传播特征分析
首发平台、主要传播平台、传播速度、意见领袖

### 五、结论与启示
3-5 条总结

---

# 约束

- 必须在调用工具的循环中逐段收集数据，不能在首次调用前输出任何分析结论。
- 阶段划分必须基于工具返回的真实数值突变点，不得人为预设阶段数。
- 所有提及的数据（时间、数量、占比）必须来自实际查询结果。
- 如果某阶段数据不足以支撑分析，在该阶段标题下注明"数据不足以详细分析"。
- `generate_trace_report` 是一次性输出，调用后不再追加修改。"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_keyword_timeline",
            "description": "按天粒度查询某关键词的时间序列数据，返回每日提及量、情感分布、互动总量",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                },
                "required": ["keyword", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_top_contents_by_period",
            "description": "查询某时间段内某关键词的热度 TOP N 内容，按互动量排序",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                    "top_n": {"type": "integer", "description": "返回条数，默认5"},
                },
                "required": ["keyword", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_platform_spread",
            "description": "查询某话题在不同平台之间的传播时序，返回首次出现时间和各平台出现顺序",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_sentiment_trend",
            "description": "查询某关键词在指定时间范围内的每日情感评分均值变化",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "start_date": {"type": "string", "description": "开始日期 YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "结束日期 YYYY-MM-DD"},
                },
                "required": ["keyword", "start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_influencer_accounts",
            "description": "查询某话题下互动量超过指定阈值的活跃账号列表",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "搜索关键词"},
                    "min_interactions": {"type": "integer", "description": "最低互动总量阈值，默认50"},
                },
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_trace_report",
            "description": "输出最终的事件脉络追踪报告。仅在数据收集完毕且确认充分后调用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "report_content": {"type": "string", "description": "完整的 Markdown 格式事件脉络报告"},
                },
                "required": ["report_content"],
            },
        },
    },
]


def _make_db() -> Session:
    return SessionLocal()


# ── Tool Handlers ──

def handle_get_keyword_timeline(args: dict) -> dict:
    db = _make_db()
    try:
        start = datetime.strptime(args["start_date"], "%Y-%m-%d")
        end = datetime.strptime(args["end_date"], "%Y-%m-%d") + timedelta(days=1)
        kw = args["keyword"]

        rows = db.query(
            func.date(Opinion.publish_time).label("date"),
            Opinion.sentiment,
            func.count(Opinion.id).label("cnt"),
            func.sum(Opinion.read_count).label("reads"),
            func.sum(Opinion.like_count + Opinion.comment_count + Opinion.share_count).label("interactions"),
        ).filter(
            Opinion.publish_time >= start, Opinion.publish_time < end,
            Opinion.content.like(f"%{kw}%"),
        ).group_by(func.date(Opinion.publish_time), Opinion.sentiment).all()

        import pandas as pd
        df = pd.DataFrame([{
            "date": str(r.date), "sentiment": r.sentiment, "count": r.cnt,
            "reads": int(r.reads or 0), "interactions": int(r.interactions or 0),
        } for r in rows])

        timeline = []
        if not df.empty:
            for date in sorted(df["date"].unique()):
                day_data = df[df["date"] == date]
                pos = int(day_data[day_data["sentiment"] == "positive"]["count"].sum())
                neg = int(day_data[day_data["sentiment"] == "negative"]["count"].sum())
                neu = int(day_data[day_data["sentiment"] == "neutral"]["count"].sum())
                total = pos + neg + neu
                interactions = int(day_data["interactions"].sum())
                reads = int(day_data["reads"].sum())
                timeline.append({
                    "date": date, "total": total, "positive": pos, "negative": neg, "neutral": neu,
                    "total_reads": reads, "total_interactions": interactions,
                })

        return {"keyword": kw, "timeline": timeline, "data_points": len(timeline),
                "total_mentions": sum(d["total"] for d in timeline)}
    finally:
        db.close()


def handle_get_top_contents_by_period(args: dict) -> dict:
    db = _make_db()
    try:
        start = datetime.strptime(args["start_date"], "%Y-%m-%d")
        end = datetime.strptime(args["end_date"], "%Y-%m-%d") + timedelta(days=1)
        kw = args["keyword"]
        top_n = args.get("top_n", 5)

        rows = db.query(Opinion).filter(
            Opinion.publish_time >= start, Opinion.publish_time < end,
            Opinion.content.like(f"%{kw}%"),
        ).order_by(desc(Opinion.read_count + Opinion.like_count + Opinion.comment_count + Opinion.share_count)).limit(top_n).all()

        return {
            "keyword": kw, "period": f"{args['start_date']} ~ {args['end_date']}",
            "items": [{
                "content": o.content, "platform": PLATFORM_MAP.get(o.source_platform, o.source_platform),
                "sentiment": o.sentiment, "sentiment_score": o.sentiment_score,
                "read_count": o.read_count, "like_count": o.like_count,
                "comment_count": o.comment_count, "share_count": o.share_count,
                "total_interactions": (o.like_count or 0) + (o.comment_count or 0) + (o.share_count or 0),
                "publish_time": o.publish_time.isoformat() if o.publish_time else None,
                "author": o.author or "",
            } for o in rows],
        }
    finally:
        db.close()


def handle_get_platform_spread(args: dict) -> dict:
    db = _make_db()
    try:
        kw = args["keyword"]
        rows = db.query(
            Opinion.source_platform,
            func.min(Opinion.publish_time).label("first_seen"),
            func.count(Opinion.id).label("cnt"),
        ).filter(Opinion.content.like(f"%{kw}%")).group_by(Opinion.source_platform).order_by("first_seen").all()

        total = sum(r.cnt for r in rows)
        spread = []
        for plat, first_dt, cnt in rows:
            spread.append({
                "platform": PLATFORM_MAP.get(plat, plat),
                "platform_code": plat,
                "first_seen": first_dt.isoformat() if first_dt else None,
                "count": cnt,
                "percentage": round(cnt / total * 100, 1) if total else 0,
            })

        return {"keyword": kw, "spread": spread, "total_platforms": len(spread),
                "first_platform": spread[0]["platform"] if spread else None}
    finally:
        db.close()


def handle_get_sentiment_trend(args: dict) -> dict:
    db = _make_db()
    try:
        start = datetime.strptime(args["start_date"], "%Y-%m-%d")
        end = datetime.strptime(args["end_date"], "%Y-%m-%d") + timedelta(days=1)
        kw = args["keyword"]

        rows = db.query(
            func.date(Opinion.publish_time).label("date"),
            func.avg(Opinion.sentiment_score).label("avg_score"),
            func.count(Opinion.id).label("cnt"),
        ).filter(
            Opinion.publish_time >= start, Opinion.publish_time < end,
            Opinion.content.like(f"%{kw}%"),
            Opinion.sentiment_score.isnot(None),
        ).group_by(func.date(Opinion.publish_time)).all()

        trend = [{"date": str(r.date), "avg_score": round(float(r.avg_score), 3), "count": r.cnt} for r in rows]
        overall_avg = sum(t["avg_score"] for t in trend) / len(trend) if trend else 0.5

        return {"keyword": kw, "trend": trend, "overall_avg_score": round(overall_avg, 3)}
    finally:
        db.close()


def handle_get_influencer_accounts(args: dict) -> dict:
    db = _make_db()
    try:
        kw = args["keyword"]
        threshold = args.get("min_interactions", 50)

        rows = db.query(
            Opinion.author,
            func.count(Opinion.id).label("post_count"),
            func.sum(Opinion.read_count).label("total_reads"),
            func.sum(Opinion.like_count + Opinion.comment_count + Opinion.share_count).label("total_interactions"),
            func.group_concat(func.distinct(Opinion.sentiment)).label("sentiments"),
        ).filter(
            Opinion.content.like(f"%{kw}%"),
            Opinion.author.isnot(None), Opinion.author != "",
        ).group_by(Opinion.author).having(
            func.sum(Opinion.like_count + Opinion.comment_count + Opinion.share_count) >= threshold,
        ).order_by(desc("total_interactions")).limit(20).all()

        accounts = []
        pos_count = 0
        for r in rows:
            sents = set((r.sentiments or "").split(","))
            is_pos = "positive" in sents and "negative" not in sents
            is_neg = "negative" in sents and "positive" not in sents
            if is_pos:
                pos_count += 1
            accounts.append({
                "author": r.author, "post_count": r.post_count,
                "total_reads": int(r.total_reads or 0),
                "total_interactions": int(r.total_interactions or 0),
                "sentiment_type": "正向" if is_pos else "负向" if is_neg else "中性/混合",
            })

        return {
            "keyword": kw, "accounts": accounts, "total": len(accounts),
            "positive_count": pos_count, "negative_count": len(accounts) - pos_count,
        }
    finally:
        db.close()


TOOL_HANDLERS = {
    "get_keyword_timeline": handle_get_keyword_timeline,
    "get_top_contents_by_period": handle_get_top_contents_by_period,
    "get_platform_spread": handle_get_platform_spread,
    "get_sentiment_trend": handle_get_sentiment_trend,
    "get_influencer_accounts": handle_get_influencer_accounts,
}


# ── Agent Loop ──

async def run_trace_agent(keyword: str) -> Optional[dict]:
    if not DEEPSEEK_API_KEY:
        logger.error("DEEPSEEK_API_KEY not set")
        return None

    now = datetime.now()
    user_msg = f"请追踪关键词「{keyword}」的完整事件脉络。请从该关键词最早出现的时间开始分析到当前时间（{now.strftime('%Y-%m-%d')}）。"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    report_content = None

    async with httpx.AsyncClient(timeout=120) as client:
        for turn in range(MAX_TOOL_TURNS):
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
                json={"model": DEEPSEEK_MODEL, "messages": messages, "tools": TOOLS, "temperature": 0.3},
            )
            resp.raise_for_status()
            body = resp.json()
            choice = body["choices"][0]
            msg = choice["message"]

            if choice["finish_reason"] == "stop" and not msg.get("tool_calls"):
                if msg.get("content"):
                    report_content = msg["content"]
                break

            if not msg.get("tool_calls"):
                messages.append(msg)
                continue

            tool_msgs = []
            for tc in msg["tool_calls"]:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])

                if func_name == "generate_trace_report":
                    report_content = func_args.get("report_content", "")
                    tool_msgs.append({"role": "tool", "tool_call_id": tc["id"], "content": "报告已生成。"})
                    break

                handler = TOOL_HANDLERS.get(func_name)
                if handler:
                    try:
                        result = handler(func_args)
                        tool_msgs.append({"role": "tool", "tool_call_id": tc["id"],
                            "content": json.dumps(result, ensure_ascii=False, default=str)})
                    except Exception as e:
                        logger.error("Tool %s error: %s", func_name, e)
                        tool_msgs.append({"role": "tool", "tool_call_id": tc["id"],
                            "content": json.dumps({"error": str(e)}, ensure_ascii=False)})

            messages.append(msg)
            messages.extend(tool_msgs)

            if report_content:
                break

    if not report_content:
        return None

    # Save to reports table
    db = _make_db()
    try:
        report = Report(
            title=f"事件脉络：{keyword}",
            content=report_content,
            report_type="trace",
            period_start=now - timedelta(days=90),
            period_end=now,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        result = report.to_dict()

        # 推送到微信
        sct_key = os.getenv("SCT_KEY", "")
        if sct_key:
            try:
                async with httpx.AsyncClient(timeout=15) as push:
                    await push.post(f"https://sctapi.ftqq.com/{sct_key}.send", data={
                        "title": f"事件脉络｜{keyword}",
                        "desp": report_content[:8000],
                    })
                logger.info("微信推送成功")
            except Exception as e:
                logger.warning("微信推送失败: %s", e)

        return result
    except Exception as e:
        db.rollback()
        logger.error("Failed to save trace report: %s", e)
        return None
    finally:
        db.close()
