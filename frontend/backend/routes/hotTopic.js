const express = require('express');
const router = express.Router();

// 获取相对时间的辅助函数
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

// 模拟热点话题数据（使用实时时间）
const mockHotTopics = [
  {
    id: '1',
    title: '校园图书馆扩建计划获批',
    description: '我校图书馆扩建计划近日获得批准，扩建后图书馆面积将增加一倍，新增各类藏书20万册，并将建设现代化的电子阅读区和学术交流空间。项目预计明年年初完工，将极大改善师生的学习和科研条件。',
    keywords: ['图书馆', '扩建', '学习条件', '科研'],
    related_opinions_count: 235,
    start_time: getRelativeTime(0, 6, 0),
    end_time: getRelativeTime(0, 0, 0),
    peak_time: getRelativeTime(0, 3, 0),
    hot_value: 95,
    trend_status: 'rising',
    platforms: ['微博', '微信公众号', '校园论坛', '知乎'],
    sentiment_distribution: {
      positive: 85,
      negative: 5,
      neutral: 10
    },
    topic_category: 'campus_facility',
    is_official: true,
    source_link: 'https://example.com/topic/1',
    influencers: [
      {
        id: 'inf1',
        name: '校长办公室',
        platform: '微博',
        influence_score: 92
      },
      {
        id: 'inf2',
        name: '图书馆馆长',
        platform: '微信公众号',
        influence_score: 88
      }
    ]
  },
  {
    id: '2',
    title: '食堂菜品质量改善计划',
    description: '为提升学生用餐体验，后勤处启动食堂菜品质量改善计划，邀请专业营养师设计菜单，增加菜品多样性，并严格把控食材质量。同时，食堂将延长营业时间，增设夜宵窗口。',
    keywords: ['食堂', '菜品', '质量改善', '学生生活'],
    related_opinions_count: 189,
    start_time: getRelativeTime(1, 4, 0),
    end_time: getRelativeTime(0, 0, 0),
    peak_time: getRelativeTime(0, 8, 0),
    hot_value: 88,
    trend_status: 'stable',
    platforms: ['微博', '微信公众号', '校园论坛', '知乎'],
    sentiment_distribution: {
      positive: 65,
      negative: 20,
      neutral: 15
    },
    topic_category: 'campus_life',
    is_official: true,
    source_link: 'https://example.com/topic/2',
    influencers: [
      {
        id: 'inf3',
        name: '后勤处处长',
        platform: '校园论坛',
        influence_score: 85
      }
    ]
  },
  {
    id: '3',
    title: '校园运动会报名创新高',
    description: '今年的校园运动会报名人数突破2000人，创历史新高。运动会将增设电子竞技、攀岩等新兴项目，同时保留传统田径项目。开幕式将邀请知名校友回母校表演。',
    keywords: ['运动会', '报名', '创新高', '校园活动'],
    related_opinions_count: 165,
    start_time: getRelativeTime(2, 2, 0),
    end_time: getRelativeTime(0, 0, 0),
    peak_time: getRelativeTime(1, 5, 0),
    hot_value: 82,
    trend_status: 'rising',
    platforms: ['微博', '微信公众号', '校园论坛', '抖音'],
    sentiment_distribution: {
      positive: 72,
      negative: 8,
      neutral: 20
    },
    topic_category: 'campus_life',
    is_official: true,
    source_link: 'https://example.com/topic/3',
    influencers: [
      {
        id: 'inf4',
        name: '校团委书记',
        platform: '微信公众号',
        influence_score: 88
      },
      {
        id: 'inf5',
        name: '体育学院院长',
        platform: '校园论坛',
        influence_score: 82
      }
    ]
  }
];

// 获取实时话题趋势数据
function getRealTimeTopicTrend() {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  // 生成过去7天的日期
  const trendData = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
    const hotValue = Math.floor(Math.random() * 50) + 60; // 60-110之间的随机数
    const opinionCount = Math.floor(Math.random() * 100) + 50; // 50-150之间的随机数
    trendData.push({ date: dateStr, hot_value: hotValue, opinion_count: opinionCount });
  }
  
  return trendData;
}

