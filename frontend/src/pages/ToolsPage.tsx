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
import { toolService } from '../services/toolService'
import { Tool, ToolCreate } from '../types'

const ToolsPage: React.FC = () => {
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [deletingTool, setDeletingTool] = useState<Tool | null>(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [editingTool, setEditingTool] = useState<Tool | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  const [formData, setFormData] = useState<ToolCreate>({
    name: '',
    type: '',
    zhiJing: 0,
    chiShu: 0,
    vc_max: 0,
    fz_max: 0,
    ct: 0,
    s_xiShu: 0,
    f_xiShu: 0,
    ap_xiShu: 0,
    ap_max: 0,
    ff_max: 0,
    daoJianR: 0,
    zhuPianJiao: 0,
    qianJiao: 0,
  })

  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadTools()
  }, [])

  const loadTools = async () => {
    try {
      setLoading(true)
      const data = await toolService.getAll()
      setTools(data)
    } catch (err) {
      setError('加载刀具数据失败')
      console.error('Error loading tools:', err)
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.name.trim()) errors.name = '刀具名称不能为空'
    if (!formData.type.trim()) errors.type = '刀具类型不能为空'
    if (formData.zhiJing <= 0) errors.zhiJing = '直径必须大于0'
    if (formData.chiShu <= 0) errors.chiShu = '齿数必须大于0'
    if (formData.vc_max <= 0) errors.vc_max = '最大线速度必须大于0'
    if (formData.fz_max <= 0) errors.fz_max = '最大每齿进给必须大于0'
    if (formData.ct <= 0) errors.ct = '耐用度系数必须大于0'

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleAdd = () => {
    setEditingTool(null)
    setFormData({
      name: '',
      type: '',
      zhiJing: 0,
      chiShu: 0,
      vc_max: 0,
      fz_max: 0,
      ct: 0,
      s_xiShu: 0,
      f_xiShu: 0,
      ap_xiShu: 0,
      ap_max: 0,
      ff_max: 0,
      daoJianR: 0,
      zhuPianJiao: 0,
      qianJiao: 0,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleEdit = (tool: Tool) => {
    setEditingTool(tool)
    setFormData({
      name: tool.name,
      type: tool.type,
      zhiJing: tool.zhiJing,
      chiShu: tool.chiShu,
      vc_max: tool.vc_max,
      fz_max: tool.fz_max,
      ct: tool.ct,
      s_xiShu: tool.s_xiShu,
      f_xiShu: tool.f_xiShu,
      ap_xiShu: tool.ap_xiShu,
      ap_max: tool.ap_max || 0,
      ff_max: tool.ff_max || 0,
      daoJianR: tool.daoJianR || 0,
      zhuPianJiao: tool.zhuPianJiao || 0,
      qianJiao: tool.qianJiao || 0,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleDelete = (tool: Tool) => {
    setDeletingTool(tool)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (deletingTool) {
      try {
        await toolService.delete(deletingTool.id)
        setSuccessMessage('刀具删除成功')
        setShowDeleteModal(false)
        setDeletingTool(null)
        loadTools()
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        setError('删除刀具失败')
        console.error('Error deleting tool:', err)
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
      if (editingTool) {
        await toolService.update(editingTool.id, formData)
        setSuccessMessage('刀具更新成功')
      } else {
        await toolService.create(formData)
        setSuccessMessage('刀具添加成功')
      }
      setShowModal(false)
      loadTools()
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(editingTool ? '更新刀具失败' : '添加刀具失败')
      console.error('Error saving tool:', err)
    }
  }

  // 搜索和分页
  const filteredTools = tools.filter(tool =>
    tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tool.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    tool.id.toString().includes(searchTerm)
  )

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredTools.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(filteredTools.length / itemsPerPage)

  const getToolTypeBadge = (type: string) => {
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
            <i className="bi bi-tools me-2"></i>
            刀具管理
          </h2>
          <p className="text-muted">管理系统中的刀具参数</p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Form.Label htmlFor="tool-search" className="visually-hidden">搜索刀具</Form.Label>
          <Form.Control
            type="text"
            id="tool-search"
            name="tool-search"
            placeholder="搜索刀具..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '200px' }}
          />
          <Button variant="primary" onClick={handleAdd}>
            <i className="bi bi-plus-lg me-2"></i>
            添加刀具
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
          ) : filteredTools.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              {searchTerm ? '未找到匹配的刀具' : '暂无刀具数据，请点击"添加刀具"按钮创建'}
            </Alert>
          ) : (
            <>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>直径 (mm)</th>
                    <th>齿数</th>
                    <th>最大线速度</th>
                    <th>最大每齿进给</th>
                    <th>耐用度系数</th>
                    <th>刀尖半径</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((tool) => (
                    <tr key={tool.id}>
                      <td>
                        <Badge bg="secondary">{tool.id}</Badge>
                      </td>
                      <td>
                        <strong>{tool.name}</strong>
                      </td>
                      <td>
                        <Badge bg={getToolTypeBadge(tool.type)}>
                          {tool.type}
                        </Badge>
                      </td>
                      <td>
                        <span className="font-monospace">Φ{tool.zhiJing}</span>
                      </td>
                      <td>{tool.chiShu}</td>
                      <td>{tool.vc_max} m/min</td>
                      <td>{tool.fz_max} mm</td>
                      <td>{tool.ct}</td>
                      <td>
                        <Badge bg="info">
                          R{tool.nose_radius || tool.daoJianR || 0}
                        </Badge>
                      </td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="me-1"
                          onClick={() => handleEdit(tool)}
                        >
                          <i className="bi bi-pencil"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(tool)}
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
      <Modal show={showModal} onHide={() => setShowModal(false)} size="xl" scrollable>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingTool ? '编辑刀具' : '添加刀具'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>刀具名称 <span className="text-danger">*</span></Form.Label>
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
                  <Form.Label>刀具类型 <span className="text-danger">*</span></Form.Label>
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
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>直径 (mm) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.zhiJing}
                    onChange={(e) => setFormData({ ...formData, zhiJing: Number(e.target.value) })}
                    isInvalid={!!formErrors.zhiJing}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.zhiJing}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>齿数 <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.chiShu}
                    onChange={(e) => setFormData({ ...formData, chiShu: Number(e.target.value) })}
                    isInvalid={!!formErrors.chiShu}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.chiShu}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>最大线速度 (m/min) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.vc_max}
                    onChange={(e) => setFormData({ ...formData, vc_max: Number(e.target.value) })}
                    isInvalid={!!formErrors.vc_max}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.vc_max}</Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>最大每齿进给 (mm) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    value={formData.fz_max}
                    onChange={(e) => setFormData({ ...formData, fz_max: Number(e.target.value) })}
                    isInvalid={!!formErrors.fz_max}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.fz_max}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>耐用度系数 <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.ct}
                    onChange={(e) => setFormData({ ...formData, ct: Number(e.target.value) })}
                    isInvalid={!!formErrors.ct}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.ct}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>最大切深 (mm)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.ap_max}
                    onChange={(e) => setFormData({ ...formData, ap_max: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <h6 className="mb-3">高级参数</h6>
            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>速度系数</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.s_xiShu}
                    onChange={(e) => setFormData({ ...formData, s_xiShu: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>进给系数</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.f_xiShu}
                    onChange={(e) => setFormData({ ...formData, f_xiShu: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>切深系数</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.ap_xiShu}
                    onChange={(e) => setFormData({ ...formData, ap_xiShu: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>最大进给力 (N)</Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.ff_max}
                    onChange={(e) => setFormData({ ...formData, ff_max: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>刀尖半径 (mm)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.daoJianR}
                    onChange={(e) => setFormData({ ...formData, daoJianR: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>主偏角 (°)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.zhuPianJiao}
                    onChange={(e) => setFormData({ ...formData, zhuPianJiao: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={4}>
                <Form.Group className="mb-3">
                  <Form.Label>前角 (°)</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.qianJiao}
                    onChange={(e) => setFormData({ ...formData, qianJiao: Number(e.target.value) })}
                  />
                </Form.Group>
              </Col>
            </Row>

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
          确定要删除刀具 <strong>{deletingTool?.name}</strong> 吗？此操作不可撤销。
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

export default ToolsPage