import { apiClient } from './api'

// 设备状态类型
export type DeviceStatus = 'RUNNING' | 'IDLE' | 'ALARM' | 'MAINTENANCE' | 'OFFLINE'

export interface DeviceStatusData {
  id: number
  device_id: number
  status: DeviceStatus
  current_x: number | null
  current_y: number | null
  current_z: number | null
  spindle_speed: number | null
  feed_rate: number | null
  load_percent: number | null
  alarm_code: string | null
  alarm_message: string | null
  recorded_at: string
}

export interface RealtimeData {
  device_id: number
  status: DeviceStatus
  coordinates: {
    x: number | null
    y: number | null
    z: number | null
  }
  parameters: {
    spindle_speed: number | null
    feed_rate: number | null
    load: number | null
  }
  sensors: Record<string, any>
  timestamp: string
}

export interface MonitoringStats {
  total_devices: number
  running_devices: number
  idle_devices: number
  alarm_devices: number
  maintenance_devices: number
  offline_devices: number
}

export interface TimeSeriesData {
  time: string
  value: number
  field: string
}

// 设备监控服务
class DeviceMonitorService {
  async getAllDevicesStatus(): Promise<DeviceStatusData[]> {
    return apiClient.get<DeviceStatusData[]>('/device/')
  }

  async getDeviceStatus(deviceId: number): Promise<DeviceStatusData> {
    return apiClient.get<DeviceStatusData>(`/device/${deviceId}/status`)
  }

  async getRealtimeData(deviceId: number): Promise<RealtimeData> {
    return apiClient.get<RealtimeData>(`/monitoring/${deviceId}/realtime`)
  }

  async getMonitoringStats(): Promise<MonitoringStats> {
    return apiClient.get<MonitoringStats>('/monitoring/stats')
  }

  async startDeviceMonitoring(deviceId: number, opcuaUrl?: string): Promise<any> {
    return apiClient.post<any>(`/device/${deviceId}/start`, { device_id: deviceId, opcua_url: opcuaUrl })
  }

  async stopDeviceMonitoring(deviceId: number): Promise<any> {
    return apiClient.post<any>(`/device/${deviceId}/stop`, { device_id: deviceId })
  }

  async getHistoryData(
    deviceId: number,
    startTime: string,
    endTime: string,
    measurement: string = 'device_sensor_data',
    limit: number = 1000
  ): Promise<any> {
    return apiClient.post<any>(`/monitoring/${deviceId}/history`, {
      device_id: deviceId,
      start_time: startTime,
      end_time: endTime,
      measurement,
      limit,
    })
  }

  async getTimeSeriesData(
    deviceId: number,
    field: string,
    startTime: string,
    endTime: string,
    aggregation?: string,
    window?: string
  ): Promise<{ device_id: number; field: string; data: TimeSeriesData[]; count: number }> {
    const params: any = {
      field,
      start_time: startTime,
      end_time: endTime,
    }
    if (aggregation) params.aggregation = aggregation
    if (window) params.window = window

    return apiClient.get<{ device_id: number; field: string; data: TimeSeriesData[]; count: number }>(
      `/monitoring/${deviceId}/timeseries`,
      params
    )
  }

  // WebSocket 连接
  connectToWebSocket(deviceId: number, onMessage: (data: any) => void, onError?: (error: Event) => void): WebSocket {
    const wsUrl = `ws://localhost:5008/api/v1/ws/monitoring/${deviceId}`
    const ws = new WebSocket(wsUrl)

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      onMessage(data)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    ws.onclose = () => {
      console.log('WebSocket connection closed')
    }

    return ws
  }
}

export const deviceMonitorService = new DeviceMonitorService()