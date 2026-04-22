// API数据缓存模块 - 性能优化版本
import { getOpinions as getOpinionsApi } from '../api/databaseApi';

// 舆情数据类型定义
interface Opinion {
  id: string;
  content: string;
  platform: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  published_at: string;
  url?: string;
  author?: string;
  [key: string]: any;
}

// API响应类型
interface ApiResponse {
  items: Opinion[];
  total?: number;
}

// 缓存统计
interface CacheStats {
  hits: number;
  misses: number;
  requests: number;
  cacheSize: number;
}

// 缓存项接口
interface CacheItem {
  data: Opinion[];
  timestamp: number;
  params: { skip: number; limit: number };
  lastAccessTime: number; // 最后访问时间，用于LRU缓存策略
}

// 缓存配置
const CACHE_CONFIG = {
  DURATION: 30000, // 缓存30秒（从1分钟减少到30秒，提高数据新鲜度）
  MAX_ITEMS: 20, // 最大缓存项数（从10增加到20）
  WARMUP_BATCH_SIZE: 500, // 预热批次大小
};

// 缓存存储 - 使用Map提高查找性能
const cachedApiData = new Map<string, CacheItem>();
let fetchPromises: Record<string, Promise<Opinion[]>> = {}; // 用于处理并发请求的锁
let cacheStats: CacheStats = { hits: 0, misses: 0, requests: 0, cacheSize: 0 };
let isWarmingUp = false;

// 生成缓存键
const generateCacheKey = (skip: number, limit: number): string => {
  return `skip:${skip}-limit:${limit}`;
};

// LRU缓存策略 - 按最后访问时间排序，移除最久未使用的缓存
const evictLRUCache = () => {
  if (cachedApiData.size <= CACHE_CONFIG.MAX_ITEMS) return;
  
  // 找到最后访问时间最早的缓存项
  let oldestAccessTime = Infinity;
  let lruKey: string | null = null;
  
  cachedApiData.forEach((item, key) => {
    if (item.lastAccessTime< oldestAccessTime) {
      oldestAccessTime = item.lastAccessTime;
      lruKey = key;
    }
  });
  
  // 移除最久未使用的缓存项
  if (lruKey) {
    cachedApiData.delete(lruKey);
  }
};

// 更新缓存最后访问时间
const updateCacheAccess = (cacheKey: string) => {
  const cachedItem = cachedApiData.get(cacheKey);
  if (cachedItem) {
    cachedItem.lastAccessTime = Date.now();
  }
};

// 缓存预热函数 - 并行处理优化
export const warmupCache = async () => {
  if (isWarmingUp) return;
  isWarmingUp = true;
  
  try {
    console.log(`[${new Date().toISOString()}] 开始缓存预热...`);
    const totalItems = 1000; // 预热1000条数据
    const batches = Math.ceil(totalItems / CACHE_CONFIG.WARMUP_BATCH_SIZE);
    const batchPromises: Promise<Opinion[]>[] = [];
    
    console.log(`[${new Date().toISOString()}] 预热配置: 总条数=${totalItems}, 批次大小=${CACHE_CONFIG.WARMUP_BATCH_SIZE}, 批次数=${batches}`);
    
    // 创建所有批次的请求Promise
    for (let i = 0; i < batches; i++) {
      const skip = i * CACHE_CONFIG.WARMUP_BATCH_SIZE;
      const limit = Math.min(CACHE_CONFIG.WARMUP_BATCH_SIZE, totalItems - skip);
      batchPromises.push(fetchApiData(skip, limit));
    }
    
    // 并行执行所有批次请求
    const results = await Promise.all(batchPromises);
    const totalCachedItems = results.reduce((sum, result) => sum + result.length, 0);
    
    console.log(`[${new Date().toISOString()}] 缓存预热完成，共缓存 ${totalCachedItems} 条数据`);
  } catch (error) {
    console.error(`[${new Date().toISOString()}] 缓存预热失败:`, error);
    console.error('错误详情:', (error as Error).stack);
  } finally {
    isWarmingUp = false;
  }
};

