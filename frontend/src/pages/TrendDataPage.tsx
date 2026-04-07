import React, { useState, useEffect } from 'react'
import { Typography, Card, Select, Button, Row, Col, Statistic, Spin, message } from 'antd'
import { DownloadOutlined, SyncOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import TrendAnalysis from '../components/TrendAnalysis'

const { Title, Text } = Typography

// 模拟趋势数据
const mockTrendData = {
  opinionTrend: [
    { date: '09-25', count: 120 },
    { date: '09-26', count: 145 },
    { date: '09-27', count: 180 },
    { date: '09-28', count: 165 },
    { date: '09-29', count: 210 },
    { date: '09-30', count: 230 },
    { date: '10-01', count: 250 }
  ],
  sentimentTrend: [
    { date: '09-25', positive: 45, negative: 30, neutral: 45 },
    { date: '09-26', positive: 50, negative: 25, neutral: 70 },
    { date: '09-27', positive: 65, negative: 40, neutral: 75 },
    { date: '09-28', positive: 55, negative: 35, neutral: 75 },
    { date: '09-29', positive: 75, negative: 50, neutral: 85 },
    { date: '09-30', positive: 85, negative: 45, neutral: 100 },
    { date: '10-01', positive: 90, negative: 60, neutral: 100 }
  ],
  platformDistribution: [
    { name: '校园论坛', value: 35 },
    { name: '微信公众号', value: 28 },
    { name: '微博', value: 22 },
    { name: '校园官网', value: 15 }
  ],
  stats: {
    totalOpinions: 1300,
    growthRate: 12.5,
    avgSentiment: 0.62,
    topPlatform: '校园论坛'
  }
}

const TrendDataPage: React.FC = () => {
  const [selectedDays, setSelectedDays] = useState<string>('7')
  const [refreshing, setRefreshing] = useState(false)
  const [trendData, setTrendData] = useState(mockTrendData)
  const [loading, setLoading] = useState(false)

  // 加载数据
  const loadData = (days: string = selectedDays) => {
    setLoading(true)
    // 模拟API请求延迟
    setTimeout(() => {
      // 这里可以根据不同的时间范围调整数据
      // 目前直接使用模拟数据
      setTrendData(mockTrendData)
      setLoading(false)
    }, 800)
  }

  // 组件加载时加载数据
  useEffect(() => {
    loadData()
  }, [])

  // 监听时间范围变化
  useEffect(() => {
    loadData(selectedDays)
  }, [selectedDays])

  // 刷新数据
  const handleRefresh = () => {
    setRefreshing(true)
    loadData(selectedDays)
    setTimeout(() => {
      setRefreshing(false)
      message.success('数据刷新成功')
    }, 800)
  }

  // 导出数据
  const handleExport = () => {
    message.success(`已导出${selectedDays}天的趋势数据`)
  }

  // 计算变化趋势
  const getGrowthTrend = (rate: number) => {
    if (rate > 0) {
      return (
        <Text style={{ color: '#ff4d4f' }}>
          <ArrowUpOutlined /> {rate}%
        </Text>
      )
    } else if (rate < 0) {
      return (
        <Text style={{ color: '#52c41a' }}>
          <ArrowDownOutlined /> {Math.abs(rate)}%
        </Text>
      )
    }
    return <Text style={{ color: '#faad14' }}>—</Text>
  }

  // 获取情感等级描述
  const getSentimentLevel = (score: number) => {
    if (score > 0.7) return '正面偏强'
    if (score > 0.5) return '轻微正面'
    if (score > 0.3) return '中性偏正'
    return '中性偏弱'
  }

  return (
    <div>
      <Title level={3}>趋势分析</Title>
      
      {/* 控制面板 */}
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
        <div>
          <Select 
            value={selectedDays} 
            style={{ width: 120 }} 
            onChange={(value) => setSelectedDays(value)}
          >
            <Select.Option value="7">近7天</Select.Option>
            <Select.Option value="14">近14天</Select.Option>
            <Select.Option value="30">近30天</Select.Option>
          </Select>
        </div>
        <div style={{ display: 'flex', gap: 12 }}>
          <Button 
            type="primary" 
            icon={<SyncOutlined />} 
            onClick={handleRefresh}
            loading={refreshing}
          >
            刷新数据
          </Button>
          <Button 
            icon={<DownloadOutlined />}
            onClick={handleExport}
          >
            导出报表
          </Button>
        </div>
      </div>
      
      {/* 统计卡片 */}
      <Spin spinning={loading || refreshing}>
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="总舆情数"
                value={trendData.stats.totalOpinions}
                suffix="条"
                precision={0}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="增长率"
                value={trendData.stats.growthRate}
                suffix="%"
                precision={1}
                valueStyle={{ color: trendData.stats.growthRate > 0 ? '#ff4d4f' : '#52c41a' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="平均情感指数"
                value={trendData.stats.avgSentiment}
                suffix={getSentimentLevel(trendData.stats.avgSentiment)}
                precision={2}
                valueStyle={{ color: trendData.stats.avgSentiment > 0.5 ? '#52c41a' : '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="主要来源平台"
                value={trendData.stats.topPlatform}
              />
            </Card>
          </Col>
        </Row>
        
        {/* 趋势图表 */}
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="舆情数量趋势">
              <TrendAnalysis 
                type="line" 
                data={trendData.opinionTrend} 
                xField="date" 
                yField="count" 
                height={300}
              />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="情感倾向趋势">
              <TrendAnalysis 
                type="area" 
                data={trendData.sentimentTrend} 
                xField="date" 
                yFields={['positive', 'negative', 'neutral']}
                height={300}
              />
            </Card>
          </Col>
        </Row>
        
        {/* 平台分布 */}
        <Row>
          <Col xs={24} md={12}>
            <Card title="信息源平台分布">
              <TrendAnalysis 
                type="pie" 
                data={trendData.platformDistribution} 
                height={300}
              />
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="趋势洞察">
              <div style={{ padding: 16, lineHeight: 1.8 }}>
                <h4 style={{ marginBottom: 12, color: '#1890ff' }}>关键发现</h4>
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  <li>近{selectedDays}天舆情总量呈{trendData.stats.growthRate > 0 ? '上升' : '下降'}趋势</li>
                  <li>情感倾向整体偏{trendData.stats.avgSentiment > 0.5 ? '正面' : '中性'}</li>
                  <li>{trendData.stats.topPlatform}是主要信息来源</li>
                  <li>最近两天舆情活跃度明显{trendData.stats.growthRate > 10 ? '增加' : '稳定'}</li>
                </ul>
                
                <h4 style={{ marginTop: 24, marginBottom: 12, color: '#1890ff' }}>建议措施</h4>
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  <li>持续关注{trendData.stats.topPlatform}平台的热点话题</li>
                  <li>针对{trendData.stats.avgSentiment < 0.5 ? '负面' : '关键'}舆情进行重点监控</li>
                  <li>定期分析舆情趋势变化，及时调整应对策略</li>
                </ul>
              </div>
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
}

export default TrendDataPage