# -*- coding: utf-8 -*-
"""
生成有故事线的Demo数据集 — 30天 + 6个热点事件 + 趋势曲线

用法：
    python generate_demo_data.py                          # 正常生成并写入
    python generate_demo_data.py --dry-run                 # 只打印统计，不动数据库
    python generate_demo_data.py --batch-size 1000         # 每批插入1000条
    python generate_demo_data.py --env-file /path/.env     # 指定 .env 路径
"""
import sys, os, random, time, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

import pymysql
from datetime import datetime, timedelta
from collections import defaultdict
from ml.bert_sentiment import get_bert_analyzer
from dotenv import load_dotenv

# ---- 数据库连接从环境变量读取（不硬编码）----
def get_db_config():
    """从环境变量获取数据库连接信息"""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', '3306')),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', 'campus_opinion'),
        'charset': 'utf8mb4',
    }


# ============================================================
# 6个热点事件定义：每个有明确的时间线和情感倾向
# ============================================================
EVENTS = [
    {
        "topic": "食堂涨价风波",
        "keyword": "食堂涨价",
        "days": (3, 12),   # 爆发在第3天，消失在第12天
        "peak_day": 7,     # 第7天达到峰值
        "sentiment": "negative",
        "base_daily": 80,  # 基础日产量
        "peak_multiplier": 5,
        "desc": "学校食堂突然涨价引发学生不满",
        "platforms": ["weibo", "wechat", "zhihu"],
    },
    {
        "topic": "图书馆扩建计划",
        "keyword": "图书馆扩建",
        "days": (5, 18),
        "peak_day": 10,
        "sentiment": "positive",
        "base_daily": 60,
        "peak_multiplier": 4,
        "desc": "校方宣布投资5000万扩建图书馆，学生热议",
        "platforms": ["weibo", "zhihu", "sina"],
    },
    {
        "topic": "期末考试安排争议",
        "keyword": "期末考安排",
        "days": (10, 22),
        "peak_day": 15,
        "sentiment": "negative",
        "base_daily": 100,
        "peak_multiplier": 6,
        "desc": "期末考试连续排考引发学生集体抗议",
        "platforms": ["weibo", "wechat", "zhihu", "sina"],
    },
    {
        "topic": "校园网大面积故障",
        "keyword": "校园网络",
        "days": (15, 25),
        "peak_day": 20,
        "sentiment": "negative",
        "base_daily": 70,
        "peak_multiplier": 5,
        "desc": "校园网反复断网，在线考试和选课受影响",
        "platforms": ["weibo", "wechat", "zhihu"],
    },
    {
        "topic": "奖学金评选质疑",
        "keyword": "奖学金内定",
        "days": (18, 28),
        "peak_day": 23,
        "sentiment": "negative",
        "base_daily": 90,
        "peak_multiplier": 7,
        "desc": "学生质疑奖学金评选存在关系户黑幕操作",
        "platforms": ["weibo", "zhihu", "sina", "wechat"],
    },
    {
        "topic": "校运动会盛况",
        "keyword": "校运会",
        "days": (22, 30),
        "peak_day": 25,
        "sentiment": "positive",
        "base_daily": 120,
        "peak_multiplier": 3,
        "desc": "一年一度校运动会开幕，各院系比拼精彩纷呈",
        "platforms": ["weibo", "wechat", "sina", "zhihu", "eol"],
    },
]

# ============================================================
# 日常背景舆情模板 (中性为主)
# ============================================================
BACKGROUND_POSITIVE = [
    ("{author}觉得{detail}", "positive"),
    ("今天{dept}{detail}，{comment}", "positive"),
    ("{place}新来了{staff}，{comment}", "positive"),
    ("学校{dept}效率提高了，{comment}", "positive"),
]

BACKGROUND_NEGATIVE = [
    ("{place}的{issue}又出现了，{comment}", "negative"),
    ("{dept}的服务态度真的{comment}", "negative"),
    ("{author}吐槽{place}的{issue}", "negative"),
]

BACKGROUND_NEUTRAL = [
    ("{dept}通知：{notice}", "neutral"),
    ("关于{notice}的公告已发布", "neutral"),
    ("{author}分享了{share}", "neutral"),
    ("{dept}发布{subject}相关信息", "neutral"),
    ("学校发布{notice}通知", "neutral"),
]

POS_DETAIL = ["天气很好适合运动", "今天食堂饭菜不错", "图书馆自习效率高", "和同学打球很开心", "校园花开得很漂亮", "老师讲课很生动", "社团活动很有趣"]
NEG_DETAIL = ["又停水了", "网速太慢", "等了好久才排到", "态度很不好", "设备又坏了", "通知太晚了"]
NEU_DETAIL = ["选课通知已发布", "考试安排公布", "收费标准调整", "宿舍检查通知", "社团招新公告", "学术讲座通知"]

