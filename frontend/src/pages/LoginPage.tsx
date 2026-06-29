import React, { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Checkbox, Typography, Alert, Row, Col, message } from 'antd'
import { LockOutlined, UserOutlined } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { login, fetchCurrentUser, selectUserLoading, selectUserError } from '../store/features/userSlice'
import { useNavigate, useLocation, Link } from 'react-router-dom'

const { Title, Paragraph } = Typography

const LoginPage: React.FC = () => {
  const dispatch = useDispatch()
  const loading = useSelector(selectUserLoading)
  const error = useSelector(selectUserError)
  const navigate = useNavigate()
  const location = useLocation()
  const [form] = Form.useForm()

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/'

  const handleLogin = async (values: { username: string; password: string; remember: boolean }) => {
    try {
      await dispatch(login(values)).unwrap()
      navigate(from, { replace: true })
    } catch (err) {
      console.error('登录失败:', err)
    }
  }

  useEffect(() => {
    const checkLoginStatus = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          await dispatch(fetchCurrentUser()).unwrap()
          navigate(from, { replace: true })
        } catch (error) {
          localStorage.removeItem('token')
        }
      }
    }
    checkLoginStatus()
  }, [navigate, from, dispatch])

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 50%, #f8f9fc 100%)',
      padding: 20,
    }}>
      <Row style={{ width: '100%', maxWidth: 960 }}>
        <Col xs={0} md={12} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Title level={2} style={{ marginBottom: 16, background: 'linear-gradient(135deg, #667eea, #764ba2)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
              校园舆情检测与热点话题分析系统
            </Title>
            <Paragraph style={{ color: '#888', marginBottom: 32, fontSize: 15 }}>
              全面监测校园热点，智能分析舆情趋势，助力校园管理决策
            </Paragraph>
            <div style={{ display: 'flex', justifyContent: 'center', gap: 48 }}>
              {[
                { value: '100+', label: '监测平台', color: '#667eea' },
                { value: '99.9%', label: '数据准确率', color: '#52c41a' },
                { value: '24/7', label: '实时监测', color: '#764ba2' },
              ].map(item => (
                <div key={item.label} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: item.color }}>{item.value}</div>
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
              <Title level={3} style={{ margin: 0, color: '#1a1a2e' }}>欢迎登录</Title>
            </div>

            {error && (
              <Alert
                message="登录失败"
                description={error}
                type="error"
                showIcon
                style={{ marginBottom: 16 }}
              />
            )}

            <Form
              form={form}
              layout="vertical"
              onFinish={handleLogin}
              initialValues={{
                username: 'admin',
                password: 'admin123',
                remember: true
              }}
            >
              <Form.Item
                label="用户名"
                name="username"
                rules={[
                  { required: true, message: '请输入用户名' },
                  { min: 3, message: '用户名长度至少为3位' }
                ]}
              >
                <Input
                  prefix={<UserOutlined style={{ color: '#999' }} />}
                  placeholder="请输入用户名"
                  size="large"
                />
              </Form.Item>

              <Form.Item
                label="密码"
                name="password"
                rules={[
                  { required: true, message: '请输入密码' },
                  { min: 6, message: '密码长度至少为6位' }
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined style={{ color: '#999' }} />}
                  placeholder="请输入密码"
                  size="large"
                />
              </Form.Item>

              <Form.Item>
                <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                  <Form.Item name="remember" valuePropName="checked" noStyle>
                    <Checkbox>记住我</Checkbox>
                  </Form.Item>
                  <a href="#" onClick={(e) => { e.preventDefault(); message.info('请联系系统管理员重置密码'); }}>
                    忘记密码？
                  </a>
                </div>
              </Form.Item>

              <Form.Item style={{ marginBottom: 12 }}>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={loading}
                  block
                  size="large"
                  style={{
                    height: 44,
                    borderRadius: 10,
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    border: 'none',
                    fontWeight: 600,
                    fontSize: 15,
                  }}
                >
                  {loading ? '登录中...' : '登录'}
                </Button>
              </Form.Item>

              <div style={{ textAlign: 'center', color: '#999', fontSize: 13 }}>
                没有账号？<Link to="/register">立即注册</Link>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default LoginPage
