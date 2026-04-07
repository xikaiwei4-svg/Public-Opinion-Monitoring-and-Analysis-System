import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import { RootState } from '../index';
import { getOpinions } from '../../api/databaseApi';
import { handleApiRequest } from '../../utils/mockData';

// 定义趋势数据类型
interface TrendDataPoint {
  date: string;
  count: number;
  heat: number;
}

interface SentimentTrendData {
  date: string;
  positive: number;
  negative: number;
  neutral: number;
}

interface PlatformDistributionData {
  platform: string;
  count: number;
  percentage: number;
  color: string;
}

interface TrendState {
  opinionTrend: TrendDataPoint[];
  sentimentTrend: SentimentTrendData[];
  platformDistribution: PlatformDistributionData[];
  loading: boolean;
  error: string | null;
  timeRange: '7' | '15' | '30';
  selectedPlatform: string | null;
}

// 定义初始状态
export const initialState: TrendState = {
  opinionTrend: [],
  sentimentTrend: [],
  platformDistribution: [],
  loading: false,
  error: null,
  timeRange: '7',
  selectedPlatform: null
};

// 导入API缓存模块
import { fetchApiData } from '../../utils/apiCache';

// 异步获取舆情趋势数据 - 使用真实API
export const fetchOpinionTrend = createAsyncThunk(
  'trend/fetchOpinionTrend',
  async (params: {
    days: '7' | '15' | '30';
    platform?: string;
  }) => {
    console.log('fetchOpinionTrend called with params:', params);
    try {
      // 从API获取数据（使用缓存）
      const apiData = await fetchApiData();
      
      // 过滤平台
      let filteredData = apiData;
      if (params.platform) {
        filteredData = apiData.filter((item: any) => item.source_platform === params.platform);
      }
      
      // 按日期统计
      const dateMap = new Map<string, number>();
      const days = parseInt(params.days);
      
      // 初始化最近N天的日期
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        dateMap.set(dateStr, 0);
      }
      
      // 统计每天的数据量
      filteredData.forEach((item: any) => {
        const date = item.publish_time ? item.publish_time.split('T')[0] : null;
        if (date && dateMap.has(date)) {
          dateMap.set(date, (dateMap.get(date) || 0) + 1);
        }
      });
      
      // 转换为数组格式
      const trendData: TrendDataPoint[] = Array.from(dateMap.entries())
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, count]) => ({
          date,
          count,
          heat: Math.round(count * 1.5) // 热度值
        }));
      
      return trendData;
    } catch (error) {
      console.error('获取舆情趋势数据失败:', error);
      // 返回空数据，不回退到mock数据
      return [];
    }
  }
);

// 异步获取情感趋势数据 - 使用真实API
export const fetchSentimentTrend = createAsyncThunk(
  'trend/fetchSentimentTrend',
  async (params: {
    days: '7' | '15' | '30';
    platform?: string;
  }) => {
    console.log('fetchSentimentTrend called with params:', params);
    try {
      // 从API获取数据（使用缓存）
      const apiData = await fetchApiData();
      
      // 过滤平台
      let filteredData = apiData;
      if (params.platform) {
        filteredData = apiData.filter((item: any) => item.source_platform === params.platform);
      }
      
      // 按日期和情感统计
      const dateMap = new Map<string, { positive: number; negative: number; neutral: number }>();
      const days = parseInt(params.days);
      
      // 初始化最近N天的日期
      for (let i = days - 1; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        dateMap.set(dateStr, { positive: 0, negative: 0, neutral: 0 });
      }
      
      // 统计每天的情感分布
      filteredData.forEach((item: any) => {
        const date = item.publish_time ? item.publish_time.split('T')[0] : null;
        if (date && dateMap.has(date)) {
          const current = dateMap.get(date)!;
          const sentiment = item.sentiment || 'neutral';
          if (sentiment === 'positive') {
            current.positive += 1;
          } else if (sentiment === 'negative') {
            current.negative += 1;
          } else {
            current.neutral += 1;
          }
        }
      });
      
      // 转换为数组格式
      const sentimentData: SentimentTrendData[] = Array.from(dateMap.entries())
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([date, counts]) => ({
          date,
          positive: counts.positive,
          negative: counts.negative,
          neutral: counts.neutral
        }));
      
      return sentimentData;
    } catch (error) {
      console.error('获取情感趋势数据失败:', error);
      // 返回空数据，不回退到mock数据
      return [];
    }
  }
);

// 异步获取平台分布数据 - 使用真实API
export const fetchPlatformDistribution = createAsyncThunk(
  'trend/fetchPlatformDistribution',
  async (params: {
    days: '7' | '15' | '30';
  }) => {
    console.log('fetchPlatformDistribution called with params:', params);
    try {
      // 从API获取数据（使用缓存）
      const apiData = await fetchApiData();
      
      // 按平台统计
      const platformMap = new Map<string, number>();
      const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2'];
      
      apiData.forEach((item: any) => {
        const platform = item.source_platform || '其他';
        platformMap.set(platform, (platformMap.get(platform) || 0) + 1);
      });
      
      const total = apiData.length || 1;
      
      // 转换为数组格式
      const platformData: PlatformDistributionData[] = Array.from(platformMap.entries())
        .sort((a, b) => b[1] - a[1])
        .map(([platform, count], index) => ({
          platform,
          count,
          percentage: Math.round((count / total) * 100),
          color: colors[index % colors.length]
        }));
      
      return platformData;
    } catch (error) {
      console.error('获取平台分布数据失败:', error);
      // 返回空数据，不回退到mock数据
      return [];
    }
  }
);

// 创建slice
const trendSlice = createSlice({
  name: 'trend',
  initialState,
  reducers: {
    setTimeRange: (state: { timeRange: any }, action: PayloadAction<'7' | '15' | '30'>) => {
      state.timeRange = action.payload;
    },
    setSelectedPlatform: (state: { selectedPlatform: any }, action: PayloadAction<string | null>) => {
      state.selectedPlatform = action.payload;
    },
    clearError: (state: { error: null }) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // 获取舆情趋势数据
      .addCase(fetchOpinionTrend.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOpinionTrend.fulfilled, (state, action) => {
        state.loading = false;
        state.opinionTrend = action.payload;
      })
      .addCase(fetchOpinionTrend.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取舆情趋势数据失败';
      })
      
      // 获取情感趋势数据
      .addCase(fetchSentimentTrend.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSentimentTrend.fulfilled, (state, action) => {
        state.loading = false;
        state.sentimentTrend = action.payload;
      })
      .addCase(fetchSentimentTrend.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取情感趋势数据失败';
      })
      
      // 获取平台分布数据
      .addCase(fetchPlatformDistribution.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchPlatformDistribution.fulfilled, (state, action) => {
        state.loading = false;
        state.platformDistribution = action.payload;
      })
      .addCase(fetchPlatformDistribution.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || '获取平台分布数据失败';
      });
  }
});

// 导出actions
export const { setTimeRange, setSelectedPlatform, clearError } = trendSlice.actions;

// 导出selectors
export const selectOpinionTrend = (state: RootState) => state.trend.opinionTrend;
export const selectSentimentTrend = (state: RootState) => state.trend.sentimentTrend;
export const selectPlatformDistribution = (state: RootState) => state.trend.platformDistribution;
export const selectTrendLoading = (state: RootState) => state.trend.loading;
export const selectTrendError = (state: RootState) => state.trend.error;
export const selectTrendTimeRange = (state: RootState) => state.trend.timeRange;
export const selectTrendSelectedPlatform = (state: RootState) => state.trend.selectedPlatform;

export default trendSlice.reducer;
