import React, { useState, useEffect } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Table,
  Alert,
  Modal,
  Form,
  Spinner,
  Badge,
  Pagination,
  Tabs,
  Tab,
  ProgressBar,
} from 'react-bootstrap'
import { theme } from '../theme'
import { optimizationService } from '../services/optimizationService'
import { materialService } from '../services/materialService'
import { toolService } from '../services/toolService'
import { machineService } from '../services/machineService'
import { strategyService } from '../services/strategyService'
import { Material, Tool, Machine, Strategy } from '../types'

interface OptimizationHistory {
  id: number
  timestamp: string
  material_id: string
  material_name: string
  tool_id: number
  tool_name: string
  machine_id: number
  machine_name: string
  strategy_id: number
  strategy_name: string
  algorithm_params: {
    population_size: number
    generations: number
    crossover_rate: number
    mutation_rate: number
  }
  result: {
    speed: number
    feed: number
    cut_depth: number
    cut_width: number
    cutting_speed: number
    feed_per_tooth: number
    power: number
    torque: number
    feed_force: number
    bottom_roughness: number
    side_roughness: number
    tool_life: number
    material_removal_rate: number
    fitness: number
  }
  execution_time: number
  user: string
}

const HistoryPage: React.FC = () => {
  const [histories, setHistories] = useState<OptimizationHistory[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)
  
  // 搜索和筛选
  const [searchTerm, setSearchTerm] = useState('')
  const [filterMaterial, setFilterMaterial] = useState('')
  const [filterDateStart, setFilterDateStart] = useState('')
  const [filterDateEnd, setFilterDateEnd] = useState('')
  
  // 详情模态框
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedHistory, setSelectedHistory] = useState<OptimizationHistory | null>(null)
  
  // 数据缓存
  const [materials, setMaterials] = useState<Material[]>([])
  const [tools, setTools] = useState<Tool[]>([])
  const [machines, setMachines] = useState<Machine[]>([])
  const [strategies, setStrategies] = useState<Strategy[]>([])

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      // 加载基础数据
      const [materialsData, toolsData, machinesData, strategiesData] = await Promise.all([
        materialService.getAll(),
        toolService.getAll(),
        machineService.getAll(),
        strategyService.getAll(),
      ])
      setMaterials(materialsData)
      setTools(toolsData)
      setMachines(machinesData)
      setStrategies(strategiesData)
      
      // 加载历史记录
      await loadHistories()
    } catch (err) {
      setError('加载数据失败')
      console.error('Error loading data:', err)
    } finally {
      setLoading(false)
    }
  }

  const loadHistories = async () => {
    try {
      // 模拟数据 - 实际应从API获取
      const mockHistories: OptimizationHistory[] = [
        {
          id: 1,
          timestamp: '2025-12-15 14:30:25',
          material_id: 'P1',
          material_name: '45钢',
          tool_id: 1,
          tool_name: '面铣刀-φ80',
          machine_id: 1,
          machine_name: 'FANUC-5AX',
          strategy_id: 1,
          strategy_name: '精加工策略',
          algorithm_params: {
            population_size: 10240,
            generations: 200,
            crossover_rate: 0.6,
            mutation_rate: 0.3,
          },
          result: {
            speed: 2500,
            feed: 400,
            cut_depth: 2.5,
            cut_width: 15,
            cutting_speed: 628.32,
            feed_per_tooth: 0.0267,
            power: 8.5,
            torque: 32.5,
            feed_force: 850,
            bottom_roughness: 2.8,
            side_roughness: 5.5,
            tool_life: 180,
            material_removal_rate: 15.0,
            fitness: 0.985,
          },
          execution_time: 15.2,
          user: '管理员',
        },
        {
          id: 2,
          timestamp: '2025-12-15 10:15:42',
          material_id: 'K1',
          material_name: 'HT200铸铁',
          tool_id: 2,
          tool_name: '立铣刀-φ10',
          machine_id: 2,
          machine_name: 'SIEMENS-3AX',
          strategy_id: 2,
          strategy_name: '粗加工策略',
          algorithm_params: {
            population_size: 20480,
            generations: 300,
            crossover_rate: 0.7,
            mutation_rate: 0.25,
          },
          result: {
            speed: 3200,
            feed: 600,
            cut_depth: 4.0,
            cut_width: 8,
            cutting_speed: 100.53,
            feed_per_tooth: 0.0469,
            power: 10.2,
            torque: 30.4,
            feed_force: 620,
            bottom_roughness: 3.2,
            side_roughness: 6.3,
            tool_life: 120,
            material_removal_rate: 19.2,
            fitness: 0.972,
          },
          execution_time: 28.5,
          user: '张工程师',
        },
        {
          id: 3,
          timestamp: '2025-12-14 16:45:18',
          material_id: 'N1',
          material_name: '6061铝合金',
          tool_id: 1,
          tool_name: '面铣刀-φ80',
          machine_id: 1,
          machine_name: 'FANUC-5AX',
          strategy_id: 1,
          strategy_name: '精加工策略',
          algorithm_params: {
            population_size: 10240,
            generations: 200,
            crossover_rate: 0.6,
            mutation_rate: 0.3,
          },
          result: {
            speed: 4000,
            feed: 800,
            cut_depth: 2.0,
            cut_width: 20,
            cutting_speed: 1005.31,
            feed_per_tooth: 0.0333,
            power: 7.8,
            torque: 18.6,
            feed_force: 480,
            bottom_roughness: 1.8,
            side_roughness: 3.8,
            tool_life: 240,
            material_removal_rate: 32.0,
            fitness: 0.991,
          },
          execution_time: 12.3,
          user: '李工程师',
        },
      ]
      setHistories(mockHistories)
    } catch (err) {
      setError('加载历史记录失败')
      console.error('Error loading histories:', err)
    }
  }

  const handleViewDetail = (history: OptimizationHistory) => {
    setSelectedHistory(history)
    setShowDetailModal(true)
  }

  const handleExport = async () => {
    try {
      // 模拟导出
      setSuccessMessage('历史记录已导出到Excel')
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError('导出失败')
    }
  }

  const handleReOptimize = (history: OptimizationHistory) => {
    // 跳转到优化页面并预填充参数
    alert(`将跳转到优化页面，使用参数：\n材料：${history.material_name}\n刀具：${history.tool_name}\n设备：${history.machine_name}`)
  }

  // 筛选和分页
  const filteredHistories = histories.filter(history => {
    const matchesSearch = 
      history.material_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      history.tool_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      history.machine_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      history.user.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesMaterial = !filterMaterial || history.material_id === filterMaterial
    
    const matchesDateStart = !filterDateStart || history.timestamp >= filterDateStart
    const matchesDateEnd = !filterDateEnd || history.timestamp <= filterDateEnd
    
    return matchesSearch && matchesMaterial && matchesDateStart && matchesDateEnd
  })

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredHistories.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(filteredHistories.length / itemsPerPage)

  const getMaterialBadge = (materialId: string) => {
    const variants: Record<string, string> = {
      'P': 'danger',
      'M': 'warning',
      'K': 'success',
      'N': 'info',
    }
    return variants[materialId.charAt(0)] || 'secondary'
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className={`bi ${theme.icons.history} me-2`}></i>
            历史记录
          </h2>
          <p className="text-muted">
            查看参数优化的历史记录，支持搜索、筛选和详情查看
          </p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Button variant="outline-secondary" onClick={loadData} disabled={loading}>
            {loading ? (
              <Spinner animation="border" size="sm" className="me-2" />
            ) : (
              <i className={`bi ${theme.icons.refresh} me-2`}></i>
            )}
            刷新
          </Button>
          <Button variant="primary" onClick={handleExport}>
            <i className={`bi ${theme.icons.download} me-2`}></i>
            导出
          </Button>
        </Col>
      </Row>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          <i className="bi bi-exclamation-triangle-fill me-2"></i>
          {error}
        </Alert>
      )}

      {successMessage && (
        <Alert variant="success" dismissible onClose={() => setSuccessMessage(null)}>
          <i className="bi bi-check-circle-fill me-2"></i>
          {successMessage}
        </Alert>
      )}

      {/* 统计卡片 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card stat-card-primary border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{histories.length}</h3>
              <p className="mb-0">优化记录总数</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-success border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {histories.length > 0 
                  ? (histories.reduce((sum, h) => sum + h.result.material_removal_rate, 0) / histories.length).toFixed(2)
                  : 0}
              </h3>
              <p className="mb-0">平均去除率 (cm³/min)</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-warning border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {histories.length > 0 
                  ? (histories.reduce((sum, h) => sum + h.execution_time, 0) / histories.length).toFixed(1)
                  : 0}
              </h3>
              <p className="mb-0">平均执行时间 (秒)</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-info border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {new Set(histories.map(h => h.user)).size}
              </h3>
              <p className="mb-0">使用用户数</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm">
        <Card.Body>
          {/* 筛选条件 */}
          <div className="mb-4 p-3 bg-light rounded">
            <Row>
              <Col md={3}>
                <Form.Label htmlFor="history-search">搜索</Form.Label>
                <Form.Control
                  type="text"
                  id="history-search"
                  name="history-search"
                  placeholder="材料/刀具/设备/用户..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </Col>
              <Col md={2}>
                <Form.Label htmlFor="filter-material">材料</Form.Label>
                <Form.Select
                  id="filter-material"
                  name="filter-material"
                  value={filterMaterial}
                  onChange={(e) => setFilterMaterial(e.target.value)}
                >
                  <option value="">全部</option>
                  {materials.map(m => (
                    <option key={m.caiLiaoZu} value={m.caiLiaoZu}>{m.name}</option>
                  ))}
                </Form.Select>
              </Col>
              <Col md={2}>
                <Form.Label htmlFor="filter-date-start">开始日期</Form.Label>
                <Form.Control
                  type="datetime-local"
                  id="filter-date-start"
                  name="filter-date-start"
                  value={filterDateStart}
                  onChange={(e) => setFilterDateStart(e.target.value)}
                />
              </Col>
              <Col md={2}>
                <Form.Label htmlFor="filter-date-end">结束日期</Form.Label>
                <Form.Control
                  type="datetime-local"
                  id="filter-date-end"
                  name="filter-date-end"
                  value={filterDateEnd}
                  onChange={(e) => setFilterDateEnd(e.target.value)}
                />
              </Col>
              <Col md={3} className="d-flex align-items-end">
                <Button
                  variant="outline-secondary"
                  onClick={() => {
                    setSearchTerm('')
                    setFilterMaterial('')
                    setFilterDateStart('')
                    setFilterDateEnd('')
                  }}
                >
                  清除筛选
                </Button>
              </Col>
            </Row>
          </div>

          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
              <p className="mt-2 text-muted">加载中...</p>
            </div>
          ) : filteredHistories.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              {searchTerm || filterMaterial || filterDateStart || filterDateEnd
                ? '未找到匹配的记录'
                : '暂无优化历史记录'}
            </Alert>
          ) : (
            <>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>优化时间</th>
                    <th>材料</th>
                    <th>刀具</th>
                    <th>设备</th>
                    <th>策略</th>
                    <th>材料去除率</th>
                    <th>适应度</th>
                    <th>执行时间</th>
                    <th>用户</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((history) => (
                    <tr key={history.id}>
                      <td>
                        <Badge bg="secondary">{history.id}</Badge>
                      </td>
                      <td>
                        <small>{history.timestamp}</small>
                      </td>
                      <td>
                        <Badge bg={getMaterialBadge(history.material_id)}>
                          {history.material_name}
                        </Badge>
                      </td>
                      <td>
                        <small>{history.tool_name}</small>
                      </td>
                      <td>
                        <small>{history.machine_name}</small>
                      </td>
                      <td>
                        <small>{history.strategy_name}</small>
                      </td>
                      <td>
                        <Badge bg="success" className="fs-6">
                          {history.result.material_removal_rate.toFixed(2)}
                        </Badge>
                        <small className="text-muted d-block">cm³/min</small>
                      </td>
                      <td>
                        <span className="font-monospace">
                          {history.result.fitness.toFixed(4)}
                        </span>
                      </td>
                      <td>
                        {history.execution_time.toFixed(1)}s
                      </td>
                      <td>
                        <small>{history.user}</small>
                      </td>
                      <td>
                        <Button
                          size="sm"
                          variant="outline-primary"
                          className="me-1"
                          onClick={() => handleViewDetail(history)}
                        >
                          <i className={`bi ${theme.icons.view}`}></i>
                        </Button>
                        <Button
                          size="sm"
                          variant="outline-success"
                          onClick={() => handleReOptimize(history)}
                        >
                          <i className={`bi ${theme.icons.refresh}`}></i>
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>

              {totalPages > 1 && (
                <Pagination className="justify-content-center">
                  <Pagination.First onClick={() => setCurrentPage(1)} disabled={currentPage === 1} />
                  <Pagination.Prev 
                    onClick={() => setCurrentPage(p => Math.max(1, p - 1))} 
                    disabled={currentPage === 1} 
                  />
                  {[...Array(totalPages)].map((_, i) => (
                    <Pagination.Item
                      key={i + 1}
                      active={currentPage === i + 1}
                      onClick={() => setCurrentPage(i + 1)}
                    >
                      {i + 1}
                    </Pagination.Item>
                  ))}
                  <Pagination.Next 
                    onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} 
                    disabled={currentPage === totalPages} 
                  />
                  <Pagination.Last onClick={() => setCurrentPage(totalPages)} disabled={currentPage === totalPages} />
                </Pagination>
              )}
            </>
          )}
        </Card.Body>
      </Card>

      {/* 详情模态框 */}
      <Modal show={showDetailModal} onHide={() => setShowDetailModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className={`bi ${theme.icons.view} me-2`}></i>
            优化记录详情
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedHistory && (
            <>
              <Alert variant="success">
                <i className="bi bi-clock-history me-2"></i>
                优化时间：{selectedHistory.timestamp}
                <span className="ms-3">用户：{selectedHistory.user}</span>
                <span className="ms-3">执行时间：{selectedHistory.execution_time.toFixed(2)}秒</span>
              </Alert>

              <Tabs defaultActiveKey="result">
                <Tab eventKey="result" title="优化结果">
                  <Row className="mb-4">
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h4>{selectedHistory.result.speed.toFixed(0)}</h4>
                          <p className="text-muted mb-0">转速 (r/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h4>{selectedHistory.result.feed.toFixed(0)}</h4>
                          <p className="text-muted mb-0">进给量 (mm/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card className="text-center bg-success text-white">
                        <Card.Body>
                          <h4>{selectedHistory.result.material_removal_rate.toFixed(2)}</h4>
                          <p className="mb-0">去除率 (cm³/min)</p>
                        </Card.Body>
                      </Card>
                    </Col>
                    <Col md={3}>
                      <Card className="text-center">
                        <Card.Body>
                          <h4>{selectedHistory.result.fitness.toFixed(4)}</h4>
                          <p className="text-muted mb-0">适应度</p>
                        </Card.Body>
                      </Card>
                    </Col>
                  </Row>

                  <Table striped bordered hover>
                    <tbody>
                      <tr>
                        <td><strong>转速</strong></td>
                        <td>{selectedHistory.result.speed.toFixed(0)} r/min</td>
                      </tr>
                      <tr>
                        <td><strong>进给量</strong></td>
                        <td>{selectedHistory.result.feed.toFixed(0)} mm/min</td>
                      </tr>
                      <tr>
                        <td><strong>切深</strong></td>
                        <td>{selectedHistory.result.cut_depth.toFixed(2)} mm</td>
                      </tr>
                      <tr>
                        <td><strong>切宽</strong></td>
                        <td>{selectedHistory.result.cut_width.toFixed(2)} mm</td>
                      </tr>
                      <tr>
                        <td><strong>线速度</strong></td>
                        <td>{selectedHistory.result.cutting_speed.toFixed(2)} m/min</td>
                      </tr>
                      <tr>
                        <td><strong>每齿进给</strong></td>
                        <td>{selectedHistory.result.feed_per_tooth.toFixed(4)} mm</td>
                      </tr>
                      <tr>
                        <td><strong>功率</strong></td>
                        <td>{selectedHistory.result.power.toFixed(2)} Kw</td>
                      </tr>
                      <tr>
                        <td><strong>扭矩</strong></td>
                        <td>{selectedHistory.result.torque.toFixed(2)} Nm</td>
                      </tr>
                      <tr>
                        <td><strong>进给力</strong></td>
                        <td>{selectedHistory.result.feed_force.toFixed(2)} N</td>
                      </tr>
                      <tr>
                        <td><strong>底面粗糙度</strong></td>
                        <td>{selectedHistory.result.bottom_roughness.toFixed(2)} um</td>
                      </tr>
                      <tr>
                        <td><strong>侧面粗糙度</strong></td>
                        <td>{selectedHistory.result.side_roughness.toFixed(2)} um</td>
                      </tr>
                      <tr>
                        <td><strong>刀具寿命</strong></td>
                        <td>{selectedHistory.result.tool_life.toFixed(0)} min</td>
                      </tr>
                    </tbody>
                  </Table>
                </Tab>

                <Tab eventKey="input" title="输入参数">
                  <Table bordered>
                    <tbody>
                      <tr>
                        <td width="30%"><strong>材料</strong></td>
                        <td>
                          <Badge bg={getMaterialBadge(selectedHistory.material_id)}>
                            {selectedHistory.material_name} ({selectedHistory.material_id})
                          </Badge>
                        </td>
                      </tr>
                      <tr>
                        <td><strong>刀具</strong></td>
                        <td>{selectedHistory.tool_name} (ID: {selectedHistory.tool_id})</td>
                      </tr>
                      <tr>
                        <td><strong>设备</strong></td>
                        <td>{selectedHistory.machine_name} (ID: {selectedHistory.machine_id})</td>
                      </tr>
                      <tr>
                        <td><strong>策略</strong></td>
                        <td>{selectedHistory.strategy_name} (ID: {selectedHistory.strategy_id})</td>
                      </tr>
                    </tbody>
                  </Table>

                  <h6 className="mt-4 mb-3">算法参数</h6>
                  <Table bordered>
                    <tbody>
                      <tr>
                        <td width="30%"><strong>种群大小</strong></td>
                        <td>{selectedHistory.algorithm_params.population_size}</td>
                      </tr>
                      <tr>
                        <td><strong>迭代次数</strong></td>
                        <td>{selectedHistory.algorithm_params.generations}</td>
                      </tr>
                      <tr>
                        <td><strong>交叉概率</strong></td>
                        <td>{selectedHistory.algorithm_params.crossover_rate}</td>
                      </tr>
                      <tr>
                        <td><strong>变异概率</strong></td>
                        <td>{selectedHistory.algorithm_params.mutation_rate}</td>
                      </tr>
                    </tbody>
                  </Table>
                </Tab>
              </Tabs>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDetailModal(false)}>
            关闭
          </Button>
          <Button variant="primary" onClick={() => selectedHistory && handleReOptimize(selectedHistory)}>
            <i className={`bi ${theme.icons.refresh} me-2`}></i>
            使用此参数重新优化
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default HistoryPage