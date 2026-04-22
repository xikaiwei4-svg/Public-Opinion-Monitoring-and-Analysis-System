import React from 'react'
import { Outlet, useNavigate } from 'react-router-dom'
import { Layout as AntLayout, Card, Row, Col, List, Button } from 'antd'
import Header from './Header'
import Footer from './Footer'
import './Layout.css'
import { HomeOutlined, MessageOutlined, FireOutlined, LineChartOutlined, UserOutlined, DatabaseOutlined, SettingOutlined } from '@ant-design/icons'

const { Content } = AntLayout

const Layout: React.FC = () => {
  const navigate = useNavigate()
  
  // 导航菜单项
  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: '仪表盘', route: '/' },
    { key: 'opinion', icon: <MessageOutlined />, label: '舆情管理', route: '/opinion/list' },
    { key: 'hot-topic', icon: <FireOutlined />, label: '热点话题', route: '/hot-topic/list' },
    { key: 'trend', icon: <LineChartOutlined />, label: '趋势分析', route: '/trend-analysis' },
    { key: 'user', icon: <UserOutlined />, label: '用户管理', route: '/user/manage' },
    { key: 'database', icon: <DatabaseOutlined />, label: '数据库管理', route: '/database/manage' },
    { key: 'settings', icon: <SettingOutlined />, label: '系统设置', route: '/settings' }
  ]

  return (
    <AntLayout className="app-layout" style={{ backgroundColor: '#ffffff' }}>
      <Header />
      <AntLayout className="main-content" style={{ backgroundColor: '#ffffff' }}>
        <Content className="content-wrapper" style={{ backgroundColor: '#ffffff' }}>
          {/* 导航区域 */}
          <Card style={{ marginBottom: 16 }}>
            <Row gutter={16}>
              <Col xs={24}>
                <List
                  grid={{ gutter: 16, xs: 2, sm: 3, md: 4, lg: 7 }}
                  dataSource={menuItems}
                  renderItem={(item) => (
                    <List.Item>
                      <Button
                        type={window.location.pathname === item.route ? 'primary' : 'default'}
                        icon={item.icon}
                        onClick={() => navigate(item.route)}
                        style={{ width: '100%' }}
                      >
                        {item.label}
                      </Button>
                    </List.Item>
                  )}
                />
              </Col>
            </Row>
          </Card>
          <Outlet />
        </Content>
        <Footer />
      </AntLayout>
    </AntLayout>
  )
}

export default Layout