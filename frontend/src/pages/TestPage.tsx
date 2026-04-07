import React from 'react'
import { Card, Typography, Button } from 'antd'
import { HomeOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'

const { Title, Paragraph } = Typography

const TestPage: React.FC = () => {
  const navigate = useNavigate()

  const handleGoHome = () => {
    navigate('/')
  }

  return (
    <Card style={{ margin: '20px' }}>
      <Title level={2}>测试页面</Title>
      <Paragraph>这是一个测试页面，用于验证路由系统是否正常工作。</Paragraph>
      <Button 
        type="primary" 
        icon={<HomeOutlined />} 
        onClick={handleGoHome}
      >
        返回首页
      </Button>
    </Card>
  )
}

export default TestPage