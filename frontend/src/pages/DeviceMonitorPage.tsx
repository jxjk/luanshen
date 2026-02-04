import React, { useState, useEffect, useRef } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Badge,
  Spinner,
  Alert,
  Button,
  Table,
  Tabs,
  Tab,
} from 'react-bootstrap'
import {
  deviceMonitorService,
  DeviceStatusData,
  RealtimeData,
  DeviceStatus,
  TimeSeriesData,
} from '../services/deviceMonitorService'
import { alarmService, Alarm } from '../services/alarmService'
import { useParams } from 'react-router-dom'

const DeviceMonitorPage: React.FC = () => {
  const { deviceId } = useParams<{ deviceId: string }>()
  const device_id = parseInt(deviceId || '0')

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [realtimeData, setRealtimeData] = useState<RealtimeData | null>(null)
  const [historyData, setHistoryData] = useState<TimeSeriesData[]>([])
  const [activeAlarms, setActiveAlarms] = useState<Alarm[]>([])
  const [isMonitoring, setIsMonitoring] = useState(false)
  const [wsConnected, setWsConnected] = useState(false)

  const wsRef = useRef<WebSocket | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    loadData()
    loadAlarms()
    connectWebSocket()

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [device_id])

  const loadData = async () => {
    try {
      setLoading(true)
      const data = await deviceMonitorService.getRealtimeData(device_id)
      setRealtimeData(data)
      setError(null)
    } catch (err) {
      setError('加载数据失败')
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadAlarms = async () => {
    try {
      const alarms = await alarmService.getDeviceActiveAlarms(device_id)
      setActiveAlarms(alarms)
    } catch (err) {
      console.error('Error loading alarms:', err)
    }
  }

  const connectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close()
    }

    wsRef.current = deviceMonitorService.connectToWebSocket(
      device_id,
      (data) => {
        setWsConnected(true)
        if (data.type === 'device_status') {
          setRealtimeData(data.data)
        }
      },
      (error) => {
        setWsConnected(false)
        console.error('WebSocket error:', error)
      }
    )

    wsRef.current.onopen = () => {
      setWsConnected(true)
      setIsMonitoring(true)
    }

    wsRef.current.onclose = () => {
      setWsConnected(false)
      setIsMonitoring(false)
    }
  }

  const handleStartMonitoring = async () => {
    try {
      await deviceMonitorService.startDeviceMonitoring(device_id)
      setIsMonitoring(true)
      connectWebSocket()
    } catch (err) {
      setError('启动监控失败')
    }
  }

  const handleStopMonitoring = async () => {
    try {
      await deviceMonitorService.stopDeviceMonitoring(device_id)
      setIsMonitoring(false)
      if (wsRef.current) {
        wsRef.current.close()
      }
    } catch (err) {
      setError('停止监控失败')
    }
  }

  const handleLoadHistory = async () => {
    try {
      const endTime = new Date()
      const startTime = new Date(endTime.getTime() - 3600000) // 1小时前

      const data = await deviceMonitorService.getTimeSeriesData(
        device_id,
        'load',
        startTime.toISOString(),
        endTime.toISOString()
      )
      setHistoryData(data.data)
    } catch (err) {
      setError('加载历史数据失败')
    }
  }

  const getStatusBadge = (status: DeviceStatus) => {
    const variants: Record<DeviceStatus, string> = {
      RUNNING: 'success',
      IDLE: 'secondary',
      ALARM: 'danger',
      MAINTENANCE: 'warning',
      OFFLINE: 'dark',
    }
    return <Badge bg={variants[status]}>{status}</Badge>
  }

  const drawChart = () => {
    const canvas = canvasRef.current
    if (!canvas || historyData.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const width = canvas.width
    const height = canvas.height

    // 清空画布
    ctx.clearRect(0, 0, width, height)

    // 绘制背景
    ctx.fillStyle = '#f8f9fa'
    ctx.fillRect(0, 0, width, height)

    // 计算数据范围
    const values = historyData.map((d) => d.value)
    const minValue = Math.min(...values)
    const maxValue = Math.max(...values)
    const range = maxValue - minValue || 1

    // 绘制曲线
    ctx.strokeStyle = '#0d6efd'
    ctx.lineWidth = 2
    ctx.beginPath()

    historyData.forEach((data, index) => {
      const x = (index / (historyData.length - 1)) * width
      const y = height - ((data.value - minValue) / range) * height * 0.8 - height * 0.1

      if (index === 0) {
        ctx.moveTo(x, y)
      } else {
        ctx.lineTo(x, y)
      }
    })

    ctx.stroke()

    // 绘制网格线
    ctx.strokeStyle = '#dee2e6'
    ctx.lineWidth = 1
    for (let i = 0; i <= 4; i++) {
      const y = (height / 4) * i
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }
  }

  useEffect(() => {
    if (historyData.length > 0) {
      drawChart()
    }
  }, [historyData])

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-hdd-rack me-2"></i>
            设备监控 - {device_id}
          </h2>
          <p className="text-muted">实时监控设备 {device_id} 的运行状态和参数</p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <div className="d-flex align-items-center">
            <Badge bg={wsConnected ? 'success' : 'secondary'}>
              {wsConnected ? '● WebSocket 已连接' : '○ WebSocket 未连接'}
            </Badge>
          </div>
          {!isMonitoring ? (
            <Button variant="success" onClick={handleStartMonitoring}>
              <i className="bi bi-play-fill me-2"></i>
              启动监控
            </Button>
          ) : (
            <Button variant="danger" onClick={handleStopMonitoring}>
              <i className="bi bi-stop-fill me-2"></i>
              停止监控
            </Button>
          )}
          <Button variant="primary" onClick={loadData}>
            <i className="bi bi-arrow-clockwise me-2"></i>
            刷新
          </Button>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {/* 实时数据卡片 */}
      {realtimeData && (
        <Row className="mb-4">
          <Col md={3} className="mb-3">
            <Card className="stat-card">
              <Card.Body className="text-center">
                <h3>{getStatusBadge(realtimeData.status)}</h3>
                <p className="mb-0">设备状态</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} className="mb-3">
            <Card className="stat-card primary">
              <Card.Body className="text-center">
                <h3>
                  {realtimeData.parameters.spindle_speed
                    ? realtimeData.parameters.spindle_speed.toFixed(0)
                    : '-'}
                </h3>
                <p className="mb-0">主轴转速 (r/min)</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} className="mb-3">
            <Card className="stat-card success">
              <Card.Body className="text-center">
                <h3>
                  {realtimeData.parameters.feed_rate
                    ? realtimeData.parameters.feed_rate.toFixed(1)
                    : '-'}
                </h3>
                <p className="mb-0">进给率 (mm/min)</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3} className="mb-3">
            <Card className="stat-card warning">
              <Card.Body className="text-center">
                <h3>
                  {realtimeData.parameters.load !== null
                    ? realtimeData.parameters.load.toFixed(1)
                    : '-'}
                </h3>
                <p className="mb-0">负载 (%)</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* 详细信息 */}
      <Row className="mb-4">
        <Col>
          <Tabs defaultActiveKey="realtime" className="mb-3">
            <Tab eventKey="realtime" title="实时数据">
              <Card>
                <Card.Body>
                  {realtimeData ? (
                    <Table striped bordered hover>
                      <tbody>
                        <tr>
                          <td><strong>设备ID</strong></td>
                          <td>{realtimeData.device_id}</td>
                        </tr>
                        <tr>
                          <td><strong>状态</strong></td>
                          <td>{getStatusBadge(realtimeData.status)}</td>
                        </tr>
                        <tr>
                          <td><strong>X轴位置</strong></td>
                          <td>
                            {realtimeData.coordinates.x !== null
                              ? `${realtimeData.coordinates.x.toFixed(3)} mm`
                              : '-'}
                          </td>
                        </tr>
                        <tr>
                          <td><strong>Y轴位置</strong></td>
                          <td>
                            {realtimeData.coordinates.y !== null
                              ? `${realtimeData.coordinates.y.toFixed(3)} mm`
                              : '-'}
                          </td>
                        </tr>
                        <tr>
                          <td><strong>Z轴位置</strong></td>
                          <td>
                            {realtimeData.coordinates.z !== null
                              ? `${realtimeData.coordinates.z.toFixed(3)} mm`
                              : '-'}
                          </td>
                        </tr>
                        <tr>
                          <td><strong>主轴转速</strong></td>
                          <td>
                            {realtimeData.parameters.spindle_speed !== null
                              ? `${realtimeData.parameters.spindle_speed.toFixed(2)} r/min`
                              : '-'}
                          </td>
                        </tr>
                        <tr>
                          <td><strong>进给率</strong></td>
                          <td>
                            {realtimeData.parameters.feed_rate !== null
                              ? `${realtimeData.parameters.feed_rate.toFixed(2)} mm/min`
                              : '-'}
                          </td>
                        </tr>
                        <tr>
                          <td><strong>负载</strong></td>
                          <td>
                            {realtimeData.parameters.load !== null
                              ? `${realtimeData.parameters.load.toFixed(2)} %`
                              : '-'}
                          </td>
                        </tr>
                        <tr>
                          <td><strong>更新时间</strong></td>
                          <td>
                            {new Date(realtimeData.timestamp).toLocaleString()}
                          </td>
                        </tr>
                      </tbody>
                    </Table>
                  ) : (
                    <div className="text-center py-5">
                      <Spinner animation="border" />
                      <p className="mt-2">加载中...</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Tab>

            <Tab eventKey="history" title="历史数据">
              <Card>
                <Card.Header>
                  <div className="d-flex justify-content-between align-items-center">
                    <span>负载历史数据（最近1小时）</span>
                    <Button variant="primary" size="sm" onClick={handleLoadHistory}>
                      加载数据
                    </Button>
                  </div>
                </Card.Header>
                <Card.Body>
                  {historyData.length > 0 ? (
                    <canvas
                      ref={canvasRef}
                      width={800}
                      height={300}
                      style={{ width: '100%', border: '1px solid #dee2e6', borderRadius: '4px' }}
                    />
                  ) : (
                    <div className="text-center py-5">
                      <i className="bi bi-bar-chart display-4 text-muted mb-3"></i>
                      <p className="text-muted">点击"加载数据"查看历史曲线</p>
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Tab>

            <Tab eventKey="alarms" title="报警记录">
              <Card>
                <Card.Header>活跃报警</Card.Header>
                <Card.Body>
                  {activeAlarms.length === 0 ? (
                    <div className="text-center py-5">
                      <i className="bi bi-check-circle display-4 text-success mb-3"></i>
                      <p className="text-muted">暂无活跃报警</p>
                    </div>
                  ) : (
                    <div className="d-flex flex-column gap-2">
                      {activeAlarms.map((alarm) => (
                        <Card key={alarm.id}>
                          <Card.Body>
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              <Badge
                                bg={
                                  alarm.alarm_level === 'WARNING'
                                    ? 'warning'
                                    : alarm.alarm_level === 'ALARM'
                                    ? 'danger'
                                    : 'dark'
                                }
                              >
                                {alarm.alarm_level}
                              </Badge>
                              <small className="text-muted">
                                {new Date(alarm.created_at).toLocaleString()}
                              </small>
                            </div>
                            <h6 className="mb-1">{alarm.alarm_code}</h6>
                            <p className="mb-2">{alarm.alarm_message}</p>
                            <div className="d-flex gap-2">
                              <Button
                                size="sm"
                                variant="warning"
                                onClick={() =>
                                  alarmService.acknowledgeAlarm(alarm.id, {
                                    acknowledged_by: 'operator',
                                  })
                                }
                              >
                                确认
                              </Button>
                              <Button
                                size="sm"
                                variant="success"
                                onClick={() =>
                                  alarmService.resolveAlarm(alarm.id, {
                                    resolved_by: 'operator',
                                    resolution_note: '已解决',
                                  })
                                }
                              >
                                解决
                              </Button>
                            </div>
                          </Card.Body>
                        </Card>
                      ))}
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Tab>
          </Tabs>
        </Col>
      </Row>
    </Container>
  )
}

export default DeviceMonitorPage