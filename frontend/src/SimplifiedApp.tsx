import React from 'react'
import ReactDOM from 'react-dom/client'

// 最简单的App组件，不依赖任何外部组件或库
const App: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '20px',
      backgroundColor: '#f0f2f5'
    }}>
      <h1 style={{
        color: '#1890ff',
        fontSize: '32px',
        marginBottom: '20px'
      }}>
        React应用运行成功！
      </h1>
      <p style={{
        color: '#333',
        fontSize: '16px',
        textAlign: 'center',
        maxWidth: '600px'
      }}>
        这是一个完全简化的React应用，没有使用Redux、路由或其他复杂依赖。
        现在应用可以正常运行而不会出现Redux上下文错误。
      </p>
    </div>
  )
}

// 渲染应用
const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
)

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)