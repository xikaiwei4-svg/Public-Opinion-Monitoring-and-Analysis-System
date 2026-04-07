import store from './store/index'

// 检查store是否能正常导入
console.log('Store imported successfully:', !!store)
console.log('Store state:', store.getState())

// 检查Redux工具包的功能是否正常工作
try {
  // 尝试dispatch一个简单的action
  store.dispatch({ type: 'test/action' })
  console.log('Dispatch test successful')
} catch (error) {
  console.error('Dispatch test failed:', error)
}