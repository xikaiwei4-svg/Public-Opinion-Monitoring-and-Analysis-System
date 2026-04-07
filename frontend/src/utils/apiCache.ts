// API数据缓存模块
import { getOpinions as getOpinionsApi } from '../api/databaseApi';

// 缓存API数据，避免重复请求
interface CacheItem {
  data: any[];
  timestamp: number;
  params: { skip: number; limit: number };
}

const cachedApiData: CacheItem[] = [];
const CACHE_DURATION = 60000; // 缓存1分钟
const MAX_CACHE_ITEMS = 10; // 最大缓存项数
let fetchPromises: Record<string, Promise<any[]>> = {}; // 用于处理并发请求的锁

// 生成缓存键
const generateCacheKey = (skip: number, limit: number): string => {
  return `skip:${skip}-limit:${limit}`;
};

// 获取API数据的辅助函数
export const fetchApiData = async (skip: number = 0, limit: number = 1000): Promise<any[]> => {
  const now = Date.now();
  const cacheKey = generateCacheKey(skip, limit);
  
  // 检查缓存是否存在且未过期
  const cachedItem = cachedApiData.find(item => 
    item.params.skip === skip && 
    item.params.limit === limit && 
    now - item.timestamp < CACHE_DURATION
  );
  
  if (cachedItem) {
    console.log('使用缓存数据:', cacheKey);
    return cachedItem.data;
  }
  
  // 如果已经有一个请求正在获取数据，等待它完成
  if (fetchPromises[cacheKey]) {
    console.log('等待正在进行的请求:', cacheKey);
    return fetchPromises[cacheKey];
  }
  
  // 否则从API获取数据
  try {
    // 创建一个新的Promise来获取数据
    console.log('发送API请求:', cacheKey);
    fetchPromises[cacheKey] = (async () => {
      const apiResponse = await getOpinionsApi(skip, limit);
      const apiData = apiResponse.items || [];
      
      // 更新缓存
      const newCacheItem: CacheItem = {
        data: apiData,
        timestamp: now,
        params: { skip, limit }
      };
      
      // 移除旧缓存
      const existingIndex = cachedApiData.findIndex(item => 
        item.params.skip === skip && item.params.limit === limit
      );
      
      if (existingIndex >= 0) {
        cachedApiData.splice(existingIndex, 1);
      } else if (cachedApiData.length >= MAX_CACHE_ITEMS) {
        // 如果缓存已满，移除最早的缓存
        cachedApiData.shift();
      }
      
      // 添加新缓存
      cachedApiData.push(newCacheItem);
      
      return apiData;
    })();
    
    // 等待请求完成
    const result = await fetchPromises[cacheKey];
    return result;
  } catch (error) {
    console.error('获取API数据失败:', error);
    // 如果获取失败，返回缓存数据（如果有），否则返回空数组
    const oldCachedItem = cachedApiData.find(item => 
      item.params.skip === skip && item.params.limit === limit
    );
    
    if (oldCachedItem) {
      return oldCachedItem.data;
    }
    return [];
  } finally {
    // 无论成功还是失败，都清除锁
    delete fetchPromises[cacheKey];
  }
};

// 清除缓存
export const clearApiCache = () => {
  cachedApiData.length = 0;
  fetchPromises = {};
};
