import React, { useEffect, useState } from 'react'
import {
  Table,
  Button,
  Space,
  Input,
  Select,
  Card,
  Modal,
  Form,
  Input as AntInput,
  message,
  Popconfirm,
  Tag,
  Typography,
  Row,
  Col,
  Statistic
} from 'antd'
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  UserOutlined,
  TeamOutlined
} from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import {
  fetchUsers,
  deleteUser,
  createUser,
  updateUser,
  selectUsers,
  selectUserTotal,
  selectUserCurrentPage,
  selectUserPageSize,
  selectUserLoading,
  User
} from '../store/features/userSlice'
import type { ColumnsType } from 'antd/es/table'

const { Title } = Typography
const { Option } = Select
const { Search } = Input

const UserManagementPage: React.FC = () => {
  const dispatch = useDispatch()
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [form] = Form.useForm()
  const [searchKeyword, setSearchKeyword] = useState('')
  const [filterRole, setFilterRole] = useState<string>('')
  const [filterStatus, setFilterStatus] = useState<string>('')

  const users = useSelector(selectUsers)
  const total = useSelector(selectUserTotal)
  const currentPage = useSelector(selectUserCurrentPage)
  const pageSize = useSelector(selectUserPageSize)
  const loading = useSelector(selectUserLoading)

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = (page = 1, size = 10) => {
    dispatch(fetchUsers({
      page,
      pageSize: size,
      keyword: searchKeyword,
      role: filterRole,
      status: filterStatus
    }) as any)
  }

  const handleSearch = () => {
    loadUsers(1, pageSize)
  }

  const handleReset = () => {
    setSearchKeyword('')
    setFilterRole('')
    setFilterStatus('')
    loadUsers(1, pageSize)
  }

  const handleCreate = () => {
    setEditingUser(null)
    form.resetFields()
    setIsModalVisible(true)
  }

  const handleEdit = (record: User) => {
    setEditingUser(record)
    form.setFieldsValue({
      username: record.username,
      email: record.email,
      role: record.role,
      status: record.status,
      phone: record.phone,
      department: record.department,
      position: record.position
    })
    setIsModalVisible(true)
  }

  const handleDelete = async (id: string) => {
    try {
      await dispatch(deleteUser(id) as any)
      message.success('用户删除成功')
      loadUsers(currentPage, pageSize)
    } catch (error) {
      message.error('删除失败')
    }
  }

  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()
      
      if (editingUser) {
        await dispatch(updateUser({ id: editingUser.id, userData: values }) as any)
        message.success('用户更新成功')
      } else {
        await dispatch(createUser(values) as any)
        message.success('用户创建成功')
      }
      
      setIsModalVisible(false)
      loadUsers(currentPage, pageSize)
    } catch (error) {
      message.error('操作失败')
    }
  }

  const handleTableChange = (pagination: any) => {
    loadUsers(pagination.current, pagination.pageSize)
  }

  const columns: ColumnsType<User> = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120,
      render: (text: string) => (
        <Space>
          <UserOutlined />
          {text}
        </Space>
      )
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 100,
      render: (role: string) => (
        <Tag color={role === 'admin' ? 'red' : 'blue'}>
          {role === 'admin' ? '管理员' : '普通用户'}
        </Tag>
      )
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'orange'}>
          {status === 'active' ? '正常' : '禁用'}
        </Tag>
      )
    },
    {
      title: '部门',
      dataIndex: 'department',
      key: 'department',
      width: 120
    },
    {
      title: '职位',
      dataIndex: 'position',
      key: 'position',
      width: 120
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
      width: 130
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN')
    },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      fixed: 'right',
      render: (_: any, record: User) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => message.info('查看详情功能待实现')}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个用户吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              size="small"
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div style={{ padding: '20px' }}>
      <Title level={3}>用户管理</Title>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="总用户数"
              value={total}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="管理员"
              value={users.filter(u => u.role === 'admin').length}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="正常用户"
              value={users.filter(u => u.status === 'active').length}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="禁用用户"
              value={users.filter(u => u.status === 'inactive').length}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Search
            placeholder="搜索用户名或邮箱"
            allowClear
            style={{ width: 250 }}
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            onSearch={handleSearch}
            enterButton={<SearchOutlined />}
          />
          <Select
            placeholder="角色筛选"
            style={{ width: 150 }}
            allowClear
            value={filterRole || undefined}
            onChange={(value) => setFilterRole(value || '')}
          >
            <Option value="admin">管理员</Option>
            <Option value="user">普通用户</Option>
          </Select>
          <Select
            placeholder="状态筛选"
            style={{ width: 150 }}
            allowClear
            value={filterStatus || undefined}
            onChange={(value) => setFilterStatus(value || '')}
          >
            <Option value="active">正常</Option>
            <Option value="inactive">禁用</Option>
          </Select>
          <Button type="primary" icon={<SearchOutlined />} onClick={handleSearch}>
            搜索
          </Button>
          <Button onClick={handleReset}>重置</Button>
        </Space>
      </Card>

      <Card
        title="用户列表"
        extra={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
            新增用户
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={users}
          rowKey="id"
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`
          }}
          onChange={handleTableChange}
          scroll={{ x: 1200 }}
        />
      </Card>

      <Modal
        title={editingUser ? '编辑用户' : '新增用户'}
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={() => setIsModalVisible(false)}
        okText="确定"
        cancelText="取消"
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            role: 'user',
            status: 'active'
          }}
        >
          {!editingUser && (
            <Form.Item
              name="username"
              label="用户名"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <AntInput placeholder="请输入用户名" />
            </Form.Item>
          )}
          {!editingUser && (
            <Form.Item
              name="password"
              label="密码"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 6, message: '密码至少6个字符' }
              ]}
            >
              <AntInput.Password placeholder="请输入密码" />
            </Form.Item>
          )}
          <Form.Item
            name="email"
            label="邮箱"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <AntInput placeholder="请输入邮箱" />
          </Form.Item>
          <Form.Item
            name="role"
            label="角色"
            rules={[{ required: true, message: '请选择角色' }]}
          >
            <Select placeholder="请选择角色">
              <Option value="admin">管理员</Option>
              <Option value="user">普通用户</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="status"
            label="状态"
            rules={[{ required: true, message: '请选择状态' }]}
          >
            <Select placeholder="请选择状态">
              <Option value="active">正常</Option>
              <Option value="inactive">禁用</Option>
            </Select>
          </Form.Item>
          <Form.Item name="phone" label="电话">
            <AntInput placeholder="请输入电话" />
          </Form.Item>
          <Form.Item name="department" label="部门">
            <AntInput placeholder="请输入部门" />
          </Form.Item>
          <Form.Item name="position" label="职位">
            <AntInput placeholder="请输入职位" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default UserManagementPage
