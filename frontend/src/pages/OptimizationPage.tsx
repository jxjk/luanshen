import React, { useState, useEffect, useCallback } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
  Spinner,
  Tab,
  Tabs,
  Table,
  Badge,
  ProgressBar,
  Modal,
  Tooltip,
  OverlayTrigger,
} from 'react-bootstrap'
import { optimizationService } from '../services/optimizationService'
import { materialService } from '../services/materialService'
import PDFService from '../services/pdfService'
import { toolService } from '../services/toolService'
import { machineService } from '../services/machineService'
import { strategyService } from '../services/strategyService'
import {
  OptimizationRequest,
  OptimizationResult,
  Material,
  Tool,
  Machine,
  Strategy,
} from '../types'

const OptimizationPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [dataLoading, setDataLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<OptimizationResult | null>(null)
  const [optimizationProgress, setOptimizationProgress] = useState(0)
  const [showResultModal, setShowResultModal] = useState(false)

  // 数据
  const [materials, setMaterials] = useState<Material[]>([])
  const [tools, setTools] = useState<Tool[]>([])
  const [machines, setMachines] = useState<Machine[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])

  // 表单数据
  const [formData, setFormData] = useState<OptimizationRequest>({
    material_id: '',
    tool_id: '',
    machine_id: '',
    strategy_id: '',
    population_size: 10240,
    generations: 200,
    crossover_rate: 0.6,
    mutation_rate: 0.3,
  })

  // 表单验证错误
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setDataLoading(true)
      const [materialsData, toolsData, machinesData, strategiesData] =
        await Promise.all([
          materialService.getAll(),
          toolService.getAll(),
          machineService.getAll(),
          strategyService.getAll(),
        ])
      setMaterials(materialsData)
      setTools(toolsData)
      setMachines(machinesData)
      setStrategies(strategiesData)

      // 设置默认值
      if (materialsData.length > 0) {
        setFormData((prev) => ({ ...prev, material_id: materialsData[0].caiLiaoZu }))
      }
      if (toolsData.length > 0) {
        setFormData((prev) => ({ ...prev, tool_id: String(toolsData[0].id) }))
      }
      if (machinesData.length > 0) {
        setFormData((prev) => ({ ...prev, machine_id: String(machinesData[0].id) }))
      }
      if (strategiesData.length > 0) {
        setFormData((prev) => ({ ...prev, strategy_id: String(strategiesData[0].id) }))
      }
    } catch (err) {
      setError('加载数据失败，请检查后端服务是否正常运行')
      console.error('Error loading data:', err)
    } finally {
      setDataLoading(false)
    }
  }

  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.material_id) errors.material_id = '请选择材料'
    if (!formData.tool_id) errors.tool_id = '请选择刀具'
    if (!formData.machine_id) errors.machine_id = '请选择设备'
    if (!formData.strategy_id) errors.strategy_id = '请选择策略'
    
    if (formData.population_size < 100 || formData.population_size > 100000) {
      errors.population_size = '种群大小必须在 100 到 100000 之间'
    }
    if (formData.generations < 10 || formData.generations > 1000) {
      errors.generations = '迭代次数必须在 10 到 1000 之间'
    }
    if (formData.crossover_rate < 0 || formData.crossover_rate > 1) {
      errors.crossover_rate = '交叉概率必须在 0 到 1 之间'
    }
    if (formData.mutation_rate < 0 || formData.mutation_rate > 1) {
      errors.mutation_rate = '变异概率必须在 0 到 1 之间'
    }

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }, [formData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    if (!validateForm()) {
      setError('请检查表单中的错误')
      return
    }

    setLoading(true)
    setOptimizationProgress(0)

    // 模拟进度
    const progressInterval = setInterval(() => {
      setOptimizationProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval)
          return 95
        }
        return prev + Math.random() * 10
      })
    }, 500)

    try {
      const response = await optimizationService.optimize(formData)
      clearInterval(progressInterval)
      setOptimizationProgress(100)
      
      if (response.success) {
        setResult(response.result)
        setShowResultModal(true)
      } else {
        setError(response.message || '优化失败')
      }
    } catch (err) {
      clearInterval(progressInterval)
      setError('优化请求失败，请检查网络连接')
      console.error('Optimization error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReset = () => {
    setResult(null)
    setError(null)
    setOptimizationProgress(0)
    setFormErrors({})
  }

  const getSelectedMaterial = () => materials.find((m) => m.caiLiaoZu === formData.material_id)
  const getSelectedTool = () => tools.find((t) => t.id === Number(formData.tool_id))
  const getSelectedMachine = () => machines.find((m) => m.id === Number(formData.machine_id))
  const getSelectedStrategy = () =>
    strategies.find((s) => s.id === Number(formData.strategy_id))

  const getConstraintUsage = (result: OptimizationResult) => {
    const constraints = [
      { name: '功率', value: result.power, unit: 'Kw', max: getSelectedMachine()?.pw_max },
      { name: '扭矩', value: result.torque, unit: 'Nm', max: getSelectedMachine()?.tnm_max },
      { name: '进给', value: result.feed_force, unit: 'N', max: getSelectedTool()?.ff_max },
    ]
    
    return constraints.map(c => {
      if (!c.max) return null
      const percentage = (c.value / c.max) * 100
      let variant: 'success' | 'warning' | 'danger' = 'success'
      if (percentage > 90) variant = 'danger'
      else if (percentage > 70) variant = 'warning'
      return { ...c, percentage, variant }
    }).filter(Boolean)
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-speedometer2 me-2"></i>
            参数优化
          </h2>
          <p className="text-muted">
            基于微生物遗传算法，在满足所有约束条件的前提下，最大化材料去除率
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="outline-secondary" onClick={loadData} disabled={dataLoading}>
            <i className="bi bi-arrow-clockwise me-2"></i>
            刷新数据
          </Button>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      <Row>
        <Col lg={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Header className="bg-primary text-white">
              <i className="bi bi-sliders me-2"></i>
              优化参数设置
            </Card.Header>
            <Card.Body>
              {dataLoading ? (
                <div className="text-center py-5">
                  <Spinner animation="border" />
                  <p className="mt-2 text-muted">加载数据中...</p>
                </div>
              ) : (
                <Form onSubmit={handleSubmit}>
                  <Form.Group className="mb-3">
                    <Form.Label htmlFor="material-select">
                      材料 <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Select
                      id="material-select"
                      name="material-select"
                      value={formData.material_id}
                      onChange={(e) =>
                        setFormData({ ...formData, material_id: e.target.value })
                      }
                      isInvalid={!!formErrors.material_id}
                      disabled={materials.length === 0}
                    >
                      <option value="">请选择材料</option>
                      {materials.map((material) => (
                        <option key={material.caiLiaoZu} value={material.caiLiaoZu}>
                          {material.name} ({material.caiLiaoZu})
                        </option>
                      ))}
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">
                      {formErrors.material_id}
                    </Form.Control.Feedback>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label htmlFor="tool-select">
                      刀具 <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Select
                      id="tool-select"
                      name="tool-select"
                      value={formData.tool_id}
                      onChange={(e) =>
                        setFormData({ ...formData, tool_id: e.target.value })
                      }
                      isInvalid={!!formErrors.tool_id}
                      disabled={tools.length === 0}
                    >
                      <option value="">请选择刀具</option>
                      {tools.map((tool) => (
                        <option key={tool.id} value={tool.id}>
                          {tool.name} (Φ{tool.zhiJing}mm, {tool.chiShu}齿)
                        </option>
                      ))}
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">
                      {formErrors.tool_id}
                    </Form.Control.Feedback>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label htmlFor="machine-select">
                      设备 <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Select
                      id="machine-select"
                      name="machine-select"
                      value={formData.machine_id}
                      onChange={(e) =>
                        setFormData({ ...formData, machine_id: e.target.value })
                      }
                      isInvalid={!!formErrors.machine_id}
                      disabled={machines.length === 0}
                    >
                      <option value="">请选择设备</option>
                      {machines.map((machine) => (
                        <option key={machine.id} value={machine.id}>
                          {machine.name} ({machine.type})
                        </option>
                      ))}
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">
                      {formErrors.machine_id}
                    </Form.Control.Feedback>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label htmlFor="strategy-select">
                      策略 <span className="text-danger">*</span>
                    </Form.Label>
                    <Form.Select
                      id="strategy-select"
                      name="strategy-select"
                      value={formData.strategy_id}
                      onChange={(e) =>
                        setFormData({ ...formData, strategy_id: e.target.value })
                      }
                      isInvalid={!!formErrors.strategy_id}
                      disabled={strategies.length === 0}
                    >
                      <option value="">请选择策略</option>
                      {strategies.map((strategy) => (
                        <option key={strategy.id} value={strategy.id}>
                          {strategy.name} ({strategy.type})
                        </option>
                      ))}
                    </Form.Select>
                    <Form.Control.Feedback type="invalid">
                      {formErrors.strategy_id}
                    </Form.Control.Feedback>
                  </Form.Group>

                  <hr />

                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h6 className="mb-0">算法参数</h6>
                    <Button
                      variant="link"
                      size="sm"
                      onClick={() => {
                        setFormData({
                          ...formData,
                          population_size: 10240,
                          generations: 200,
                          crossover_rate: 0.6,
                          mutation_rate: 0.3,
                        })
                      }}
                    >
                      重置默认
                    </Button>
                  </div>

                  <Form.Group className="mb-3">
                    <Form.Label htmlFor="population-size">种群大小</Form.Label>
                    <Form.Control
                      type="number"
                      id="population-size"
                      name="population-size"
                      value={formData.population_size}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          population_size: Number(e.target.value),
                        })
                      }
                      min={100}
                      max={100000}
                      isInvalid={!!formErrors.population_size}
                    />
                    <Form.Control.Feedback type="invalid">
                      {formErrors.population_size}
                    </Form.Control.Feedback>
                    <Form.Text className="text-muted">
                      值越大精度越高，但计算时间越长
                    </Form.Text>
                  </Form.Group>

                  <Form.Group className="mb-3">
                    <Form.Label htmlFor="generations">迭代次数</Form.Label>
                    <Form.Control
                      type="number"
                      id="generations"
                      name="generations"
                      value={formData.generations}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          generations: Number(e.target.value),
                        })
                      }
                      min={10}
                      max={1000}
                      isInvalid={!!formErrors.generations}
                    />
                    <Form.Control.Feedback type="invalid">
                      {formErrors.generations}
                    </Form.Control.Feedback>
                  </Form.Group>

                  <Row>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label htmlFor="crossover-rate">交叉概率</Form.Label>
                        <Form.Control
                          type="number"
                          step="0.1"
                          id="crossover-rate"
                          name="crossover-rate"
                          value={formData.crossover_rate}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              crossover_rate: Number(e.target.value),
                            })
                          }
                          min={0}
                          max={1}
                          isInvalid={!!formErrors.crossover_rate}
                        />
                        <Form.Control.Feedback type="invalid">
                          {formErrors.crossover_rate}
                        </Form.Control.Feedback>
                      </Form.Group>
                    </Col>
                    <Col md={6}>
                      <Form.Group className="mb-3">
                        <Form.Label htmlFor="mutation-rate">变异概率</Form.Label>
                        <Form.Control
                          type="number"
                          step="0.1"
                          id="mutation-rate"
                          name="mutation-rate"
                          value={formData.mutation_rate}
                          onChange={(e) =>
                            setFormData({
                              ...formData,
                              mutation_rate: Number(e.target.value),
                            })
                          }
                          min={0}
                          max={1}
                          isInvalid={!!formErrors.mutation_rate}
                        />
                        <Form.Control.Feedback type="invalid">
                          {formErrors.mutation_rate}
                        </Form.Control.Feedback>
                      </Form.Group>
                    </Col>
                  </Row>

                  {loading && optimizationProgress > 0 && (
                    <div className="mb-3">
                      <div className="d-flex justify-content-between mb-1">
                        <small>优化进度</small>
                        <small>{Math.round(optimizationProgress)}%</small>
                      </div>
                      <ProgressBar animated now={optimizationProgress} variant="primary" />
                    </div>
                  )}

                  <div className="d-grid gap-2">
                    <Button
                      type="submit"
                      variant="primary"
                      disabled={loading || dataLoading}
                      size="lg"
                    >
                      {loading ? (
                        <>
                          <Spinner animation="border" size="sm" className="me-2" />
                          优化中...
                        </>
                      ) : (
                        <>
                          <i className="bi bi-play-fill me-2"></i>
                          开始优化
                        </>
                      )}
                    </Button>
                    
                    {result && (
                      <Button
                        variant="outline-secondary"
                        onClick={handleReset}
                        disabled={loading}
                      >
                        <i className="bi bi-arrow-counterclockwise me-2"></i>
                        重置
                      </Button>
                    )}
                  </div>
                </Form>
              )}
            </Card.Body>
          </Card>

          {/* 选择信息卡片 */}
          <Card className="shadow-sm">
            <Card.Header>
              <i className="bi bi-info-circle me-2"></i>
              当前选择
            </Card.Header>
            <Card.Body>
              {getSelectedMaterial() && (
                <div className="mb-2">
                  <Badge bg="primary" className="me-2">材料</Badge>
                  {getSelectedMaterial()?.name}
                  <br />
                  <small className="text-muted">
                    抗拉强度: {getSelectedMaterial()?.rm_min}-{getSelectedMaterial()?.rm_max} MPa
                  </small>
                </div>
              )}
              {getSelectedTool() && (
                <div className="mb-2">
                  <Badge bg="success" className="me-2">刀具</Badge>
                  {getSelectedTool()?.name}
                  <br />
                  <small className="text-muted">
                    直径: Φ{getSelectedTool()?.zhiJing}mm, 齿数: {getSelectedTool()?.chiShu}
                  </small>
                </div>
              )}
              {getSelectedMachine() && (
                <div className="mb-2">
                  <Badge bg="info" className="me-2">设备</Badge>
                  {getSelectedMachine()?.name}
                  <br />
                  <small className="text-muted">
                    功率: {getSelectedMachine()?.pw_max}Kw, 转速: {getSelectedMachine()?.rp_max}r/min
                  </small>
                </div>
              )}
              {getSelectedStrategy() && (
                <div className="mb-2">
                  <Badge bg="warning" className="me-2">策略</Badge>
                  {getSelectedStrategy()?.name}
                  <br />
                  <small className="text-muted">
                    类型: {getSelectedStrategy()?.type}
                  </small>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col lg={8}>
          {result ? (
            <>
              {/* 核心参数 */}
              <Card className="mb-4 shadow-sm">
                <Card.Header className="bg-success text-white">
                  <i className="bi bi-check-circle-fill me-2"></i>
                  优化结果
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6} className="mb-3">
                      <Card className="stat-card primary border-0">
                        <Card.Body className="text-center">
                          <h3 className="mb-1">{result.speed.toFixed(0)}</h3>
                          <p className="mb-0">转速 (r/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={6} className="mb-3">
                      <Card className="stat-card success border-0">
                        <Card.Body className="text-center">
                          <h3 className="mb-1">{result.feed.toFixed(0)}</h3>
                          <p className="mb-0">进给量 (mm/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={6} className="mb-3">
                      <Card className="stat-card warning border-0">
                        <Card.Body className="text-center">
                          <h3 className="mb-1">{result.cut_depth.toFixed(2)}</h3>
                          <p className="mb-0">切深 (mm)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={6} className="mb-3">
                      <Card className="stat-card secondary border-0">
                        <Card.Body className="text-center">
                          <h3 className="mb-1">{result.cut_width.toFixed(2)}</h3>
                          <p className="mb-0">切宽 (mm)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>

              {/* 详细参数 */}
              <Card className="mb-4 shadow-sm">
                <Card.Header>
                  <i className="bi bi-list-ul me-2"></i>
                  详细参数
                </Card.Header>
                <Card.Body>
                  <Tabs defaultActiveKey="cutting" className="mb-3">
                    <Tab eventKey="cutting" title="切削参数">
                      <Table striped bordered hover responsive className="mb-0">
                        <tbody>
                          <tr>
                            <td><strong>线速度</strong></td>
                            <td>
                              <Badge bg="primary" className="fs-6">
                                {result.cutting_speed.toFixed(2)} m/min
                              </Badge>
                            </td>
                          </tr>
                          <tr>
                            <td><strong>每齿进给</strong></td>
                            <td>{result.feed_per_tooth.toFixed(4)} mm</td>
                          </tr>
                          <tr>
                            <td><strong>转速</strong></td>
                            <td>{result.speed.toFixed(0)} r/min</td>
                          </tr>
                          <tr>
                            <td><strong>进给量</strong></td>
                            <td>{result.feed.toFixed(0)} mm/min</td>
                          </tr>
                          <tr>
                            <td><strong>切深</strong></td>
                            <td>{result.cut_depth.toFixed(2)} mm</td>
                          </tr>
                          <tr>
                            <td><strong>切宽</strong></td>
                            <td>{result.cut_width.toFixed(2)} mm</td>
                          </tr>
                        </tbody>
                      </Table>
                    </Tab>

                    <Tab eventKey="performance" title="性能指标">
                      <div className="mb-4">
                        <h6 className="mb-3">约束使用情况</h6>
                        {getConstraintUsage(result).map((constraint, idx) => (
                          <div key={idx} className="mb-3">
                            <div className="d-flex justify-content-between mb-1">
                              <small>{constraint.name}</small>
                              <small>
                                {constraint.value.toFixed(2)} {constraint.unit} / {constraint.max} {constraint.unit}
                              </small>
                            </div>
                            <ProgressBar 
                              now={constraint.percentage} 
                              variant={constraint.variant} 
                              label={`${constraint.percentage.toFixed(0)}%`}
                            />
                          </div>
                        ))}
                      </div>
                      <Table striped bordered hover responsive className="mb-0">
                        <tbody>
                          <tr>
                            <td><strong>功率</strong></td>
                            <td>{result.power.toFixed(2)} Kw</td>
                          </tr>
                          <tr>
                            <td><strong>扭矩</strong></td>
                            <td>{result.torque.toFixed(2)} Nm</td>
                          </tr>
                          <tr>
                            <td><strong>进给力</strong></td>
                            <td>{result.feed_force.toFixed(2)} N</td>
                          </tr>
                          <tr>
                            <td><strong>材料去除率</strong></td>
                            <td>
                              <Badge bg="success" className="fs-6">
                                {result.material_removal_rate.toFixed(2)} cm³/min
                              </Badge>
                            </td>
                          </tr>
                        </tbody>
                      </Table>
                    </Tab>

                    <Tab eventKey="quality" title="质量指标">
                      <Table striped bordered hover responsive className="mb-0">
                        <tbody>
                          <tr>
                            <td><strong>底面粗糙度</strong></td>
                            <td>
                              <Badge bg={result.bottom_roughness < 3.2 ? 'success' : 'warning'}>
                                {result.bottom_roughness.toFixed(2)} um
                              </Badge>
                            </td>
                          </tr>
                          <tr>
                            <td><strong>侧面粗糙度</strong></td>
                            <td>
                              <Badge bg={result.side_roughness < 6.3 ? 'success' : 'warning'}>
                                {result.side_roughness.toFixed(2)} um
                              </Badge>
                            </td>
                          </tr>
                          <tr>
                            <td><strong>刀具寿命</strong></td>
                            <td>{result.tool_life.toFixed(0)} min</td>
                          </tr>
                          <tr>
                            <td><strong>适应度</strong></td>
                            <td className="font-monospace">{result.fitness.toFixed(6)}</td>
                          </tr>
                        </tbody>
                      </Table>
                    </Tab>
                  </Tabs>
                </Card.Body>
              </Card>
            </>
          ) : (
            <Card className="text-center py-5 shadow-sm">
              <Card.Body>
                <i className="bi bi-lightbulb display-1 text-muted mb-3"></i>
                <h4 className="text-muted">等待优化</h4>
                <p className="text-muted mb-4">
                  请在左侧选择材料、刀具、设备和策略，然后点击"开始优化"按钮
                </p>
                {dataLoading && (
                  <div>
                    <Spinner animation="border" />
                    <p className="mt-2 text-muted">正在加载必要数据...</p>
                  </div>
                )}
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* 结果详情模态框 */}
      <Modal show={showResultModal} onHide={() => setShowResultModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-check-circle-fill text-success me-2"></i>
            优化结果详情
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {result && (
            <>
              <Alert variant="success">
                <i className="bi bi-trophy-fill me-2"></i>
                优化完成！材料去除率达到 <strong>{result.material_removal_rate.toFixed(2)} cm³/min</strong>
              </Alert>
              
              <Tabs defaultActiveKey="summary">
                <Tab eventKey="summary" title="摘要">
                  <Row>
                    <Col md={4} className="mb-3">
                      <Card className="text-center">
                        <Card.Body>
                          <h4>{result.speed.toFixed(0)}</h4>
                          <p className="text-muted mb-0">转速 (r/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={4} className="mb-3">
                      <Card className="text-center">
                        <Card.Body>
                          <h4>{result.feed.toFixed(0)}</h4>
                          <p className="text-muted mb-0">进给量 (mm/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={4} className="mb-3">
                      <Card className="text-center bg-success text-white">
                        <Card.Body>
                          <h4>{result.material_removal_rate.toFixed(2)}</h4>
                          <p className="mb-0">去除率 (cm³/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>
                </Tab>
                <Tab eventKey="all" title="全部参数">
                  <Table striped bordered hover responsive>
                    <tbody>
                      <tr>
                        <td><strong>线速度</strong></td>
                        <td>{result.cutting_speed.toFixed(2)} m/min</td>
                        <td><strong>每齿进给</strong></td>
                        <td>{result.feed_per_tooth.toFixed(4)} mm</td>
                      </tr>
                      <tr>
                        <td><strong>转速</strong></td>
                        <td>{result.speed.toFixed(0)} r/min</td>
                        <td><strong>进给量</strong></td>
                        <td>{result.feed.toFixed(0)} mm/min</td>
                      </tr>
                      <tr>
                        <td><strong>切深</strong></td>
                        <td>{result.cut_depth.toFixed(2)} mm</td>
                        <td><strong>切宽</strong></td>
                        <td>{result.cut_width.toFixed(2)} mm</td>
                      </tr>
                      <tr>
                        <td><strong>功率</strong></td>
                        <td>{result.power.toFixed(2)} Kw</td>
                        <td><strong>扭矩</strong></td>
                        <td>{result.torque.toFixed(2)} Nm</td>
                      </tr>
                      <tr>
                        <td><strong>进给力</strong></td>
                        <td>{result.feed_force.toFixed(2)} N</td>
                        <td><strong>底面粗糙度</strong></td>
                        <td>{result.bottom_roughness.toFixed(2)} um</td>
                      </tr>
                      <tr>
                        <td><strong>侧面粗糙度</strong></td>
                        <td>{result.side_roughness.toFixed(2)} um</td>
                        <td><strong>刀具寿命</strong></td>
                        <td>{result.tool_life.toFixed(0)} min</td>
                      </tr>
                      <tr>
                        <td colSpan={3}><strong>适应度</strong></td>
                        <td className="font-monospace">{result.fitness.toFixed(6)}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Tab>
              </Tabs>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowResultModal(false)}>
            关闭
          </Button>
          <Button 
            variant="primary" 
            onClick={() => {
              if (result) {
                const selectedTool = getSelectedTool();
                const selectedMachine = getSelectedMachine();
                const selectedStrategy = getSelectedStrategy();
                const pdfData = {
                  result,
                  material: { ...getSelectedMaterial(), id: String(getSelectedMaterial().id) },
                  tool: { ...selectedTool, ap_max: selectedTool.ap_max || 5.0, daoJianR: selectedTool.daoJianR || 0.0 },
                  machine: { ...selectedMachine, id: String(selectedMachine.id) },
                  strategy: { ...selectedStrategy, id: String(selectedStrategy.id) },
                  constraints: getConstraintUsage(result)
                }
                PDFService.generateOptimizationReport(pdfData)
              }
            }}
          >
            <i className="bi bi-file-earmark-pdf me-2"></i>
            导出 PDF
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default OptimizationPage