// 获取实时话题比较数据
function getRealTimeComparisonData() {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  return [
    {
      id: '1',
      title: '校园图书馆扩建计划获批',
      hot_value: 95,
      change_rate: 25,
      sentiment_distribution: {
        positive: 85,
        negative: 5,
        neutral: 10
      },
      platform_distribution: [
        { platform: '微博', count: Math.floor(Math.random() * 30) + 110 },
        { platform: '微信公众号', count: Math.floor(Math.random() * 20) + 75 },
        { platform: '校园论坛', count: Math.floor(Math.random() * 10) + 10 },
        { platform: '知乎', count: Math.floor(Math.random() * 10) + 5 }
      ],
      related_opinions_count: 235
    },
    {
      id: '2',
      title: '食堂菜品质量改善计划',
      hot_value: 88,
      change_rate: 12,
      sentiment_distribution: {
        positive: 65,
        negative: 20,
        neutral: 15
      },
      platform_distribution: [
        { platform: '微博', count: Math.floor(Math.random() * 20) + 85 },
        { platform: '微信公众号', count: Math.floor(Math.random() * 15) + 55 },
        { platform: '校园论坛', count: Math.floor(Math.random() * 10) + 20 },
        { platform: '知乎', count: Math.floor(Math.random() * 5) + 2 }
      ],
      related_opinions_count: 189
    },
    {
      id: '3',
      title: '校园运动会报名创新高',
      hot_value: 82,
      change_rate: 18,
      sentiment_distribution: {
        positive: 72,
        negative: 8,
        neutral: 20
      },
      platform_distribution: [
        { platform: '微博', count: Math.floor(Math.random() * 20) + 75 },
        { platform: '微信公众号', count: Math.floor(Math.random() * 15) + 45 },
        { platform: '校园论坛', count: Math.floor(Math.random() * 10) + 15 },
        { platform: '抖音', count: Math.floor(Math.random() * 5) + 3 }
      ],
      related_opinions_count: 165
    }
  ];
}

// 获取热点话题列表
router.get('/list', (req, res) => {
  const { page = 1, page_size = 10, keyword, category, trend_status, start_time, end_time } = req.query;
  
  // 筛选数据
  let filteredData = [...mockHotTopics];
  
  if (keyword) {
    filteredData = filteredData.filter(item => 
      item.title.includes(keyword) || 
      item.description.includes(keyword) || 
      item.keywords.some(kw => kw.includes(keyword))
    );
  }
  
  if (category) {
    filteredData = filteredData.filter(item => item.topic_category === category);
  }
  
  if (trend_status) {
    filteredData = filteredData.filter(item => item.trend_status === trend_status);
  }
  
  if (start_time) {
    filteredData = filteredData.filter(item => new Date(item.start_time) >= new Date(start_time));
  }
  
  if (end_time) {
    filteredData = filteredData.filter(item => new Date(item.end_time) <= new Date(end_time));
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
    page_size: parseInt(page_size),
    total_pages: Math.ceil(total / page_size)
  });
});

// 获取热点话题详情
router.get('/:id', (req, res) => {
  const { id } = req.params;
  const topic = mockHotTopics.find(item => item.id === id);
  
  if (!topic) {
    return res.status(404).json({
      code: 404,
      message: '热点话题不存在'
    });
  }
  
  res.json(topic);
});

// 获取热点话题趋势数据
router.get('/trend', (req, res) => {
  const { topic_id, days = 7 } = req.query;
  
  // 返回实时趋势数据
  res.json(getRealTimeTopicTrend());
});

// 比较热点话题
router.get('/compare', (req, res) => {
  const { topic_ids } = req.query;
  const ids = topic_ids ? topic_ids.split(',') : [];
  
  // 筛选指定ID的话题
  const comparisonData = getRealTimeComparisonData().filter(item => ids.includes(item.id));
  
  res.json(comparisonData);
});

module.exports = router;
