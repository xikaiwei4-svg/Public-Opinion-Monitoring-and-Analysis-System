import axios from 'axios'

// 注意：API_BASE_URL 从 .env.production 读取
// 在 Docker 部署中 VITE_API_BASE_URL=/api，但 API 路径已包含 /api/ 前缀
// 所以这里不用 baseURL（留空），让请求走同源的完整路径
const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 获取数据库统计信息
export const getDatabaseStats = async () => {
  const response = await api.get('/api/database/stats')
  return response.data
}

// 获取集合列表
export const getCollections = async () => {
  const response = await api.get('/api/database/collections')
  return response.data
}

// 获取集合详情
export const getCollectionDetail = async (collectionName: string) => {
  const response = await api.get(`/api/database/collections/${collectionName}`)
  return response.data
}

// 删除集合
export const deleteCollection = async (collectionName: string) => {
  const response = await api.delete(`/api/database/collections/${collectionName}`)
  return response.data
}

// 获取数据库配置
export const getDatabaseConfig = async () => {
  const response = await api.get('/api/database/config')
  return response.data
}

// 运行爬虫任务
export const runCrawler = async (platform: string = 'all', keywords?: string[]) => {
  const response = await api.post('/api/database/crawler/run', { platform, keywords })
  return response.data
}

// 获取爬虫任务状态
export const getCrawlerTaskStatus = async (taskId: string) => {
  const response = await api.get(`/api/database/crawler/task/${taskId}`)
  return response.data
}

// 添加数据库配置
export const addDatabaseConfig = async (config: any) => {
  const response = await api.post('/api/database/config', config)
  return response.data
}

// 更新数据库配置
export const updateDatabaseConfig = async (id: string, config: any) => {
  const response = await api.put(`/api/database/config/${id}`, config)
  return response.data
}

// 删除数据库配置
export const removeDatabaseConfig = async (id: string) => {
  const response = await api.delete(`/api/database/config/${id}`)
  return response.data
}

// 获取数据库统计
export const getDatabaseStatsDetail = async (days: number = 7) => {
  const response = await api.get(`/api/database/stats?days=${days}`)
  return response.data
}

// 获取数据库日志
export const getDatabaseLogs = async (page: number = 1, pageSize: number = 20) => {
  const response = await api.get(`/api/database/logs?page=${page}&pageSize=${pageSize}`)
  return response.data
}

// 初始化数据库
export const initDatabase = async () => {
  const response = await api.post('/api/database/init')
  return response.data
}

// 删除集合中的所有文档
export const clearCollection = async (collectionName: string) => {
  const response = await api.delete(`/api/database/collections/${collectionName}/clear`)
  return response.data
}
