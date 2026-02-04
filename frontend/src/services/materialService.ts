import { apiClient } from './api'
import { Material, MaterialCreate } from '../types'

export const materialService = {
  // 获取所有材料
  async getAll(): Promise<Material[]> {
    const response = await apiClient.get<Material[]>('/materials')
    return response || []
  },

  // 根据组别获取材料
  async getByGroup(group: string): Promise<Material> {
    const response = await apiClient.get<Material>(`/materials/group/${group}`)
    return response!
  },

  // 根据ID获取材料
  async getById(id: number): Promise<Material> {
    const response = await apiClient.get<Material>(`/materials/${id}`)
    return response!
  },

  // 创建材料
  async create(material: MaterialCreate): Promise<Material> {
    const response = await apiClient.post<Material>('/materials', material)
    return response!
  },

  // 更新材料
  async update(id: number, material: MaterialCreate): Promise<Material> {
    const response = await apiClient.put<Material>(`/materials/${id}`, material)
    return response!
  },

  // 删除材料
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/materials/${id}`)
  },
}