POS_COMMENT = ["心情很好", "值得点赞", "继续保持", "真不错"]
NEG_COMMENT = ["让人无语", "需要改进", "希望重视", "太差劲了"]
NEU_COMMENT = ["请关注", "互相转告", "注意查看", "按时完成"]

PLACES = ["图书馆", "食堂", "教学楼", "宿舍", "体育馆", "实验楼", "学生活动中心"]
DEPTS = ["教务处", "学生处", "后勤部", "信息中心", "图书馆", "招生办"]
AUTHORS = ["小明", "小红", "大三学长", "新生一枚", "考研党", "某同学", "匿名"]

# ============================================================
# 按事件生成舆情内容
# ============================================================
def event_opinion(event, day, sentiment_type):
    """为特定事件生成一条舆情"""
    t = event["topic"]
    if sentiment_type == "negative":
        neg_comments = [
            f"{t}真的太过分了，学校不考虑学生感受吗？",
            f"实在受不了{t}了，已经影响到正常生活了。",
            f"关于{t}，大家怎么看？我觉得很不合理。",
            f"{t}这件事希望学校能给个说法。",
            f"已经投诉了{t}的问题，但一直没回复。",
            f"{t}什么时候才能解决？每天都很困扰。",
            f"强烈抗议{t}，要求学校重视学生权益！",
            f"又是因为{t}，今天又白跑一趟，气死了。",
            f"{t}不是第一次了，每次都这样，无语。",
            f"和同学讨论了一下{t}，大家都觉得不公平。",
        ]
        return random.choice(neg_comments)
    elif sentiment_type == "positive":
        pos_comments = [
            f"{t}真的很期待，希望能早日实现！",
            f"支持{t}，这对我们学生来说是好消息。",
            f"关于{t}，看到学校在认真推进，点赞！",
            f"{t}的进展让人振奋，期待后续发展。",
            f"终于等到{t}了，学校这次做得很对。",
            f"为{t}点赞，这对学校发展很有帮助。",
            f"{t}这个决定很明智，学生们都很支持。",
            f"听说{t}要落实了，大家都很高兴。",
            f"{t}的消息太好了，转发给同学们看看。",
            f"感谢学校在{t}上的努力，我们很满意。",
        ]
        return random.choice(pos_comments)
    else:
        neu_comments = [
            f"关于{t}的最新消息，大家关注一下。",
            f"有人了解{t}的具体情况吗？",
            f"{t}的后续发展待观察，保持关注。",
            f"转发了{t}相关通知，需要的同学自取。",
            f"关于{t}的一些个人看法，仅供参考。",
        ]
        return random.choice(neu_comments)


def background_opinion(sentiment_type):
    """生成日常背景舆情"""
    if sentiment_type == "positive":
        tmpl = random.choice(BACKGROUND_POSITIVE)[0]
        return tmpl.format(
            author=random.choice(AUTHORS), detail=random.choice(POS_DETAIL),
            dept=random.choice(DEPTS), place=random.choice(PLACES),
            staff=random.choice(["新管理员", "维修师傅", "保洁阿姨", "值班老师"]),
            comment=random.choice(POS_COMMENT),
        )
    elif sentiment_type == "negative":
        tmpl = random.choice(BACKGROUND_NEGATIVE)[0]
        return tmpl.format(
            author=random.choice(AUTHORS), place=random.choice(PLACES),
            issue=random.choice(NEG_DETAIL), dept=random.choice(DEPTS),
            comment=random.choice(NEG_COMMENT),
        )
    else:
        tmpl = random.choice(BACKGROUND_NEUTRAL)[0]
        return tmpl.format(
            dept=random.choice(DEPTS), notice=random.choice(NEU_DETAIL),
            author=random.choice(AUTHORS), share=random.choice(NEU_DETAIL),
            subject=random.choice(["课程", "考试", "选课", "缴费", "住宿"]),
        )


