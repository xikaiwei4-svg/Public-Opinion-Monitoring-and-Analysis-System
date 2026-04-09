import React, { useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Provider } from 'react-redux'
import App from './App'
import store from './store'
import { warmupCache } from './utils/apiCache'
import { fetchCurrentUser } from './store/features/userSlice'

// 性能监控和用户状态恢复组件
const PerformanceMonitor: React.FC = () => {
  useEffect(() => {
    // 恢复用户状态
    const token = localStorage.getItem('token')
    if (token) {
      store.dispatch(fetchCurrentUser())
    }
    
    // 启动缓存预热
    warmupCache().catch(error => {
      console.error('缓存预热失败:', error)
    })
    
    // 性能监控
    const performanceObserver = new PerformanceObserver((list) => {
      list.getEntries().forEach(entry => {
        if (entry.entryType === 'measure' && entry.duration > 100) {
          console.warn(`性能警告: ${entry.name} 耗时 ${entry.duration.toFixed(2)}ms`)
        }
      })
    })
    
    performanceObserver.observe({ entryTypes: ['measure'] })
    
    return () => {
      performanceObserver.disconnect()
    }
  }, [])
  
  return null
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
)

root.render(
  <React.StrictMode>
    <Provider store={store}>
      <BrowserRouter>
        <PerformanceMonitor />
        <App />
      </BrowserRouter>
    </Provider>
  </React.StrictMode>
)