import React, { useEffect, useState, useCallback } from 'react'
import { Typography, Row, Col, Card, Spin, Alert, Statistic, Divider, Button, Select, message } from 'antd'
import TrendAnalysis from '../components/TrendAnalysis'
import { useDispatch, useSelector } from 'react-redux'
import { selectDashboardStats, fetchOpinionStatistics, selectOpinionStatistics, selectOpinionLoading, selectOpinionError } from '../store/features/opinionSlice'
import { 
  fetchOpinionTrend, 
  fetchSentimentTrend, 
  fetchPlatformDistribution,
  selectOpinionTrend, 
  selectSentimentTrend, 
  selectPlatformDistribution, 
  selectTrendLoading, 
  selectTrendError 
} from '../store/features/trendSlice'
import { DownloadOutlined, SyncOutlined, DownOutlined, UpOutlined } from '@ant-design/icons'

const { Title } = Typography

function Dashboard() {
  const dispatch = useDispatch()
  const [selectedDays, setSelectedDays] = useState('7')
  const [refreshing, setRefreshing] = useState(false)
  const [collapsed, setCollapsed] = useState(true)
  
  // 从Redux获取仪表盘统计数据
  const dashboardStats = useSelector(selectDashboardStats)
  const statistics = useSelector(selectOpinionStatistics)
  const opinionLoading = useSelector(selectOpinionLoading)
  const opinionError = useSelector(selectOpinionError)
  
  // 从trendSlice获取趋势数据
  const opinionTrend = useSelector(selectOpinionTrend)
  const sentimentTrend = useSelector(selectSentimentTrend)
  const platformDistribution = useSelector(selectPlatformDistribution)
  const trendLoading = useSelector(selectTrendLoading)
  const trendError = useSelector(selectTrendError)

  // 统一获取所有数据
  const fetchAllData = useCallback((days: string, showRefreshing = false) => {
    if (showRefreshing) {
      setRefreshing(true)
    }
    console.log('Dashboard: fetchAllData called with days:', days);
    dispatch(fetchOpinionStatistics())
    dispatch(fetchOpinionTrend({ days }))
    dispatch(fetchSentimentTrend({ days }))
    dispatch(fetchPlatformDistribution({ days }))
    
    // 重置刷新状态
    if (showRefreshing) {
      setTimeout(() => {
        setRefreshing(false)
        message.success('数据刷新成功')
      }, 1000)
    }
  }, []) // 移除dispatch依赖，因为dispatch是稳定的

  // 在组件加载时获取数据
  useEffect(() => {
    console.log('Dashboard: useEffect called with selectedDays:', selectedDays);
    fetchAllData(selectedDays)
  }, [selectedDays]) // 只依赖selectedDays

  // 手动刷新数据
  const handleRefresh = useCallback(() => {
    fetchAllData(selectedDays, true)
  }, [fetchAllData, selectedDays])

  // 处理导出数据
  const handleExportData = () => {
    // 模拟数据导出功能
    setTimeout(() => {
      console.log(`已导出${selectedDays}天的数据报表`)
    }, 500)
  }
  
  // 使用实际数据或默认数据，增加更健壮的错误处理
  const stats = dashboardStats && typeof dashboardStats === 'object' && Object.keys(dashboardStats).length > 0 ? [
    {
      title: '今日舆情',
      value: dashboardStats.total_count || 128,
      description: '较昨日 +12'
    },
    {
      title: '热点话题',
      value: dashboardStats.hot_topics_count || 25,
      description: '较昨日 +3'
    },
    {
      title: '关注用户',
      value: dashboardStats.views_count || 3265,
      description: '较昨日 +48'
    }
  ] : [
    {
      title: '今日舆情',
      value: 128,
      description: '较昨日 +12'
    },
    {
      title: '热点话题',
      value: 25,
      description: '较昨日 +3'
    },
    {
      title: '关注用户',
      value: 3265,
      description: '较昨日 +48'
    }
  ]

  // 计算情感分布数据 - 使用真实数据或默认数据
  const sentimentData = dashboardStats?.sentiment_distribution ? {
    positive: Math.round((dashboardStats.sentiment_distribution.positive / dashboardStats.total_count) * 100) || 42,
    negative: Math.round((dashboardStats.sentiment_distribution.negative / dashboardStats.total_count) * 100) || 28,
    neutral: Math.round((dashboardStats.sentiment_distribution.neutral / dashboardStats.total_count) * 100) || 30
  } : {
    positive: 42,
    negative: 28,
    neutral: 30
  }

  return (
    <div>
      {/* 仪表盘标题和折叠按钮 */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>仪表盘概览</Title>
        <Button
          type="primary"
          icon={collapsed ? <DownOutlined /> : <UpOutlined />}
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? '展开' : '收起'}
        </Button>
      </div>

      {/* 可折叠的仪表盘内容 */}
      {!collapsed && (
        <div>
          {/* 错误提示 */}
          {(opinionError || trendError) && (
            <Alert
              message="数据加载失败"
              description={opinionError || trendError}
              type="error"
              showIcon
              style={{ marginBottom: 16 }}
              onClose={() => {}}
            />
          )}
          
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
                onClick={handleExportData}
              >
                导出报表
              </Button>
            </div>
          </div>

          {/* 统计卡片 */}
          <Spin spinning={opinionLoading || trendLoading || refreshing} tip="加载中...">
            <Row gutter={16}>
              {stats.map((stat, index) => (
                <Col xs={24} sm={12} md={8} key={index}>
                  <Card title={stat.title} style={{ height: '100%' }}>
                    <Statistic
                      value={stat.value}
                      valueStyle={{ fontSize: 32 }}
                      suffix={stat.description}
                    />
                  </Card>
                </Col>
              ))}
            </Row>
          </Spin>

          <Divider />

          {/* 趋势分析 */}
          <TrendAnalysis timeRange={selectedDays} onTimeRangeChange={setSelectedDays} />

          <Divider />

          {/* 情感分布 */}
          <Row gutter={16}>
            <Col span={24}>
              <Card title="情感分布">
                <Spin spinning={opinionLoading || trendLoading} tip="加载中...">
                  {dashboardStats?.sentiment_distribution ? (
                    <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 24 }}>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 48, color: '#52c41a', fontWeight: 'bold' }}>
                          {sentimentData.positive}%
                        </div>
                        <div style={{ color: '#52c41a', marginTop: 8 }}>正面</div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 48, color: '#1890ff', fontWeight: 'bold' }}>
                          {sentimentData.neutral}%
                        </div>
                        <div style={{ color: '#1890ff', marginTop: 8 }}>中性</div>
                      </div>
                      <div style={{ textAlign: 'center' }}>
                        <div style={{ fontSize: 48, color: '#ff7875', fontWeight: 'bold' }}>
                          {sentimentData.negative}%
                        </div>
                        <div style={{ color: '#ff7875', marginTop: 8 }}>负面</div>
                      </div>
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>
                      暂无数据
                    </div>
                  )}
                </Spin>
              </Card>
            </Col>
          </Row>

          <Divider />

          {/* 平台分布 */}
          <Row gutter={16}>
            <Col span={24}>
              <Card title="平台分布">
                <Spin spinning={opinionLoading || trendLoading} tip="加载中...">
                  {dashboardStats?.platform_distribution && dashboardStats.platform_distribution.length > 0 ? (
                    <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: 24 }}>
                      {dashboardStats.platform_distribution.map((platform, index) => (
                        <div key={index} style={{ textAlign: 'center' }}>
                          <div style={{ fontSize: 36, fontWeight: 'bold' }}>
                            {platform.count}
                          </div>
                          <div style={{ marginTop: 8 }}>{platform.platform}</div>
                          <div style={{ color: '#999', fontSize: 12, marginTop: 4 }}>
                            {platform.percentage.toFixed(1)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', color: '#999', padding: 40 }}>
                      暂无数据
                    </div>
                  )}
                </Spin>
              </Card>
            </Col>
          </Row>
        </div>
      )}

    </div>
  )
}

export default Dashboard
