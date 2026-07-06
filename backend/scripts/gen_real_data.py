"""生成真实中文校园舆情数据"""

import random
from datetime import datetime, timedelta

start_date = datetime(2025, 9, 1)
end_date = datetime(2026, 7, 1)
days = (end_date - start_date).days

platforms = ["微博", "微信", "知乎", "抖音", "小红书", "B站", "头条"]
sentiments = ["positive", "negative", "neutral"]

# 正面舆情模板
positive_templates = [
    "新装修的{kw}太棒了，环境焕然一新，同学们都很满意！",
    "今天去{kw}体验很好，工作人员服务态度特别热情。",
    "学校{kw}最近改进很大，必须表扬一下！",
    "{kw}新增了自助服务，方便多了，效率提升不少。",
    "参加了{kw}的活动，组织得很用心，收获满满！",
    "图书馆延长开放时间，{kw}太贴心了，期末复习有去处了。",
    "食堂新开的{kw}窗口，味道太赞了！价格也实惠。",
    "学校的{kw}政策很人性化，真正为学生考虑。",
    "{kw}老师讲课特别有激情，这学期的课很有意思。",
    "校园{kw}设施维护得很好，感谢后勤的辛苦付出。",
    "这次{kw}改革力度很大，看到了学校的决心。",
    "申请{kw}的过程很顺利，线上办理太方便了。",
    "校园{kw}环境越来越美了，花开了特别好看。",
    "学校请了{kw}专家来做讲座，干货满满！",
    "{kw}比赛办得很成功，参赛队伍水平都很高。",
    "今天{kw}推出了新功能，体验感很好！",
    "实习基地{kw}条件不错，能学到真东西。",
    "学校{kw}奖学金覆盖面更广了，激励作用明显。",
    "宿舍装的{kw}特别好用，生活质量提高了。",
    "校园{kw}的WiFi覆盖更好了，网速也快了很多。",
    "参加{kw}志愿活动很有意义，希望多组织。",
    "选修了{kw}的课，意外收获很大。",
    "运动场{kw}设施更新了，终于可以好好锻炼了。",
    "学校{kw}系统升级后好用多了，选课不再卡。",
    "这学期{kw}课程安排很合理，学习压力没那么大。",
]

# 负面舆情模板
negative_templates = [
    "食堂{kw}又涨价了，份量还变少了，太坑了！",
    "宿舍{kw}坏了一个星期了还没人来修，报修多次没人管。",
    "学校{kw}的通知每次都临时发，完全没有给学生准备时间。",
    "这学期的{kw}排课太不合理了，全挤在一起。",
    "图书馆{kw}位置不够，每天都要抢座，太累了。",
    "学校{kw}收费不合理，没有明确说明费用构成。",
    "教务系统选课又崩了，{kw}体验极差！",
    "校园网{kw}经常断，看个视频都卡，还收这么贵。",
    "学校周边{kw}环境太差了，安全隐患很大。",
    "选修课{kw}的老师上课就是念PPT，浪费时间。",
    "实验设备{kw}太老旧了，做个实验都要排队。",
    "奖学金评定{kw}不透明，存在暗箱操作。",
    "学校{kw}施工噪音太大了，影响学习和休息。",
    "教室空调{kw}坏了整个夏天都没修，上课像蒸桑拿。",
    "{kw}处的办事效率太低了，一个证明跑了三趟。",
    "学校{kw}通知渠道混乱，重要信息经常漏看。",
    "期末考试{kw}安排太紧凑了，一周考八门。",
    "学校{kw}停车场根本不够，老师的车都停到学生宿舍区了。",
    "快递站{kw}取件排队半小时，能不能加几个窗口。",
    "外卖{kw}被偷了好几次，学校安保形同虚设。",
    "浴室{kw}水温忽冷忽热，冬天洗澡全靠勇气。",
    "学校{kw}的行政流程太繁琐了，一个小事要盖五个章。",
    "自习室{kw}占座现象严重，一整天都没来人的座位也占着。",
    "校园班车{kw}班次太少，每次都挤不上去。",
    "打印店{kw}价格比外面贵一倍，学校也不管管。",
]

