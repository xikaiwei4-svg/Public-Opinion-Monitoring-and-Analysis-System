import React, { useState } from 'react'
import type { Dayjs } from 'dayjs'
import { Typography, Card, Row, Col, Select, DatePicker, Space } from 'antd'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts'
import TrendAnalysis from '../components/TrendAnalysis'
import { selectOpinionTrend, selectSentimentTrend, selectPlatformDistribution, selectTrendLoading } from '../store/features/trendSlice'
import { useSelector } from 'react-redux'

const { Title, Text } = Typography
const { Option } = Select
const { RangePicker } = DatePicker

const TrendAnalysisPage: React.FC = () => {
  const opinionTrend = useSelector(selectOpinionTrend)
  const sentimentTrend = useSelector(selectSentimentTrend)
  const platformDistribution = useSelector(selectPlatformDistribution)
  const loading = useSelector(selectTrendLoading)
  const [timeRange, setTimeRange] = useState<[Dayjs, Dayjs] | null>(null)
  const [chartType, setChartType] = useState<string>('opinion') // 'opinion', 'sentiment', 'platform'
  
  // 生成情感分布数据
  const generateSentimentDistribution = () => {
    if (!Array.isArray(sentimentTrend) || sentimentTrend.length === 0) return []
    
    const positive = sentimentTrend.reduce((sum, item) => sum + (item.positive || 0), 0)
    const neutral = sentimentTrend.reduce((sum, item) => sum + (item.neutral || 0), 0)
    const negative = sentimentTrend.reduce((sum, item) => sum + (item.negative || 0), 0)
    
    return [
      { name: '积极', value: positive, color: '#52c41a' },
      { name: '中性', value: neutral, color: '#faad14' },
      { name: '消极', value: negative, color: '#ff4d4f' }
    ]
  }
  
  // 生成平台分布数据
  const generatePlatformDistribution = () => {
    if (!Array.isArray(platformDistribution) || platformDistribution.length === 0) return []
    
    return platformDistribution.map((item) => ({
      name: item.platform,
      value: item.count,
      color: item.color
    }))
  }
  
  const handleTimeRangeChange = (dates: [Dayjs, Dayjs] | null) => {
    setTimeRange(dates)
    // 可以根据需要实现按时间范围筛选数据的逻辑
  }
  
  const handleChartTypeChange = (value: string) => {
    setChartType(value)
  }
  
  const sentimentData = generateSentimentDistribution()
  const platformData = generatePlatformDistribution()
  
  return (
    <div className="trend-analysis-container">
      <Title level={2}>趋势分析</Title>
      
      {/* 趋势分析组件 */}
      <TrendAnalysis />
      
      {/* 统计摘要卡片 */}
      <Row gutter={[16, 16]} style={{ marginTop: '20px' }}>
        <Col xs={24} sm={8}>
          <Card className="stat-card" variant="outlined">
            <Text strong style={{ fontSize: '32px', color: '#1890ff' }}>
              {Array.isArray(opinionTrend) ? opinionTrend.reduce((sum, item) => sum + item.count, 0) : 0}
            </Text>
            <Text style={{ display: 'block', marginTop: '8px' }}>总舆情数量</Text>
          </Card>
        </Col>
        
        <Col xs={24} sm={8}>
          <Card className="stat-card" variant="outlined">
            <Text strong style={{ fontSize: '32px', color: '#52c41a' }}>
              {Array.isArray(opinionTrend) && opinionTrend.length > 0 ? opinionTrend[opinionTrend.length - 1]?.count || 0 : 0}
            </Text>
            <Text style={{ display: 'block', marginTop: '8px' }}>今日新增</Text>
          </Card>
        </Col>
        
        <Col xs={24} sm={8}>
          <Card className="stat-card" variant="outlined">
            <Text strong style={{ fontSize: '32px', color: '#faad14' }}>
              {5}
            </Text>
            <Text style={{ display: 'block', marginTop: '8px' }}>热点话题</Text>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default TrendAnalysisPage