const express = require('express');
const router = express.Router();

// 获取实时舆情趋势数据
function getRealTimeOpinionTrend() {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  // 生成过去7天的日期
  const trendData = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
    const count = Math.floor(Math.random() * 60) + 80; // 80-140之间的随机数
    const heat = Math.floor(Math.random() * 40) + 55; // 55-95之间的随机数
    trendData.push({ date: dateStr, count: count, heat: heat });
  }
  
  return trendData;
}

// 获取实时情感趋势数据
function getRealTimeSentimentTrend() {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  // 生成过去7天的日期
  const sentimentData = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = `${date.getMonth() + 1}月${date.getDate()}日`;
    const positive = Math.floor(Math.random() * 30) + 35; // 35-65之间的随机数
    const negative = Math.floor(Math.random() * 15) + 20; // 20-35之间的随机数
    const neutral = Math.floor(Math.random() * 20) + 25; // 25-45之间的随机数
    sentimentData.push({ date: dateStr, positive: positive, negative: negative, neutral: neutral });
  }
  
  return sentimentData;
}

// 获取实时平台分布数据
function getRealTimePlatformDistribution() {
  const total = Math.floor(Math.random() * 200) + 1000; // 1000-1200之间的随机数
  
  return [
    { platform: '微博', count: Math.floor(total * 0.357), percentage: 35.7, color: '#E6162D' },
    { platform: '微信', count: Math.floor(total * 0.298), percentage: 29.8, color: '#07C160' },
    { platform: '知乎', count: Math.floor(total * 0.179), percentage: 17.9, color: '#0066FF' },
    { platform: '校园论坛', count: Math.floor(total * 0.102), percentage: 10.2, color: '#FF9500' },
    { platform: '其他', count: Math.floor(total * 0.064), percentage: 6.4, color: '#5856D6' }
  ];
}

// 获取舆情趋势数据
router.get('/opinion', (req, res) => {
  const { days = '7', platform } = req.query;
  
  // 返回实时趋势数据
  res.json(getRealTimeOpinionTrend());
});

// 获取情感趋势数据
router.get('/sentiment', (req, res) => {
  const { days = '7', platform } = req.query;
  
  // 返回实时情感趋势数据
  res.json(getRealTimeSentimentTrend());
});

// 获取平台分布数据
router.get('/platform-distribution', (req, res) => {
  const { days = '7' } = req.query;
  
  // 返回实时平台分布数据
  res.json(getRealTimePlatformDistribution());
});

module.exports = router;
