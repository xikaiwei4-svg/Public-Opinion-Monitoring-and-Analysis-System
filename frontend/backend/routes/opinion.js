const express = require('express');
const router = express.Router();

// 获取当前时间相关的辅助函数
function getCurrentTime() {
  const now = new Date();
  return now.toISOString();
}

function getRelativeTime(daysAgo = 0, hoursAgo = 0, minutesAgo = 0) {
  const now = new Date();
  if (daysAgo > 0) {
    now.setDate(now.getDate() - daysAgo);
  }
  if (hoursAgo > 0) {
    now.setHours(now.getHours() - hoursAgo);
  }
  if (minutesAgo > 0) {
    now.setMinutes(now.getMinutes() - minutesAgo);
  }
  return now.toISOString();
}

// 模拟舆情数据（使用实时时间）
const mockOpinions = [
  {
    id: '1',
    content: '教育部近日发布新政策，将加大对乡村教师的支持力度，提高乡村教师待遇，改善乡村学校办学条件。这一政策的出台，将有助于促进教育公平，推动乡村教育振兴。',
    source: '中国教育报',
    source_platform: '微博',
    publish_time: getRelativeTime(0, 2, 30),
    crawl_time: getRelativeTime(0, 2, 0),
    sentiment: 0.8,
    sentiment_type: 'positive',
    keywords: ['教育部', '政策', '教育公平', '振兴乡村'],
    url: 'https://example.com/news/1',
    views: 12543,
    likes: 892,
    comments: 235,
    shares: 578,
    heat_score: 92,
    is_sensitive: false,
    sensitive_level: 0
  },
  {
    id: '2',
    content: '据最新调查数据显示，今年高校毕业生就业形势总体平稳，但结构性矛盾依然存在。IT、人工智能、医疗健康等行业需求旺盛，而传统制造业、服务业就业压力较大。专家建议，高校应加强专业设置与市场需求的对接，提高学生实践能力。',
    source: '中国青年报',
    source_platform: '微信',
    publish_time: getRelativeTime(0, 5, 15),
    crawl_time: getRelativeTime(0, 5, 0),
    sentiment: 0.5,
    sentiment_type: 'neutral',
    keywords: ['高校毕业生', '就业形势', '人工智能', '医疗健康'],
    url: 'https://example.com/news/2',
    views: 9870,
    likes: 654,
    comments: 189,
    shares: 132,
    heat_score: 78,
    is_sensitive: false,
    sensitive_level: 0
  },
  {
    id: '3',
    content: '近期，多所高校发生网络安全事件，导致部分学生信息泄露。专家提醒，学校应加强网络安全防护措施，定期进行安全漏洞扫描，同时提高师生网络安全意识，避免点击可疑链接、下载不明软件。',
    source: '科技日报',
    source_platform: '知乎',
    publish_time: getRelativeTime(1, 3, 45),
    crawl_time: getRelativeTime(1, 3, 0),
    sentiment: 0.2,
    sentiment_type: 'negative',
    keywords: ['网络安全', '校园安全', '信息泄露'],
    url: 'https://example.com/news/3',
    views: 15680,
    likes: 1234,
    comments: 342,
    shares: 215,
    heat_score: 92,
    is_sensitive: true,
    sensitive_level: 7
  },
  {
    id: '4',
    content: '为鼓励大学生创业创新，国家近日升级了大学生创业扶持政策，符合条件的创业项目最高可获得50万元补贴。此外，还将提供创业培训、导师指导、场地支持等一站式服务。这一政策的出台，将继续激发大学生创业热情。',
    source: '经济参考报',
    source_platform: '校园论坛',
    publish_time: getRelativeTime(1, 8, 30),
    crawl_time: getRelativeTime(1, 8, 0),
    sentiment: 0.9,
    sentiment_type: 'positive',
    keywords: ['大学生创业', '扶持政策', '补贴'],
    url: 'https://example.com/news/4',
    views: 8960,
    likes: 789,
    comments: 175,
    shares: 128,
    heat_score: 76,
    is_sensitive: false,
    sensitive_level: 0
  },
  {
    id: '5',
    content: '据教育部公布的数据，今年全国硕士研究生招生考试报名人数突破500万，创历史新高。专家分析，就业压力、学历提升需求是报名人数增长主要原因。面对激烈的竞争，考生应提前做好复习规划，理性选择报考院校和专业。',
    source: '新华社',
    source_platform: '微博',
    publish_time: getRelativeTime(2, 4, 0),
    crawl_time: getRelativeTime(2, 3, 30),
    sentiment: 0.5,
    sentiment_type: 'neutral',
    keywords: ['研究生考试', '报名人数', '竞争'],
    url: 'https://example.com/news/5',
    views: 14530,
    likes: 987,
    comments: 321,
    shares: 198,
    heat_score: 88,
    is_sensitive: false,
    sensitive_level: 0
  }
];

