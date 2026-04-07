import axios from 'axios';
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';
import { getOpinions as getOpinionsApi } from '../../api/databaseApi';
import { handleApiRequest } from '../../utils/mockData';

// 定义舆情项接口
export interface OpinionItem {
  id: string;
  content: string;
  source: string;
  source_platform: string;
  publish_time: string;
  crawl_time: string;
  sentiment: number;
  sentiment_type: 'positive' | 'negative' | 'neutral';
  keywords: string[];
  url?: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  heat_score: number;
  is_sensitive: boolean;
  sensitive_level: number;
  location?: string;
  user_info?: Record<string, any>;
  raw_data?: Record<string, any>;
}

// 定义舆情列表响应类型
export interface OpinionListResponse {
  items: OpinionItem[];
  total: number;
  page: number;
  page_size: number;
}

// 定义平台分布类型
export interface PlatformDistribution {
  platform: string;
  count: number;
  percentage: number;
}

// 定义统计数据类型
export interface StatisticsData {
  total_opinions: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  daily_trend: Array<{ date: string; count: number }>;
  platform_distribution: PlatformDistribution[];
  category_distribution: Array<{ category: string; count: number }>;
}

// 定义舆情状态类型
interface OpinionState {
  list: OpinionItem[];
  total: number;
  currentPage: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  selectedOpinion: OpinionItem | null;
  filters: {
    keyword: string;
    source: string;
    sentiment_type: string;
    start_time: string;
    end_time: string;
    is_sensitive: boolean | null;
    category: string;
  };
  statistics: StatisticsData | null;
}

// 初始状态
const initialState: OpinionState = {
  list: [],
  total: 0,
  currentPage: 1,
  pageSize: 10,
  loading: false,
  error: null,
  selectedOpinion: null,
  filters: {
    keyword: '',
    source: '',
    sentiment_type: '',
    start_time: '',
    end_time: '',
    is_sensitive: null,
    category: ''
  },
  statistics: null
};

// 异步获取舆情列表 - 使用真实API
export const fetchOpinions = createAsyncThunk(
  'opinion/fetchOpinions',
  async (params: {
    page: number;
    pageSize: number;
    keyword?: string;
    source?: string;
    sentiment_type?: string;
    start_time?: string;
    end_time?: string;
    is_sensitive?: boolean | null;
    category?: string;
  }) => {
    try {
      // 从真实API获取数据（使用缓存）
      const skip = (params.page - 1) * params.pageSize;
      const apiData = await fetchApiData(skip, params.pageSize);
      
      // 获取总数和items
      const total = 1000; // 假设总数为1000
      const items: OpinionItem[] = apiData.map((item: any) => ({
        id: String(item.id),
        content: item.content || item.title || '',
        source: item.author || item.source_platform || '未知来源',
        source_platform: item.source_platform || '未知平台',
        publish_time: item.publish_time || new Date().toISOString(),
        crawl_time: item.crawl_time || new Date().toISOString(),
        sentiment: item.sentiment_score || 0,
        sentiment_type: item.sentiment || 'neutral',
        keywords: item.keywords ? item.keywords.split(',') : [],
        url: item.source_url,
        views: item.read_count || 0,
        likes: item.like_count || 0,
        comments: item.comment_count || 0,
        shares: item.share_count || 0,
        heat_score: item.hot_score || 0,
        is_sensitive: false,
        sensitive_level: 0,
        location: undefined,
        user_info: undefined,
        raw_data: item
      }));
      
      // 过滤数据（仅对当前页数据进行过滤）
      let filteredItems = items;
      if (params.keyword) {
        filteredItems = filteredItems.filter(item => 
          item.content.includes(params.keyword!) || 
          item.source.includes(params.keyword!)
        );
      }
      if (params.source) {
        filteredItems = filteredItems.filter(item => 
          item.source_platform === params.source
        );
      }
      if (params.sentiment_type) {
        filteredItems = filteredItems.filter(item => 
          item.sentiment_type === params.sentiment_type
        );
      }
      
      return {
        items: filteredItems,
        total: total,  // 使用假设的总数
        page: params.page,
        page_size: params.pageSize
      };
    } catch (error) {
      console.error('获取舆情列表失败:', error);
      // 返回空数据，不回退到mock数据
      return {
        items: [],
        total: 0,
        page: params.page,
        page_size: params.pageSize
      };
    }
  }
);

// 异步获取舆情详情
export const fetchOpinionDetail = createAsyncThunk(
  'opinion/fetchOpinionDetail',
  async (id: string) => {
    try {
      const data = await handleApiRequest<OpinionItem>({
        method: 'GET',
        url: `/api/opinion/${id}`
      });
      return data;
    } catch (error) {
      console.error('获取舆情详情失败:', error);
      throw error;
    }
  }
);

// 导入API缓存模块
import { fetchApiData } from '../../utils/apiCache';

