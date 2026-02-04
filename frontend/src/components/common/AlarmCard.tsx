import React from 'react'
import { Card, Badge, Button } from 'react-bootstrap'
import { theme, alarmLevels } from '../../theme'
import { Alarm } from '../../types'

interface AlarmCardProps {
  alarm: Alarm
  onAcknowledge?: (alarm: Alarm) => void
  onResolve?: (alarm: Alarm) => void
}

const AlarmCard: React.FC<AlarmCardProps> = ({
  alarm,
  onAcknowledge,
  onResolve,
}) => {
  const levelConfig = alarmLevels[alarm.alarm_level as keyof typeof alarmLevels] || alarmLevels.WARNING
  const isResolved = alarm.status === 'RESOLVED'
  const isAcknowledged = alarm.status === 'ACKNOWLEDGED'

  return (
    <Card
      className={`alarm-card mb-3 ${isResolved ? 'opacity-50' : ''}`}
      style={{
        borderLeft: `4px solid ${levelConfig.color}`,
        borderRadius: theme.borderRadius.DEFAULT,
        boxShadow: theme.shadows.sm,
      }}
    >
      <Card.Body className="p-3">
        <div className="d-flex justify-content-between align-items-start mb-2">
          <div className="d-flex align-items-center gap-2">
            <Badge bg={levelConfig.variant}>{levelConfig.label}</Badge>
            {isAcknowledged && <Badge bg="info">已确认</Badge>}
            {isResolved && <Badge bg="success">已解决</Badge>}
          </div>
          <small className="text-muted">
            {new Date(alarm.created_at).toLocaleString('zh-CN')}
          </small>
        </div>

        <h6 className="mb-1">
          <i className="bi bi-hdd-network me-1"></i>
          设备 {alarm.device_id}
        </h6>

        <p className="mb-2" style={{ fontSize: theme.typography.fontSize.sm }}>
          <strong>{alarm.alarm_code}</strong>: {alarm.alarm_message}
        </p>

        {alarm.alarm_value && (
          <small className="text-muted d-block mb-2">
            当前值: {alarm.alarm_value} {alarm.unit || ''}
          </small>
        )}

        {!isResolved && (
          <div className="d-flex gap-2">
            {!isAcknowledged && onAcknowledge && (
              <Button
                size="sm"
                variant="outline-warning"
                onClick={() => onAcknowledge(alarm)}
              >
                <i className="bi bi-check-circle me-1"></i>
                确认
              </Button>
            )}
            {onResolve && (
              <Button
                size="sm"
                variant="outline-success"
                onClick={() => onResolve(alarm)}
              >
                <i className="bi bi-check2-circle me-1"></i>
                解决
              </Button>
            )}
          </div>
        )}

        {alarm.resolution_note && (
          <div className="mt-2 pt-2 border-top">
            <small className="text-muted">
              <i className="bi bi-chat-quote me-1"></i>
              {alarm.resolution_note}
            </small>
          </div>
        )}
      </Card.Body>
    </Card>
  )
}

export default AlarmCard