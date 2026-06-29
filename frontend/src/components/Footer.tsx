import React from 'react'
import { Layout, Row, Col } from 'antd'

const { Footer: AntFooter } = Layout

const Footer: React.FC = () => (
  <AntFooter style={{
    background: 'transparent',
    borderTop: '1px solid #e8ecf3',
    padding: '12px 28px',
    marginLeft: 230,
    fontSize: 12, color: '#94a3b8',
  }}>
    <Row justify="space-between">
      <Col>© 2026 校园舆情监测与热点话题分析系统</Col>
      <Col>v2.0 · BERT 情感分析引擎 · Redis 缓存加速</Col>
    </Row>
  </AntFooter>
)

export default Footer
