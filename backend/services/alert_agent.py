# -*- coding: utf-8 -*-
"""实时监控告警 Agent —— 自主巡检 → 异常检测 → 联动报告/脉络 → 分级推送"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import httpx
from sqlalchemy import func, desc

from db.mysql_config import SessionLocal
from models.mysql_models import Opinion, HotTopic, AlertRecord

logger = logging.getLogger(__name__)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"
MAX_TOOL_TURNS = 15

SCT_KEY = os.getenv("SCT_KEY", "")

PLATFORM_MAP = {
    "weibo": "微博", "wechat": "微信", "zhihu": "知乎",
    "douyin": "抖音", "xiaohongshu": "小红书", "bilibili": "B站",
    "toutiao": "头条", "people_edu": "人民网", "sina_edu": "新浪教育",
    "eol": "中国教育在线",
}

SENSITIVE_KEYWORDS = {
    "red": ["集体罢课", "学生死亡", "校园安全事故", "食品安全事故", "教师性侵",
            "学术造假曝光", "招生舞弊", "学生自杀", "校园暴力致死"],
    "orange": ["罢课", "集体抗议", "食堂中毒", "食物中毒", "校园欺凌",
               "教师不当言论", "学术不端", "泄题", "作弊丑闻"],
    "yellow": ["投诉", "举报", "维权", "争议", "不满", "质疑", "抗议",
               "安全隐患", "管理混乱", "乱收费"],
}

SYSTEM_PROMPT = """你是一名高校网络舆情监控中心的值班分析师。你的核心任务是：**实时监控校园舆情数据流，识别异常信号，需要时联动报告生成与事件溯源进行深度研判，最终输出分级预警并推送至微信**。

# 核心原则

- 你有完整的数据查询工具，可以自主决定检查哪些维度的数据。
- 当初步扫描发现异常时，你可以**触发报告 Agent 生成即时报告**和**触发事件脉络 Agent 追溯话题生命周期**，基于两者的输出做综合研判。
- 预警等级严格按照标准判定，不得人为升高或降低。
- 每一条预警消息必须包含：异常现象描述、数据证据、风险等级、研判依据、处置建议。
- 不得在未确认异常时推送预警，不得在推送预警后重复推送同一条异常。
- 如果某个维度的数据查询失败，应在预警中如实说明数据缺失。

# 预警等级标准

| 等级 | 判定条件 | 响应要求 |
|------|---------|---------|
| 绿 | 所有指标在基线范围内 | 不推送，仅记录 |
| 黄 | 单项指标超出阈值 < 50%，或命中黄级敏感词 | 推送关注提醒，建议人工复核 |
| 橙 | 多项指标同时超出阈值，或负面占比 > 50%，或命中橙级敏感词 | 触发报告 Agent 生成即时分析，连同预警一并推送 |
| 红 | 负面占比 > 65%，或阅读/评论量暴涨 > 300%，或命中红级敏感词 | 触发报告 Agent + 事件脉络 Agent，立即推送紧急预警 |

# 检查维度

1. **舆论总量异常**：当日新增量较过去7日均值偏离 > 标准差×2
2. **负面情感占比**：> 35%黄，> 50%橙，> 65%红
3. **敏感关键词命中**：按词库等级对应预警等级
4. **热点话题爆发**：话题mention_count在短时间内增长 > 过去24小时的50%
5. **多平台同步异常**：同一话题同时在3+平台出现热度上升
6. **高互动异常**：单条舆论评论+转发 > 过去3日均值×5

# 工作流程

1. 拉取基线数据 → 2. 扫描当前窗口 → 3. 对比判定 → 4. 去重检查 → 5. 联动深度分析 → 6. 综合研判推送

