// API configuration
// In dev: uses Vite proxy (empty base URL)
// In production: uses VITE_API_BASE_URL from environment
//
// 注意：Docker 部署时 Nginx 已代理 /api/* → backend
// 因此 API 路径（如 /api/database/stats）已是完整请求路径，
// baseURL 为空字符串即可（同源请求）。
// 若前后端分离部署（如 Vercel + 独立服务器），
// 设 VITE_API_BASE_URL=https://api.yourdomain.com
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

export function apiUrl(path: string): string {
  return ${API_BASE_URL}
}
