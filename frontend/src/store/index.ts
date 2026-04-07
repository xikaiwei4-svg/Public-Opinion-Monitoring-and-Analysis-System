import { configureStore } from '@reduxjs/toolkit'
import opinionReducer from './features/opinionSlice'
import hotTopicReducer from './features/hotTopicSlice'
import trendReducer from './features/trendSlice'
import userReducer from './features/userSlice'

// 创建Redux store
export const store = configureStore({
  reducer: {
    opinion: opinionReducer,
    hotTopic: hotTopicReducer,
    trend: trendReducer,
    user: userReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // 忽略不可序列化的值
        ignoredActionPaths: ['payload.timeStamp', 'meta.arg'],
        ignoredPaths: ['items.dates', 'opinion.list', 'hotTopic.list'],
      },
    }),
})

// 导出store类型
export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

export default store