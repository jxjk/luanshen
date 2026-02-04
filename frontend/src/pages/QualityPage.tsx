import React, { useState, useRef } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Badge,
  Form,
  Modal,
  Alert,
  Tabs,
  Tab,
  Table,
  ProgressBar,
  InputGroup,
} from 'react-bootstrap'
import { theme } from '../theme'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface QualityRecord {
  id: number
  partNumber: string
  batchNumber: string
  station: string
  inspectionTime: string
  dimensions: Array<{
    name: string
    nominal: number
    actual: number
    tolerance: string
    result: 'pass' | 'fail'
  }>
  overallStatus: 'pass' | 'fail' | 'warning'
  inspector: string
}

interface PredictionResult {
  partNumber: string
  currentQuality: number
  predictedQuality: number
  trend: 'up' | 'down' | 'stable'
  riskFactors: string[]
  recommendations: string[]
}

const QualityPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('traceability')
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  // 模拟数据 - 质量追溯记录
  const [qualityRecords] = useState<QualityRecord[]>([
    {
      id: 1,
      partNumber: 'PRT-2025-0123',
      batchNumber: 'BATCH-001',
      station: 'CNC-001',
      inspectionTime: '2025-12-15 14:30:00',
      dimensions: [
        { name: '长度A', nominal: 100, actual: 100.02, tolerance: '±0.05', result: 'pass' },
        { name: '宽度B', nominal: 50, actual: 50.01, tolerance: '±0.03', result: 'pass' },
        { name: '高度C', nominal: 25, actual: 25.04, tolerance: '±0.02', result: 'pass' },
        { name: '孔径D', nominal: 20, actual: 20.06, tolerance: 'H7', result: 'pass' },
      ],
      overallStatus: 'pass',
      inspector: '张质检',
    },
    {
      id: 2,
      partNumber: 'PRT-2025-0124',
      batchNumber: 'BATCH-001',
      station: 'CNC-002',
      inspectionTime: '2025-12-15 15:15:00',
      dimensions: [
        { name: '长度A', nominal: 100, actual: 100.06, tolerance: '±0.05', result: 'fail' },
        { name: '宽度B', nominal: 50, actual: 50.02, tolerance: '±0.03', result: 'pass' },
        { name: '高度C', nominal: 25, actual: 25.03, tolerance: '±0.02', result: 'warning' },
        { name: '孔径D', nominal: 20, actual: 20.04, tolerance: 'H7', result: 'pass' },
      ],
      overallStatus: 'fail',
      inspector: '李质检',
    },
  ])

  // 模拟数据 - 质量预测
  const [predictionData] = useState<PredictionResult[]>([
    {
      partNumber: 'PRT-2025-0125',
      currentQuality: 96.5,
      predictedQuality: 94.2,
      trend: 'down',
      riskFactors: ['刀具磨损加剧', '主轴温度偏高'],
      recommendations: ['建议更换刀具', '检查冷却系统'],
    },
    {
      partNumber: 'PRT-2025-0126',
      currentQuality: 98.2,
      predictedQuality: 98.5,
      trend: 'up',
      riskFactors: [],
      recommendations: ['保持当前工艺参数'],
    },
  ])

  // 模拟数据 - SPC控制图数据
  const [spcData] = useState([
    { sample: 1, value: 10.02, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 2, value: 10.01, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 3, value: 9.99, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 4, value: 10.03, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 5, value: 10.04, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 6, value: 10.00, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 7, value: 9.98, ucl: 10.05, lcl: 9.95, mean: 10.00 },
    { sample: 8, value: 10.02, ucl: 10.05, lcl: 9.95, mean: 10.00 },
  ])

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      pass: { bg: 'success', text: '合格' },
      fail: { bg: 'danger', text: '不合格' },
      warning: { bg: 'warning', text: '警告' },
    }
    const config = variants[status] || variants.pass
    return <Badge bg={config.bg}>{config.text}</Badge>
  }

  const getDimensionResultBadge = (result: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      pass: { bg: 'success', text: '合格' },
      fail: { bg: 'danger', text: '超差' },
      warning: { bg: 'warning', text: '警告' },
    }
    const config = variants[result] || variants.pass
    return <Badge bg={config.bg}>{config.text}</Badge>
  }

  const getTrendIcon = (trend: string) => {
    return trend === 'up' ? (
      <i className="bi bi-arrow-up-circle-fill text-success"></i>
    ) : trend === 'down' ? (
      <i className="bi bi-arrow-down-circle-fill text-danger"></i>
    ) : (
      <i className="bi bi-dash-circle-fill text-secondary"></i>
    )
  }

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className={`bi ${theme.icons.quality} me-2`}></i>
            质量追溯与预测
          </h2>
          <p className="text-muted">
            全过程质量追溯、SPC监控和质量预测分析
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="primary">
            <i className={`bi ${theme.icons.add} me-2`}></i>
            新增检验记录
          </Button>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card stat-card-success border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">98.5%</h3>
              <p className="mb-0">一次合格率</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-primary border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">1.65</h3>
              <p className="mb-0">CPK指数</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-warning border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">3</h3>
              <p className="mb-0">待处理异常</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-info border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">256</h3>
              <p className="mb-0">本月检验数</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm">
        <Card.Body className="p-0">
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k || 'traceability')}
            className="border-0"
          >
            {/* 质量追溯 */}
            <Tab eventKey="traceability" title="质量追溯">
              <div className="p-4">
                <div className="d-flex gap-3 mb-4">
                  <InputGroup style={{ maxWidth: '400px' }}>
                    <InputGroup.Text>
                      <i className={`bi ${theme.icons.search}`}></i>
                    </InputGroup.Text>
                    <Form.Control
                      type="text"
                      placeholder="输入零件号或批次号..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </InputGroup>
                  <Button variant="outline-secondary">
                    <i className={`bi ${theme.icons.filter} me-2`}></i>
                    筛选
                  </Button>
                </div>

                <Alert variant="info">
                  <i className={`bi ${theme.icons.info} me-2`}></i>
                  通过扫描零件二维码或输入零件号，可追溯完整的加工过程数据
                </Alert>

                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>零件号</th>
                      <th>批次号</th>
                      <th>加工站点</th>
                      <th>检验时间</th>
                      <th>检验员</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {qualityRecords.map((record) => (
                      <tr key={record.id}>
                        <td>{record.id}</td>
                        <td>
                          <strong>{record.partNumber}</strong>
                        </td>
                        <td>{record.batchNumber}</td>
                        <td>{record.station}</td>
                        <td>{record.inspectionTime}</td>
                        <td>{record.inspector}</td>
                        <td>{getStatusBadge(record.overallStatus)}</td>
                        <td>
                          <Button
                            size="sm"
                            variant="outline-primary"
                            onClick={() => setShowDetailModal(true)}
                          >
                            <i className={`bi ${theme.icons.view} me-1`}></i>
                            详情
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>

            {/* SPC监控 */}
            <Tab eventKey="spc" title="SPC监控">
              <div className="p-4">
                <Row className="mb-4">
                  <Col md={4}>
                    <Card>
                      <Card.Header>控制图类型</Card.Header>
                      <Card.Body>
                        <Form.Select>
                          <option>Xbar-R 控制图</option>
                          <option>Xbar-S 控制图</option>
                          <option>I-MR 控制图</option>
                          <option>P 控制图</option>
                        </Form.Select>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4}>
                    <Card>
                      <Card.Header>控制参数</Card.Header>
                      <Card.Body>
                        <Form.Select>
                          <option>长度A</option>
                          <option>宽度B</option>
                          <option>高度C</option>
                          <option>孔径D</option>
                        </Form.Select>
                      </Card.Body>
                    </Card>
                  </Col>
                  <Col md={4}>
                    <Card>
                      <Card.Header>统计指标</Card.Header>
                      <Card.Body>
                        <Table size="sm">
                          <tbody>
                            <tr>
                              <td>CPK</td>
                              <td className="text-end">
                                <strong>1.65</strong>
                              </td>
                            </tr>
                            <tr>
                              <td>PPK</td>
                              <td className="text-end">
                                <strong>1.58</strong>
                              </td>
                            </tr>
                            <tr>
                              <td>过程能力</td>
                              <td className="text-end">
                                <Badge bg="success">充足</Badge>
                              </td>
                            </tr>
                          </tbody>
                        </Table>
                      </Card.Body>
                    </Card>
                  </Col>
                </Row>

                <Card>
                  <Card.Header>Xbar-R 控制图 - 长度A</Card.Header>
                  <Card.Body>
                    <Line
                      data={{
                        labels: spcData.map(d => `样本${d.sample}`),
                        datasets: [
                          {
                            label: '实测值',
                            data: spcData.map(d => d.value),
                            borderColor: '#0d6efd',
                            backgroundColor: 'rgba(13, 110, 253, 0.1)',
                            fill: true,
                            tension: 0.1,
                            pointRadius: 4,
                            pointBackgroundColor: spcData.map(d => {
                              if (d.value > d.ucl) return '#dc3545' // 红色：超上控制限
                              if (d.value < d.lcl) return '#dc3545' // 红色：超下控制限
                              return '#0d6efd' // 蓝色：正常
                            }),
                            pointBorderWidth: 2,
                          },
                          {
                            label: 'UCL (上控制限)',
                            data: spcData.map(d => d.ucl),
                            borderColor: '#dc3545',
                            backgroundColor: 'transparent',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            borderWidth: 2,
                          },
                          {
                            label: 'LCL (下控制限)',
                            data: spcData.map(d => d.lcl),
                            borderColor: '#dc3545',
                            backgroundColor: 'transparent',
                            borderDash: [5, 5],
                            pointRadius: 0,
                            borderWidth: 2,
                          },
                          {
                            label: '平均值',
                            data: spcData.map(d => d.mean),
                            borderColor: '#198754',
                            backgroundColor: 'transparent',
                            borderDash: [10, 5],
                            pointRadius: 0,
                            borderWidth: 2,
                          },
                        ],
                      }}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                          legend: {
                            position: 'top' as const,
                            labels: {
                              usePointStyle: true,
                              padding: 20,
                            },
                          },
                          tooltip: {
                            mode: 'index' as const,
                            intersect: false,
                            callbacks: {
                              footer: (tooltipItems) => {
                                const index = tooltipItems[0]?.dataIndex
                                if (index !== undefined) {
                                  const data = spcData[index]
                                  return [
                                    `UCL: ${data.ucl.toFixed(3)}`,
                                    `LCL: ${data.lcl.toFixed(3)}`,
                                    `Mean: ${data.mean.toFixed(3)}`,
                                  ]
                                }
                                return ''
                              },
                            },
                          },
                          title: {
                            display: true,
                            text: 'SPC 控制图',
                            font: {
                              size: 16,
                              weight: 'bold' as const,
                            },
                          },
                        },
                        scales: {
                          y: {
                            beginAtZero: false,
                            title: {
                              display: true,
                              text: '测量值 (mm)',
                            },
                            grid: {
                              color: 'rgba(0, 0, 0, 0.05)',
                            },
                          },
                          x: {
                            title: {
                              display: true,
                              text: '样本编号',
                            },
                            grid: {
                              display: false,
                            },
                          },
                        },
                        interaction: {
                          mode: 'index' as const,
                          intersect: false,
                        },
                      }}
                      height={300}
                    />
                  </Card.Body>
                </Card>
              </div>
            </Tab>

            {/* 质量预测 */}
            <Tab eventKey="prediction" title="质量预测">
              <div className="p-4">
                <Alert variant="warning">
                  <i className="bi bi-exclamation-triangle-fill me-2"></i>
                  基于实时加工数据和历史质量数据，预测当前批次的质量趋势
                </Alert>

                <Row>
                  {predictionData.map((item, idx) => (
                    <Col md={6} key={idx} className="mb-4">
                      <Card className="h-100 shadow-sm">
                        <Card.Header className="d-flex justify-content-between align-items-center">
                          <strong>{item.partNumber}</strong>
                          {getTrendIcon(item.trend)}
                        </Card.Header>
                        <Card.Body>
                          <Row className="mb-3">
                            <Col md={6}>
                              <div className="text-center">
                                <small className="text-muted">当前合格率</small>
                                <h3 className="mb-0">{item.currentQuality}%</h3>
                              </div>
                            </Col>
                            <Col md={6}>
                              <div className="text-center">
                                <small className="text-muted">预测合格率</small>
                                <h3 className={`mb-0 ${item.trend === 'down' ? 'text-danger' : 'text-success'}`}>
                                  {item.predictedQuality}%
                                </h3>
                              </div>
                            </Col>
                          </Row>

                          <div className="mb-3">
                            <small className="text-muted">趋势变化</small>
                                <ProgressBar
                                  now={item.predictedQuality}
                                  variant={item.trend === 'down' ? 'danger' : 'success'}
                                  label={`${item.predictedQuality}%`}
                                />
                          </div>

                          {item.riskFactors.length > 0 && (
                            <div className="mb-3">
                              <h6 className="mb-2">
                                <i className="bi bi-exclamation-triangle text-warning me-2"></i>
                                风险因素
                              </h6>
                              <ul className="mb-0">
                                {item.riskFactors.map((factor, fIdx) => (
                                  <li key={fIdx}>{factor}</li>
                                ))}
                              </ul>
                            </div>
                          )}

                          <div>
                            <h6 className="mb-2">
                              <i className="bi bi-lightbulb text-info me-2"></i>
                              改进建议
                            </h6>
                            <ul className="mb-0">
                              {item.recommendations.map((rec, rIdx) => (
                                <li key={rIdx}>{rec}</li>
                              ))}
                            </ul>
                          </div>
                        </Card.Body>
                      </Card>
                    </Col>
                  ))}
                </Row>
              </div>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* 质量详情模态框 */}
      <Modal show={showDetailModal} onHide={() => setShowDetailModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className={`bi ${theme.icons.view} me-2`}></i>
            质量追溯详情
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {qualityRecords.length > 0 && (
            <>
              <Alert variant={qualityRecords[0].overallStatus === 'pass' ? 'success' : 'danger'}>
                <i className={`bi ${qualityRecords[0].overallStatus === 'pass' ? 'bi-check-circle-fill' : 'bi-x-circle-fill'} me-2`}></i>
                零件 {qualityRecords[0].partNumber} 检验结果：{qualityRecords[0].overallStatus === 'pass' ? '合格' : '不合格'}
              </Alert>

              <Row className="mb-4">
                <Col md={3}>
                  <Card>
                    <Card.Body>
                      <small className="text-muted">零件号</small>
                      <h5 className="mb-0">{qualityRecords[0].partNumber}</h5>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card>
                    <Card.Body>
                      <small className="text-muted">批次号</small>
                      <h5 className="mb-0">{qualityRecords[0].batchNumber}</h5>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card>
                    <Card.Body>
                      <small className="text-muted">加工站点</small>
                      <h5 className="mb-0">{qualityRecords[0].station}</h5>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card>
                    <Card.Body>
                      <small className="text-muted">检验员</small>
                      <h5 className="mb-0">{qualityRecords[0].inspector}</h5>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>

              <h5 className="mb-3">尺寸检验明细</h5>
              <Table bordered responsive>
                <thead>
                  <tr>
                    <th>尺寸名称</th>
                    <th>公称值</th>
                    <th>实测值</th>
                    <th>公差</th>
                    <th>偏差</th>
                    <th>结果</th>
                  </tr>
                </thead>
                <tbody>
                  {qualityRecords[0].dimensions.map((dim, idx) => (
                    <tr key={idx}>
                      <td>{dim.name}</td>
                      <td>{dim.nominal}</td>
                      <td>
                        <strong>{dim.actual}</strong>
                      </td>
                      <td>{dim.tolerance}</td>
                      <td className={(dim.actual - dim.nominal) > 0 ? 'text-danger' : 'text-success'}>
                        {(dim.actual - dim.nominal) > 0 ? '+' : ''}{(dim.actual - dim.nominal).toFixed(3)}
                      </td>
                      <td>{getDimensionResultBadge(dim.result)}</td>
                    </tr>
                  ))}
                </tbody>
              </Table>

              <h5 className="mb-3 mt-4">加工参数记录</h5>
              <Table bordered responsive size="sm">
                <tbody>
                  <tr>
                    <td width="30%">转速</td>
                    <td>2500 r/min</td>
                  </tr>
                  <tr>
                    <td>进给量</td>
                    <td>400 mm/min</td>
                  </tr>
                  <tr>
                    <td>切深</td>
                    <td>2.5 mm</td>
                  </tr>
                  <tr>
                    <td>切宽</td>
                    <td>15 mm</td>
                  </tr>
                </tbody>
              </Table>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
            关闭
          </Button>
          <Button variant="primary">
            <i className={`bi ${theme.icons.download} me-2`}></i>
            导出报告
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default QualityPage