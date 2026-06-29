import { useEffect, useState, useCallback } from 'react'
import { Row, Col, Card, Spin, Alert, Button, Select, message, Space } from 'antd'
import { DownloadOutlined, SyncOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { selectDashboardStats, fetchOpinionStatistics, selectOpinionLoading, selectOpinionError } from '../store/features/opinionSlice'
import { fetchOpinionTrend, fetchSentimentTrend, fetchPlatformDistribution, selectTrendLoading, selectTrendError } from '../store/features/trendSlice'
import TrendAnalysis from '../components/TrendAnalysis'
import WordCloud from '../components/WordCloud'
import LiveFeed from '../components/LiveFeed'

function Dashboard() {
  const dispatch = useDispatch()
  const [selectedDays, setSelectedDays] = useState('30')
  const [refreshing, setRefreshing] = useState(false)

  const dashboardStats = useSelector(selectDashboardStats)
  const opinionLoading = useSelector(selectOpinionLoading)
  const opinionError = useSelector(selectOpinionError)
  const trendLoading = useSelector(selectTrendLoading)
  const trendError = useSelector(selectTrendError)

  const fetchAllData = useCallback((days: string, showRefreshing = false) => {
    if (showRefreshing) setRefreshing(true)
    dispatch(fetchOpinionStatistics())
    dispatch(fetchOpinionTrend({ days }))
    dispatch(fetchSentimentTrend({ days }))
    dispatch(fetchPlatformDistribution({ days }))
    if (showRefreshing) setTimeout(() => { setRefreshing(false); message.success('数据刷新成功') }, 800)
  }, [dispatch])

  useEffect(() => { fetchAllData(selectedDays) }, [selectedDays, fetchAllData])

  const handleRefresh = useCallback(() => fetchAllData(selectedDays, true), [fetchAllData, selectedDays])

  const handleExportData = () => {
    const csv = [
      ['指标,数值'],
      [`总舆情,${dashboardStats?.total_count || 0}`],
      [`热点话题,${dashboardStats?.hot_topics_count || 0}`],
      [`正面,${dashboardStats?.sentiment_distribution?.positive || 0}`],
      [`负面,${dashboardStats?.sentiment_distribution?.negative || 0}`],
      [`中性,${dashboardStats?.sentiment_distribution?.neutral || 0}`],
    ].join('\n')
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url
    a.download = `dashboard_${new Date().toISOString().split('T')[0]}.csv`
    a.click(); URL.revokeObjectURL(url)
    message.success('报表已导出')
  }

  const totalCount = dashboardStats?.total_count || 0
  const hotCount = dashboardStats?.hot_topics_count || 0
  const posCount = dashboardStats?.sentiment_distribution?.positive || 0
  const negCount = dashboardStats?.sentiment_distribution?.negative || 0
  const neuCount = dashboardStats?.sentiment_distribution?.neutral || 0

  const statCards = [
    { label: '舆情总量', value: totalCount.toLocaleString(), sub: '条数据', type: 'primary' as const },
    { label: '热点话题', value: hotCount, sub: '个话题', type: 'warning' as const },
    { label: '正面舆情', value: totalCount > 0 ? Math.round(posCount / totalCount * 100) + '%' : '-', sub: posCount.toLocaleString() + ' 条', type: 'success' as const },
  ]

  const sentPct = {
    pos: Math.round(posCount / totalCount * 100),
    neg: Math.round(negCount / totalCount * 100),
    neu: Math.round(neuCount / totalCount * 100),
  }

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div className="page-title">仪表盘概览</div>
        <div className="page-subtitle">校园舆情实时监控与数据分析中心</div>
      </div>

      {/* Error Alert */}
      {(opinionError || trendError) && (
        <Alert message="数据加载异常" description={opinionError || trendError} type="error" showIcon style={{ marginBottom: 16, borderRadius: 12 }} />
      )}

      {/* Controls */}
      <div style={{ marginBottom: 20, display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
        <Select value={selectedDays} style={{ width: 120 }} onChange={setSelectedDays} size="middle">
          <Select.Option value="7">近7天</Select.Option>
          <Select.Option value="14">近14天</Select.Option>
          <Select.Option value="30">近30天</Select.Option>
        </Select>
        <Button type="primary" icon={<SyncOutlined />} onClick={handleRefresh} loading={refreshing}>刷新数据</Button>
        <Button icon={<DownloadOutlined />} onClick={handleExportData}>导出报表</Button>
      </div>

      <Spin spinning={opinionLoading || trendLoading || refreshing}>

        {/* Stats Cards */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          {statCards.map((s, i) => (
            <Col xs={24} sm={8} key={i}>
              <Card className={`stat-card stat-card-${s.type} fade-in-up`} style={{ animationDelay: `${i * 0.08}s` }} bodyStyle={{ padding: '20px 24px' }}>
                <div className="stat-label">{s.label}</div>
                <div className={`stat-value stat-card-${s.type}`}>
                  {s.value}
                </div>
                <div className="stat-label" style={{ marginTop: 4 }}>{s.sub}</div>
              </Card>
            </Col>
          ))}
        </Row>

        {/* WordCloud + LiveFeed */}
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={14}>
            <Card className="content-card" title={<span style={{ fontWeight: 600 }}>🔥 热点词云</span>}>
              <WordCloud height={380} />
            </Card>
          </Col>
          <Col xs={24} lg={10}>
            <Card className="content-card" title={<span style={{ fontWeight: 600 }}>⚡ 实时舆情推送</span>} bodyStyle={{ padding: '12px 16px' }}>
              <LiveFeed />
            </Card>
          </Col>
        </Row>

        {/* Trend Analysis */}
        <div style={{ marginBottom: 24 }}>
          <TrendAnalysis timeRange={selectedDays} onTimeRangeChange={setSelectedDays} />
        </div>

        {/* Sentiment Distribution */}
        <Card className="content-card" title={<span style={{ fontWeight: 600 }}>📊 情感分布</span>}>
          <div>
            {/* Progress bar */}
            <div style={{ display: 'flex', height: 44, borderRadius: 22, overflow: 'hidden', marginBottom: 28 }}>
              <div style={{ width: `${sentPct.pos}%`, background: 'linear-gradient(90deg, #22c55e, #4ade80)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: '#fff', transition: 'width 0.6s ease' }}>
                {sentPct.pos}%
              </div>
              <div style={{ width: `${sentPct.neu}%`, background: 'linear-gradient(90deg, #6366f1, #818cf8)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: '#fff', transition: 'width 0.6s ease' }}>
                {sentPct.neu}%
              </div>
              <div style={{ width: `${sentPct.neg}%`, background: 'linear-gradient(90deg, #ef4444, #f87171)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, fontWeight: 700, color: '#fff', transition: 'width 0.6s ease' }}>
                {sentPct.neg}%
              </div>
            </div>

            {/* Stats row */}
            <Row gutter={24} justify="center">
              <Col>
                <div style={{ textAlign: 'center' }}>
                  <Space><span className="sentiment-dot sentiment-dot-positive" /> 正面</Space>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#22c55e', margin: '4px 0' }}>{sentPct.pos}%</div>
                  <div style={{ fontSize: 13, color: '#94a3b8' }}>{posCount.toLocaleString()} 条</div>
                </div>
              </Col>
              <Col>
                <div style={{ textAlign: 'center' }}>
                  <Space><span className="sentiment-dot sentiment-dot-neutral" /> 中性</Space>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#6366f1', margin: '4px 0' }}>{sentPct.neu}%</div>
                  <div style={{ fontSize: 13, color: '#94a3b8' }}>{neuCount.toLocaleString()} 条</div>
                </div>
              </Col>
              <Col>
                <div style={{ textAlign: 'center' }}>
                  <Space><span className="sentiment-dot sentiment-dot-negative" /> 负面</Space>
                  <div style={{ fontSize: 32, fontWeight: 800, color: '#ef4444', margin: '4px 0' }}>{sentPct.neg}%</div>
                  <div style={{ fontSize: 13, color: '#94a3b8' }}>{negCount.toLocaleString()} 条</div>
                </div>
              </Col>
            </Row>
          </div>
        </Card>

      </Spin>
    </div>
  )
}

export default Dashboard
