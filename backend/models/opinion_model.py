import enum


class SourcePlatform(str, enum.Enum):
    WEIBO = "weibo"
    WECHAT = "wechat"
    ZHIHU = "zhihu"
    FORUM = "forum"
    OTHER = "other"


class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