// 获取实时统计数据
function getRealTimeStatistics() {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  // 生成过去7天的日期
  const dailyTrend = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
    const count = Math.floor(Math.random() * 100) + 100; // 100-200之间的随机数
    dailyTrend.push({ date: dateStr, count: count });
  }
  
  return {
    total_opinions: Math.floor(Math.random() * 500) + 1000, // 1000-1500之间的随机数
    positive_count: Math.floor(Math.random() * 200) + 400, // 400-600之间的随机数
    negative_count: Math.floor(Math.random() * 100) + 200, // 200-300之间的随机数
    neutral_count: Math.floor(Math.random() * 150) + 300, // 300-450之间的随机数
    daily_trend: dailyTrend,
    platform_distribution: [
      { platform: '微博', count: Math.floor(Math.random() * 100) + 500, percentage: 45.1 },
      { platform: '微信', count: Math.floor(Math.random() * 50) + 300, percentage: 27.2 },
      { platform: '知乎', count: Math.floor(Math.random() * 50) + 150, percentage: 15.0 },
      { platform: '校园论坛', count: Math.floor(Math.random() * 50) + 100, percentage: 12.6 }
    ],
    category_distribution: [
      { category: '政策解读', count: Math.floor(Math.random() * 50) + 300 },
      { category: '就业情况', count: Math.floor(Math.random() * 50) + 250 },
      { category: '科技创新', count: Math.floor(Math.random() * 50) + 200 },
      { category: '校园安全', count: Math.floor(Math.random() * 50) + 150 },
      { category: '教育改革', count: Math.floor(Math.random() * 50) + 150 }
    ]
  };
}

// 获取舆情列表
router.get('/list', (req, res) => {
  const { page = 1, page_size = 10, keyword, source, sentiment_type, start_time, end_time, is_sensitive, category } = req.query;
  
  // 筛选数据
  let filteredData = [...mockOpinions];
  
  if (keyword) {
    filteredData = filteredData.filter(item => 
      item.content.includes(keyword) || 
      item.keywords.some(kw => kw.includes(keyword))
    );
  }
  
  if (source) {
    filteredData = filteredData.filter(item => item.source_platform === source);
  }
  
  if (sentiment_type) {
    filteredData = filteredData.filter(item => item.sentiment_type === sentiment_type);
  }
  
  if (start_time) {
    filteredData = filteredData.filter(item => new Date(item.publish_time) >= new Date(start_time));
  }
  
  if (end_time) {
    filteredData = filteredData.filter(item => new Date(item.publish_time) <= new Date(end_time));
  }
  
  if (is_sensitive !== undefined) {
    filteredData = filteredData.filter(item => item.is_sensitive === (is_sensitive === 'true'));
  }
  
  // 分页
  const total = filteredData.length;
  const startIndex = (page - 1) * page_size;
  const endIndex = startIndex + parseInt(page_size);
  const paginatedData = filteredData.slice(startIndex, endIndex);
  
  res.json({
    items: paginatedData,
    total: total,
    page: parseInt(page),
    page_size: parseInt(page_size)
  });
});

// 获取舆情统计数据 - 必须放在 /:id 路由之前
router.get('/statistics', (req, res) => {
  const { start_time, end_time } = req.query;
  
  // 返回实时统计数据
  res.json(getRealTimeStatistics());
});

// 获取舆情统计摘要
router.get('/statistics/summary', (req, res) => {
  const { days = 7 } = req.query;
  const stats = getRealTimeStatistics();
  
  res.json({
    platform_distribution: stats.platform_distribution,
    time_range: `${days}天`,
    total_count: stats.total_opinions,
    average_daily_count: Math.round(stats.total_opinions / days),
    sentiment_distribution: {
      positive: stats.positive_count,
      negative: stats.negative_count,
      neutral: stats.neutral_count
    }
  });
});

// 获取舆情详情 - 必须放在最后，因为它会匹配所有路径
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const opinion = mockOpinions.find(item => item.id === id);
  
  if (!opinion) {
    return res.status(404).json({
      code: 404,
      message: '舆情数据不存在'
    });
  }
  
  res.json(opinion);
});

module.exports = router;
