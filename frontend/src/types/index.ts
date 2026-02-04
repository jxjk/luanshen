// 优化相关类型
export interface OptimizationRequest {
  material_id: string
  tool_id: string
  machine_id: string
  strategy_id: string
  population_size?: number
  generations?: number
  crossover_rate?: number
  mutation_rate?: number
}

export interface OptimizationResult {
  speed: number
  feed: number
  cut_depth: number
  cut_width: number
  cutting_speed: number
  feed_per_tooth: number
  bottom_roughness: number
  side_roughness: number
  power: number
  torque: number
  feed_force: number
  material_removal_rate: number
  tool_life: number
  fitness: number
}

export interface OptimizationResponse {
  success: boolean
  message: string
  result: OptimizationResult
}

export interface HealthCheck {
  status: string
  service: string
}

// 材料类型
export interface Material {
  id?: number
  caiLiaoZu: string
  name: string
  rm_min: number
  rm_max: number
  kc11: number
  mc: number
}

export interface MaterialCreate {
  caiLiaoZu: string
  name: string
  rm_min: number
  rm_max: number
  kc11: number
  mc: number
}

// 刀具类型
export interface Tool {
  id: number
  name: string
  type: string
  zhiJing: number
  chiShu: number
  vc_max: number
  fz_max: number
  ct: number
  s_xiShu: number
  f_xiShu: number
  ap_xiShu: number
  ap_max?: number
  ff_max?: number
  daoJianR?: number
  nose_radius?: number  // 后端返回的刀尖半径字段
  zhuPianJiao?: number
  qianJiao?: number
}

export interface ToolCreate {
  name: string
  type: string
  zhiJing: number
  chiShu: number
  vc_max: number
  fz_max: number
  ct: number
  s_xiShu: number
  f_xiShu: number
  ap_xiShu: number
  ap_max?: number
  ff_max?: number
  daoJianR?: number
  zhuPianJiao?: number
  qianJiao?: number
}

// 设备类型
export interface Machine {
  id: number
  name: string
  type: string
  pw_max: number
  rp_max: number
  tnm_max: number
  xiaoLv: number
  f_max: number
}

export interface MachineCreate {
  name: string
  type: string
  pw_max: number
  rp_max: number
  tnm_max: number
  xiaoLv: number
  f_max: number
}

// 策略类型
export interface Strategy {
  id: number
  name: string
  type: string
  rx_min: number
  rz_min: number
  lft_min: number
  ae: number
  moSunXiShu?: number
}

export interface StrategyCreate {
  name: string
  type: string
  rx_min: number
  rz_min: number
  lft_min: number
  ae: number
  moSunXiShu?: number
}

// 历史记录类型
export interface OptimizationHistory {
  id: number
  material_id: string
  tool_id: string
  machine_id: string
  strategy_id: string
  speed: number
  feed: number
  cut_depth: number
  cut_width: number
  cutting_speed: number
  feed_per_tooth: number
  bottom_roughness: number
  side_roughness: number
  power: number
  torque: number
  feed_force: number
  material_removal_rate: number
  tool_life: number
  created_at?: string
}

// API响应类型
export interface ApiResponse<T> {
  success: boolean
  message: string
  data?: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// 表单类型
export type MaterialFormData = MaterialCreate
export type ToolFormData = ToolCreate
export type MachineFormData = MachineCreate
export type StrategyFormData = StrategyCreate

// 报警类型
export interface Alarm {
  id: number
  device_id: string
  alarm_code: string
  alarm_message: string
  alarm_level: 'WARNING' | 'ALARM' | 'CRITICAL'
  alarm_value?: number
  unit?: string
  threshold?: number
  status: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED'
  created_at: string
  acknowledged_at?: string
  resolved_at?: string
  acknowledged_by?: string
  resolved_by?: string
  resolution_note?: string
}

export interface AlarmQueryParams {
  device_id?: string
  status?: 'OPEN' | 'ACKNOWLEDGED' | 'RESOLVED'
  alarm_level?: 'WARNING' | 'ALARM' | 'CRITICAL'
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

// 设备监控类型
export type DeviceStatus = 'RUNNING' | 'IDLE' | 'ALARM' | 'MAINTENANCE' | 'OFFLINE'

export interface DeviceStatusData {
  id: number
  device_id: string
  status: DeviceStatus
  spindle_speed: number | null
  feed_rate: number | null
  load_percent: number | null
  current_x: number | null
  current_y: number | null
  current_z: number | null
  recorded_at: string
}

export interface MonitoringStats {
  total_devices: number
  running_devices: number
  idle_devices: number
  alarm_devices: number
  maintenance_devices: number
  offline_devices: number
}

// 报警操作类型
export interface AlarmAcknowledgeRequest {
  acknowledged_by: string
}

export interface AlarmResolveRequest {
  resolved_by: string
  resolution_note: string
}