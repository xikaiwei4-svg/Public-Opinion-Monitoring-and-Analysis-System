import React from 'react'
import ReactDOM from 'react-dom/client'

const App: React.FC = () => {
  return (
    <div style={{ textAlign: 'center', padding: '50px' }}>
      <h1>测试页面</h1>
      <p>如果能看到这个页面，说明Vite配置基本正常</p>
    </div>
  )
}

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
)

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)