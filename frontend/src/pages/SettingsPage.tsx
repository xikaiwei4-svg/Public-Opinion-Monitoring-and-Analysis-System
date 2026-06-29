import React from 'react'
import { Card, Row, Col, Descriptions, Tag, Button, message, Space, Spin } from 'antd'
import { CheckCircleOutlined, SyncOutlined } from '@ant-design/icons'

const SettingsPage: React.FC = () => {
  const [cacheStatus, setCacheStatus] = React.useState<any>(null)

  const checkCache = async () => {
    try {
      const res = await fetch('/api/cache/status')
      const data = await res.json()
      setCacheStatus(data)
      message.success('缓存状态已更新')
    } catch {
      message.error('获取状态失败')
    }
  }

  const refreshCache = async () => {
    try {
      const res = await fetch('/api/cache/refresh', { method: 'POST' })
      const data = await res.json()
      message.success(data.message || '缓存已刷新')
      checkCache()
    } catch {
      message.error('刷新失败')
    }
  }

  React.useEffect(() => { checkCache() }, [])

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <div className="page-title">系统设置</div>
        <div className="page-subtitle">系统状态监控与配置管理</div>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card className="content-card" title="系统信息">
            <Descriptions column={1} size="small" bordered>
              <Descriptions.Item label="系统版本">v2.0.0</Descriptions.Item>
              <Descriptions.Item label="前端框架">React 18 + TypeScript + Ant Design 5</Descriptions.Item>
              <Descriptions.Item label="后端框架">FastAPI + Python 3.10</Descriptions.Item>
              <Descriptions.Item label="数据库">MySQL 8.0 + Redis</Descriptions.Item>
              <Descriptions.Item label="AI引擎">BERT (bert-base-chinese) + LogisticRegression</Descriptions.Item>
              <Descriptions.Item label="情感准确率">
                <Tag color="green">91.7%</Tag>
              </Descriptions.Item>
            </Descriptions>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            className="content-card"
            title="缓存管理"
            extra={<Button size="small" icon={<SyncOutlined />} onClick={checkCache}>刷新</Button>}
          >
            {cacheStatus ? (
              <Descriptions column={1} size="small" bordered>
                <Descriptions.Item label="缓存模式">
                  <Tag color={cacheStatus.redis_available ? 'green' : 'orange'} icon={<CheckCircleOutlined />}>
                    {cacheStatus.mode}
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="Redis状态">
                  {cacheStatus.redis_available ? '已连接' : '未连接（使用内存缓存）'}
                </Descriptions.Item>
              </Descriptions>
            ) : (
              <div style={{ textAlign: 'center', padding: 20, color: '#94a3b8' }}>加载中...</div>
            )}
            <div style={{ marginTop: 16 }}>
              <Button type="primary" icon={<SyncOutlined />} onClick={refreshCache} block>
                刷新全部缓存
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default SettingsPage
