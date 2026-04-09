import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'

// 所有页面都同步加载
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import Dashboard from './pages/Dashboard'
import OpinionListPage from './pages/OpinionListPage'
import HotTopicListPage from './pages/HotTopicListPage'
import TrendDataPage from './pages/TrendDataPage'
import TrendAnalysisPage from './pages/TrendAnalysisPage'
import UserManagementPage from './pages/UserManagementPage'
import DatabaseManagePage from './pages/DatabaseManagePage'
import NotFound from './pages/NotFound'

// 对于尚未创建专门页面的路由，创建一个简单的临时组件
const TemporaryComponent = () => (
  <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
    <h2>页面开发中</h2>
    <p>该功能正在开发中，敬请期待...</p>
  </div>
);

const App: React.FC = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="opinion/list" element={<OpinionListPage />} />
        <Route path="hot-topic/list" element={<HotTopicListPage />} />
        <Route path="test/trend-data" element={<TrendDataPage />} />
        <Route path="trend-analysis" element={<TrendAnalysisPage />} />
        <Route path="user/manage" element={<UserManagementPage />} />
        <Route path="database/manage" element={<DatabaseManagePage />} />
        <Route path="settings" element={<TemporaryComponent />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App