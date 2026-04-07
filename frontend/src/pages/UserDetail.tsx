import React, { useEffect, useState } from 'react'
import { Card, Typography, Descriptions, Avatar, Space, Button, Divider, List, Tag, Row, Col, Table } from 'antd'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts'
import { ArrowLeftOutlined, EditOutlined, UserOutlined, MailOutlined, PhoneOutlined, CalendarOutlined, LockOutlined, CheckCircleOutlined, UserSwitchOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchUserDetail, selectUserDetail, selectUserDetailLoading } from '../store/features/userSlice'

const { Title, Text } = Typography
const { Item } = Descriptions

interface UserDetail {
  id: string
  username: string
  email: string
  role: string
  status: string
  created_at: string
  last_login: string
  avatar?: string
  phone?: string
  department?: string
  position?: string
  permissions?: string[]
  login_history?: {
    time: string
    ip: string
    device: string
  }[]
}

const UserDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const userDetail = useSelector(selectUserDetail)
  const loading = useSelector(selectUserDetailLoading)

  // 加载用户详情数据
  useEffect(() => {
    if (id) {
      dispatch(fetchUserDetail({ id }))
    }
  }, [dispatch, id])

  // 返回上一页
  const handleBack = () => {
    navigate(-1)
  }

  // 编辑用户
  const handleEdit = () => {
    navigate(`/user/edit/${id}`)
  }

  // 获取角色对应的标签
  const getRoleTag = (role: string) => {
    const roleMap: Record<string, { label: string; color: string }> = {
      'admin': { label: '管理员', color: 'red' },
      'editor': { label: '编辑', color: 'orange' },
      'viewer': { label: '查看者', color: 'green' },
      'user': { label: '普通用户', color: 'blue' }
    }
    
    const roleInfo = roleMap[role] || { label: role, color: 'default' }
    return <Tag color={roleInfo.color}>{roleInfo.label}</Tag>
  }

  // 获取状态对应的标签
  const getStatusTag = (status: string) => {
    const statusMap: Record<string, { label: string; color: string }> = {
      'active': { label: '活跃', color: 'green' },
      'inactive': { label: '禁用', color: 'red' },
      'pending': { label: '待审核', color: 'orange' }
    }
    
    const statusInfo = statusMap[status] || { label: status, color: 'default' }
    return <Tag color={statusInfo.color}>{statusInfo.label}</Tag>
  }

  // 获取权限对应的标签
  const getPermissionTag = (permission: string) => {
    const permissionMap: Record<string, { label: string; color: string }> = {
      'view_dashboard': { label: '查看仪表盘', color: 'blue' },
      'manage_opinions': { label: '管理舆情', color: 'green' },
      'manage_hot_topics': { label: '管理热点话题', color: 'orange' },
      'manage_users': { label: '管理用户', color: 'red' },
      'manage_settings': { label: '管理设置', color: 'purple' },
    }
    
    const permissionInfo = permissionMap[permission] || { label: permission, color: 'default' }
    return <Tag color={permissionInfo.color}>{permissionInfo.label}</Tag>
  }

  if (loading) {
    return (
      <div className="loading-container">
        <Title level={4} className="mb-6">用户详情</Title>
        <Card loading={true} className="h-64" />
      </div>
    )
  }
  
  // 生成模拟的登录趋势数据
  const [loginTrendData, setLoginTrendData] = useState<any[]>([])
  
  useEffect(() => {
    // 生成过去30天的登录趋势数据
    const generateLoginTrendData = () => {
      const data = []
      const today = new Date()
      
      // 为过去30天生成数据
      for (let i = 29; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        
        // 随机生成登录次数，周末可能登录次数较少
        const dayOfWeek = date.getDay()
        const isWeekend = dayOfWeek === 0 || dayOfWeek === 6
        const baseCount = isWeekend ? 1 : 3
        const randomFactor = Math.random() * 3 + 1 // 1-4的随机因子
        const loginCount = Math.floor(baseCount * randomFactor)
        
        // 生成活跃时长（分钟）
        const activeTime = loginCount > 0 ? Math.floor(loginCount * (Math.random() * 30 + 10)) : 0
        
        data.push({
          date: date.toLocaleDateString(),
          loginCount,
          activeTime
        })
      }
      return data
    }
    
    setLoginTrendData(generateLoginTrendData())
  }, [userDetail])
  
  // 渲染登录趋势图表
  const renderLoginTrendChart = () => {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={loginTrendData}
          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <RechartsTooltip />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone" 
            dataKey="loginCount" 
            name="登录次数" 
            stroke="#1890ff" 
            activeDot={{ r: 8 }} 
          />
          <Line
            yAxisId="right"
            type="monotone" 
            dataKey="activeTime" 
            name="活跃时长(分钟)" 
            stroke="#ff7875" 
          />
        </LineChart>
      </ResponsiveContainer>
    )
  }

  if (!userDetail) {
    return (
      <div className="error-container">
        <Title level={4} className="mb-6">用户详情</Title>
        <Card>
          <Text type="danger">未找到该用户数据</Text>
          <Button type="primary" onClick={handleBack} className="mt-4">返回列表</Button>
        </Card>
      </div>
    )
  }

  const { 
    username, email, role, status, created_at, last_login, avatar, 
    phone, department, position, permissions, login_history 
  } = userDetail

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <Title level={4} className="mb-0">用户详情</Title>
        <Space>
          <Button type="primary" icon={<EditOutlined />} onClick={handleEdit}>
            编辑用户
          </Button>
          <Button onClick={handleBack} icon={<ArrowLeftOutlined />}>返回列表</Button>
        </Space>
      </div>

      {/* 用户基本信息卡片 */}
      <Card className="mb-6">
        <div className="flex flex-wrap items-center mb-6">
          <Avatar size={80} src={avatar} icon={<UserOutlined />} className="mr-6" />
          <div>
            <h2 className="text-2xl font-bold mb-2">{username}</h2>
            <div className="flex flex-wrap items-center gap-2">
              {getRoleTag(role)}
              {getStatusTag(status)}
              {status === 'active' && (
                <Tag color="blue" icon={<CheckCircleOutlined />}>当前在线</Tag>
              )}
            </div>
          </div>
        </div>

        <Descriptions column={1} size="small" bordered>
          <Item label="用户名">{username}</Item>
          <Item label="邮箱">
            <Space>
              <MailOutlined />
              <Text>{email}</Text>
            </Space>
          </Item>
          <Item label="电话">
            <Space>
              <PhoneOutlined />
              <Text>{phone || '未设置'}</Text>
            </Space>
          </Item>
          <Item label="部门">{department || '未设置'}</Item>
          <Item label="职位">{position || '未设置'}</Item>
          <Item label="创建时间">
            <Space>
              <CalendarOutlined />
              <Text>{new Date(created_at).toLocaleString()}</Text>
            </Space>
          </Item>
          <Item label="最后登录">
            <Space>
              <UserSwitchOutlined />
              <Text>{new Date(last_login).toLocaleString()}</Text>
            </Space>
          </Item>
        </Descriptions>
      </Card>

      {/* 权限信息 */}
      {permissions && permissions.length > 0 && (
        <Card title="权限信息" className="mb-6">
          <Space wrap>
            {permissions.map((permission, index) => (
              <React.Fragment key={index}>
                {getPermissionTag(permission)}
              </React.Fragment>
            ))}
          </Space>
        </Card>
      )}

      {/* 登录趋势分析 */}
      <Card title="登录趋势分析" className="mb-6">
        {renderLoginTrendChart()}
      </Card>

      {/* 登录历史 */}
      {login_history && login_history.length > 0 && (
        <Card title="登录历史" className="mb-6">
          <Table
            dataSource={login_history}
            rowKey={(record, index) => index}
            pagination={{
              pageSize: 5,
              showSizeChanger: false,
              showTotal: (total) => `共 ${total} 条记录`,
            }}
            columns={[
              {
                title: '登录时间',
                dataIndex: 'time',
                key: 'time',
                render: (time: string) => new Date(time).toLocaleString(),
              },
              {
                title: '登录IP',
                dataIndex: 'ip',
                key: 'ip',
              },
              {
                title: '设备信息',
                dataIndex: 'device',
                key: 'device',
              },
            ]}
          />
        </Card>
      )}

      {/* 操作历史 */}
      <Card title="操作历史" className="mb-6">
        <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
          <Text>暂无操作历史数据</Text>
        </div>
      </Card>

      {/* 安全信息 */}
      <Card title="安全信息" className="mb-6">
        <Descriptions column={2} size="small" bordered>
          <Item label="账户安全等级">中级</Item>
          <Item label="最近修改密码">{new Date(new Date().getTime() - 7 * 24 * 60 * 60 * 1000).toLocaleDateString()}</Item>
          <Item label="双因素认证">未开启</Item>
          <Item label="登录设备数量">3台</Item>
        </Descriptions>
        <div className="mt-4">
          <Button type="primary" icon={<LockOutlined />}>重置密码</Button>
          <Button className="ml-2">绑定邮箱</Button>
          <Button className="ml-2">绑定手机</Button>
        </div>
      </Card>

      {/* 系统设置 */}
      <Card title="系统设置" className="mb-6">
        <Descriptions column={2} size="small" bordered>
          <Item label="语言偏好">中文</Item>
          <Item label="时区设置">GMT+8</Item>
          <Item label="主题偏好">默认主题</Item>
          <Item label="通知设置">已开启</Item>
        </Descriptions>
      </Card>
    </div>
  )
}

export default UserDetail