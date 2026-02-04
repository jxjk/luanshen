import { apiClient } from './api'
import { Machine, MachineCreate } from '../types'

export const machineService = {
  // 获取所有设备
  async getAll(): Promise<Machine[]> {
    const response = await apiClient.get<Machine[]>('/machines')
    return response || []
  },

  // 根据ID获取设备
  async getById(id: number): Promise<Machine> {
    const response = await apiClient.get<Machine>(`/machines/${id}`)
    return response!
  },

  // 根据类型获取设备
  async getByType(type: string): Promise<Machine[]> {
    const response = await apiClient.get<Machine[]>(`/machines/type/${type}`)
    return response || []
  },

  // 创建设备
  async create(machine: MachineCreate): Promise<Machine> {
    const response = await apiClient.post<Machine>('/machines', machine)
    return response!
  },

  // 更新设备
  async update(id: number, machine: MachineCreate): Promise<Machine> {
    const response = await apiClient.put<Machine>(`/machines/${id}`, machine)
    return response!
  },

  // 删除设备
  async delete(id: number): Promise<void> {
    await apiClient.delete(`/machines/${id}`)
  },
}