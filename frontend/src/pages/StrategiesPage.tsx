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
} from 'react-bootstrap'
import { strategyService } from '../services/strategyService'
import { Strategy, StrategyCreate } from '../types'

const StrategiesPage: React.FC = () => {
  const [strategies, setStrategies] = useState<Strategy[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [deletingStrategy, setDeletingStrategy] = useState<Strategy | null>(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [editingStrategy, setEditingStrategy] = useState<Strategy | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  const [formData, setFormData] = useState<StrategyCreate>({
    name: '',
    type: '',
    rx_min: 0,
    rz_min: 0,
    lft_min: 0,
    ae: 0,
    moSunXiShu: 0,
  })

  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadStrategies()
  }, [])

  const loadStrategies = async () => {
    try {
      setLoading(true)
      const data = await strategyService.getAll()
      setStrategies(data)
    } catch (err) {
      setError('加载策略数据失败')
      console.error('Error loading strategies:', err)
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.name.trim()) errors.name = '策略名称不能为空'
    if (!formData.type.trim()) errors.type = '策略类型不能为空'
    if (formData.rx_min <= 0) errors.rx_min = '最小底面粗糙度必须大于0'
    if (formData.rz_min <= 0) errors.rz_min = '最小侧面粗糙度必须大于0'
    if (formData.lft_min <= 0) errors.lft_min = '最小刀具寿命必须大于0'
    if (formData.ae <= 0) errors.ae = '切宽必须大于0'

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleAdd = () => {
    setEditingStrategy(null)
    setFormData({
      name: '',
      type: '',
      rx_min: 0,
      rz_min: 0,
      lft_min: 0,
      ae: 0,
      moSunXiShu: 0,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleEdit = (strategy: Strategy) => {
    setEditingStrategy(strategy)
    setFormData({
      name: strategy.name,
      type: strategy.type,
      rx_min: strategy.rx_min,
      rz_min: strategy.rz_min,
      lft_min: strategy.lft_min,
      ae: strategy.ae,
      moSunXiShu: strategy.moSunXiShu || 0,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleDelete = (strategy: Strategy) => {
    setDeletingStrategy(strategy)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (deletingStrategy) {
      try {
        await strategyService.delete(deletingStrategy.id)
        setSuccessMessage('策略删除成功')
        setShowDeleteModal(false)
        setDeletingStrategy(null)
        loadStrategies()
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        setError('删除策略失败')
        console.error('Error deleting strategy:', err)
      }
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!validateForm()) {
      setError('请检查表单中的错误')
      return
    }

    try {
      if (editingStrategy) {
        await strategyService.update(editingStrategy.id, formData)
        setSuccessMessage('策略更新成功')
      } else {
        await strategyService.create(formData)
        setSuccessMessage('策略添加成功')
      }
      setShowModal(false)
      loadStrategies()
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(editingStrategy ? '更新策略失败' : '添加策略失败')
      console.error('Error saving strategy:', err)
    }
  }

  // 搜索和分页
  const filteredStrategies = strategies.filter(strategy =>
    strategy.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    strategy.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    strategy.id.toString().includes(searchTerm)
  )

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredStrategies.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(filteredStrategies.length / itemsPerPage)

  const getStrategyTypeBadge = (type: string) => {
    const variants: Record<string, string> = {
      'milling': 'primary',
      'drilling': 'success',
      'boring': 'warning',
      'turning': 'info',
    }
    return variants[type.toLowerCase()] || 'secondary'
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-list-task me-2"></i>
            策略管理
          </h2>
          <p className="text-muted">管理系统中的加工策略</p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Form.Control
            type="text"
            placeholder="搜索策略..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '200px' }}
          />
          <Button variant="primary" onClick={handleAdd}>
            <i className="bi bi-plus-lg me-2"></i>
            添加策略
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

      <Card className="shadow-sm">
        <Card.Body>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
              <p className="mt-2 text-muted">加载中...</p>
            </div>
          ) : filteredStrategies.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              {searchTerm ? '未找到匹配的策略' : '暂无策略数据，请点击"添加策略"按钮创建'}
            </Alert>
          ) : (
            <>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>最小底面粗糙度</th>
                    <th>最小侧面粗糙度</th>
                    <th>最小刀具寿命</th>
                    <th>切宽</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((strategy) => (
                    <tr key={strategy.id}>
                      <td>
                        <Badge bg="secondary">{strategy.id}</Badge>
                      </td>
                      <td>
                        <strong>{strategy.name}</strong>
                      </td>
                      <td>
                        <Badge bg={getStrategyTypeBadge(strategy.type)}>
                          {strategy.type}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg="primary">{strategy.rx_min} um</Badge>
                      </td>
                      <td>
                        <Badge bg="success">{strategy.rz_min} um</Badge>
                      </td>
                      <td>{strategy.lft_min} min</td>
                      <td>
                        <span className="font-monospace">{strategy.ae} mm</span>
                      </td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="me-1"
                          onClick={() => handleEdit(strategy)}
                        >
                          <i className="bi bi-pencil"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(strategy)}
                        >
                          <i className="bi bi-trash"></i>
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

      {/* 添加/编辑模态框 */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingStrategy ? '编辑策略' : '添加策略'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>策略名称 <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    isInvalid={!!formErrors.name}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.name}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>策略类型 <span className="text-danger">*</span></Form.Label>
                  <Form.Select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    isInvalid={!!formErrors.type}
                  >
                    <option value="">请选择类型</option>
                    <option value="milling">铣削</option>
                    <option value="drilling">钻孔</option>
                    <option value="boring">镗孔</option>
                    <option value="turning">车削</option>
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">{formErrors.type}</Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>最小底面粗糙度 (um) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.rx_min}
                    onChange={(e) => setFormData({ ...formData, rx_min: Number(e.target.value) })}
                    isInvalid={!!formErrors.rx_min}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.rx_min}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>最小侧面粗糙度 (um) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.rz_min}
                    onChange={(e) => setFormData({ ...formData, rz_min: Number(e.target.value) })}
                    isInvalid={!!formErrors.rz_min}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.rz_min}</Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>最小刀具寿命 (min) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.lft_min}
                    onChange={(e) => setFormData({ ...formData, lft_min: Number(e.target.value) })}
                    isInvalid={!!formErrors.lft_min}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.lft_min}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>切宽 (mm) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.ae}
                    onChange={(e) => setFormData({ ...formData, ae: Number(e.target.value) })}
                    isInvalid={!!formErrors.ae}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.ae}</Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>磨损系数</Form.Label>
              <Form.Control
                type="number"
                step="0.01"
                value={formData.moSunXiShu}
                onChange={(e) => setFormData({ ...formData, moSunXiShu: Number(e.target.value) })}
              />
              <Form.Text className="text-muted">
                用于计算刀具寿命，默认为0
              </Form.Text>
            </Form.Group>

            <div className="text-end">
              <Button variant="secondary" onClick={() => setShowModal(false)} className="me-2">
                取消
              </Button>
              <Button type="submit" variant="primary">
                <i className="bi bi-check-lg me-2"></i>
                保存
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>

      {/* 删除确认模态框 */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)} centered>
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-exclamation-triangle text-warning me-2"></i>
            确认删除
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          确定要删除策略 <strong>{deletingStrategy?.name}</strong> 吗？此操作不可撤销。
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            取消
          </Button>
          <Button variant="danger" onClick={confirmDelete}>
            <i className="bi bi-trash me-2"></i>
            删除
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default StrategiesPage