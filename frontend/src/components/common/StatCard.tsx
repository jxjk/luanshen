import React from 'react'
import { Card } from 'react-bootstrap'
import { theme } from '../../theme'

interface StatCardProps {
  title: string
  value: string | number
  icon?: string
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'secondary' | 'dark' | 'blue' | 'teal' | 'purple'
  trend?: {
    value: number
    isPositive: boolean
  }
  onClick?: () => void
}

const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  icon,
  variant = 'primary',
  trend,
  onClick,
}) => {
  const getGradient = () => {
    return theme.colors.gradients[variant] || theme.colors.gradients.primary
  }

  return (
    <Card
      className={`stat-card stat-card-${variant} ${onClick ? 'cursor-pointer' : ''}`}
      style={{
        background: getGradient(),
        color: 'white',
        border: 'none',
        borderRadius: theme.borderRadius.lg,
        transition: theme.transitions.duration.DEFAULT,
      }}
      onClick={onClick}
    >
      <Card.Body className="p-4">
        <div className="d-flex justify-content-between align-items-start">
          <div className="flex-grow-1">
            <p className="mb-2" style={{ fontSize: theme.typography.fontSize.sm, opacity: 0.9 }}>
              {title}
            </p>
            <h3 className="mb-0" style={{ fontSize: theme.typography.fontSize['4xl'], fontWeight: theme.typography.fontWeight.bold }}>
              {value}
            </h3>
            {trend && (
              <small className={trend.isPositive ? 'text-white' : 'text-white'} style={{ opacity: 0.8 }}>
                <i className={`bi bi-arrow-${trend.isPositive ? 'up' : 'down'} me-1`}></i>
                {Math.abs(trend.value)}%
              </small>
            )}
          </div>
          {icon && (
            <i className={`bi ${icon}`} style={{ fontSize: theme.typography.fontSize['3xl'], opacity: 0.7 }}></i>
          )}
        </div>
      </Card.Body>
    </Card>
  )
}

export default StatCard