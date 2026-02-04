import React, { useState, useEffect } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Badge,
  Table,
  Spinner,
  Alert,
  Button,
  ProgressBar,
} from 'react-bootstrap'
import { deviceMonitorService, DeviceStatusData, MonitoringStats, DeviceStatus } from '../services/deviceMonitorService'
import { alarmService, Alarm } from '../services/alarmService'
import { Link } from 'react-router-dom'

const WorkshopPage: React.FC = () => {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [devices, setDevices] = useState<DeviceStatusData[]>([])
  const [stats, setStats] = useState<MonitoringStats | null>(null)
  const [activeAlarms, setActiveAlarms] = useState<Alarm[]>([])
  const [useMockData, setUseMockData] = useState(false)

  // 模拟数据
  const mockDevices: DeviceStatusData[] = [
    { 
      id: 1,
      device_id: 1, 
      status: 'RUNNING' as DeviceStatus, 
      current_x: 150.5, 
      current_y: 75.2, 
      current_z: -10.8, 
      spindle_speed: 3500, 
      feed_rate: 450.0, 
      load_percent: 75.5, 
      alarm_code: null, 
      alarm_message: null, 
      recorded_at: new Date().toISOString() 
    },
    { 
      id: 2,
      device_id: 2, 
      status: 'IDLE' as DeviceStatus, 
      current_x: 0, 
      current_y: 0, 
      current_z: 0, 
      spindle_speed: 0, 
      feed_rate: 0, 
      load_percent: 0, 
      alarm_code: null, 
      alarm_message: null, 
      recorded_at: new Date().toISOString() 
    },
    { 
      id: 3,
      device_id: 3, 
      status: 'ALARM' as DeviceStatus, 
      current_x: 220.3, 
      current_y: 110.5, 
      current_z: -5.2, 
      spindle_speed: 2800, 
      feed_rate: 0, 
      load_percent: 95.2, 
      alarm_code: 'ALM-001', 
      alarm_message: '主轴温度过高', 
      recorded_at: new Date().toISOString() 
    },
    { 
      id: 4,
      device_id: 4, 
      status: 'RUNNING' as DeviceStatus, 
      current_x: 85.7, 
      current_y: 42.3, 
      current_z: -8.5, 
      spindle_speed: 4200, 
      feed_rate: 680.0, 
      load_percent: 82.8, 
      alarm_code: null, 
      alarm_message: null, 
      recorded_at: new Date().toISOString() 
    },
    { 
      id: 5,
      device_id: 5, 
      status: 'MAINTENANCE' as DeviceStatus, 
      current_x: null, 
      current_y: null, 
      current_z: null, 
      spindle_speed: null, 
      feed_rate: null, 
      load_percent: null, 
      alarm_code: null, 
      alarm_message: '定期维护', 
      recorded_at: new Date().toISOString() 
    },
  ]

  const mockStats: MonitoringStats = {
    total_devices: 5,
    running_devices: 2,
    idle_devices: 1,
    alarm_devices: 1,
    maintenance_devices: 1,
    offline_devices: 0,
  }

  const mockAlarms: Alarm[] = [
    { id: 1, device_id: 3, alarm_code: 'ALM-001', alarm_level: 'ALARM' as const, alarm_message: '主轴温度过高', status: 'OPEN', created_at: new Date().toISOString() },
    { id: 2, device_id: 3, alarm_code: 'ALM-002', alarm_level: 'WARNING' as const, alarm_message: '刀具寿命即将到期', status: 'OPEN', created_at: new Date().toISOString() },
  ]

  useEffect(() => {
    loadData()
    // 只在非模拟数据模式下定时刷新
    if (!useMockData) {
      const interval = setInterval(loadData, 5000)
      return () => clearInterval(interval)
    }
  }, [useMockData])

  const loadData = async () => {
    try {
      setLoading(true)
      if (useMockData) {
        // 使用模拟数据
        setDevices(mockDevices)
        setStats(mockStats)
        setActiveAlarms(mockAlarms)
        setError(null)
        setLoading(false)
        return
      }

      const [devicesData, statsData, alarmsData] = await Promise.all([
        deviceMonitorService.getAllDevicesStatus(),
        deviceMonitorService.getMonitoringStats(),
        alarmService.getAlarms({ status: 'OPEN', page_size: 10 }),
      ])
      setDevices(devicesData)
      setStats(statsData)
      setActiveAlarms(alarmsData)
      setError(null)
      setUseMockData(false)
    } catch (err) {
      console.error('Error loading data:', err)
      // API调用失败时使用模拟数据
      setError('后端服务连接失败，显示模拟数据')
      setDevices(mockDevices)
      setStats(mockStats)
      setActiveAlarms(mockAlarms)
      setUseMockData(true)
    } finally {
      setLoading(false)
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

  const getStatusText = (status: DeviceStatus) => {
    const texts: Record<DeviceStatus, string> = {
      RUNNING: '运行中',
      IDLE: '空闲',
      ALARM: '报警',
      MAINTENANCE: '维护',
      OFFLINE: '离线',
    }
    return texts[status]
  }

  const getAlarmLevelBadge = (level: string) => {
    const variants: Record<string, string> = {
      WARNING: 'warning',
      ALARM: 'danger',
      CRITICAL: 'dark',
    }
    return <Badge bg={variants[level] || 'secondary'}>{level}</Badge>
  }

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-grid-3x3-gap me-2"></i>
            车间视图
          </h2>
          <p className="text-muted">实时监控车间内所有设备的运行状态</p>
        </Col>
        <Col xs="auto">
          <Button variant="primary" onClick={loadData} disabled={loading}>
            {loading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                刷新中...
              </>
            ) : (
              <>
                <i className="bi bi-arrow-clockwise me-2"></i>
                刷新
              </>
            )}
          </Button>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {/* 统计卡片 */}
      {stats && (
        <Row className="mb-4">
          <Col md={2} className="mb-3">
            <Card className="stat-card">
              <Card.Body className="text-center">
                <h3>{stats.total_devices}</h3>
                <p className="mb-0">设备总数</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={2} className="mb-3">
            <Card className="stat-card success">
              <Card.Body className="text-center">
                <h3>{stats.running_devices}</h3>
                <p className="mb-0">运行中</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={2} className="mb-3">
            <Card className="stat-card secondary">
              <Card.Body className="text-center">
                <h3>{stats.idle_devices}</h3>
                <p className="mb-0">空闲</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={2} className="mb-3">
            <Card className="stat-card danger">
              <Card.Body className="text-center">
                <h3>{stats.alarm_devices}</h3>
                <p className="mb-0">报警</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={2} className="mb-3">
            <Card className="stat-card warning">
              <Card.Body className="text-center">
                <h3>{stats.maintenance_devices}</h3>
                <p className="mb-0">维护</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={2} className="mb-3">
            <Card className="stat-card dark">
              <Card.Body className="text-center">
                <h3>{stats.offline_devices}</h3>
                <p className="mb-0">离线</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* 运行率进度条 */}
      {stats && stats.total_devices > 0 && (
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                <i className="bi bi-activity me-2"></i>
                设备运行率
              </Card.Header>
              <Card.Body>
                <div className="mb-2">
                  <small>运行中</small>
                  <ProgressBar
                    now={(stats.running_devices / stats.total_devices) * 100}
                    variant="success"
                    className="mb-2"
                    label={`${Math.round((stats.running_devices / stats.total_devices) * 100)}%`}
                  />
                </div>
                <div className="mb-2">
                  <small>空闲</small>
                  <ProgressBar
                    now={(stats.idle_devices / stats.total_devices) * 100}
                    variant="secondary"
                    className="mb-2"
                    label={`${Math.round((stats.idle_devices / stats.total_devices) * 100)}%`}
                  />
                </div>
                <div className="mb-2">
                  <small>报警</small>
                  <ProgressBar
                    now={(stats.alarm_devices / stats.total_devices) * 100}
                    variant="danger"
                    className="mb-2"
                    label={`${Math.round((stats.alarm_devices / stats.total_devices) * 100)}%`}
                  />
                </div>
                <div className="mb-2">
                  <small>维护</small>
                  <ProgressBar
                    now={(stats.maintenance_devices / stats.total_devices) * 100}
                    variant="warning"
                    className="mb-2"
                    label={`${Math.round((stats.maintenance_devices / stats.total_devices) * 100)}%`}
                  />
                </div>
                <div>
                  <small>离线</small>
                  <ProgressBar
                    now={(stats.offline_devices / stats.total_devices) * 100}
                    variant="dark"
                    label={`${Math.round((stats.offline_devices / stats.total_devices) * 100)}%`}
                  />
                </div>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      <Row>
        {/* 设备列表 */}
        <Col lg={8}>
          <Card>
            <Card.Header>
              <i className="bi bi-list-ul me-2"></i>
              设备列表
            </Card.Header>
            <Card.Body>
              {loading && devices.length === 0 ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                  <p className="mt-2">加载中...</p>
                </div>
              ) : devices.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-inbox display-4 text-muted mb-3"></i>
                  <p className="text-muted">暂无设备数据</p>
                </div>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>设备ID</th>
                      <th>状态</th>
                      <th>主轴转速</th>
                      <th>进给率</th>
                      <th>负载</th>
                      <th>位置 (X,Y,Z)</th>
                      <th>更新时间</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {devices.map((device) => (
                      <tr key={device.id}>
                        <td>
                          <strong>{device.device_id}</strong>
                        </td>
                        <td>{getStatusBadge(device.status)}</td>
                        <td>
                          {device.spindle_speed
                            ? `${device.spindle_speed.toFixed(0)} r/min`
                            : '-'}
                        </td>
                        <td>
                          {device.feed_rate
                            ? `${device.feed_rate.toFixed(1)} mm/min`
                            : '-'}
                        </td>
                        <td>
                          {device.load_percent !== null ? (
                            <>
                              <ProgressBar
                                now={device.load_percent}
                                variant={
                                  device.load_percent > 90
                                    ? 'danger'
                                    : device.load_percent > 70
                                    ? 'warning'
                                    : 'success'
                                }
                                style={{ height: '20px' }}
                              />
                              <small className="text-muted">
                                {device.load_percent.toFixed(1)}%
                              </small>
                            </>
                          ) : (
                            '-'
                          )}
                        </td>
                        <td>
                          <small>
                            X: {device.current_x?.toFixed(2) || '-'}
                            <br />
                            Y: {device.current_y?.toFixed(2) || '-'}
                            <br />
                            Z: {device.current_z?.toFixed(2) || '-'}
                          </small>
                        </td>
                        <td>
                          <small>
                            {new Date(device.recorded_at).toLocaleTimeString()}
                          </small>
                        </td>
                        <td>
                          <Link
                            to={`/monitoring/${device.device_id}`}
                            className="btn btn-sm btn-primary"
                          >
                            详情
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>

        {/* 活跃报警 */}
        <Col lg={4}>
          <Card>
            <Card.Header className="bg-danger text-white">
              <i className="bi bi-exclamation-triangle-fill me-2"></i>
              活跃报警
              <Badge bg="light" text="dark" className="ms-2">
                {activeAlarms.length}
              </Badge>
            </Card.Header>
            <Card.Body style={{ maxHeight: '600px', overflowY: 'auto' }}>
              {activeAlarms.length === 0 ? (
                <div className="text-center py-5">
                  <i className="bi bi-check-circle display-4 text-success mb-3"></i>
                  <p className="text-muted">暂无活跃报警</p>
                </div>
              ) : (
                <div className="d-flex flex-column gap-2">
                  {activeAlarms.map((alarm) => (
                    <Card key={alarm.id} className="mb-2">
                      <Card.Body className="p-3">
                        <div className="d-flex justify-content-between align-items-start mb-2">
                          {getAlarmLevelBadge(alarm.alarm_level)}
                          <small className="text-muted">
                            {new Date(alarm.created_at).toLocaleString()}
                          </small>
                        </div>
                        <h6 className="mb-1">
                          <i className="bi bi-hdd-network me-1"></i>
                          设备 {alarm.device_id}
                        </h6>
                        <p className="mb-2 small">
                          <strong>{alarm.alarm_code}</strong>: {alarm.alarm_message}
                        </p>
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
        </Col>
      </Row>
    </Container>
  )
}

export default WorkshopPage