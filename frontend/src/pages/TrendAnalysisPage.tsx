import React from 'react'
import { Typography, Card, Row, Col } from 'antd'
import TrendAnalysis from '../components/TrendAnalysis'
import { selectOpinionTrend } from '../store/features/trendSlice'
import { useSelector } from 'react-redux'

const { Title, Text } = Typography

const TrendAnalysisPage: React.FC = () => {
  const opinionTrend = useSelector(selectOpinionTrend)
  
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