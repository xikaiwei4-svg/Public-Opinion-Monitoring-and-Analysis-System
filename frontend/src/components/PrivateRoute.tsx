import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { selectIsAuthenticated } from '../store/features/userSlice'

interface PrivateRouteProps {
  children: React.ReactNode
  roles?: string[]
}

const PrivateRoute: React.FC<PrivateRouteProps> = ({ children, roles }) => {
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const location = useLocation()

  // 如果未登录，重定向到登录页面
  if (!isAuthenticated) {
    // 保存当前页面路径，登录后可以返回
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // 如果有角色限制，检查用户角色是否匹配
  // 注意：这里简化了角色检查逻辑，实际项目中需要从Redux store获取用户角色信息
  if (roles && roles.length > 0) {
    // 实际实现时，应该从Redux store获取用户角色信息
    // const userRole = useSelector(selectUserRole)
    // if (!roles.includes(userRole)) {
    //   return <Navigate to="/403" replace />
    // }
  }

  // 如果已登录且角色匹配（如果有角色限制），则渲染子组件
  return <>{children}</>
}

export default PrivateRoute