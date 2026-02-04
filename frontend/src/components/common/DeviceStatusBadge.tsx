import React from 'react'
import { Badge } from 'react-bootstrap'
import { theme, deviceStatus } from '../../theme'

interface DeviceStatusBadgeProps {
  status: keyof typeof deviceStatus
  showIcon?: boolean
  size?: 'sm' | 'md' | 'lg'
}

const DeviceStatusBadge: React.FC<DeviceStatusBadgeProps> = ({
  status,
  showIcon = true,
  size = 'md',
}) => {
  const statusConfig = deviceStatus[status]
  const sizeClasses = {
    sm: 'small',
    md: '',
    lg: 'fs-6',
  }

  return (
    <Badge
      bg={status === 'RUNNING' ? 'success' : status === 'ALARM' ? 'danger' : status === 'MAINTENANCE' ? 'warning' : status === 'OFFLINE' ? 'dark' : 'secondary'}
      className={sizeClasses[size]}
    >
      {showIcon && <i className={`bi ${statusConfig.icon} me-1`}></i>}
      {statusConfig.label}
    </Badge>
  )
}

export default DeviceStatusBadge