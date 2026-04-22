import axios, { AxiosInstance } from 'axios';

// 创建axios实例，真正调用后端API
export const apiClient: AxiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 真正的API请求函数
export const handleApiRequest = async <T>(config: { method: string, url: string, data?: any, params?: any }): Promise<T>=> {
  try {
    // 真正调用后端API
    const response = await apiClient.request({
      method: config.method,
      url: config.url,
      data: config.data,
      params: config.params
    });
    
    // 返回后端响应数据
    return response.data as T;
  } catch (error) {
    console.error('API请求失败:', error);
    // 抛出错误，让调用者处理
    throw error;
  }
};

// 获取单个舆情详情的模拟数据（保持向后兼容性）
export const getMockOpinionDetail = async (id: string) => {
  try {
    const response = await apiClient.get(`/api/opinion/${id}`);
    return response.data;
  } catch (error) {
    console.error('获取舆情详情失败:', error);
    throw error;
  }
};

// 获取单个热点话题详情的模拟数据（保持向后兼容性）
export const getMockHotTopicDetail = async (id: string) => {
  try {
    const response = await apiClient.get(`/api/hot-topic/${id}`);
    return response.data;
  } catch (error) {
    console.error('获取热点话题详情失败:', error);
    throw error;
  }
};

// 获取单个用户详情的模拟数据（保持向后兼容性）
export const getMockUserDetail = async (id: string) => {
  try {
    const response = await apiClient.get(`/api/users/${id}`);
    return response.data;
  } catch (error) {
    console.error('获取用户详情失败:', error);
    throw error;
  }
};
