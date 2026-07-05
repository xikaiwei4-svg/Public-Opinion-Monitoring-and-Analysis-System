import React, { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import { ConfigProvider, Spin } from 'antd'
import zhCN from 'antd/locale/zh_CN'
import Layout from './components/Layout'

import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import NotFound from './pages/NotFound'

// 懒加载重量级页面
const Dashboard = lazy(() => import('./pages/Dashboard'))
const OpinionListPage = lazy(() => import('./pages/OpinionListPage'))
const HotTopicListPage = lazy(() => import('./pages/HotTopicListPage'))
const TrendAnalysisPage = lazy(() => import('./pages/TrendAnalysisPage'))

const PageLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
    <Spin size="large" tip="加载中..." />
  </div>
)

const App: React.FC = () => (
  <ConfigProvider
    locale={zhCN}
    theme={{
      token: {
        colorPrimary: '#6366f1',
        colorInfo: '#6366f1',
        borderRadius: 10,
        colorBgLayout: '#f8fafc',
        colorBgContainer: '#ffffff',
        colorBgElevated: '#ffffff',
        colorBorderSecondary: '#e8ecf3',
        boxShadow: '0 2px 12px rgba(0, 0, 0, 0.04)',
        fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif",
      },
      components: {
        Menu: { itemBorderRadius: 10, itemMarginInline: 8, subMenuItemBg: 'transparent' },
        Card: { borderRadiusLG: 16, paddingLG: 20 },
        Button: { borderRadius: 8, controlHeight: 36 },
        Table: { borderRadius: 12, headerBg: '#f8fafc' },
        Input: { borderRadius: 8, controlHeight: 36 },
        Select: { borderRadius: 8, controlHeight: 36 },
        Spin: { dotSize: 20 },
      },
    }}
  >
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Suspense fallback={<PageLoader />}><Dashboard /></Suspense>} />
        <Route path="opinion/list" element={<Suspense fallback={<PageLoader />}><OpinionListPage /></Suspense>} />
        <Route path="hot-topic/list" element={<Suspense fallback={<PageLoader />}><HotTopicListPage /></Suspense>} />
        <Route path="trend-analysis" element={<Suspense fallback={<PageLoader />}><TrendAnalysisPage /></Suspense>} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  </ConfigProvider>
)

export default App
