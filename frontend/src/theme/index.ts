/**
 * 工艺数字孪生系统 - 统一UI设计规范
 * Process Digital Twin System - Unified UI Design System
 */

// ==================== 颜色系统 Color System ====================
export const colors = {
  // 主色调 Primary Colors
  primary: {
    50: '#e7f1ff',
    100: '#cbe4ff',
    200: '#a3d4ff',
    300: '#72b2ff',
    400: '#4b96ff',
    500: '#0d6efd',  // 主色
    600: '#0a58ca',
    700: '#0846a3',
    800: '#063880',
    900: '#042e66',
  },

  // 功能色 Functional Colors
  success: {
    light: '#d1e7dd',
    DEFAULT: '#198754',
    dark: '#146c43',
  },

  warning: {
    light: '#fff3cd',
    DEFAULT: '#ffc107',
    dark: '#b68900',
  },

  danger: {
    light: '#f8d7da',
    DEFAULT: '#dc3545',
    dark: '#a71d2a',
  },

  info: {
    light: '#cff4fc',
    DEFAULT: '#0dcaf0',
    dark: '#055160',
  },

  // 中性色 Neutral Colors
  gray: {
    50: '#f8f9fa',
    100: '#e9ecef',
    200: '#dee2e6',
    300: '#ced4da',
    400: '#adb5bd',
    500: '#6c757d',
    600: '#495057',
    700: '#343a40',
    800: '#212529',
    900: '#0f1115',
  },

  // 工业色 Industrial Colors (设备状态)
  industrial: {
    running: '#198754',      // 运行中
    idle: '#6c757d',         // 空闲
    alarm: '#dc3545',        // 报警
    maintenance: '#ffc107',  // 维护
    offline: '#212529',      // 离线
    online: '#0d6efd',       // 在线
  },

  // 渐变色 Gradients (用于统计卡片)
  gradients: {
    primary: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    success: 'linear-gradient(135deg, #11998e 0%, #38ef7d 100%)',
    warning: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    danger: 'linear-gradient(135deg, #ff0844 0%, #ffb199 100%)',
    info: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    secondary: 'linear-gradient(135deg, #606c88 0%, #3f4c6b 100%)',
    dark: 'linear-gradient(135deg, #232526 0%, #414345 100%)',
    blue: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    teal: 'linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%)',
    purple: 'linear-gradient(135deg, #6a11cb 0%, #2575fc 100%)',
  },
}

// ==================== 字体系统 Typography System ====================
export const typography = {
  // 字体栈 Font Stack
  fontFamily: {
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    mono: '"SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace',
  },

  // 字体大小 Font Sizes
  fontSize: {
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem',  // 36px
    '5xl': '3rem',     // 48px
  },

  // 字重 Font Weight
  fontWeight: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  // 行高 Line Height
  lineHeight: {
    tight: 1.25,
    normal: 1.5,
    relaxed: 1.75,
  },
}

// ==================== 间距系统 Spacing System ====================
export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
}

// ==================== 圆角系统 Border Radius ====================
export const borderRadius = {
  none: '0',
  sm: '0.25rem',   // 4px
  DEFAULT: '0.375rem', // 6px
  md: '0.5rem',    // 8px
  lg: '0.75rem',   // 12px
  xl: '1rem',      // 16px
  '2xl': '1.5rem', // 24px
  full: '9999px',  // 圆形
}

// ==================== 阴影系统 Shadow System ====================
export const shadows = {
  xs: '0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)',
  sm: '0 0.125rem 0.25rem rgba(0, 0, 0, 0.075)',
  DEFAULT: '0 0.5rem 1rem rgba(0, 0, 0, 0.15)',
  md: '0 0.5rem 1.5rem rgba(0, 0, 0, 0.175)',
  lg: '0 1rem 3rem rgba(0, 0, 0, 0.175)',
  xl: '0 1.5rem 4rem rgba(0, 0, 0, 0.2)',
  inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
}

// ==================== 过渡动画 Transitions ====================
export const transitions = {
  duration: {
    fast: '150ms',
    DEFAULT: '300ms',
    slow: '500ms',
  },
  easing: {
    ease: 'ease',
    easeIn: 'ease-in',
    easeOut: 'ease-out',
    easeInOut: 'ease-in-out',
  },
}

// ==================== 断点系统 Breakpoints ====================
export const breakpoints = {
  xs: '0',
  sm: '576px',
  md: '768px',
  lg: '992px',
  xl: '1200px',
  '2xl': '1400px',
}

// ==================== z-index层级系统 Z-Index ====================
export const zIndex = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modalBackdrop: 1040,
  modal: 1050,
  popover: 1060,
  tooltip: 1070,
}

// ==================== 设备状态 Device Status ====================
export const deviceStatus = {
  RUNNING: {
    label: '运行中',
    color: colors.industrial.running,
    icon: 'bi-play-circle-fill',
  },
  IDLE: {
    label: '空闲',
    color: colors.industrial.idle,
    icon: 'bi-pause-circle-fill',
  },
  ALARM: {
    label: '报警',
    color: colors.industrial.alarm,
    icon: 'bi-exclamation-triangle-fill',
  },
  MAINTENANCE: {
    label: '维护',
    color: colors.industrial.maintenance,
    icon: 'bi-tools',
  },
  OFFLINE: {
    label: '离线',
    color: colors.industrial.offline,
    icon: 'bi-circle-fill',
  },
}

