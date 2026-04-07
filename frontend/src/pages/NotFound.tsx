import React from 'react'
import { Card, Typography, Button } from 'antd'
import { HomeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Paragraph } = Typography

const NotFound: React.FC = () => {
  const navigate = useNavigate()

  const handleGoHome = () => {
    navigate('/')
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}>
      <Card style={{ width: '100%', maxWidth: '400px', textAlign: 'center' }}>
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '64px', fontWeight: 'bold', color: '#f0f0f0', marginBottom: '16px' }}>404</div>
          <Title level={2} style={{ marginBottom: '16px' }}>页面不存在</Title>
          <Paragraph style={{ color: '#8c8c8c' }}>
            抱歉，您访问的页面不存在或已被删除
          </Paragraph>
        </div>
        <Button 
          type="primary" 
          icon={<HomeOutlined />} 
          onClick={handleGoHome}
          size="large"
        >
          返回首页
        </Button>
      </Card>
    </div>
  )
}

export default NotFound