# 约束
- 必须先调 get_baseline_stats 获取基线
- 未确认异常不调 push_wechat_alert
- 橙级必须调 trigger_report_agent
- 红级必须同时调 trigger_report_agent 和 trigger_trace_agent
- 所有数值来自工具返回的真实数据
- 数据不足输出 {"status": "insufficient_data"}，不推送"""

TOOLS = [
    {
        "type": "function", "function": {
            "name": "get_baseline_stats",
            "description": "查询过去N天的舆情基线统计：日均总量、情感分布均值、标准差",
            "parameters": {"type": "object", "properties": {"days": {"type": "integer", "description": "基线天数，默认7"}}, "required": []},
        },
    },
    {
        "type": "function", "function": {
            "name": "get_recent_window",
            "description": "查询最近N分钟的新增舆情数据",
            "parameters": {"type": "object", "properties": {"minutes": {"type": "integer", "description": "时间窗口，默认30"}, "platform": {"type": "string"}, "sentiment_filter": {"type": "string"}}, "required": []},
        },
    },
    {
        "type": "function", "function": {
            "name": "get_sensitive_keywords",
            "description": "查询敏感词库及其等级配置",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function", "function": {
            "name": "check_recent_alerts",
            "description": "查询最近N小时内已推送的预警记录用于去重",
            "parameters": {"type": "object", "properties": {"hours": {"type": "integer", "description": "查询小时数，默认1"}}, "required": []},
        },
    },
    {
        "type": "function", "function": {
            "name": "get_topic_burst",
            "description": "检测热点话题的短期增长速率，返回爆发指数",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function", "function": {
            "name": "trigger_report_agent",
            "description": "触发报告Agent生成即时舆情分析报告，返回报告摘要",
            "parameters": {"type": "object", "properties": {"keyword": {"type": "string", "description": "分析关键词"}, "days": {"type": "integer", "description": "统计天数，默认3"}}, "required": ["keyword"]},
        },
    },
    {
        "type": "function", "function": {
            "name": "trigger_trace_agent",
            "description": "触发事件脉络Agent追溯话题生命周期，返回脉络摘要",
            "parameters": {"type": "object", "properties": {"keyword": {"type": "string", "description": "追踪关键词"}}, "required": ["keyword"]},
        },
    },
    {
        "type": "function", "function": {
            "name": "push_wechat_alert",
            "description": "推送预警消息到微信（Server酱）。仅确认异常后调用。",
            "parameters": {"type": "object", "properties": {"title": {"type": "string", "description": "预警标题，含等级标签"}, "content": {"type": "string", "description": "完整预警正文"}, "level": {"type": "string", "enum": ["yellow", "orange", "red"]}}, "required": ["title", "content", "level"]},
        },
    },
]


def _make_db():
    return SessionLocal()


# ── Tool Handlers ──

def handle_get_baseline_stats(args: dict) -> dict:
    db = _make_db()
    try:
        days = args.get("days", 7)
        end = datetime.now()
        start = end - timedelta(days=days)
        rows = db.query(
            func.date(Opinion.publish_time).label("date"),
            Opinion.sentiment,
            func.count(Opinion.id).label("cnt"),
        ).filter(Opinion.publish_time >= start, Opinion.publish_time < end).group_by(
            func.date(Opinion.publish_time), Opinion.sentiment).all()

        daily = {}
        for r in rows:
            d = str(r.date)
            if d not in daily:
                daily[d] = {"positive": 0, "negative": 0, "neutral": 0}
            daily[d][r.sentiment] = r.cnt

        totals = [sum(v.values()) for v in daily.values()]
        neg_pcts = [v["negative"] / sum(v.values()) * 100 if sum(v.values()) > 0 else 0 for v in daily.values()]

        avg_total = sum(totals) / len(totals) if totals else 0
        std_total = (sum((t - avg_total) ** 2 for t in totals) / len(totals)) ** 0.5 if totals else 0
        avg_neg = sum(neg_pcts) / len(neg_pcts) if neg_pcts else 0

        return {"days": days, "daily_totals": totals, "avg_daily_total": round(avg_total, 1),
                "std_daily_total": round(std_total, 1), "avg_negative_pct": round(avg_neg, 1),
                "threshold_total_high": round(avg_total + std_total * 2, 1)}
    finally:
        db.close()


def handle_get_recent_window(args: dict) -> dict:
    db = _make_db()
    try:
        minutes = args.get("minutes", 30)
        start = datetime.now() - timedelta(minutes=minutes)
        q = db.query(Opinion).filter(Opinion.publish_time >= start)
        if args.get("platform"):
            q = q.filter(Opinion.source_platform == args["platform"])
        if args.get("sentiment_filter"):
            q = q.filter(Opinion.sentiment == args["sentiment_filter"])

        total = q.count()
        sentiments = q.with_entities(Opinion.sentiment, func.count(Opinion.id)).group_by(Opinion.sentiment).all()
        dist = {"positive": 0, "negative": 0, "neutral": 0}
        for s, c in sentiments:
            if s in dist: dist[s] = c

        top_items = q.order_by(desc(Opinion.read_count + Opinion.like_count + Opinion.comment_count)).limit(5).all()

        return {"minutes": minutes, "total_new": total, "sentiment_distribution": dist,
                "negative_pct": round(dist["negative"] / total * 100, 1) if total else 0,
                "positive_pct": round(dist["positive"] / total * 100, 1) if total else 0,
                "top_contents": [{"content": o.content[:100], "platform": PLATFORM_MAP.get(o.source_platform, o.source_platform),
                                   "sentiment": o.sentiment, "read_count": o.read_count or 0,
                                   "interactions": (o.like_count or 0) + (o.comment_count or 0) + (o.share_count or 0),
                                   "time": o.publish_time.isoformat() if o.publish_time else None} for o in top_items]}
    finally:
        db.close()


def handle_get_sensitive_keywords(args: dict) -> dict:
    return {"keywords": SENSITIVE_KEYWORDS, "total_red": len(SENSITIVE_KEYWORDS["red"]),
            "total_orange": len(SENSITIVE_KEYWORDS["orange"]), "total_yellow": len(SENSITIVE_KEYWORDS["yellow"])}


def handle_check_recent_alerts(args: dict) -> dict:
    db = _make_db()
    try:
        hours = args.get("hours", 1)
        since = datetime.now() - timedelta(hours=hours)
        alerts = db.query(AlertRecord).filter(AlertRecord.created_at >= since).all()
        return {"recent_alerts": [{"title": a.title, "level": a.alert_level, "time": a.created_at.isoformat() if a.created_at else None,
                                    "description": (a.description or "")[:120]} for a in alerts], "count": len(alerts)}
    finally:
        db.close()


def handle_get_topic_burst(args: dict) -> dict:
    db = _make_db()
    try:
        topics = db.query(HotTopic).order_by(desc(HotTopic.mention_count)).limit(15).all()
        burst_list = []
        for t in topics:
            burst_score = t.mention_count or 0
            trend = t.trend or "稳定"
            if burst_score > 500:
                risk = "high"
            elif burst_score > 100:
                risk = "medium"
            else:
                risk = "low"
            burst_list.append({"topic": t.topic, "mention_count": burst_score, "trend": trend,
                               "sentiment": t.sentiment_distribution, "risk": risk})
        return {"topics": burst_list, "high_risk_count": sum(1 for b in burst_list if b["risk"] == "high")}
    finally:
        db.close()


async def handle_trigger_report_agent(args: dict) -> dict:
    """调用报告 Agent"""
    from services.report_agent import run_report_agent
    try:
        result = await run_report_agent(report_type="manual")
        if result and result.get("content"):
            return {"status": "success", "report_id": result["id"],
                    "summary": result["content"][:600], "title": result["title"]}
        return {"status": "failed", "reason": "报告生成失败"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


async def handle_trigger_trace_agent(args: dict) -> dict:
    """调用事件脉络 Agent"""
    from services.trace_agent import run_trace_agent
    try:
        keyword = args.get("keyword", "")
        if not keyword:
            return {"status": "failed", "reason": "未指定关键词"}
        result = await run_trace_agent(keyword)
        if result and result.get("content"):
            return {"status": "success", "trace_id": result["id"],
                    "summary": result["content"][:600], "title": result["title"]}
        return {"status": "failed", "reason": "脉络分析失败"}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def handle_push_wechat_alert(args: dict) -> dict:
    """推送预警到微信 + 记录到 DB"""
    title = args.get("title", "舆情预警")
    content = args.get("content", "")
    level = args.get("level", "yellow")

    # 推送微信
    if SCT_KEY:
        import httpx as sync_httpx
        try:
            with sync_httpx.Client(timeout=15) as client:
                r = client.post(f"https://sctapi.ftqq.com/{SCT_KEY}.send",
                                data={"title": title, "desp": content[:8000]})
                logger.info("预警推送微信: %s (HTTP %d)", title, r.status_code)
        except Exception as e:
            logger.warning("预警推送微信失败: %s", e)

    # 记录到 DB
    db = _make_db()
    try:
        alert = AlertRecord(alert_type="monitor", alert_level=level, title=title,
                           description=content[:500], trigger_condition="agent_scan",
                           created_at=datetime.now())
        db.add(alert)
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("预警记录保存失败: %s", e)
    finally:
        db.close()

    return {"status": "sent", "title": title, "level": level, "time": datetime.now().isoformat()}


# ── Agent Loop ──

async def run_alert_agent() -> Optional[dict]:
    if not DEEPSEEK_API_KEY:
        logger.error("DEEPSEEK_API_KEY not set")
        return None

    now = datetime.now()
    user_msg = f"请执行一次完整的舆情巡检。当前时间：{now.strftime('%Y-%m-%d %H:%M')}。请按流程：基线→扫描→判定→去重→深度分析→推送。"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]

    final_result = None

    async with httpx.AsyncClient(timeout=180) as client:
        for turn in range(MAX_TOOL_TURNS):
            resp = await client.post(
                f"{DEEPSEEK_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
                json={"model": DEEPSEEK_MODEL, "messages": messages, "tools": TOOLS, "temperature": 0.2},
            )
            resp.raise_for_status()
            body = resp.json()
            choice = body["choices"][0]
            msg = choice["message"]

            if choice["finish_reason"] == "stop" and not msg.get("tool_calls"):
                final_result = {"status": "completed", "summary": msg.get("content", "")}
                break

            if not msg.get("tool_calls"):
                messages.append(msg)
                continue

            tool_msgs = []
            for tc in msg["tool_calls"]:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])

                if func_name == "trigger_report_agent":
                    result = await handle_trigger_report_agent(func_args)
                elif func_name == "trigger_trace_agent":
                    result = await handle_trigger_trace_agent(func_args)
                elif func_name == "push_wechat_alert":
                    result = handle_push_wechat_alert(func_args)
                else:
                    handler = {
                        "get_baseline_stats": handle_get_baseline_stats,
                        "get_recent_window": handle_get_recent_window,
                        "get_sensitive_keywords": handle_get_sensitive_keywords,
                        "check_recent_alerts": handle_check_recent_alerts,
                        "get_topic_burst": handle_get_topic_burst,
                    }.get(func_name)
                    try:
                        result = handler(func_args) if handler else {"error": f"Unknown tool: {func_name}"}
                    except Exception as e:
                        result = {"error": str(e)}

                tool_msgs.append({"role": "tool", "tool_call_id": tc["id"],
                                  "content": json.dumps(result, ensure_ascii=False, default=str)})

                if func_name == "push_wechat_alert":
                    final_result = result

            messages.append(msg)
            messages.extend(tool_msgs)

    return final_result or {"status": "completed", "summary": "巡检完成，无异常"}