// 获取API数据的辅助函数 - 优化版本
export const fetchApiData = async (skip: number = 0, limit: number = 1000): Promise<Opinion[]>=> {
  const now = Date.now();
  const cacheKey = generateCacheKey(skip, limit);
  
  // 更新统计
  cacheStats.requests++;
  
  // 检查缓存是否存在且未过期
  const cachedItem = cachedApiData.get(cacheKey);
  if (cachedItem && now - cachedItem.timestamp< CACHE_CONFIG.DURATION) {
    console.log(`[${new Date().toISOString()}] 使用缓存数据: ${cacheKey}`);
    cacheStats.hits++;
    updateCacheAccess(cacheKey);
    return cachedItem.data;
  }
  
  // 缓存未命中
  cacheStats.misses++;
  
  // 如果已经有一个请求正在获取数据，等待它完成
  const pendingPromise = fetchPromises[cacheKey];
  if (pendingPromise) {
    console.log(`[${new Date().toISOString()}] 等待正在进行的请求: ${cacheKey}`);
    return pendingPromise;
  }
  
  // 否则从API获取数据
  try {
    // 创建一个新的Promise来获取数据
    console.log(`[${new Date().toISOString()}] 发送API请求: ${cacheKey}`);
    fetchPromises[cacheKey] = (async () =>{
      const startTime = Date.now();
      const apiData = await getOpinionsApi(skip, limit);
      const endTime = Date.now();
      
      console.log(`[${new Date().toISOString()}] API请求完成: ${cacheKey}, 耗时: ${endTime - startTime}ms, 返回 ${apiData.length} 条数据`);
      
      // 更新缓存
      const newCacheItem: CacheItem = {
        data: apiData,
        timestamp: now,
        params: { skip, limit },
        lastAccessTime: now // 初始最后访问时间为当前时间
      };
      
      // 添加新缓存（Map会自动覆盖同名key）
      cachedApiData.set(cacheKey, newCacheItem);
      
      // 应用LRU缓存策略
      evictLRUCache();
      
      // 更新缓存统计
      cacheStats.cacheSize = cachedApiData.size;
      
      return apiData;
    })();
    
    // 等待请求完成
    const result = await fetchPromises[cacheKey];
    return result;
  } catch (error) {
    console.error(`[${new Date().toISOString()}] 获取API数据失败: ${cacheKey}`, error);
    console.error('错误详情:', (error as Error).stack);
    
    // 如果获取失败，返回缓存数据（如果有），否则返回空数组
    const oldCachedItem = cachedApiData.get(cacheKey);
    if (oldCachedItem) {
      console.log(`[${new Date().toISOString()}] 返回过期缓存数据: ${cacheKey}`);
      return oldCachedItem.data;
    }
    console.log(`[${new Date().toISOString()}] 无缓存数据可用，返回空数组: ${cacheKey}`);
    return [];
  } finally {
    // 无论成功还是失败，都清除锁
    delete fetchPromises[cacheKey];
  }
};

// 清除缓存
export const clearApiCache = () => {
  cachedApiData.clear();
  fetchPromises = {};
  cacheStats = { hits: 0, misses: 0, requests: 0, cacheSize: 0 };
};

// 获取缓存统计
export const getCacheStats = (): CacheStats => {
  return { ...cacheStats };
};

// 定期清理过期缓存
setInterval(() => {
  const now = Date.now();
  let deletedCount = 0;
  
  cachedApiData.forEach((item, key) => {
    if (now - item.timestamp >= CACHE_CONFIG.DURATION) {
      cachedApiData.delete(key);
      deletedCount++;
    }
  });
  
  cacheStats.cacheSize = cachedApiData.size;
  
  if (deletedCount >0) {
    console.log(`清理了 ${deletedCount} 个过期缓存`);
  }
}, 60000); // 每分钟清理一次