// 异步获取舆情统计数据 - 使用真实API
export const fetchOpinionStatistics = createAsyncThunk(
  'opinion/fetchOpinionStatistics',
  async (params: {
    start_time?: string;
    end_time?: string;
  }) => {
    console.log('fetchOpinionStatistics called with params:', params);
    try {
      // 从API获取数据（使用缓存）
      const apiData = await fetchApiData();
      
      // 计算统计数据
      const total_opinions = apiData.length;
      const positive_count = apiData.filter((item: any) => item.sentiment === 'positive').length;
      const negative_count = apiData.filter((item: any) => item.sentiment === 'negative').length;
      const neutral_count = apiData.filter((item: any) => item.sentiment === 'neutral').length;
      
      // 平台分布统计
      const platformMap = new Map<string, number>();
      apiData.forEach((item: any) => {
        const platform = item.source_platform || '未知平台';
        platformMap.set(platform, (platformMap.get(platform) || 0) + 1);
      });
      const platform_distribution = Array.from(platformMap.entries()).map(([platform, count]) => ({
        platform,
        count,
        percentage: Math.round((count / total_opinions) * 100)
      }));
      
      // 按日期统计
      const dateMap = new Map<string, number>();
      apiData.forEach((item: any) => {
        const date = item.publish_time ? item.publish_time.split('T')[0] : new Date().toISOString().split('T')[0];
        dateMap.set(date, (dateMap.get(date) || 0) + 1);
      });
      const daily_trend = Array.from(dateMap.entries())
        .sort(([a], [b]) => a.localeCompare(b))
        .slice(-7) // 最近7天
        .map(([date, count]) => ({ date, count }));
      
      // 分类统计（根据关键词简单分类）
      const categoryMap = new Map<string, number>();
      apiData.forEach((item: any) => {
        const keywords = item.keywords ? item.keywords.split(',') : [];
        if (keywords.length > 0) {
          const category = keywords[0];
          categoryMap.set(category, (categoryMap.get(category) || 0) + 1);
        }
      });
      const category_distribution = Array.from(categoryMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([category, count]) => ({ category, count }));
      
      return {
        total_opinions,
        positive_count,
        negative_count,
        neutral_count,
        daily_trend,
        platform_distribution,
        category_distribution
      };
    } catch (error) {
      console.error('获取舆情统计数据失败:', error);
      // 返回空数据，不回退到mock数据
      return {
        total_opinions: 0,
        positive_count: 0,
        negative_count: 0,
        neutral_count: 0,
        daily_trend: [],
        platform_distribution: [],
        category_distribution: []
      };
    }
  }
);

// 创建slice
const opinionSlice = createSlice({
  name: 'opinion',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<OpinionState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    setCurrentPage: (state, action: PayloadAction<number>) => {
      state.currentPage = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    clearSelectedOpinion: (state) => {
      state.selectedOpinion = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 获取舆情列表
      .addCase(fetchOpinions.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOpinions.fulfilled, (state, action) => {
        state.loading = false;
        state.list = action.payload.items;
        state.total = action.payload.total;
        state.currentPage = action.payload.page;
        state.pageSize = action.payload.page_size;
      })
      .addCase(fetchOpinions.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取舆情列表失败';
      })
      
      // 获取舆情详情
      .addCase(fetchOpinionDetail.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOpinionDetail.fulfilled, (state, action) => {
        state.loading = false;
        state.selectedOpinion = action.payload;
      })
      .addCase(fetchOpinionDetail.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取舆情详情失败';
      })
      
      // 获取舆情统计数据
      .addCase(fetchOpinionStatistics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOpinionStatistics.fulfilled, (state, action) => {
        state.loading = false;
        state.statistics = action.payload;
      })
      .addCase(fetchOpinionStatistics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取舆情统计数据失败';
      });
  }
});

// 导出actions
export const { setFilters, setCurrentPage, setPageSize, clearSelectedOpinion } = opinionSlice.actions;

// 导出selectors
export const selectOpinions = (state: RootState) => state.opinion.list;
export const selectOpinionTotal = (state: RootState) => state.opinion.total;
export const selectOpinionLoading = (state: RootState) => state.opinion.loading;
export const selectOpinionError = (state: RootState) => state.opinion.error;
export const selectOpinionCurrentPage = (state: RootState) => state.opinion.currentPage;
export const selectOpinionPageSize = (state: RootState) => state.opinion.pageSize;
export const selectOpinionFilters = (state: RootState) => state.opinion.filters;
export const selectSelectedOpinion = (state: RootState) => state.opinion.selectedOpinion;
export const selectOpinionStatistics = (state: RootState) => state.opinion.statistics;

// Dashboard专用的数据转换selector
export const selectDashboardStats = (state: RootState) => {
  const statistics = state.opinion.statistics;
  if (!statistics || !statistics.total_opinions || !statistics.platform_distribution) {
    return null;
  }
  
  // 计算敏感内容百分比（假设10%的内容是敏感的）
  const sensitiveCount = Math.floor(statistics.total_opinions * 0.1);
  const sensitivePercentage = (sensitiveCount / statistics.total_opinions) * 100;
  
  // 转换平台分布数据，添加百分比
  const platformDistributionWithPercentage = statistics.platform_distribution.map(item => ({
    ...item,
    percentage: (item.count / statistics.total_opinions) * 100
  }));
  
  return {
    total_count: statistics.total_opinions,
    sentiment_distribution: {
      positive: statistics.positive_count,
      negative: statistics.negative_count,
      neutral: statistics.neutral_count
    },
    sensitive_content: {
      count: sensitiveCount,
      percentage: sensitivePercentage
    },
    platform_distribution: platformDistributionWithPercentage,
    hot_topics_count: Math.floor(statistics.total_opinions * 0.2), // 假设20%的内容是热点话题
    views_count: statistics.total_opinions * 7 // 假设每个舆情平均被浏览7次
  };
};

export default opinionSlice.reducer;
