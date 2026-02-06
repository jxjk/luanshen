import React, { useState } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  Form,
  Tabs,
  Tab,
  Table,
  ProgressBar,
  Alert,
} from 'react-bootstrap'
import { theme } from '../theme'

interface EnergyData {
  device_id: string
  device_name: string
  total_energy: number // kWh
  active_energy: number // kWh
  idle_energy: number // kWh
  peak_power: number // kW
  avg_power: number // kW
  efficiency: number // %
  co2_emission: number // kg
  cost: number // 元
}

interface SavingOpportunity {
  id: number
  device_id: string
  device_name: string
  type: 'idle_reduction' | 'load_optimization' | 'process_optimization' | 'equipment_upgrade'
  description: string
  current_energy: number
  potential_saving: number
  saving_percentage: number
  investment: number
  payback_period: number // months
}

const EnergyAnalysisPage: React.FC = () => {
  const [selectedPeriod, setSelectedPeriod] = useState('month')
  const [selectedDevice, setSelectedDevice] = useState('all')
  const [loading, setLoading] = useState(false)

  // 模拟能耗数据
  const [energyData] = useState<EnergyData[]>([
    {
      device_id: 'CNC-001',
      device_name: 'FANUC-5AX',
      total_energy: 1250.5,
      active_energy: 980.2,
      idle_energy: 270.3,
      peak_power: 15.2,
      avg_power: 8.5,
      efficiency: 78.4,
      co2_emission: 725.3,
      cost: 1375.55,
    },
    {
      device_id: 'CNC-002',
      device_name: 'SIEMENS-3AX',
      total_energy: 890.3,
      active_energy: 720.5,
      idle_energy: 169.8,
      peak_power: 11.8,
      avg_power: 6.2,
      efficiency: 80.9,
      co2_emission: 516.4,
      cost: 979.33,
    },
    {
      device_id: 'CNC-003',
      device_name: 'DMG-MORI',
      total_energy: 1580.2,
      active_energy: 1180.5,
      idle_energy: 399.7,
      peak_power: 18.5,
      avg_power: 10.8,
      efficiency: 74.7,
      co2_emission: 916.5,
      cost: 1738.22,
    },
    {
      device_id: 'CNC-004',
      device_name: 'MAZAK-5AX',
      total_energy: 945.8,
      active_energy: 780.3,
      idle_energy: 165.5,
      peak_power: 14.2,
      avg_power: 7.8,
      efficiency: 82.5,
      co2_emission: 548.6,
      cost: 1040.38,
    },
  ])

  // 模拟节能机会
  const [savingOpportunities] = useState<SavingOpportunity[]>([
    {
      id: 1,
      device_id: 'CNC-001',
      device_name: 'FANUC-5AX',
      type: 'idle_reduction',
      description: '减少待机时间，启用自动休眠功能',
      current_energy: 270.3,
      potential_saving: 135.15,
      saving_percentage: 50,
      investment: 5000,
      payback_period: 8,
    },
    {
      id: 2,
      device_id: 'CNC-003',
      device_name: 'DMG-MORI',
      type: 'load_optimization',
      description: '优化负载率，避免低负载运行',
      current_energy: 399.7,
      potential_saving: 119.91,
      saving_percentage: 30,
      investment: 0,
      payback_period: 0,
    },
    {
      id: 3,
      device_id: 'CNC-002',
      device_name: 'SIEMENS-3AX',
      type: 'process_optimization',
      description: '优化切削参数，提高材料去除率',
      current_energy: 169.8,
      potential_saving: 50.94,
      saving_percentage: 30,
      investment: 2000,
      payback_period: 12,
    },
    {
      id: 4,
      device_id: 'CNC-004',
      device_name: 'MAZAK-5AX',
      type: 'equipment_upgrade',
      description: '升级为能效等级更高的主轴电机',
      current_energy: 165.5,
      potential_saving: 66.2,
      saving_percentage: 40,
      investment: 25000,
      payback_period: 24,
    },
  ])

  const getSavingTypeBadge = (type: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      idle_reduction: { bg: 'warning', text: '待机优化' },
      load_optimization: { bg: 'info', text: '负载优化' },
      process_optimization: { bg: 'success', text: '工艺优化' },
      equipment_upgrade: { bg: 'primary', text: '设备升级' },
    }
    return variants[type] || variants.idle_reduction
  }

  const getEfficiencyVariant = (efficiency: number) => {
    if (efficiency >= 80) return 'success'
    if (efficiency >= 70) return 'warning'
    return 'danger'
  }

  const totalEnergy = energyData.reduce((sum, d) => sum + d.total_energy, 0)
  const totalCost = energyData.reduce((sum, d) => sum + d.cost, 0)
  const totalCO2 = energyData.reduce((sum, d) => sum + d.co2_emission, 0)
  const totalPotentialSaving = savingOpportunities.reduce((sum, s) => sum + s.potential_saving, 0)

  const handleExport = () => {
    alert('导出能效分析报告')
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-lightning-charge me-2"></i>
            能效分析
          </h2>
          <p className="text-muted">
            设备能耗监控、节能潜力识别和绿色加工参数推荐
          </p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Form.Select
            id="period-selector"
            name="period-selector"
            value={selectedPeriod}
            onChange={(e) => setSelectedPeriod(e.target.value)}
            style={{ width: '150px' }}
          >
            <option value="day">今日</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="quarter">本季度</option>
            <option value="year">本年</option>
          </Form.Select>
          <Button variant="outline-secondary">
            <i className={`bi ${theme.icons.refresh} me-2`}></i>
            刷新
          </Button>
          <Button variant="primary" onClick={handleExport}>
            <i className={`bi ${theme.icons.download} me-2`}></i>
            导出报告
          </Button>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card stat-card-primary border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{totalEnergy.toFixed(1)}</h3>
              <p className="mb-0">总能耗 (kWh)</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-success border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                ¥{totalCost.toFixed(2)}
              </h3>
              <p className="mb-0">电费成本 (元)</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-warning border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{totalCO2.toFixed(1)}</h3>
              <p className="mb-0">CO₂排放 (kg)</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-info border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {energyData.length > 0 
                  ? (energyData.reduce((sum, d) => sum + d.efficiency, 0) / energyData.length).toFixed(1)
                  : 0}%
              </h3>
              <p className="mb-0">平均能效</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Row>
        <Col lg={8}>
          <Card className="shadow-sm">
            <Card.Body className="p-0">
              <Tabs defaultActiveKey="devices" className="border-0">
                <Tab eventKey="devices" title="设备能耗">
                  <div className="p-4">
                    <Table striped bordered hover responsive>
                      <thead>
                        <tr>
                          <th>设备</th>
                          <th>总能耗</th>
                          <th>有效能耗</th>
                          <th>待机能耗</th>
                          <th>能效</th>
                          <th>功率峰值</th>
                          <th>成本</th>
                          <th>CO₂排放</th>
                        </tr>
                      </thead>
                      <tbody>
                        {energyData.map((data) => (
                          <tr key={data.device_id}>
                            <td>
                              <strong>{data.device_name}</strong>
                              <br />
                              <small className="text-muted">{data.device_id}</small>
                            </td>
                            <td>
                              <Badge bg="primary" className="fs-6">
                                {data.total_energy.toFixed(1)}
                              </Badge>
                              <small className="text-muted d-block">kWh</small>
                            </td>
                            <td>
                              {data.active_energy.toFixed(1)} kWh
                              <ProgressBar
                                now={(data.active_energy / data.total_energy) * 100}
                                variant="success"
                                style={{ height: '6px', marginTop: '4px' }}
                              />
                            </td>
                            <td>
                              {data.idle_energy.toFixed(1)} kWh
                              <ProgressBar
                                now={(data.idle_energy / data.total_energy) * 100}
                                variant="warning"
                                style={{ height: '6px', marginTop: '4px' }}
                              />
                            </td>
                            <td>
                              <Badge bg={getEfficiencyVariant(data.efficiency)}>
                                {data.efficiency.toFixed(1)}%
                              </Badge>
                            </td>
                            <td>
                              {data.peak_power.toFixed(1)} kW
                            </td>
                            <td>
                              ¥{data.cost.toFixed(2)}
                            </td>
                            <td>
                              {data.co2_emission.toFixed(1)} kg
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </Table>
                  </div>
                </Tab>

                <Tab eventKey="trends" title="能耗趋势">
                  <div className="p-4">
                    <Alert variant="info">
                      <i className={`bi ${theme.icons.info} me-2`}></i>
                      此图表将展示能耗趋势分析
                    </Alert>
                    <div style={{ height: '400px', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                      <div className="text-center text-muted">
                        <i className="bi bi-graph-up display-4 mb-3"></i>
                        <p>能耗趋势图表</p>
                        <small>将显示各设备的能耗随时间变化趋势</small>
                      </div>
                    </div>
                  </div>
                </Tab>
              </Tabs>
            </Card.Body>
          </Card>
        </Col>

        <Col lg={4}>
          {/* 节能机会 */}
          <Card className="shadow-sm">
            <Card.Header>
              <i className="bi bi-lightbulb me-2"></i>
              节能机会
              <Badge bg="success" className="ms-2">{savingOpportunities.length}</Badge>
            </Card.Header>
            <Card.Body style={{ maxHeight: '500px', overflowY: 'auto' }}>
              <Alert variant="success">
                <i className="bi bi-check-circle-fill me-2"></i>
                潜在节能: <strong>{totalPotentialSaving.toFixed(1)} kWh</strong>
                <br />
                <small>预计节省: ¥{(totalPotentialSaving * 1.1).toFixed(2)} / 月</small>
              </Alert>

              {savingOpportunities.map((opportunity) => (
                <Card key={opportunity.id} className="mb-3 shadow-sm">
                  <Card.Header className="d-flex justify-content-between align-items-center">
                    <small>
                      <strong>{opportunity.device_name}</strong>
                    </small>
                    <Badge {...getSavingTypeBadge(opportunity.type)}>
                      {getSavingTypeBadge(opportunity.type).text}
                    </Badge>
                  </Card.Header>
                  <Card.Body>
                    <p className="mb-2 small">{opportunity.description}</p>
                    <div className="mb-2">
                      <small className="text-muted">当前能耗</small>
                      <div>{opportunity.current_energy.toFixed(1)} kWh</div>
                    </div>
                    <div className="mb-2">
                      <small className="text-muted">潜在节能</small>
                      <div className="text-success fw-bold">
                        {opportunity.potential_saving.toFixed(1)} kWh ({opportunity.saving_percentage}%)
                      </div>
                    </div>
                    {opportunity.investment > 0 && (
                      <div>
                        <small className="text-muted">投资回报期</small>
                        <div>{opportunity.payback_period} 个月</div>
                      </div>
                    )}
                  </Card.Body>
                </Card>
              ))}
            </Card.Body>
          </Card>

          {/* 绿色加工建议 */}
          <Card className="mt-4 shadow-sm">
            <Card.Header>
              <i className="bi bi-leaf me-2"></i>
              绿色加工建议
            </Card.Header>
            <Card.Body>
              <ul className="mb-0">
                <li className="mb-2">
                  <small>
                    <strong>高速切削</strong>: 提高切削速度可减少能耗约15%
                  </small>
                </li>
                <li className="mb-2">
                  <small>
                    <strong>干式切削</strong>: 减少冷却液使用可降低能耗约10%
                  </small>
                </li>
                <li className="mb-2">
                  <small>
                    <strong>刀具优化</strong>: 使用高效刀具可降低切削能耗
                  </small>
                </li>
                <li>
                  <small>
                    <strong>待机管理</strong>: 启用自动休眠可减少待机能耗
                  </small>
                </li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default EnergyAnalysisPage