import React from 'react'
import { Typography, Card, Row, Col } from 'antd'
import TrendAnalysis from '../components/TrendAnalysis'
import { selectOpinionTrend, selectTrendError } from '../store/features/trendSlice'
import { selectDashboardStats } from '../store/features/opinionSlice'
import { useSelector } from 'react-redux'

const { Title, Text } = Typography

const TrendAnalysisPage: React.FC = () => {
  const opinionTrend = useSelector(selectOpinionTrend)
  const dashboardStats = useSelector(selectDashboardStats)
  const trendError = useSelector(selectTrendError)

  const totalCount = Array.isArray(opinionTrend) ? opinionTrend.reduce((sum, item) => sum + (item.count || 0), 0) : 0
  const todayCount = Array.isArray(opinionTrend) && opinionTrend.length > 0 ? (opinionTrend[opinionTrend.length - 1]?.count || 0) : 0
  const hotTopicsCount = dashboardStats?.hot_topics_count || 6

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="page-title">趋势分析</div>
        <div className="page-subtitle">舆情数据趋势与统计分析</div>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card className="stat-card stat-card-primary">
            <div className="stat-label">总舆情数量</div>
            <div className="stat-value stat-card-primary">{totalCount.toLocaleString()}</div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card stat-card-success">
            <div className="stat-label">今日新增</div>
            <div className="stat-value stat-card-success">{todayCount}</div>
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card className="stat-card stat-card-warning">
            <div className="stat-label">热点话题</div>
            <div className="stat-value stat-card-warning">{hotTopicsCount}</div>
          </Card>
        </Col>
      </Row>

      {trendError && (
        <div style={{ padding: 16, marginBottom: 16, background: '#fef2f2', borderRadius: 8, color: '#ef4444' }}>
          数据加载异常: {trendError}
        </div>
      )}

      <TrendAnalysis showCharts={true} />
    </div>
  )
}

export default TrendAnalysisPage