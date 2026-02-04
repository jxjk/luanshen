import { apiClient } from './api'
import { Tool, ToolCreate } from '../types'

export const toolService = {
  // 获取所有刀具
  async getAll(): Promise<Tool[]> {
    const response = await apiClient.get<Tool[]>('/tools')
    return response || []
  },

  // 根据ID获取刀具
  async getById(id: number): Promise<Tool> {
    const response = await apiClient.get<Tool>(`/tools/${id}`)
    return response!
  },

  // 根据类型获取刀具
  async getByType(type: string): Promise<Tool[]> {
    const response = await apiClient.get<Tool[]>(`/tools/type/${type}`)
    return response || []
  },

  // 创建刀具
  async create(tool: ToolCreate): Promise<Tool> {
    const response = await apiClient.post<Tool>('/tools', tool)
    return response!
  },

  // 更新刀具
  async update(id: number, tool: ToolCreate): Promise<Tool> {
    const response = await apiClient.put<Tool>(`/tools/${id}`, tool)
    return response!
  },

  // 删除刀具
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/tools/${id}`)
  },
}