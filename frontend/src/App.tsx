import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import NotFound from './pages/NotFound'
import TestPage from './pages/TestPage'
import OpinionListPage from './pages/OpinionListPage'
import HotTopicListPage from './pages/HotTopicListPage'
import TrendDataPage from './pages/TrendDataPage'
import UserManagementPage from './pages/UserManagementPage'
import DatabaseManagePage from './pages/DatabaseManagePage'

const App: React.FC = () => {
  // 对于尚未创建专门页面的路由，继续使用TestPage作为临时组件
  const TemporaryComponent = TestPage;
  
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/test" element={<TestPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        {/* 为SideMenu中的菜单项添加对应的路由，使用实际组件 */}
        <Route path="opinion/list" element={<OpinionListPage />} />
        <Route path="hot-topic/list" element={<HotTopicListPage />} />
        <Route path="test/trend-data" element={<TrendDataPage />} />
        <Route path="user/manage" element={<UserManagementPage />} />
        <Route path="database/manage" element={<DatabaseManagePage />} />
        <Route path="settings" element={<TemporaryComponent />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}

export default App