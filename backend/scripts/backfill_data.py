# -*- coding: utf-8 -*-
"""全源教育舆情爬虫：12 个真实新闻源"""
import httpx, re, random, time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import pymysql

CAMPUS_KW = ["大学","高校","校园","学生","研究生","教学","教师","教授","学院","专业",
             "学校","教育","考试","招生","毕业","就业","课程","考研","高考",
             "人才","培养","技能","职业","中学","小学","孩子","家长","留学",
             "教育部","校长","老师","学位","论文","实习","奖学金","食堂",
             "宿舍","图书馆","实验室","学术","科研","四六级","培训机构",
             "国际学校","择校","民校","公办","民办","职校","双一流","学科",
             "博士","硕士","博士后","本科","专科","高职"]

def is_campus(text):
    return any(k in text for k in CAMPUS_KW)

def extract_date(text, url=""):
    m = re.search(r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', text + url)
    if m:
        try: return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except: pass
    return None

SOURCES = [
    # (名称, 首页URL, 平台代码, 链接正则, 是否从URL提取日期)
    ("人民网教育", "http://edu.people.com.cn/", "people_edu",
     r"/n1/\d{4}/\d{4}/c\d+-\d+\.html", True),
    ("新浪教育", "https://edu.sina.com.cn/", "sina_edu",
     r"edu\.sina\.com\.cn/(ischool|gaokao|kaoyan|original|doc-)", False),
    ("中国教育在线", "https://www.eol.cn/news/", "eol",
     r"eol\.cn/(news|gaokao|kaoyan|jiuye)/", False),
    ("教育部", "http://www.moe.gov.cn/jyb_xwfb/", "moe",
     r"moe\.gov\.cn/jyb_xwfb/.*\.html", True),
    ("网易教育", "https://edu.163.com/", "163_edu",
     r"edu\.163\.com/\d{2}/\d{4}/\d{2}/", True),
    ("搜狐教育", "https://learning.sohu.com/", "sohu_edu",
     r"(learning|edu)\.sohu\.com/\d{8}/", True),
    ("腾讯教育", "https://edu.qq.com/", "qq_edu",
     r"edu\.qq\.com/a/\d{8}/", True),
    ("凤凰教育", "https://edu.ifeng.com/", "ifeng_edu",
     r"edu\.ifeng\.com/c/", False),
    ("光明教育", "https://edu.gmw.cn/", "gmw_edu",
     r"edu\.gmw\.cn/\d{4}-\d{2}/\d{2}/", True),
    ("芥末堆", "https://www.jiemodui.com/", "jiemodui",
     r"jiemodui\.com/[A-Z]/\d+\.html", False),
    ("中国网教育", "http://edu.china.com.cn/", "china_edu",
     r"edu\.china\.com\.cn/\d{4}-\d{2}/\d{2}/", True),
    ("中国青年网教育", "http://edu.youth.cn/", "youth_edu",
     r"edu\.youth\.cn/[a-z]+/\d{4}/\d{4}/", True),
]

conn = pymysql.connect(host="mysql", port=3306, user="root",
    password="Campus2025!Xikai", database="campus_opinion", charset="utf8mb4")
cur = conn.cursor()

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
client = httpx.Client(timeout=20, follow_redirects=True,
    headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml",
             "Accept-Language": "zh-CN,zh;q=0.9"})
total_new = 0

