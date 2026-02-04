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
  ProgressBar,
} from 'react-bootstrap'
import { machineService } from '../services/machineService'
import { Machine, MachineCreate } from '../types'

const MachinesPage: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [deletingMachine, setDeletingMachine] = useState<Machine | null>(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [editingMachine, setEditingMachine] = useState<Machine | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  const [formData, setFormData] = useState<MachineCreate>({
    name: '',
    type: '',
    pw_max: 0,
    rp_max: 0,
    tnm_max: 0,
    xiaoLv: 0.9,
    f_max: 0,
  })

  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadMachines()
  }, [])

  const loadMachines = async () => {
    try {
      setLoading(true)
      const data = await machineService.getAll()
      setMachines(data)
    } catch (err) {
      setError('加载设备数据失败')
      console.error('Error loading machines:', err)
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.name.trim()) errors.name = '设备名称不能为空'
    if (!formData.type.trim()) errors.type = '设备类型不能为空'
    if (formData.pw_max <= 0) errors.pw_max = '最大功率必须大于0'
    if (formData.rp_max <= 0) errors.rp_max = '最大转速必须大于0'
    if (formData.tnm_max <= 0) errors.tnm_max = '最大扭矩必须大于0'
    if (formData.xiaoLv <= 0 || formData.xiaoLv > 1) {
      errors.xiaoLv = '效率必须在 0 到 1 之间'
    }
    if (formData.f_max <= 0) errors.f_max = '最大进给必须大于0'

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleAdd = () => {
    setEditingMachine(null)
    setFormData({
      name: '',
      type: '',
      pw_max: 0,
      rp_max: 0,
      tnm_max: 0,
      xiaoLv: 0.9,
      f_max: 0,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleEdit = (machine: Machine) => {
    setEditingMachine(machine)
    setFormData({
      name: machine.name,
      type: machine.type,
      pw_max: machine.pw_max,
      rp_max: machine.rp_max,
      tnm_max: machine.tnm_max,
      xiaoLv: machine.xiaoLv,
      f_max: machine.f_max,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleDelete = (machine: Machine) => {
    setDeletingMachine(machine)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (deletingMachine) {
      try {
        await machineService.delete(deletingMachine.id)
        setSuccessMessage('设备删除成功')
        setShowDeleteModal(false)
        setDeletingMachine(null)
        loadMachines()
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        setError('删除设备失败')
        console.error('Error deleting machine:', err)
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
      if (editingMachine) {
        await machineService.update(editingMachine.id, formData)
        setSuccessMessage('设备更新成功')
      } else {
        await machineService.create(formData)
        setSuccessMessage('设备添加成功')
      }
      setShowModal(false)
      loadMachines()
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(editingMachine ? '更新设备失败' : '添加设备失败')
      console.error('Error saving machine:', err)
    }
  }

  // 搜索和分页
  const filteredMachines = machines.filter(machine =>
    machine.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    machine.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    machine.id.toString().includes(searchTerm)
  )

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredMachines.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(filteredMachines.length / itemsPerPage)

  const getMachineTypeBadge = (type: string) => {
    const variants: Record<string, string> = {
      'milling': 'primary',
      'drilling': 'success',
      'boring': 'warning',
      'turning': 'info',
      'lathe': 'dark',
    }
    return variants[type.toLowerCase()] || 'secondary'
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-pc-display me-2"></i>
            设备管理
          </h2>
          <p className="text-muted">管理系统中的设备参数</p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Form.Control
            type="text"
            placeholder="搜索设备..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '200px' }}
          />
          <Button variant="primary" onClick={handleAdd}>
            <i className="bi bi-plus-lg me-2"></i>
            添加设备
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
          ) : filteredMachines.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              {searchTerm ? '未找到匹配的设备' : '暂无设备数据，请点击"添加设备"按钮创建'}
            </Alert>
          ) : (
            <>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>最大功率</th>
                    <th>最大转速</th>
                    <th>最大扭矩</th>
                    <th>效率</th>
                    <th>最大进给</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((machine) => (
                    <tr key={machine.id}>
                      <td>
                        <Badge bg="secondary">{machine.id}</Badge>
                      </td>
                      <td>
                        <strong>{machine.name}</strong>
                      </td>
                      <td>
                        <Badge bg={getMachineTypeBadge(machine.type)}>
                          {machine.type}
                        </Badge>
                      </td>
                      <td>
                        <Badge bg="primary">{machine.pw_max} Kw</Badge>
                      </td>
                      <td>{machine.rp_max} r/min</td>
                      <td>{machine.tnm_max} Nm</td>
                      <td>
                        <ProgressBar
                          now={machine.xiaoLv * 100}
                          variant={machine.xiaoLv >= 0.8 ? 'success' : machine.xiaoLv >= 0.6 ? 'warning' : 'danger'}
                          style={{ height: '20px' }}
                          label={`${(machine.xiaoLv * 100).toFixed(0)}%`}
                        />
                      </td>
                      <td>{machine.f_max} mm/min</td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="me-1"
                          onClick={() => handleEdit(machine)}
                        >
                          <i className="bi bi-pencil"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(machine)}
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
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg" scrollable>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingMachine ? '编辑设备' : '添加设备'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>设备名称 <span className="text-danger">*</span></Form.Label>
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
                  <Form.Label>设备类型 <span className="text-danger">*</span></Form.Label>
                  <Form.Select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                    isInvalid={!!formErrors.type}
                  >
                    <option value="">请选择类型</option>
                    <option value="milling">铣床</option>
                    <option value="drilling">钻床</option>
                    <option value="boring">镗床</option>
                    <option value="turning">车床</option>
                    <option value="lathe">普通车床</option>
                  </Form.Select>
                  <Form.Control.Feedback type="invalid">{formErrors.type}</Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>最大功率 (Kw) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.pw_max}
                    onChange={(e) => setFormData({ ...formData, pw_max: Number(e.target.value) })}
                    isInvalid={!!formErrors.pw_max}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.pw_max}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>最大转速 (r/min) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.rp_max}
                    onChange={(e) => setFormData({ ...formData, rp_max: Number(e.target.value) })}
                    isInvalid={!!formErrors.rp_max}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.rp_max}</Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>最大扭矩 (Nm) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.tnm_max}
                    onChange={(e) => setFormData({ ...formData, tnm_max: Number(e.target.value) })}
                    isInvalid={!!formErrors.tnm_max}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.tnm_max}</Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>效率 (0-1) <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    min={0}
                    max={1}
                    value={formData.xiaoLv}
                    onChange={(e) => setFormData({ ...formData, xiaoLv: Number(e.target.value) })}
                    isInvalid={!!formErrors.xiaoLv}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.xiaoLv}</Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    输入 0.9 表示 90%
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>最大进给 (mm/min) <span className="text-danger">*</span></Form.Label>
              <Form.Control
                type="number"
                value={formData.f_max}
                onChange={(e) => setFormData({ ...formData, f_max: Number(e.target.value) })}
                isInvalid={!!formErrors.f_max}
              />
              <Form.Control.Feedback type="invalid">{formErrors.f_max}</Form.Control.Feedback>
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
          确定要删除设备 <strong>{deletingMachine?.name}</strong> 吗？此操作不可撤销。
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

export default MachinesPage