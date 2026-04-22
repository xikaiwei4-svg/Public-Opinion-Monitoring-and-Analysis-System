import React, { useState } from 'react'
import { Card, Form, Input, Button, Typography, Row, Col, message } from 'antd'
import { LockOutlined, UserOutlined, MailOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons'
import { Link } from 'react-router-dom'

const { Title, Paragraph } = Typography
const { Password } = Input

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm()
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleRegister = async (values: { 
    username: string; 
    email: string; 
    password: string; 
    confirmPassword: string 
  }) => {
    if (values.password !== values.confirmPassword) {
      message.error('两次输入的密码不一致')
      return
    }

    setLoading(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      message.success('注册成功！请登录')
      setTimeout(() => {
        window.location.href = '/login'
      }, 1500)
    } catch (error) {
      message.error('注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-purple-50 p-4">
      <Row className="w-full max-w-4xl">
        {/* 左侧信息区域 */}
        <Col xs={0} md={12} className="hidden md:flex items-center justify-center">
          <div className="text-center p-8">
            <Title level={2} className="mb-4">加入我们</Title>
            <Paragraph className="text-gray-600 mb-6">
              创建您的账号，开始使用校园舆情检测与热点话题分析系统
            </Paragraph>
            <div className="flex justify-center gap-8 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">快速</div>
                <div className="text-gray-500">注册流程</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">安全</div>
                <div className="text-gray-500">数据保护</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">便捷</div>
                <div className="text-gray-500">一键登录</div>
              </div>
            </div>
          </div>
        </Col>

        {/* 右侧注册表单 */}
        <Col xs={24} md={12} className="flex justify-center items-center">
          <Card className="w-full max-w-md shadow-lg">
            <Title level={3} className="text-center mb-6">创建账号</Title>

            <Form
              form={form}
              layout="vertical"
              onFinish={handleRegister}
            >
              <Form.Item
                label="用户名"
                name="username"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名长度至少为3位' },
                  { max: 20, message: '用户名长度不能超过20位' }
                ]}
              >
                <Input
                  prefix={<UserOutlined className="site-form-item-icon" />}
                  placeholder="请输入用户名"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label="邮箱"
                name="email"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input
                  prefix={<MailOutlined className="site-form-item-icon" />}
                  placeholder="请输入邮箱"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label="密码"
                name="password"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码长度至少为6位' },
                  { max: 20, message: '密码长度不能超过20位' }
                ]}
              >
                <Password
                  prefix={<LockOutlined className="site-form-item-icon" />}
                  placeholder="请输入密码"
                  size="large"
                  iconRender={visible => (
                    visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                  )}
                  visibilityToggle={{ visible: showPassword, onVisibleChange: setShowPassword }}
                />
              </Form.Item>

              <Form.Item
                label="确认密码"
                name="confirmPassword"
                rules={[
                  { required: true, message: '请确认密码' },
                  { min: 6, message: '密码长度至少为6位' }
                ]}
              >
                <Password
                  prefix={<LockOutlined className="site-form-item-icon" />}
                  placeholder="请再次输入密码"
                  size="large"
                  iconRender={visible => (
                    visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                  )}
                  visibilityToggle={{ visible: showConfirmPassword, onVisibleChange: setShowConfirmPassword }}
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  className="w-full h-10 text-base"
                  loading={loading}
                >
                  {loading ? '注册中...' : '注册'}
                </Button>
              </Form.Item>

              <div className="text-center text-gray-500 text-sm">
                已有账号？<Link to="/login" className="text-blue-600 hover:text-blue-800">立即登录</Link>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default RegisterPage