# 中性舆情模板
neutral_templates = [
    "关于{kw}的最新通知已经下发了，请大家留意查看。",
    "有人知道{kw}的具体安排吗？等官方消息。",
    "{kw}的通知在官网上发布了，记得去看。",
    "学校{kw}的公众号更新了相关内容。",
    "转需：{kw}的报名截止日期是这个月底。",
    "{kw}相关通知已张贴在各教学楼公告栏。",
    "这学期{kw}的课表已经出来了，大家可以去教务系统查看。",
    "昨天{kw}的讲座有人录了吗？求分享。",
    "请教一下{kw}的选课经验，哪个老师比较好？",
    "求问{kw}社团还招新吗？想加入。",
    "有没有{kw}考研群？求拉一下。",
    "明天{kw}活动几点开始？在哪里？",
    "谁知道{kw}的办公室在哪个楼？",
    "学校{kw}公众号推送了新生入学指南。",
    "求校园{kw}地图，新生报到用。",
    "有人参加了{kw}的比赛吗？求经验分享。",
    "关于{kw}的问题，有没有知道的同学解答一下？",
    "提醒大家{kw}的缴费截止日期快到了。",
    "学校{kw}开放日改到下周了，注意时间变化。",
    "分享{kw}复习资料，有需要的自取。",
    "问问大家{kw}教材是哪个版本的？",
    "这个月{kw}的活动日程安排出来了。",
    "发个{kw}通知：原定周三的课调到了周五。",
    "大一新生请教{kw}相关的问题，谢谢学长学姐。",
    "学院{kw}换新系统了，登录方式有变化。",
]

# 关键词映射
keywords_list = [
    "食堂", "图书馆", "期末考试", "校园网", "奖学金", "运动会",
    "选修课", "社团招新", "宿舍", "考研", "就业指导", "学术讲座",
    "校庆", "校园安全", "教学楼", "实验室", "体育设施", "教务系统",
    "实习基地", "校园公交", "快递驿站", "外卖配送", "心理咨询",
    "创新创业", "志愿服务", "文艺汇演", "空调维修", "选课系统",
    "自习室", "停车场", "打印服务", "浴室热水", "网络提速",
    "食堂卫生", "寝室管理", "交通出行", "校园环境", "校医院",
    "出国交流", "助学金", "学生活动", "校园广播", "学院大楼",
]


def generate_opinion():
    days_offset = random.randint(0, days)
    created_date = start_date + timedelta(days=days_offset)
    created_at = created_date + timedelta(
        hours=random.randint(6, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    updated_at = created_at + timedelta(
        hours=random.randint(0, 48),
        minutes=random.randint(0, 59),
    )

    sentiment = random.choices(
        sentiments, weights=[0.35, 0.30, 0.35]
    )[0]

    kw = random.choice(keywords_list)

    if sentiment == "positive":
        template = random.choice(positive_templates)
    elif sentiment == "negative":
        template = random.choice(negative_templates)
    else:
        template = random.choice(neutral_templates)

    content = template.format(kw=kw)
    platform = random.choice(platforms)

    # 基于内容长度估算阅读量
    read_count = random.randint(50, 15000)
    like_count = int(read_count * random.uniform(0.01, 0.15))
    comment_count = int(read_count * random.uniform(0.005, 0.08))
    share_count = int(read_count * random.uniform(0.001, 0.03))

    # 根据情感调整互动
    if sentiment == "negative":
        read_count = int(read_count * random.uniform(1.2, 2.5))
        like_count = int(read_count * random.uniform(0.02, 0.2))
        comment_count = int(read_count * random.uniform(0.01, 0.12))

    return {
        "platform": platform,
        "content": content,
        "sentiment": sentiment,
        "read_count": read_count,
        "like_count": like_count,
        "comment_count": comment_count,
        "share_count": share_count,
        "source_url": f"https://{platform.lower()}.com/post/{random.randint(1000000, 9999999)}",
        "author": f"校园用户{random.randint(1000, 9999)}",
        "created_at": created_at.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": updated_at.strftime("%Y-%m-%d %H:%M:%S"),
    }


# 生成40000条数据
print("-- Generated campus opinion data")
print("SET NAMES utf8mb4;")
print("SET FOREIGN_KEY_CHECKS = 0;")
print("TRUNCATE TABLE opinions;")

for i in range(40000):
    d = generate_opinion()
    if i == 0:
        print(
            f"INSERT INTO opinions (platform, content, sentiment, read_count, like_count, comment_count, share_count, source_url, author, created_at, updated_at) VALUES "
        )
    if i > 0:
        print(", ", end="")
    escaped_content = d["content"].replace("'", "\\'").replace("\\", "\\\\")
    print(
        f"('{d['platform']}', '{escaped_content}', '{d['sentiment']}', "
        f"{d['read_count']}, {d['like_count']}, {d['comment_count']}, {d['share_count']}, "
        f"'{d['source_url']}', '{d['author']}', "
        f"'{d['created_at']}', '{d['updated_at']}')"
    )
print(";")
print("SET FOREIGN_KEY_CHECKS = 1;")
