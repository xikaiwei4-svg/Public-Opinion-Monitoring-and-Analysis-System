import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
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

// 获取舆情数据列表
export const getOpinions = async (skip: number = 0, limit: number = 100) => {
  const response = await api.get(`/api/database/opinions?skip=${skip}&limit=${limit}`)
  return response.data
}

// 获取舆情数据列表（带总数）
export const getOpinionsWithTotal = async (skip: number = 0, limit: number = 100) => {
  const response = await api.get(`/api/database/opinions?skip=${skip}&limit=${limit}`)
  return response.data
}

// 创建舆情数据
export const createOpinion = async (opinionData: any) => {
  const response = await api.post('/api/database/opinions', opinionData)
  return response.data
}

export default api
