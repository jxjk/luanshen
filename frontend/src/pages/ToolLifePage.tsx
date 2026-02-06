import React, { useState } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  Table,
  ProgressBar,
  Alert,
  Tabs,
  Tab,
  Form,
  Modal,
} from 'react-bootstrap'
import { theme } from '../theme'

interface ToolLife {
  id: number
  tool_id: number
  tool_name: string
  device_id: string
  device_name: string
  installed_date: string
  total_life: number // 分钟
  used_life: number // 分钟
  remaining_life: number // 分钟
  life_percentage: number
  status: 'good' | 'warning' | 'critical' | 'expired'
  wear_factor: number
  predicted_life_end: string
  last_maintenance: string
  usage_count: number
}

interface ToolReplacement {
  id: number
  tool_id: number
  tool_name: string
  device_id: string
  reason: string
  replacement_date: string
  old_tool_life: number
  new_tool_id: number
  operator: string
}

const ToolLifePage: React.FC = () => {
  const [showReplaceModal, setShowReplaceModal] = useState(false)
  const [selectedTool, setSelectedTool] = useState<ToolLife | null>(null)
  const [activeTab, setActiveTab] = useState('monitoring')

  // 模拟刀具寿命数据
  const [toolLives] = useState<ToolLife[]>([
    {
      id: 1,
      tool_id: 1,
      tool_name: '面铣刀-φ80',
      device_id: 'CNC-001',
      device_name: 'FANUC-5AX',
      installed_date: '2025-11-20 08:30:00',
      total_life: 180,
      used_life: 145,
      remaining_life: 35,
      life_percentage: 80.56,
      status: 'warning',
      wear_factor: 1.15,
      predicted_life_end: '2025-12-16 14:30:00',
      last_maintenance: '2025-11-20 08:30:00',
      usage_count: 12,
    },
    {
      id: 2,
      tool_id: 2,
      tool_name: '立铣刀-φ10',
      device_id: 'CNC-002',
      device_name: 'SIEMENS-3AX',
      installed_date: '2025-12-01 10:15:00',
      total_life: 120,
      used_life: 25,
      remaining_life: 95,
      life_percentage: 20.83,
      status: 'good',
      wear_factor: 0.95,
      predicted_life_end: '2026-01-05 09:00:00',
      last_maintenance: '2025-12-01 10:15:00',
      usage_count: 5,
    },
    {
      id: 3,
      tool_id: 3,
      tool_name: '球头刀-φ6',
      device_id: 'CNC-003',
      device_name: 'DMG-MORI',
      installed_date: '2025-10-15 14:20:00',
      total_life: 90,
      used_life: 88,
      remaining_life: 2,
      life_percentage: 97.78,
      status: 'critical',
      wear_factor: 1.25,
      predicted_life_end: '2025-12-15 16:45:00',
      last_maintenance: '2025-10-15 14:20:00',
      usage_count: 18,
    },
    {
      id: 4,
      tool_id: 4,
      tool_name: '钻头-Φ12',
      device_id: 'CNC-004',
      device_name: 'MAZAK-5AX',
      installed_date: '2025-12-10 09:00:00',
      total_life: 60,
      used_life: 15,
      remaining_life: 45,
      life_percentage: 25.00,
      status: 'good',
      wear_factor: 1.05,
      predicted_life_end: '2026-01-10 11:00:00',
      last_maintenance: '2025-12-10 09:00:00',
      usage_count: 3,
    },
    {
      id: 5,
      tool_id: 5,
      tool_name: '立铣刀-φ8',
      device_id: 'CNC-001',
      device_name: 'FANUC-5AX',
      installed_date: '2025-11-05 16:45:00',
      total_life: 150,
      used_life: 150,
      remaining_life: 0,
      life_percentage: 100.00,
      status: 'expired',
      wear_factor: 1.30,
      predicted_life_end: '2025-12-12 10:00:00',
      last_maintenance: '2025-11-05 16:45:00',
      usage_count: 22,
    },
  ])

  // 模拟换刀记录
  const [replacements] = useState<ToolReplacement[]>([
    {
      id: 1,
      tool_id: 5,
      tool_name: '立铣刀-φ8',
      device_id: 'CNC-001',
      reason: '刀具寿命到期',
      replacement_date: '2025-12-12 10:15:00',
      old_tool_life: 150,
      new_tool_id: 5,
      operator: '张操作员',
    },
    {
      id: 2,
      tool_id: 3,
      tool_name: '球头刀-φ6',
      device_id: 'CNC-003',
      reason: '加工质量下降',
      replacement_date: '2025-11-20 14:30:00',
      old_tool_life: 85,
      new_tool_id: 3,
      operator: '李操作员',
    },
  ])

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      good: { bg: 'success', text: '良好' },
      warning: { bg: 'warning', text: '警告' },
      critical: { bg: 'danger', text: '紧急' },
      expired: { bg: 'dark', text: '已过期' },
    }
    return variants[status] || variants.good
  }

  const getLifeVariant = (percentage: number) => {
    if (percentage >= 100) return 'danger'
    if (percentage >= 80) return 'warning'
    if (percentage >= 50) return 'info'
    return 'success'
  }

  const handleReplace = (tool: ToolLife) => {
    setSelectedTool(tool)
    setShowReplaceModal(true)
  }

  const confirmReplace = () => {
    if (selectedTool) {
      alert(`已标记刀具 ${selectedTool.tool_name} 需要更换`)
      setShowReplaceModal(false)
    }
  }

  const criticalTools = toolLives.filter(t => t.status === 'critical' || t.status === 'expired').length
  const warningTools = toolLives.filter(t => t.status === 'warning').length
  const goodTools = toolLives.filter(t => t.status === 'good').length

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-tools me-2"></i>
            刀具寿命管理
          </h2>
          <p className="text-muted">
            刀具寿命预测、换刀预警和刀具使用记录管理
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="outline-secondary">
            <i className={`bi ${theme.icons.refresh} me-2`}></i>
            刷新
          </Button>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card stat-card-success border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{goodTools}</h3>
              <p className="mb-0">状态良好</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-warning border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{warningTools}</h3>
              <p className="mb-0">需要关注</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-danger border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{criticalTools}</h3>
              <p className="mb-0">需要更换</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-info border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{toolLives.length}</h3>
              <p className="mb-0">刀具总数</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* 警告提示 */}
      {criticalTools > 0 && (
        <Alert variant="danger" dismissible>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          <strong>紧急:</strong> 有 {criticalTools} 把刀具需要立即更换！
        </Alert>
      )}
      {warningTools > 0 && criticalTools === 0 && (
        <Alert variant="warning" dismissible>
          <i className="bi bi-exclamation-circle-fill me-2"></i>
          <strong>注意:</strong> 有 {warningTools} 把刀具即将到达使用寿命，建议提前准备更换。
        </Alert>
      )}

      <Card className="shadow-sm">
        <Card.Body className="p-0">
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k || 'monitoring')}
            className="border-0"
          >
            <Tab eventKey="monitoring" title="刀具监控">
              <div className="p-4">
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>刀具</th>
                      <th>设备</th>
                      <th>安装日期</th>
                      <th>使用情况</th>
                      <th>剩余寿命</th>
                      <th>磨损系数</th>
                      <th>预计到期</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {toolLives.map((tool) => (
                      <tr key={tool.id}>
                        <td>
                          <strong>{tool.tool_name}</strong>
                          <br />
                          <small className="text-muted">ID: {tool.tool_id}</small>
                        </td>
                        <td>
                          {tool.device_name}
                          <br />
                          <small className="text-muted">{tool.device_id}</small>
                        </td>
                        <td>
                          <small>{tool.installed_date}</small>
                        </td>
                        <td>
                          <div className="mb-1">
                            <small className="text-muted">
                              {tool.used_life} / {tool.total_life} 分钟
                            </small>
                          </div>
                          <ProgressBar
                            now={tool.life_percentage}
                            variant={getLifeVariant(tool.life_percentage)}
                            style={{ height: '20px' }}
                            label={`${tool.life_percentage.toFixed(1)}%`}
                          />
                          <small className="text-muted d-block mt-1">
                            使用次数: {tool.usage_count}
                          </small>
                        </td>
                        <td>
                          <Badge bg={getLifeVariant(tool.life_percentage)} className="fs-6">
                            {tool.remaining_life.toFixed(0)} min
                          </Badge>
                        </td>
                        <td>
                          <span className="font-monospace">
                            {tool.wear_factor.toFixed(2)}
                          </span>
                        </td>
                        <td>
                          <small>{tool.predicted_life_end}</small>
                        </td>
                        <td>
                          <Badge {...getStatusBadge(tool.status)}>
                            {getStatusBadge(tool.status).text}
                          </Badge>
                        </td>
                        <td>
                          <Button
                            size="sm"
                            variant={tool.status === 'critical' || tool.status === 'expired' ? 'danger' : 'outline-primary'}
                            onClick={() => handleReplace(tool)}
                          >
                            {tool.status === 'critical' || tool.status === 'expired' ? '立即更换' : '更换'}
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>

            <Tab eventKey="history" title="换刀记录">
              <div className="p-4">
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>换刀日期</th>
                      <th>刀具</th>
                      <th>设备</th>
                      <th>更换原因</th>
                      <th>旧刀具寿命</th>
                      <th>操作员</th>
                    </tr>
                  </thead>
                  <tbody>
                    {replacements.map((record) => (
                      <tr key={record.id}>
                        <td>
                          <small>{record.replacement_date}</small>
                        </td>
                        <td>
                          <strong>{record.tool_name}</strong>
                        </td>
                        <td>
                          {record.device_id}
                        </td>
                        <td>
                          <Badge bg="warning">{record.reason}</Badge>
                        </td>
                        <td>
                          {record.old_tool_life} 分钟
                        </td>
                        <td>
                          {record.operator}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>

            <Tab eventKey="analysis" title="寿命分析">
              <div className="p-4">
                <Row>
                  <Col md={6}>
                    <Card>
                      <Card.Header>刀具寿命分布</Card.Header>
                      <Card.Body>
                        <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                          <div className="text-center text-muted">
                            <i className="bi bi-pie-chart display-4 mb-3"></i>
                            <p>刀具寿命分布图</p>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={6}>
                    <Card>
                      <Card.Header>磨损趋势</Card.Header>
                      <Card.Body>
                        <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                          <div className="text-center text-muted">
                            <i className="bi bi-graph-up display-4 mb-3"></i>
                            <p>磨损趋势图</p>
                          </div>
                        </div>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                <Card className="mt-4">
                  <Card.Header>寿命预测建议</Card.Header>
                  <Card.Body>
                    <ul>
                      <li className="mb-2">
                        <strong>优化切削参数</strong>: 降低进给量和切深可延长刀具寿命约20%
                      </li>
                      <li className="mb-2">
                        <strong>改善冷却条件</strong>: 充足的冷却可减少刀具磨损约15%
                      </li>
                      <li className="mb-2">
                        <strong>定期维护</strong>: 及时清理刀具和夹具可保持加工精度
                      </li>
                      <li>
                        <strong>提前备刀</strong>: 根据磨损系数预测，提前准备备用刀具
                      </li>
                    </ul>
                  </Card.Body>
                </Card>
              </div>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* 换刀确认模态框 */}
      <Modal show={showReplaceModal} onHide={() => setShowReplaceModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-tools me-2"></i>
            确认换刀
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTool && (
            <>
              <Alert variant="warning">
                <i className="bi bi-exclamation-triangle-fill me-2"></i>
                确定要更换刀具 <strong>{selectedTool.tool_name}</strong> 吗？
              </Alert>

              <Table bordered size="sm">
                <tbody>
                  <tr>
                    <td width="40%"><strong>刀具</strong></td>
                    <td>{selectedTool.tool_name}</td>
                  </tr>
                  <tr>
                    <td><strong>设备</strong></td>
                    <td>{selectedTool.device_name}</td>
                  </tr>
                  <tr>
                    <td><strong>已使用</strong></td>
                    <td>{selectedTool.used_life} 分钟</td>
                  </tr>
                  <tr>
                    <td><strong>剩余寿命</strong></td>
                    <td>{selectedTool.remaining_life} 分钟</td>
                  </tr>
                  <tr>
                    <td><strong>磨损系数</strong></td>
                    <td>{selectedTool.wear_factor.toFixed(2)}</td>
                  </tr>
                </tbody>
              </Table>

              <Form.Group className="mt-3">
                <Form.Label htmlFor="replacement-reason">更换原因</Form.Label>
                <Form.Select id="replacement-reason" name="replacement-reason">
                  <option value="expired">刀具寿命到期</option>
                  <option value="quality">加工质量下降</option>
                  <option value="damaged">刀具损坏</option>
                  <option value="process-change">工艺变更</option>
                  <option value="other">其他</option>
                </Form.Select>
              </Form.Group>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowReplaceModal(false)}>
            取消
          </Button>
          <Button variant="primary" onClick={confirmReplace}>
            <i className="bi bi-check-lg me-2"></i>
            确认更换
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default ToolLifePage