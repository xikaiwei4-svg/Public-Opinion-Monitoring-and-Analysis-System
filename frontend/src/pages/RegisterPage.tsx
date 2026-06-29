import React, { useState } from 'react'
import { Card, Form, Input, Button, Typography, Row, Col, message } from 'antd'
import { LockOutlined, UserOutlined, MailOutlined } from '@ant-design/icons'
import { Link, useNavigate } from 'react-router-dom'

const { Title, Paragraph } = Typography

const RegisterPage: React.FC = () => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

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
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: values.username, email: values.email, password: values.password }),
      })
      const data = await res.json()
      if (res.ok && data.code === 200) {
        message.success('注册成功！请登录')
        setTimeout(() => { navigate('/login') }, 1500)
      } else {
        message.error(data.detail || data.message || '注册失败')
      }
    } catch (error) {
      message.error('注册失败，请检查网络连接')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 50%, #f8f9fc 100%)',
      padding: 20,
    }}>
      <Row style={{ width: '100%', maxWidth: 900 }}>
        <Col xs={0} md={12} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Title level={2} style={{ marginBottom: 16, background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>加入我们</Title>
            <Paragraph style={{ color: '#888', marginBottom: 32, fontSize: 15 }}>
              创建账号，开始使用校园舆情检测与热点话题分析系统
            </Paragraph>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 48 }}>
              {[
                { value: '快速', label: '注册流程', color: '#667eea' },
                { value: '安全', label: '数据保护', color: '#52c41a' },
                { value: '便捷', label: '一键登录', color: '#764ba2' },
              ].map(item => (
                <div key={item.label} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: item.color }}>{item.value}</div>
                  <div style={{ color: '#999', fontSize: 13 }}>{item.label}</div>
                </div>
              ))}
            </div>
          </div>
        </Col>

        <Col xs={24} md={12} style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Card style={{ width: '100%', maxWidth: 400, borderRadius: 16, boxShadow: '0 8px 32px rgba(102, 126, 234, 0.1)' }}>
            <div style={{ textAlign: 'center', marginBottom: 28 }}>
              <div style={{
                width: 56, height: 56, margin: '0 auto 16px',
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                <UserOutlined style={{ fontSize: 26, color: '#fff' }} />
              </div>
              <Title level={3} style={{ margin: 0, color: '#1a1a2e' }}>创建账号</Title>
            </div>
            <Form form={form} layout="vertical" onFinish={handleRegister}>
              <Form.Item
                label="用户名" name="username"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名长度至少为3位' },
                  { max: 20, message: '用户名长度不能超过20位' }
                ]}
              >
                <Input prefix={<UserOutlined style={{ color: '#999' }} />} placeholder="请输入用户名" size="large" />
              </Form.Item>
              <Form.Item
                label="邮箱" name="email"
                rules={[
                  { required: true, message: '请输入邮箱' },
                  { type: 'email', message: '请输入有效的邮箱地址' }
                ]}
              >
                <Input prefix={<MailOutlined style={{ color: '#999' }} />} placeholder="请输入邮箱" size="large" />
              </Form.Item>
              <Form.Item
                label="密码" name="password"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码长度至少为6位' },
                ]}
              >
                <Input.Password prefix={<LockOutlined style={{ color: '#999' }} />} placeholder="请输入密码" size="large" />
              </Form.Item>
              <Form.Item
                label="确认密码" name="confirmPassword"
                rules={[
                  { required: true, message: '请确认密码' },
                  { min: 6, message: '密码长度至少为6位' }
                ]}
              >
                <Input.Password prefix={<LockOutlined style={{ color: '#999' }} />} placeholder="请再次输入密码" size="large" />
              </Form.Item>
              <Form.Item style={{ marginBottom: 12 }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block size="large"
                  style={{
                    height: 44, borderRadius: 10,
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    border: 'none', fontWeight: 600, fontSize: 15,
                  }}
                >
                  {loading ? '注册中...' : '注册'}
                </Button>
              </Form.Item>
              <div style={{ textAlign: 'center', color: '#999', fontSize: 13 }}>
                已有账号？<Link to="/login">立即登录</Link>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default RegisterPage