// ==================== 报警级别 Alarm Levels ====================
export const alarmLevels = {
  WARNING: {
    label: '预警',
    color: colors.warning.DEFAULT,
    variant: 'warning',
  },
  ALARM: {
    label: '报警',
    color: colors.danger.DEFAULT,
    variant: 'danger',
  },
  CRITICAL: {
    label: '严重报警',
    color: colors.gray[900],
    variant: 'dark',
  },
}

// ==================== 图标映射 Icon Mapping ====================
export const icons = {
  // 导航图标 Navigation
  dashboard: 'bi-speedometer2',
  workshop: 'bi-grid-3x3-gap',
  optimization: 'bi-sliders',
  digitalTwin: 'bi-boxes',
  monitoring: 'bi-activity',
  quality: 'bi-shield-check',
  knowledge: 'bi-book',
  reports: 'bi-file-earmark-bar-graph',

  // 资源管理图标 Resource Management
  materials: 'bi-box-seam',
  tools: 'bi-tools',
  machines: 'bi-pc-display',
  strategies: 'bi-list-task',
  fixtures: 'bi-grid-3x3',
  templates: 'bi-file-earmark-code',

  // 功能图标 Functional
  history: 'bi-clock-history',
  settings: 'bi-gear',
  notifications: 'bi-bell',
  user: 'bi-person',
  help: 'bi-question-circle',
  logout: 'bi-box-arrow-right',

  // 操作图标 Actions
  add: 'bi-plus-lg',
  edit: 'bi-pencil',
  delete: 'bi-trash',
  view: 'bi-eye',
  download: 'bi-download',
  upload: 'bi-upload',
  refresh: 'bi-arrow-clockwise',
  search: 'bi-search',
  filter: 'bi-funnel',
  save: 'bi-save',
  cancel: 'bi-x-lg',
  confirm: 'bi-check-lg',

  // 新增功能图标
  nc_simulation: 'bi-cpu',
  energy_analysis: 'bi-lightning-charge',
  tool_life: 'bi-tools',

  // 状态图标 Status
  success: 'bi-check-circle-fill',
  warning: 'bi-exclamation-triangle-fill',
  danger: 'bi-x-circle-fill',
  info: 'bi-info-circle-fill',
  loading: 'bi-arrow-repeat',
}

// ==================== 布局配置 Layout ====================
export const layout = {
  navbar: {
    height: '56px',
    backgroundColor: colors.primary[500],
  },
  sidebar: {
    width: '250px',
    backgroundColor: '#ffffff',
    collapsedWidth: '64px',
  },
  mainContent: {
    marginLeft: '250px',
    marginTop: '56px',
    padding: spacing[6],
  },
  card: {
    default: {
      padding: spacing[5],
      borderRadius: borderRadius.DEFAULT,
      boxShadow: shadows.sm,
    },
  },
}

// ==================== 表单配置 Form ====================
export const form = {
  input: {
    padding: `${spacing[2]} ${spacing[3]}`,
    borderRadius: borderRadius.DEFAULT,
    border: `1px solid ${colors.gray[200]}`,
    fontSize: typography.fontSize.base,
  },
  label: {
    fontSize: typography.fontSize.sm,
    fontWeight: typography.fontWeight.medium,
    color: colors.gray[700],
    marginBottom: spacing[2],
  },
}

// ==================== 导航菜单配置 Navigation Menu ====================
export const menuItems = [
  {
    category: '主菜单',
    items: [
      { path: '/workshop', icon: icons.workshop, label: '车间视图', badge: null },
      { path: '/optimization', icon: icons.optimization, label: '参数优化', badge: null },
      { path: '/digital-twin', icon: icons.digitalTwin, label: '数字孪生', badge: 'NEW' },
      { path: '/quality', icon: icons.quality, label: '质量追溯', badge: null },
    ],
  },
  {
    category: '高级功能',
    items: [
      { path: '/nc-simulation', icon: icons.nc_simulation, label: 'NC仿真', badge: 'NEW' },
      { path: '/energy-analysis', icon: icons.energy_analysis, label: '能效分析', badge: 'NEW' },
      { path: '/tool-life', icon: icons.tool_life, label: '刀具寿命', badge: 'NEW' },
    ],
  },
  {
    category: '资源管理',
    items: [
      { path: '/materials', icon: icons.materials, label: '材料管理', badge: null },
      { path: '/tools', icon: icons.tools, label: '刀具管理', badge: null },
      { path: '/machines', icon: icons.machines, label: '设备管理', badge: null },
      { path: '/strategies', icon: icons.strategies, label: '策略管理', badge: null },
      { path: '/fixtures', icon: icons.fixtures, label: '夹具管理', badge: null },
    ],
  },
  {
    category: '知识与分析',
    items: [
      { path: '/knowledge', icon: icons.knowledge, label: '工艺知识库', badge: null },
      { path: '/history', icon: icons.history, label: '历史记录', badge: null },
      { path: '/reports', icon: icons.reports, label: '报告生成', badge: null },
    ],
  },
]

// ==================== 导出默认主题配置 Export Default Theme ====================
export const theme = {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  breakpoints,
  zIndex,
  deviceStatus,
  alarmLevels,
  icons,
  layout,
  form,
  menuItems,
}

export default theme