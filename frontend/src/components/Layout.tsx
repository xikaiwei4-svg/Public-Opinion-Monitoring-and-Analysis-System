import React from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Layout as AntLayout, Menu, Typography } from 'antd'
import {
  DashboardOutlined, MessageOutlined, FireOutlined, LineChartOutlined, FileTextOutlined,
} from '@ant-design/icons'
import Footer from './Footer'
import './Layout.css'

const { Header, Sider, Content } = AntLayout
const { Text } = Typography

const menuItems = [
  { key: '/', icon: <DashboardOutlined />, label: '仪表盘' },
  { key: '/opinion/list', icon: <MessageOutlined />, label: '舆情管理' },
  { key: '/hot-topic/list', icon: <FireOutlined />, label: '热点话题' },
  { key: '/trend-analysis', icon: <LineChartOutlined />, label: '趋势分析' },
  { key: '/report/list', icon: <FileTextOutlined />, label: '智能报告' },
]

const Layout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()

  const pathParts = location.pathname.split('/').filter(Boolean)
  const selectedKey = menuItems.find(m => m.key === ('/' + pathParts[0]))?.key
    || menuItems.find(m => m.key !== '/' && location.pathname.startsWith(m.key))?.key
    || '/'

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Sider width={230} className="layout-sider">
        {/* Logo */}
        <div className="sider-logo">
          <div style={{
            width: 36, height: 36, borderRadius: 10,
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: '#fff', fontSize: 18, fontWeight: 700,
          }}>
            S
          </div>
          <div className="sider-logo-text">校园舆情</div>
        </div>

        {/* Menu */}
        <Menu
          mode="inline"
          selectedKeys={[selectedKey]}
          className="layout-menu"
          items={menuItems.map(item => ({
            key: item.key,
            icon: item.icon,
            label: item.label,
            onClick: () => navigate(item.key),
          }))}
        />

        {/* Bottom hint */}
        <div style={{ padding: '12px 20px', borderTop: '1px solid #f1f5f9' }}>
          <div style={{ fontSize: 11, color: '#94a3b8', display: 'flex', alignItems: 'center', gap: 6 }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e' }} />
            系统运行中
          </div>
        </div>
      </Sider>

      <AntLayout>
        {/* Header */}
        <Header className="layout-header">
          <Text className="header-title">
            校园舆情监测与热点话题分析系统
          </Text>
        </Header>

        {/* Content */}
        <Content className="layout-content">
          <div className="fade-in">
            <Outlet />
          </div>
        </Content>

        <Footer />
      </AntLayout>
    </AntLayout>
  )
}

export default Layout