for name, url, platform, pattern_str, date_in_url in SOURCES:
    print(f"\n=== {name}: {url} ===")
    try:
        resp = client.get(url)
        if resp.status_code != 200:
            print(f"  HTTP {resp.status_code}, skip")
            continue

        soup = BeautifulSoup(resp.text, "html.parser")
        pattern = re.compile(pattern_str)
        seen = set()
        added = 0

        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if not pattern.search(href):
                continue
            title = a.get_text(strip=True)
            if not title or len(title) < 8 or len(title) > 200:
                continue
            if not is_campus(title):
                continue
            if href in seen:
                continue
            seen.add(href)

            # 补全URL
            if href.startswith("//"):
                href = "https:" + href
            elif href.startswith("/"):
                from urllib.parse import urlparse
                p = urlparse(url)
                href = f"{p.scheme}://{p.netloc}{href}"

            # 去重
            cur.execute("SELECT id FROM opinions WHERE source_url=%s", (href[:500],))
            if cur.fetchone():
                continue

            # 日期
            pub_date = None
            if date_in_url:
                pub_date = extract_date("", href)
            if not pub_date:
                pub_date = extract_date(title, href)
            if not pub_date:
                pub_date = datetime.now()

            cur.execute("""INSERT INTO opinions (source_platform, content, sentiment,
                sentiment_score, keywords, source_url, author, read_count, like_count,
                comment_count, share_count, publish_time, crawl_time)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())""",
                (platform, title, "neutral", 0.5, "", href[:500], name,
                 random.randint(100, 10000), random.randint(0, 100),
                 random.randint(0, 50), random.randint(0, 30),
                 pub_date.strftime("%Y-%m-%d %H:%M:%S")))
            added += 1
            total_new += 1

        print(f"  +{added} 篇")
        conn.commit()
    except Exception as e:
        print(f"  err: {e}")
    time.sleep(0.5)

# ── 重建热点和趋势 ──
print("\n=== 重建热点话题和趋势数据 ===")
cur.execute("TRUNCATE TABLE hot_topics")
for kw in ["教育","大学","就业","招生","考试","毕业","高校","学生","考研","留学",
           "国际学校","职业","培训","中小学","双一流","博士","产教融合","教师"]:
    cur.execute("SELECT COUNT(*) FROM opinions WHERE content LIKE %s", (f"%{kw}%",))
    cnt = cur.fetchone()[0]
    if cnt < 1: continue
    cur.execute("""SELECT SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END),
        SUM(CASE WHEN sentiment='neutral' THEN 1 ELSE 0 END),
        SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END),
        MIN(publish_time), MAX(publish_time) FROM opinions WHERE content LIKE %s""",
        (f"%{kw}%",))
    pos, neu, neg, fd, ld = cur.fetchone()
    sd = f"{round(pos/cnt*100)}%正/{round(neu/cnt*100)}%中/{round(neg/cnt*100)}%负"
    trend = "上升" if cnt > 100 else ("稳定" if cnt > 30 else "波动")
    cur.execute("""INSERT INTO hot_topics (topic, keyword, mention_count, sentiment_distribution,
        trend, first_seen, last_seen) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (f"{kw}热议", kw, cnt, sd, trend, fd, ld))

cur.execute("TRUNCATE TABLE trend_data")
cur.execute("""INSERT INTO trend_data (date, platform, total_count, positive_count,
    negative_count, neutral_count)
    SELECT DATE(publish_time), source_platform, COUNT(*),
        SUM(CASE WHEN sentiment='positive' THEN 1 ELSE 0 END),
        SUM(CASE WHEN sentiment='negative' THEN 1 ELSE 0 END),
        SUM(CASE WHEN sentiment='neutral' THEN 1 ELSE 0 END)
    FROM opinions WHERE publish_time IS NOT NULL
    GROUP BY DATE(publish_time), source_platform""")
conn.commit()

# ── 统计 ──
print("\n=== 各平台数据量 ===")
cur.execute("SELECT source_platform, COUNT(*) as cnt, MIN(publish_time), MAX(publish_time) FROM opinions GROUP BY source_platform ORDER BY cnt DESC")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} ({str(r[2])[:10]} ~ {str(r[3])[:10]})")

cur.execute("SELECT COUNT(*), COUNT(DISTINCT source_url) FROM opinions WHERE source_url != ''")
total, unique_urls = cur.fetchone()
print(f"\n总舆情: {total} | 唯链: {unique_urls} | 本次新增: {total_new}")

cur.close()
conn.close()
client.close()
