import { createSlice, createAsyncThunk, PayloadAction, createSelector } from '@reduxjs/toolkit';
import { RootState } from '../index';
import { handleApiRequest } from '../../utils/apiClient';

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
  hot_topics_count: number;
  views_count: number;
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

// 异步获取舆情列表 - 调用后端API
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
      const queryParams: Record<string, string | number> = {
        page: params.page,
        pageSize: params.pageSize,
      };
      if (params.keyword) queryParams.keyword = params.keyword;
      if (params.sentiment_type) queryParams.sentiment_type = params.sentiment_type;
      if (params.source) queryParams.source = params.source;
      if (params.is_sensitive !== null && params.is_sensitive !== undefined) queryParams.is_sensitive = params.is_sensitive;

      const data = await handleApiRequest<{
        items: any[];
        total: number;
        page: number;
        page_size: number;
      }>({
        method: 'GET',
        url: '/api/opinion/list',
        params: queryParams,
      });

      const items: OpinionItem[] = (data.items || []).map((item: any) => ({
        id: item.id,
        content: item.content || '',
        source: item.source || item.source_platform || '未知来源',
        source_platform: item.source_platform || '未知平台',
        publish_time: item.publish_time || item.crawl_time || new Date().toISOString(),
        crawl_time: item.crawl_time || item.publish_time || new Date().toISOString(),
        sentiment: 0,
        sentiment_type: item.sentiment || 'neutral',
        keywords: [],
        url: item.url,
        views: 0,
        likes: 0,
        comments: 0,
        shares: 0,
        heat_score: 0,
        is_sensitive: item.is_sensitive || false,
        sensitive_level: 0,
      }));

      return {
        items,
        total: data.total || 0,
        page: data.page || params.page,
        page_size: data.page_size || params.pageSize,
      };
    } catch (error) {
      console.error('获取舆情列表失败:', error);
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

// 异步获取舆情统计数据 - 调用后端API
export const fetchOpinionStatistics = createAsyncThunk(
  'opinion/fetchOpinionStatistics',
  async (_params: {
    start_time?: string;
    end_time?: string;
  } = {}) => {
    try {
      const apiData = await handleApiRequest<any>({
        method: 'GET',
        url: '/api/opinion/statistics',
      });
      
      // 转换数据格式以匹配前端期望的结构
      return {
        total_opinions: apiData.total_count || 0,
        positive_count: apiData.sentiment_distribution?.positive || 0,
        negative_count: apiData.sentiment_distribution?.negative || 0,
        neutral_count: apiData.sentiment_distribution?.neutral || 0,
        daily_trend: [],
        platform_distribution: apiData.platform_distribution || [],
        category_distribution: [],
        hot_topics_count: apiData.hot_topics_count || 0,
        views_count: apiData.views_count || 0,
      };
    } catch (error) {
      console.error('获取舆情统计数据失败:', error);
      return {
        total_opinions: 0,
        positive_count: 0,
        negative_count: 0,
        neutral_count: 0,
        daily_trend: [],
        platform_distribution: [],
        category_distribution: [],
        hot_topics_count: 0,
        views_count: 0,
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
export const selectDashboardStats = createSelector(
  [(state: RootState) => state.opinion.statistics],
  (statistics) => {
    if (!statistics) return null;

    return {
      total_count: statistics.total_opinions,
      sentiment_distribution: {
        positive: statistics.positive_count,
        negative: statistics.negative_count,
        neutral: statistics.neutral_count
      },
      platform_distribution: statistics.platform_distribution,
      hot_topics_count: statistics.hot_topics_count,
      views_count: statistics.views_count,
    };
  }
);

export default opinionSlice.reducer;
