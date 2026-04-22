import React from 'react'
import { Layout, Avatar, Dropdown, Space, Badge } from 'antd'
import { UserOutlined, BellOutlined, LogoutOutlined, SettingOutlined, UserSwitchOutlined } from '@ant-design/icons'

const { Header: AntHeader } = Layout

const Header: React.FC = () => {
  // 模拟用户数据
  const mockUser = {
    name: '管理员',
    username: 'admin'
  }

  // 退出登录处理
  const handleLogout = () => {
    console.log('退出登录')
  }

  // 用户下拉菜单
  const userMenuItems = [
    {
      key: '1',
      label: (
        <span className="flex items-center cursor-pointer">
          <SettingOutlined className="mr-2" />
          <span>个人设置</span>
        </span>
      ),
    },
    {
      key: '2',
      label: (
        <span className="flex items-center cursor-pointer">
          <UserSwitchOutlined className="mr-2" />
          <span>用户管理</span>
        </span>
      ),
    },
    {
      type: 'divider',
    },
    {
      key: '3',
      label: (
        <a onClick={handleLogout} className="flex items-center text-red-500">
          <LogoutOutlined className="mr-2" />
          <span>退出登录</span>
        </a>
      ),
    },
  ]

  return (
    <AntHeader className="flex items-center px-4 shadow-md" style={{ backgroundColor: '#ffffff', justifyContent: 'center' }}>
      {/* 中间系统标题 */}
      <div className="flex items-center">
        <h1 className="text-xl font-bold text-blue-600 m-0 md:text-lg sm:text-base text-center">校园舆情检测与热点话题分析系统</h1>
      </div>

      {/* 右侧用户信息和通知 */}
      <div className="flex items-center space-x-4 ml-auto">
        {/* 通知图标 */}
        <Badge count={0} showZero>
          <BellOutlined 
            className="text-gray-600 cursor-pointer text-xl hover:text-blue-600 transition-colors"
          />
        </Badge>

        {/* 用户头像和下拉菜单 */}
        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <div className="flex items-center cursor-pointer">
            <Avatar icon={<UserOutlined />} className="bg-blue-500 mr-2">
              {mockUser.username?.charAt(0)?.toUpperCase()}
            </Avatar>
            <span className="hidden md:inline text-gray-700 font-medium">
              {mockUser.name || mockUser.username}
            </span>
          </div>
        </Dropdown>
      </div>
    </AntHeader>
  )
}

export default Header