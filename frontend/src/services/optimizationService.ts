import { apiClient } from './api'
import {
  OptimizationRequest,
  OptimizationResponse,
  HealthCheck,
} from '../types'

export const optimizationService = {
  // 优化参数
  async optimize(request: OptimizationRequest): Promise<OptimizationResponse> {
    return apiClient.post<OptimizationResponse>('/optimization/optimize', request)
  },

  // 健康检查
  async healthCheck(): Promise<HealthCheck> {
    return apiClient.get<HealthCheck>('/optimization/health')
  },

  // 注意：历史记录端点后端尚未实现
  // async getHistory(): Promise<any> {
  //   // 后端未实现此端点
  //   throw new Error('历史记录功能尚未实现')
  // },
}