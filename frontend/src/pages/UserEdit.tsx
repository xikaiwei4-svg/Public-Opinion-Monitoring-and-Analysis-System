import React, { useEffect, useState } from 'react'
import { Card, Typography, Form, Input, Select, Switch, Button, Space, Avatar, Upload, message } from 'antd'
import { ArrowLeftOutlined, UploadOutlined, UserOutlined, MailOutlined, PhoneOutlined, LockOutlined, SaveOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchUserDetail, updateUser, createUser, selectUserDetail, selectUserDetailLoading } from '../store/features/userSlice'

const { Title, Text } = Typography
const { Option } = Select
const { Password } = Input

interface UserData {
  username: string
  email: string
  role: string
  status: boolean
  phone?: string
  department?: string
  position?: string
  permissions?: string[]
  avatar?: string
  password?: string
}

const UserEdit: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const userDetail = useSelector(selectUserDetail)
  const loading = useSelector(selectUserDetailLoading)
  const [form] = Form.useForm<UserData>()
  const [isCreating, setIsCreating] = useState(false)
  const [fileList, setFileList] = useState<{ uid: string; name: string; status: string; url?: string }[]>([])
  const [imageUrl, setImageUrl] = useState<string>('')

  // 判断是创建用户还是编辑用户
  useEffect(() => {
    setIsCreating(!id)
  }, [id])

  // 加载用户详情数据
  useEffect(() => {
    if (id) {
      dispatch(fetchUserDetail({ id }))
    }
  }, [dispatch, id])

  // 设置表单数据
  useEffect(() => {
    if (userDetail && !isCreating) {
      form.setFieldsValue({
        username: userDetail.username,
        email: userDetail.email,
        role: userDetail.role,
        status: userDetail.status === 'active',
        phone: userDetail.phone,
        department: userDetail.department,
        position: userDetail.position,
        permissions: userDetail.permissions,
      })
      
      if (userDetail.avatar) {
        setImageUrl(userDetail.avatar)
        setFileList([{
          uid: '1',
          name: 'avatar.jpg',
          status: 'done',
          url: userDetail.avatar
        }])
      }
    } else {
      // 重置表单
      form.resetFields()
      setImageUrl('')
      setFileList([])
    }
  }, [userDetail, isCreating, form])

  // 返回上一页
  const handleBack = () => {
    navigate(-1)
  }

  // 处理表单提交
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields()
      
      // 处理表单数据
      const userData = {
        ...values,
        status: values.status ? 'active' : 'inactive',
        avatar: imageUrl || undefined,
      }
      
      // 如果是创建用户，需要密码
      if (isCreating && !userData.password) {
        message.error('创建用户必须设置密码')
        return
      }
      
      // 如果是编辑用户且没有填写密码，则不修改密码
      if (!isCreating && !userData.password) {
        delete userData.password
      }
      
      // 提交数据
      if (isCreating) {
        dispatch(createUser(userData))
        message.success('用户创建成功')
      } else {
        dispatch(updateUser({ id, ...userData }))
        message.success('用户更新成功')
      }
      
      // 返回用户列表页
      navigate('/user/manage')
    } catch (error) {
      message.error('表单验证失败，请检查输入内容')
    }
  }

  // 处理文件上传
  const handleUploadChange = ({ fileList: newFileList, file }: any) => {
    setFileList(newFileList)
    
    // 模拟上传成功
    if (file.status === 'done') {
      // 实际项目中应该使用上传后的图片URL
      const mockUrl = URL.createObjectURL(file.originFileObj)
      setImageUrl(mockUrl)
      message.success(`${file.name} 文件上传成功`)
    } else if (file.status === 'error') {
      message.error(`${file.name} 文件上传失败`)
    }
  }

  // 上传配置
  const uploadProps = {
    name: 'avatar',
    fileList,
    onChange: handleUploadChange,
    beforeUpload: (file: File) => {
      const isJpgOrPng = file.type === 'image/jpeg' || file.type === 'image/png'
      if (!isJpgOrPng) {
        message.error('只能上传 JPG/PNG 格式的图片!')
      }
      const isLt2M = file.size / 1024 / 1024 < 2
      if (!isLt2M) {
        message.error('图片大小不能超过 2MB!')
      }
      return isJpgOrPng && isLt2M
    },
    // 实际项目中应该配置action
    action: '/api/upload',
  }

  return (
    <div className="fade-in">
      <div className="flex items-center justify-between mb-6">
        <Title level={4} className="mb-0">{isCreating ? '创建用户' : '编辑用户'}</Title>
        <Button onClick={handleBack} icon={<ArrowLeftOutlined />}>返回列表</Button>
      </div>

      {/* 用户表单 */}
      <Card className="mb-6">
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            status: true,
            role: 'user',
          }}
        >
          <div className="flex flex-col sm:flex-row items-center justify-start mb-6">
            <Upload {...uploadProps}>
              {imageUrl ? (
                <Avatar size={120} src={imageUrl} />
              ) : (
                <div className="flex items-center justify-center w-30 h-30 border border-dashed rounded-full">
                  <UploadOutlined />
                  <Text className="ml-2">上传头像</Text>
                </div>
              )}
            </Upload>
            <Text type="secondary" className="mt-2 sm:ml-6">支持 JPG、PNG 格式，大小不超过 2MB</Text>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Form.Item
              name="username"
              label="用户名"
              rules={[
                { required: true, message: '请输入用户名' },
                { min: 3, max: 20, message: '用户名长度应在 3-20 个字符之间' },
                { pattern: /^[a-zA-Z0-9_]+$/, message: '用户名只能包含字母、数字和下划线' },
              ]}
            >
              <Input prefix={<UserOutlined />} placeholder="请输入用户名" />
            </Form.Item>

            <Form.Item
              name="email"
              label="邮箱"
              rules={[
                { required: true, message: '请输入邮箱' },
                { type: 'email', message: '请输入有效的邮箱地址' },
              ]}
            >
              <Input prefix={<MailOutlined />} placeholder="请输入邮箱" />
            </Form.Item>

            {isCreating && (
              <Form.Item
                name="password"
                label="密码"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, max: 20, message: '密码长度应在 6-20 个字符之间' },
                ]}
              >
                <Password prefix={<LockOutlined />} placeholder="请输入密码" />
              </Form.Item>
            )}

            {!isCreating && (
              <Form.Item
                name="password"
                label="密码（留空不修改）"
                rules={[
                  { min: 6, max: 20, message: '密码长度应在 6-20 个字符之间' },
                ]}
              >
                <Password prefix={<LockOutlined />} placeholder="留空不修改密码" />
              </Form.Item>
            )}

            <Form.Item
              name="phone"
              label="电话"
              rules={[
                { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码' },
              ]}
            >
              <Input prefix={<PhoneOutlined />} placeholder="请输入手机号码" />
            </Form.Item>

            <Form.Item
              name="role"
              label="角色"
              rules={[{ required: true, message: '请选择角色' }]}
            >
              <Select placeholder="请选择角色">
                <Option value="admin">管理员</Option>
                <Option value="editor">编辑</Option>
                <Option value="viewer">查看者</Option>
                <Option value="user">普通用户</Option>
              </Select>
            </Form.Item>

            <Form.Item
              name="department"
              label="部门"
            >
              <Input placeholder="请输入部门" />
            </Form.Item>

            <Form.Item
              name="position"
              label="职位"
            >
              <Input placeholder="请输入职位" />
            </Form.Item>

            <Form.Item
              name="status"
              label="状态"
              valuePropName="checked"
              className="md:col-span-2"
            >
              <Switch checkedChildren="启用" unCheckedChildren="禁用" />
            </Form.Item>
          </div>

          {/* 权限设置（仅管理员可见） */}
          {!isCreating && userDetail?.role === 'admin' && (
            <div className="mt-6">
              <Typography.Title level={5}>权限设置</Typography.Title>
              <Form.Item
                name="permissions"
                label="权限"
                rules={[{ required: false }]}
              >
                <Select mode="multiple" placeholder="请选择权限">
                  <Option value="view_dashboard">查看仪表盘</Option>
                  <Option value="manage_opinions">管理舆情</Option>
                  <Option value="manage_hot_topics">管理热点话题</Option>
                  <Option value="manage_users">管理用户</Option>
                  <Option value="manage_settings">管理设置</Option>
                </Select>
              </Form.Item>
            </div>
          )}

          {/* 提交按钮 */}
          <div className="flex justify-end mt-8">
            <Space>
              <Button onClick={handleBack}>取消</Button>
              <Button type="primary" icon={<SaveOutlined />} onClick={handleSubmit} loading={loading}>
                {isCreating ? '创建用户' : '保存更改'}
              </Button>
            </Space>
          </div>
        </Form>
      </Card>
    </div>
  )
}

export default UserEdit