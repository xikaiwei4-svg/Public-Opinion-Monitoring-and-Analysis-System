import React, { useState, useEffect, useCallback, useMemo } from 'react'
import { Typography, Card, Select, Button, Row, Col, Statistic, Spin, message } from 'antd'
import { DownloadOutlined, SyncOutlined, ArrowUpOutlined, ArrowDownOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import TrendAnalysis from '../components/TrendAnalysis'
import { 
  fetchOpinionTrend, 
  fetchSentimentTrend, 
  fetchPlatformDistribution,
  selectOpinionTrend,
  selectSentimentTrend,
  selectPlatformDistribution,
  selectTrendLoading
} from '../store/features/trendSlice'

const { Title, Text } = Typography

// 统计数据类型
interface Stats {
  totalOpinions: number
  growthRate: number
  avgSentiment: number
  topPlatform: string
  maxDailyOpinions: number
  sentimentRatio: { positive: number; negative: number; neutral: number }
}

const TrendDataPage: React.FC = React.memo(() => {
  const dispatch = useDispatch()
  const [selectedDays, setSelectedDays] = useState<string>('7')
  const [refreshing, setRefreshing] = useState(false)
  
  // 从Redux获取数据
  const opinionTrend = useSelector(selectOpinionTrend)
  const sentimentTrend = useSelector(selectSentimentTrend)
  const platformDistribution = useSelector(selectPlatformDistribution)
  const loading = useSelector(selectTrendLoading)

  // 加载数据
  const loadData = useCallback((days: string) => {
    console.log('TrendDataPage: Loading data for', days, 'days')
    dispatch(fetchOpinionTrend({ days: days as '7' | '15' | '30' }))
    dispatch(fetchSentimentTrend({ days: days as '7' | '15' | '30' }))
    dispatch(fetchPlatformDistribution({ days: days as '7' | '15' | '30' }))
  }, [dispatch])

  // 组件加载时加载数据
  useEffect(() => {
    loadData(selectedDays)
  }, [loadData, selectedDays])

  // 刷新数据
  const handleRefresh = useCallback(() => {
    setRefreshing(true)
    loadData(selectedDays)
    setTimeout(() => {
      setRefreshing(false)
      message.success('数据刷新成功')
    }, 1000)
  }, [loadData, selectedDays])

  // 导出数据
  const handleExport = useCallback(() => {
    const exportData = {
      opinionTrend,
      sentimentTrend,
      platformDistribution,
      selectedDays,
      exportTime: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `trend_report_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    message.success(`已导出${selectedDays}天的趋势数据`)
  }, [opinionTrend, sentimentTrend, platformDistribution, selectedDays])

  // 计算统计数据（使用useMemo缓存计算结果）
  const stats: Stats = useMemo(() => {
    // 计算总舆情数
    const totalOpinions = opinionTrend.reduce((sum, item) => sum + (item.count || 0), 0)
    
    // 计算增长率（基于最近两天的数据）
    let growthRate = 0
    if (opinionTrend.length >= 2) {
      const latest = opinionTrend[opinionTrend.length - 1]
      const previous = opinionTrend[opinionTrend.length - 2]
      if (previous.count && previous.count > 0) {
        growthRate = ((latest.count - previous.count) / previous.count) * 100
      }
    }
    
    // 计算平均情感指数和情感比例
    let avgSentiment = 0
    let sentimentRatio = { positive: 0, negative: 0, neutral: 0 }
    
    if (sentimentTrend.length > 0) {
      const totalPositive = sentimentTrend.reduce((sum, item) => sum + (item.positive || 0), 0)
      const totalNegative = sentimentTrend.reduce((sum, item) => sum + (item.negative || 0), 0)
      const totalNeutral = sentimentTrend.reduce((sum, item) => sum + (item.neutral || 0), 0)
      const total = totalPositive + totalNegative + totalNeutral
      
      if (total > 0) {
        avgSentiment = (totalPositive - totalNegative) / total
        sentimentRatio = {
          positive: Math.round((totalPositive / total) * 100),
          negative: Math.round((totalNegative / total) * 100),
          neutral: Math.round((totalNeutral / total) * 100)
        }
      }
    }
    
    // 找出主要来源平台
    let topPlatform = '暂无数据'
    if (platformDistribution.length > 0) {
      topPlatform = platformDistribution[0].platform || platformDistribution[0].name || '暂无数据'
    }
    
    // 计算最大日舆情数
    const maxDailyOpinions = opinionTrend.length > 0 
      ? Math.max(...opinionTrend.map(item => item.count || 0)) 
      : 0
    
    return {
      totalOpinions,
      growthRate: parseFloat(growthRate.toFixed(1)),
      avgSentiment: parseFloat(avgSentiment.toFixed(2)),
      topPlatform,
      maxDailyOpinions,
      sentimentRatio
    }
  }, [opinionTrend, sentimentTrend, platformDistribution])

  // 获取情感等级描述
  const getSentimentLevel = useCallback((score: number) => {
    if (score > 0.7) return '正面偏强'
    if (score > 0.5) return '轻微正面'
    if (score > 0.3) return '中性偏正'
    if (score > 0) return '轻微正面'
    if (score > -0.3) return '中性偏弱'
    if (score > -0.5) return '轻微负面'
    return '负面偏强'
  }, [])

  // 生成趋势洞察
  const trendInsights = useMemo(() => {
    const isIncreasing = stats.growthRate > 0
    const sentimentDirection = stats.avgSentiment > 0 ? '正面' : stats.avgSentiment < 0 ? '负面' : '中性'
    const isSignificantChange = Math.abs(stats.growthRate) > 10
    const activityChange = isSignificantChange ? (isIncreasing ? '增加' : '减少') : '稳定'
    
    return {
      keyFindings: [
        `近${selectedDays}天舆情总量呈${isIncreasing ? '上升' : '下降'}趋势`,
        `情感倾向整体偏${sentimentDirection}`,
        `${stats.topPlatform}是主要信息来源`,
        `最近两天舆情活跃度明显${activityChange}`
      ],
      recommendations: [
        `持续关注${stats.topPlatform}平台的热点话题`,
        `针对${stats.avgSentiment < 0 ? '负面' : '关键'}舆情进行重点监控`,
        `定期分析舆情趋势变化，及时调整应对策略`,
        `关注情感分布：正面${stats.sentimentRatio.positive}%，负面${stats.sentimentRatio.negative}%`
      ]
    }
  }, [stats, selectedDays])

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
                value={stats.totalOpinions}
                suffix="条"
                precision={0}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="增长率"
                value={stats.growthRate}
                suffix="%"
                precision={1}
                valueStyle={{ color: stats.growthRate > 0 ? '#ff4d4f' : '#52c41a' }}
                prefix={stats.growthRate > 0 ? <ArrowUpOutlined /> : stats.growthRate < 0 ? <ArrowDownOutlined /> : null}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="平均情感指数"
                value={stats.avgSentiment}
                suffix={getSentimentLevel(stats.avgSentiment)}
                precision={2}
                valueStyle={{ color: stats.avgSentiment > 0 ? '#52c41a' : stats.avgSentiment < 0 ? '#ff4d4f' : '#faad14' }}
              />
            </Card>
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Card>
              <Statistic
                title="主要来源平台"
                value={stats.topPlatform}
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
                data={opinionTrend} 
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
                data={sentimentTrend} 
                xField="date" 
                yFields={['positive', 'negative', 'neutral']}
                height={300}
              />
            </Card>
          </Col>
        </Row>
        
        {/* 平台分布和趋势洞察 */}
        <Row>
          <Col xs={24} md={12}>
            <Card title="信息源平台分布">
              <TrendAnalysis 
                type="pie" 
                data={platformDistribution} 
                height={300}
              />
            </Card>
          </Col>
          <Col xs={24} md={12}>
            <Card title="趋势洞察">
              <div style={{ padding: 16, lineHeight: 1.8 }}>
                <h4 style={{ marginBottom: 12, color: '#1890ff' }}>关键发现</h4>
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  {trendInsights.keyFindings.map((finding, index) => (
                    <li key={index}>{finding}</li>
                  ))}
                </ul>
                
                <h4 style={{ marginTop: 24, marginBottom: 12, color: '#1890ff' }}>建议措施</h4>
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  {trendInsights.recommendations.map((recommendation, index) => (
                    <li key={index}>{recommendation}</li>
                  ))}
                </ul>
              </div>
            </Card>
          </Col>
        </Row>
      </Spin>
    </div>
  )
})

TrendDataPage.displayName = 'TrendDataPage'

export default TrendDataPage