# ============================================================
# 主流程
# ============================================================
def get_db_connection(db_config):
    """创建数据库连接（带重试）"""
    try:
        conn = pymysql.connect(**db_config)
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        print(f"   主机: {db_config['host']}:{db_config['port']}")
        print(f"   数据库: {db_config['database']}")
        print(f"   用户: {db_config['user']}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="生成校园舆情Demo数据集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只打印统计信息，不操作数据库",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=500,
        help="每批插入多少条记录（默认 500）",
    )
    parser.add_argument(
        "--env-file",
        default=None,
        help=".env 文件路径",
    )
    args = parser.parse_args()

    # 尝试加载 .env 文件
    if args.env_file:
        if os.path.exists(args.env_file):
            load_dotenv(args.env_file)
            print(f"📁 已加载环境变量: {args.env_file}")
        else:
            print(f"⚠️ .env 文件不存在: {args.env_file}，仅使用系统环境变量")
    else:
        # 自动查找 .env
        for p in [os.path.join(os.path.dirname(__file__), ".env"),
                  os.path.join(os.path.dirname(__file__), "..", ".env")]:
            if os.path.exists(p):
                load_dotenv(p)
                print(f"📁 已自动加载: {p}")
                break

    batch_size = args.batch_size
    db_config = get_db_config()
    print(f"📊 数据库: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    if args.dry_run:
        print("🏁 DRY RUN 模式 — 不会执行任何写操作")
    print("=" * 60)
    print("生成Demo数据集: 30天 + 6个热点事件 + 趋势曲线")
    print("=" * 60)

    if not args.dry_run:
        conn = get_db_connection(db_config)
        cur = conn.cursor()

        # 清理旧数据
        print("\n[1/4] 清理旧数据...")
        cur.execute("DELETE FROM opinions")
        cur.execute("DELETE FROM hot_topics")
        cur.execute("DELETE FROM trend_data")
        cur.execute("DELETE FROM crawler_logs")
        conn.commit()
        print("      旧数据已清除")
    else:
        print("\n[DRY-RUN] 跳过清理旧数据（不会操作数据库）")
        conn = None
        cur = None

    # 加载BERT
    print("\n[2/4] 加载BERT模型...")
    analyzer = get_bert_analyzer()
    if not analyzer.ready:
        print("错误: BERT未就绪")
        return

    # 生成30天数据
    print("\n[3/4] 生成30天舆情数据...")
    today = datetime.now()
    all_opinions = []   # (content, sentiment, score, day_index)
    daily_stats = defaultdict(lambda: {"positive": 0, "negative": 0, "neutral": 0, "total": 0})

    for day in range(1, 31):
        day_opinions = []
        day_date = today - timedelta(days=30 - day)

        # 1) 当日活跃事件的舆情
        for ev in EVENTS:
            if ev["days"][0] <= day <= ev["days"][1]:
                # 计算当日产量 (基于峰值曲线)
                distance = abs(day - ev["peak_day"])
                span = ev["days"][1] - ev["days"][0]
                if distance <= span / 3:
                    mult = ev["peak_multiplier"] - (distance / (span / 3)) * (ev["peak_multiplier"] - 1)
                else:
                    mult = 1 + (ev["peak_multiplier"] - 1) * (span - distance) / (span * 2 / 3)
                count = max(5, int(ev["base_daily"] * mult))

                # 事件的情感分布
                if ev["sentiment"] == "positive":
                    pos_r, neg_r, neu_r = 0.70, 0.10, 0.20
                elif ev["sentiment"] == "negative":
                    pos_r, neg_r, neu_r = 0.10, 0.70, 0.20
                else:
                    pos_r, neg_r, neu_r = 0.15, 0.15, 0.70

                for _ in range(count):
                    r = random.random()
                    if r < pos_r:
                        sent = "positive"
                    elif r < pos_r + neg_r:
                        sent = "negative"
                    else:
                        sent = "neutral"
                    content = event_opinion(ev, day, sent)
                    day_opinions.append((content, sent, day_date, ev["keyword"]))

        # 2) 日常背景舆情 (每天200-400条)
        bg_count = random.randint(200, 400)
        for _ in range(bg_count):
            r = random.random()
            if r < 0.18:
                sent = "positive"
            elif r < 0.25:
                sent = "negative"
            else:
                sent = "neutral"
            content = background_opinion(sent)
            day_opinions.append((content, sent, day_date, None))

        # BERT重新预测这一天所有舆情的真实情感
        texts = [o[0] for o in day_opinions]
        results = analyzer.batch_predict(texts)

        for (content, _, date, keyword), result in zip(day_opinions, results):
            all_opinions.append((content, result["sentiment"], result["score"], date, keyword))
            daily_stats[date.strftime("%Y-%m-%d")][result["sentiment"]] += 1
            daily_stats[date.strftime("%Y-%m-%d")]["total"] += 1

        print(f"  第{day:2d}天: {len(day_opinions)} 条 | {date.strftime('%Y-%m-%d')} | 累计 {len(all_opinions)}")

    print(f"\n      共生成 {len(all_opinions)} 条舆情数据")

    # 统计
    total_pos = sum(1 for o in all_opinions if o[1] == "positive")
    total_neg = sum(1 for o in all_opinions if o[1] == "negative")
    total_neu = sum(1 for o in all_opinions if o[1] == "neutral")
    print(f"      分布: POS={total_pos} NEG={total_neg} NEU={total_neu}")

    if args.dry_run:
        print("\n🏁 DRY RUN — 数据库写入已跳过")
        print()
        for ev in EVENTS:
            print(f"  - {ev['topic']}: 第{ev['days'][0]}-{ev['days'][1]}天 (峰值第{ev['peak_day']}天, {ev['sentiment']})")
        print(f"\n预计插入 {len(all_opinions)} 条数据到数据库")
        print(f"  opinions:    {len(all_opinions)} 条")
        print(f"  hot_topics:  {len(EVENTS)} 条")
        print(f"  trend_data:  30 条")
        print(f"  batch_size:  {batch_size}")
        print("🏁 DRY RUN 完成 — 数据库未受影响")
        return

    # ============================================================
    # 写入MySQL
    # ============================================================
    print(f"\n[4/4] 写入数据库 (batch_size={batch_size})...")

    platforms = ["weibo", "wechat", "zhihu", "sina", "eol", "gaokao", "youth", "sohu"]
    inserted = 0

    for content, sentiment, score, pub_date, keyword in all_opinions:
        title = content[:80]
        plat = random.choice(platforms)
        author = random.choice(["校园观察员", "学生小明", "匿名用户", "热心同学", "校园达人", "在校生", "考研党", "大一新生"])
        crawl_time = datetime.now()
        cur.execute(
            "INSERT INTO opinions (title, content, source_platform, author, publish_time, crawl_time, sentiment, sentiment_score, keywords) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            (title, content, plat, author, pub_date, crawl_time, sentiment, score, keyword or content[:30])
        )
        inserted += 1
        if inserted % batch_size == 0:
            conn.commit()
            print(f"  已写入 {inserted} 条...")
    conn.commit()

    # ============================================================
    # 生成热点话题 (从事件中派生)
    # ============================================================
    print("  生成热点话题...")
    for ev in EVENTS:
        cur.execute(
            "INSERT INTO hot_topics (topic, keyword, mention_count, sentiment_distribution, trend, first_seen, last_seen) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (ev["topic"], ev["keyword"],
             int(ev["base_daily"] * ev["peak_multiplier"] * 5),
             '{"positive":15,"negative":70,"neutral":15}' if ev["sentiment"] == "negative" else '{"positive":70,"negative":5,"neutral":25}',
             "rising" if ev["peak_day"] > 15 else "falling",
             today - timedelta(days=30 - ev["days"][0]),
             today - timedelta(days=30 - ev["days"][1]))
        )
    conn.commit()

    # ============================================================
    # 生成趋势数据 (每日汇总)
    # ============================================================
    print("  生成趋势数据...")
    for day in range(1, 31):
        date = today - timedelta(days=30 - day)
        date_str = date.strftime("%Y-%m-%d")
        stats = daily_stats[date_str]
        cur.execute(
            "INSERT INTO trend_data (date, platform, total_count, positive_count, negative_count, neutral_count) VALUES (%s,%s,%s,%s,%s,%s)",
            (date, "all", stats["total"], stats["positive"], stats["negative"], stats["neutral"])
        )
    conn.commit()

    cur.execute("SELECT COUNT(*) FROM opinions")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    # ============================================================
    # 最终统计
    # ============================================================
    print(f"\n{'='*60}")
    print(f"Demo数据集生成完毕")
    print(f"{'='*60}")
    print(f"总数据量:    {total} 条")
    print(f"正面舆情:    {total_pos} 条 ({total_pos/total*100:.1f}%)")
    print(f"负面舆情:    {total_neg} 条 ({total_neg/total*100:.1f}%)")
    print(f"中性舆情:    {total_neu} 条 ({total_neu/total*100:.1f}%)")
    print(f"热点话题:    6 个")
    print(f"趋势数据:    30 天")
    print(f"时间跨度:    {(today - timedelta(days=29)).strftime('%Y-%m-%d')} ~ {today.strftime('%Y-%m-%d')}")
    print(f"批量大小:    {batch_size}")
    for ev in EVENTS:
        print(f"  - {ev['topic']}: 第{ev['days'][0]}-{ev['days'][1]}天 (峰值第{ev['peak_day']}天, {ev['sentiment']})")


if __name__ == "__main__":
    main()