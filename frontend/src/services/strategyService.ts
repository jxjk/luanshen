import { apiClient } from './api'
import { Strategy, StrategyCreate } from '../types'

export const strategyService = {
  // 获取所有策略
  async getAll(): Promise<Strategy[]> {
    const response = await apiClient.get<Strategy[]>('/strategies')
    return response || []
  },

  // 根据ID获取策略
  async getById(id: number): Promise<Strategy> {
    const response = await apiClient.get<Strategy>(`/strategies/${id}`)
    return response!
  },

  // 根据类型获取策略
  async getByType(type: string): Promise<Strategy[]> {
    const response = await apiClient.get<Strategy[]>(`/strategies/type/${type}`)
    return response || []
  },

  // 创建策略
  async create(strategy: StrategyCreate): Promise<Strategy> {
    const response = await apiClient.post<Strategy>('/strategies', strategy)
    return response!
  },

  // 更新策略
  async update(id: number, strategy: StrategyCreate): Promise<Strategy> {
    const response = await apiClient.put<Strategy>(`/strategies/${id}`, strategy)
    return response!
  },

  // 删除策略
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/strategies/${id}`)
  },
}