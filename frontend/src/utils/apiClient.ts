import axios, { AxiosInstance } from 'axios';

export const apiClient: AxiosInstance = axios.create({
  baseURL: '',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token && token !== 'mock-jwt-token') {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const handleApiRequest = async <T>(config: { method: string, url: string, data?: any, params?: any }): Promise<T> => {
  try {
    const response = await apiClient.request({
      method: config.method,
      url: config.url,
      data: config.data,
      params: config.params
    });
    return response.data as T;
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export const getOpinionDetailById = async (id: string) => {
  try {
    const response = await apiClient.get(`/api/opinion/${id}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get opinion detail:', error);
    throw error;
  }
};

export const getHotTopicDetailById = async (id: string) => {
  try {
    const response = await apiClient.get(`/api/hot-topic/${id}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get hot topic detail:', error);
    throw error;
  }
};

export const getUserDetailById = async (id: string) => {
  try {
    const response = await apiClient.get(`/api/users/${id}`);
    return response.data;
  } catch (error) {
    console.error('Failed to get user detail:', error);
    throw error;
  }
};
