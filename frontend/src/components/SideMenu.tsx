import React from 'react'
import { Layout, Menu } from 'antd'
import {
  PieChartOutlined,
  LineChartOutlined,
  FireOutlined,
  MessageOutlined,
  UserOutlined,
  SettingOutlined,
  HomeOutlined,
  DatabaseOutlined
} from '@ant-design/icons'
import { useNavigate, useLocation } from 'react-router-dom'

const { Sider } = Layout

const SideMenu: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const currentPath = location.pathname
  const [collapsed, setCollapsed] = React.useState(false)

  // 模拟权限数据
  const mockPermissions = ['read', 'admin']

  // 菜单项配置
  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '仪表盘',
      route: '/',
      permission: 'read'
    },
    {
      key: 'opinion',
      icon: <MessageOutlined />,
      label: '舆情管理',
      route: '/opinion/list',
      permission: 'read'
    },
    {
      key: 'hot-topic',
      icon: <FireOutlined />,
      label: '热点话题',
      route: '/hot-topic/list',
      permission: 'read'
    },
    {      key: 'trend',      icon: <LineChartOutlined />,      label: '趋势分析',      route: '/test/trend-data',      permission: 'read'    },
    
    {
      key: 'user',
      icon: <UserOutlined />,
      label: '用户管理',
      route: '/user/manage',
      permission: 'admin'
    },
    {
      key: 'database',
      icon: <DatabaseOutlined />,
      label: '数据库管理',
      route: '/database/manage',
      permission: 'admin'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '系统设置',
      route: '/settings',
      permission: 'admin'
    }
  ]

  // 过滤菜单项，只显示用户有权限的菜单项
  const filteredMenuItems = menuItems.filter(item => {
    // 如果没有设置权限，默认显示
    if (!item.permission) return true
    // 如果用户有权限或者没有设置权限列表（表示所有权限），则显示
    return mockPermissions.includes(item.permission) || mockPermissions.length === 0
  })

  // 切换侧边栏折叠状态
  const toggleCollapsed = () => {
    setCollapsed(!collapsed)
  }

  // 计算当前活动的菜单项key
  const getCurrentKey = () => {
    // 检查是否有精确匹配的路径
    const exactMatch = filteredMenuItems.find(item => item.route === currentPath)
    if (exactMatch) {
      return exactMatch.key
    }

    // 检查是否有部分匹配的路径（例如详情页）
    for (const item of filteredMenuItems) {
      if (currentPath.startsWith(item.route) && item.route !== '/') {
        return item.key
      }
    }

    // 默认返回仪表盘
    return '/'
  }

  // 转换为Ant Design v5 Menu组件需要的items格式
  const menuItemsForAntd = filteredMenuItems.map((item) => ({
    key: item.key,
    icon: item.icon,
    label: item.label,
    onClick: () => {
      console.log(`点击了${item.label}`)
      navigate(item.route)
    }
  }))

  return (
    <Sider
      width={200}
      collapsible
      collapsed={collapsed}
      onCollapse={toggleCollapsed}
      className="bg-white shadow-md"
      theme="light"
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 64,
        bottom: 0
      }}
    >
      <Menu
        mode="inline"
        selectedKeys={[getCurrentKey()]}
        style={{ height: '100%', borderRight: 0 }}
        className="pt-4"
        items={menuItemsForAntd}
      />
    </Sider>
  )
}

export default SideMenu