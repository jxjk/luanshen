import { apiClient } from './api'

// 报警类型定义
export type AlarmLevel = 'WARNING' | 'ALARM' | 'CRITICAL'
export type AlarmStatus = 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED' | 'CLOSED'
export type AlarmType =
  | 'DEVICE_OFFLINE'
  | 'DEVICE_ALARM'
  | 'PARAMETER_EXCEED'
  | 'VIBRATION_HIGH'
  | 'TEMPERATURE_HIGH'
  | 'QUALITY_DEVIATION'
  | 'TOOL_WEAR'
  | 'MAINTENANCE_DUE'

export interface Alarm {
  id: number
  device_id: number
  alarm_level: AlarmLevel
  alarm_type: AlarmType
  alarm_code: string
  alarm_message: string
  status: AlarmStatus
  acknowledged_by: string | null
  acknowledged_at: string | null
  resolved_by: string | null
  resolved_at: string | null
  resolution_note: string | null
  created_at: string
  updated_at?: string
}

export interface AlarmStatistics {
  total: number
  open: number
  acknowledged: number
  resolved: number
  closed: number
  by_level: Record<string, number>
  by_type: Record<string, number>
}

export interface AlarmCreateRequest {
  device_id: number
  alarm_level: AlarmLevel
  alarm_type: AlarmType
  alarm_code: string
  alarm_message: string
  metadata?: Record<string, any>
}

export interface AlarmAcknowledgeRequest {
  acknowledged_by: string
  note?: string
}

export interface AlarmResolveRequest {
  resolved_by: string
  resolution_note: string
}

// 报警管理服务
class AlarmService {
  async getAlarms(params?: {
    device_id?: number
    alarm_level?: AlarmLevel
    status?: AlarmStatus
    start_time?: string
    end_time?: string
    page?: number
    page_size?: number
  }): Promise<Alarm[]> {
    return apiClient.get<Alarm[]>('/alarms/', params)
  }

  async getAlarm(alarmId: number): Promise<Alarm> {
    return apiClient.get<Alarm>(`/alarms/${alarmId}`)
  }

  async createAlarm(request: AlarmCreateRequest): Promise<Alarm> {
    return apiClient.post<Alarm>('/alarms/', request)
  }

  async acknowledgeAlarm(alarmId: number, request: AlarmAcknowledgeRequest): Promise<any> {
    return apiClient.post<any>(`/alarms/${alarmId}/acknowledge`, request)
  }

  async resolveAlarm(alarmId: number, request: AlarmResolveRequest): Promise<any> {
    return apiClient.post<any>(`/alarms/${alarmId}/resolve`, request)
  }

  async closeAlarm(alarmId: number, closedBy: string, note?: string): Promise<any> {
    return apiClient.post<any>(`/alarms/${alarmId}/close`, { closed_by: closedBy, note })
  }

  async getAlarmStatistics(): Promise<AlarmStatistics> {
    return apiClient.get<AlarmStatistics>('/alarms/statistics/summary')
  }

  async getDeviceActiveAlarms(deviceId: number): Promise<Alarm[]> {
    return apiClient.get<Alarm[]>(`/alarms/devices/${deviceId}/active`)
  }
}

export const alarmService = new AlarmService()