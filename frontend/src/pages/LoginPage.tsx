import React, { useState, useEffect } from 'react'
import { Card, Form, Input, Button, Checkbox, Typography, Alert, Row, Col, message } from 'antd'
import { LockOutlined, UserOutlined, EyeInvisibleOutlined, EyeTwoTone } from '@ant-design/icons'
import { useDispatch, useSelector } from 'react-redux'
import { login, fetchCurrentUser, selectUserLoading, selectUserError } from '../store/features/userSlice'
import { useNavigate, useLocation, Link } from 'react-router-dom'

const { Title, Paragraph } = Typography
const { Password } = Input

const LoginPage: React.FC = () => {
  const dispatch = useDispatch()
  const loading = useSelector(selectUserLoading)
  const error = useSelector(selectUserError)
  const navigate = useNavigate()
  const location = useLocation()
  const [form] = Form.useForm()
  const [showPassword, setShowPassword] = useState(false)

  // 获取登录成功后要跳转的路径，如果没有则跳转到首页
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/'

  // 处理登录表单提交
  const handleLogin = async (values: { username: string; password: string; remember: boolean }) => {
    try {
      // 调用登录action
      await dispatch(login(values)).unwrap()
      // 登录成功后跳转到之前的页面或首页
      navigate(from, { replace: true })
    } catch (err) {
      // 登录失败，错误信息已经在userSlice中处理
      console.error('登录失败:', err)
    }
  }

  // 切换密码显示/隐藏
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  // 检查登录状态，如果已登录则直接跳转到首页
  useEffect(() => {
    const checkLoginStatus = async () => {
      const token = localStorage.getItem('token')
      if (token) {
        try {
          // 验证token有效性
          await dispatch(fetchCurrentUser()).unwrap()
          navigate(from, { replace: true })
        } catch (error) {
          // token无效或过期，继续显示登录页面
          localStorage.removeItem('token')
        }
      }
    }

    checkLoginStatus()
  }, [navigate, from, dispatch])

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <Row className="w-full max-w-5xl">
        {/* 左侧图片区域 */}
        <Col xs={0} md={12} className="hidden md:flex items-center justify-center">
          <div className="text-center p-8">
            <img 
              src="https://api.dicebear.com/7.x/bottts/svg?seed=campus" 
              alt="校园舆情系统" 
              className="h-24 w-24 mx-auto mb-6"
            />
            <Title level={2} className="mb-4">校园舆情检测与热点话题分析系统</Title>
            <Paragraph className="text-gray-600 mb-6">
              全面监测校园热点，智能分析舆情趋势，助力校园管理决策
            </Paragraph>
            <div className="flex justify-center gap-8 mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600">100+</div>
                <div className="text-gray-500">监测平台</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600">99.9%</div>
                <div className="text-gray-500">数据准确率</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600">24/7</div>
                <div className="text-gray-500">实时监测</div>
              </div>
            </div>
          </div>
        </Col>

        {/* 右侧登录表单 */}
        <Col xs={24} md={12} className="flex justify-center items-center">
          <Card className="w-full max-w-md shadow-lg">
            <Title level={3} className="text-center mb-6">欢迎登录</Title>
            
            {/* 错误提示 */}
            {error && (
              <Alert
                message="登录失败"
                description={error}
                type="error"
                showIcon
                className="mb-4"
              />
            )}

            {/* 登录表单 */}
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
                  prefix={<UserOutlined className="site-form-item-icon" />}
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
                <Password
                  prefix={<LockOutlined className="site-form-item-icon" />}
                  placeholder="请输入密码"
                  size="large"
                  iconRender={visible => (
                    visible ? <EyeTwoTone /> : <EyeInvisibleOutlined />
                  )}
                  visibilityToggle={{ visible: showPassword, onVisibleChange: togglePasswordVisibility }}
                />
              </Form.Item>

              <Form.Item>
                <Form.Item name="remember" valuePropName="checked" noStyle>
                  <Checkbox>记住我</Checkbox>
                </Form.Item>
                <a href="#" className="float-right" onClick={(e) => { e.preventDefault(); message.info('请联系系统管理员重置密码'); }}>忘记密码？</a>
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  className="w-full h-10 text-base"
                  loading={loading}
                >
                  {loading ? '登录中...' : '登录'}
                </Button>
              </Form.Item>

              <div className="text-center text-gray-500 text-sm">
                没有账号？<Link to="/register" className="text-blue-600 hover:text-blue-800">立即注册</Link>
              </div>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default LoginPage