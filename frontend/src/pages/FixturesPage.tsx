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
} from 'react-bootstrap'
import { theme } from '../theme'

interface Fixture {
  id: number
  name: string
  type: string
  model_number: string
  clamping_range_min: number
  clamping_range_max: number
  accuracy: number
  max_clamping_force: number
  weight: number
  dimensions: {
    length: number
    width: number
    height: number
  }
  positioning_method: string
  model_file: string
  status: 'active' | 'inactive' | 'maintenance'
  created_at: string
  last_used: string
  usage_count: number
}

interface FixtureCreate {
  name: string
  type: string
  model_number: string
  clamping_range_min: number
  clamping_range_max: number
  accuracy: number
  max_clamping_force: number
  weight: number
  dimensions: {
    length: number
    width: number
    height: number
  }
  positioning_method: string
}

const FixturesPage: React.FC = () => {
  const [fixtures, setFixtures] = useState<Fixture[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [deletingFixture, setDeletingFixture] = useState<Fixture | null>(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [editingFixture, setEditingFixture] = useState<Fixture | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  const [formData, setFormData] = useState<FixtureCreate>({
    name: '',
    type: '',
    model_number: '',
    clamping_range_min: 0,
    clamping_range_max: 0,
    accuracy: 0,
    max_clamping_force: 0,
    weight: 0,
    dimensions: {
      length: 0,
      width: 0,
      height: 0,
    },
    positioning_method: '',
  })

  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadFixtures()
  }, [])

  const loadFixtures = async () => {
    try {
      setLoading(true)
      // 模拟数据 - 实际应从API获取
      const mockFixtures: Fixture[] = [
        {
          id: 1,
          name: '精密虎钳-100mm',
          type: '机用虎钳',
          model_number: 'HV-100A',
          clamping_range_min: 0,
          clamping_range_max: 100,
          accuracy: 0.02,
          max_clamping_force: 15000,
          weight: 8.5,
          dimensions: {
            length: 320,
            width: 150,
            height: 120,
          },
          positioning_method: 'T型槽',
          model_file: 'fixture_vise_100.stp',
          status: 'active',
          created_at: '2025-10-15 10:30:00',
          last_used: '2025-12-14 16:45:00',
          usage_count: 156,
        },
        {
          id: 2,
          name: '精密虎钳-150mm',
          type: '机用虎钳',
          model_number: 'HV-150A',
          clamping_range_min: 0,
          clamping_range_max: 150,
          accuracy: 0.03,
          max_clamping_force: 22000,
          weight: 12.3,
          dimensions: {
            length: 420,
            width: 180,
            height: 140,
          },
          positioning_method: 'T型槽',
          model_file: 'fixture_vise_150.stp',
          status: 'active',
          created_at: '2025-10-18 14:20:00',
          last_used: '2025-12-15 09:30:00',
          usage_count: 89,
        },
        {
          id: 3,
          name: '气动夹具-方板',
          type: '气动夹具',
          model_number: 'PA-200S',
          clamping_range_min: 50,
          clamping_range_max: 200,
          accuracy: 0.05,
          max_clamping_force: 5000,
          weight: 15.6,
          dimensions: {
            length: 300,
            width: 300,
            height: 80,
          },
          positioning_method: '定位销',
          model_file: 'fixture_pneumatic_200.stp',
          status: 'active',
          created_at: '2025-11-05 09:15:00',
          last_used: '2025-12-13 14:20:00',
          usage_count: 45,
        },
        {
          id: 4,
          name: '组合夹具套装',
          type: '组合夹具',
          model_number: 'MF-500SET',
          clamping_range_min: 10,
          clamping_range_max: 500,
          accuracy: 0.05,
          max_clamping_force: 10000,
          weight: 45.2,
          dimensions: {
            length: 600,
            width: 400,
            height: 200,
          },
          positioning_method: '模块化组合',
          model_file: 'fixture_modular_500.stp',
          status: 'active',
          created_at: '2025-09-20 11:00:00',
          last_used: '2025-12-15 10:15:00',
          usage_count: 234,
        },
        {
          id: 5,
          name: '三爪卡盘-200mm',
          type: '卡盘',
          model_number: 'CK-200',
          clamping_range_min: 10,
          clamping_range_max: 200,
          accuracy: 0.02,
          max_clamping_force: 18000,
          weight: 18.5,
          dimensions: {
            length: 200,
            width: 200,
            height: 150,
          },
          positioning_method: '螺纹传动',
          model_file: 'fixture_chuck_200.stp',
          status: 'maintenance',
          created_at: '2025-08-10 16:30:00',
          last_used: '2025-12-10 08:45:00',
          usage_count: 312,
        },
      ]
      setFixtures(mockFixtures)
    } catch (err) {
      setError('加载夹具数据失败')
      console.error('Error loading fixtures:', err)
    } finally {
      setLoading(false)
    }
  }

  const validateForm = (): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.name.trim()) errors.name = '夹具名称不能为空'
    if (!formData.type.trim()) errors.type = '夹具类型不能为空'
    if (!formData.model_number.trim()) errors.model_number = '型号不能为空'
    if (formData.clamping_range_min < 0) errors.clamping_range_min = '最小夹持范围不能为负数'
    if (formData.clamping_range_max <= 0) errors.clamping_range_max = '最大夹持范围必须大于0'
    if (formData.clamping_range_max < formData.clamping_range_min) {
      errors.clamping_range_max = '最大夹持范围不能小于最小夹持范围'
    }
    if (formData.accuracy <= 0) errors.accuracy = '精度必须大于0'
    if (formData.max_clamping_force <= 0) errors.max_clamping_force = '最大夹紧力必须大于0'
    if (formData.weight <= 0) errors.weight = '重量必须大于0'
    if (!formData.positioning_method.trim()) errors.positioning_method = '定位方式不能为空'

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleAdd = () => {
    setEditingFixture(null)
    setFormData({
      name: '',
      type: '',
      model_number: '',
      clamping_range_min: 0,
      clamping_range_max: 0,
      accuracy: 0,
      max_clamping_force: 0,
      weight: 0,
      dimensions: {
        length: 0,
        width: 0,
        height: 0,
      },
      positioning_method: '',
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleEdit = (fixture: Fixture) => {
    setEditingFixture(fixture)
    setFormData({
      name: fixture.name,
      type: fixture.type,
      model_number: fixture.model_number,
      clamping_range_min: fixture.clamping_range_min,
      clamping_range_max: fixture.clamping_range_max,
      accuracy: fixture.accuracy,
      max_clamping_force: fixture.max_clamping_force,
      weight: fixture.weight,
      dimensions: fixture.dimensions,
      positioning_method: fixture.positioning_method,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleDelete = (fixture: Fixture) => {
    setDeletingFixture(fixture)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (deletingFixture) {
      try {
        // 模拟删除
        setSuccessMessage('夹具删除成功')
        setShowDeleteModal(false)
        setDeletingFixture(null)
        loadFixtures()
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        setError('删除夹具失败')
        console.error('Error deleting fixture:', err)
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
      if (editingFixture) {
        setSuccessMessage('夹具更新成功')
      } else {
        setSuccessMessage('夹具添加成功')
      }
      setShowModal(false)
      loadFixtures()
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(editingFixture ? '更新夹具失败' : '添加夹具失败')
      console.error('Error saving fixture:', err)
    }
  }

  // 搜索和分页
  const filteredFixtures = fixtures.filter(fixture =>
    fixture.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    fixture.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
    fixture.model_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
    fixture.id.toString().includes(searchTerm)
  )

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredFixtures.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(filteredFixtures.length / itemsPerPage)

  const getFixtureTypeBadge = (type: string) => {
    const variants: Record<string, string> = {
      '机用虎钳': 'primary',
      '气动夹具': 'success',
      '液压夹具': 'info',
      '卡盘': 'warning',
      '组合夹具': 'secondary',
      '专用夹具': 'dark',
    }
    return variants[type] || 'secondary'
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      active: { bg: 'success', text: '正常' },
      inactive: { bg: 'secondary', text: '停用' },
      maintenance: { bg: 'warning', text: '维护中' },
    }
    const config = variants[status] || variants.active
    return <Badge bg={config.bg}>{config.text}</Badge>
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className={`bi ${theme.icons.fixtures} me-2`}></i>
            夹具管理
          </h2>
          <p className="text-muted">
            管理夹具库，包括夹具的基本信息、3D模型、定位参数和使用记录
          </p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Form.Control
            type="text"
            placeholder="搜索夹具..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '200px' }}
          />
          <Button variant="primary" onClick={handleAdd}>
            <i className={`bi ${theme.icons.add} me-2`}></i>
            添加夹具
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
              <h3 className="mb-1">{fixtures.length}</h3>
              <p className="mb-0">夹具总数</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-success border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {fixtures.filter(f => f.status === 'active').length}
              </h3>
              <p className="mb-0">正常使用</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-warning border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {fixtures.filter(f => f.status === 'maintenance').length}
              </h3>
              <p className="mb-0">维护中</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-info border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">
                {fixtures.reduce((sum, f) => sum + f.usage_count, 0)}
              </h3>
              <p className="mb-0">总使用次数</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm">
        <Card.Body>
          {loading ? (
            <div className="text-center py-5">
              <Spinner animation="border" />
              <p className="mt-2 text-muted">加载中...</p>
            </div>
          ) : filteredFixtures.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              {searchTerm ? '未找到匹配的夹具' : '暂无夹具数据，请点击"添加夹具"按钮创建'}
            </Alert>
          ) : (
            <>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>名称</th>
                    <th>类型</th>
                    <th>型号</th>
                    <th>夹持范围</th>
                    <th>精度</th>
                    <th>最大夹紧力</th>
                    <th>重量</th>
                    <th>使用次数</th>
                    <th>状态</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((fixture) => (
                    <tr key={fixture.id}>
                      <td>
                        <Badge bg="secondary">{fixture.id}</Badge>
                      </td>
                      <td>
                        <strong>{fixture.name}</strong>
                      </td>
                      <td>
                        <Badge bg={getFixtureTypeBadge(fixture.type)}>
                          {fixture.type}
                        </Badge>
                      </td>
                      <td>
                        <small>{fixture.model_number}</small>
                      </td>
                      <td>
                        <small>
                          {fixture.clamping_range_min} - {fixture.clamping_range_max} mm
                        </small>
                      </td>
                      <td>
                        <Badge bg="primary">±{fixture.accuracy} mm</Badge>
                      </td>
                      <td>
                        <span className="font-monospace">
                          {fixture.max_clamping_force.toLocaleString()} N
                        </span>
                      </td>
                      <td>
                        {fixture.weight} kg
                      </td>
                      <td>
                        <Badge bg="info">{fixture.usage_count}</Badge>
                      </td>
                      <td>{getStatusBadge(fixture.status)}</td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="me-1"
                          onClick={() => handleEdit(fixture)}
                        >
                          <i className="bi bi-pencil"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(fixture)}
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
            {editingFixture ? '编辑夹具' : '添加夹具'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Tabs defaultActiveKey="basic">
              <Tab eventKey="basic" title="基本信息">
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>夹具名称 <span className="text-danger">*</span></Form.Label>
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
                      <Form.Label>夹具类型 <span className="text-danger">*</span></Form.Label>
                      <Form.Select
                        value={formData.type}
                        onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                        isInvalid={!!formErrors.type}
                      >
                        <option value="">请选择类型</option>
                        <option value="机用虎钳">机用虎钳</option>
                        <option value="气动夹具">气动夹具</option>
                        <option value="液压夹具">液压夹具</option>
                        <option value="卡盘">卡盘</option>
                        <option value="组合夹具">组合夹具</option>
                        <option value="专用夹具">专用夹具</option>
                      </Form.Select>
                      <Form.Control.Feedback type="invalid">{formErrors.type}</Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3">
                  <Form.Label>型号 <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.model_number}
                    onChange={(e) => setFormData({ ...formData, model_number: e.target.value })}
                    isInvalid={!!formErrors.model_number}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.model_number}</Form.Control.Feedback>
                </Form.Group>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>最小夹持范围 (mm) <span className="text-danger">*</span></Form.Label>
                      <Form.Control
                        type="number"
                        value={formData.clamping_range_min}
                        onChange={(e) => setFormData({ ...formData, clamping_range_min: Number(e.target.value) })}
                        isInvalid={!!formErrors.clamping_range_min}
                      />
                      <Form.Control.Feedback type="invalid">{formErrors.clamping_range_min}</Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>最大夹持范围 (mm) <span className="text-danger">*</span></Form.Label>
                      <Form.Control
                        type="number"
                        value={formData.clamping_range_max}
                        onChange={(e) => setFormData({ ...formData, clamping_range_max: Number(e.target.value) })}
                        isInvalid={!!formErrors.clamping_range_max}
                      />
                      <Form.Control.Feedback type="invalid">{formErrors.clamping_range_max}</Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>定位精度 (mm) <span className="text-danger">*</span></Form.Label>
                      <Form.Control
                        type="number"
                        step="0.01"
                        value={formData.accuracy}
                        onChange={(e) => setFormData({ ...formData, accuracy: Number(e.target.value) })}
                        isInvalid={!!formErrors.accuracy}
                      />
                      <Form.Control.Feedback type="invalid">{formErrors.accuracy}</Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>最大夹紧力 (N) <span className="text-danger">*</span></Form.Label>
                      <Form.Control
                        type="number"
                        value={formData.max_clamping_force}
                        onChange={(e) => setFormData({ ...formData, max_clamping_force: Number(e.target.value) })}
                        isInvalid={!!formErrors.max_clamping_force}
                      />
                      <Form.Control.Feedback type="invalid">{formErrors.max_clamping_force}</Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>重量 (kg) <span className="text-danger">*</span></Form.Label>
                      <Form.Control
                        type="number"
                        step="0.1"
                        value={formData.weight}
                        onChange={(e) => setFormData({ ...formData, weight: Number(e.target.value) })}
                        isInvalid={!!formErrors.weight}
                      />
                      <Form.Control.Feedback type="invalid">{formErrors.weight}</Form.Control.Feedback>
                    </Form.Group>
                  </Col>
                </Row>

                <Form.Group className="mb-3">
                  <Form.Label>定位方式 <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.positioning_method}
                    onChange={(e) => setFormData({ ...formData, positioning_method: e.target.value })}
                    isInvalid={!!formErrors.positioning_method}
                  />
                  <Form.Control.Feedback type="invalid">{formErrors.positioning_method}</Form.Control.Feedback>
                </Form.Group>
              </Tab>

              <Tab eventKey="dimensions" title="尺寸规格">
                <h6 className="mb-3">外形尺寸 (mm)</h6>
                <Row>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>长度</Form.Label>
                      <Form.Control
                        type="number"
                        value={formData.dimensions.length}
                        onChange={(e) => setFormData({
                          ...formData,
                          dimensions: { ...formData.dimensions, length: Number(e.target.value) }
                        })}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>宽度</Form.Label>
                      <Form.Control
                        type="number"
                        value={formData.dimensions.width}
                        onChange={(e) => setFormData({
                          ...formData,
                          dimensions: { ...formData.dimensions, width: Number(e.target.value) }
                        })}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group className="mb-3">
                      <Form.Label>高度</Form.Label>
                      <Form.Control
                        type="number"
                        value={formData.dimensions.height}
                        onChange={(e) => setFormData({
                          ...formData,
                          dimensions: { ...formData.dimensions, height: Number(e.target.value) }
                        })}
                      />
                    </Form.Group>
                  </Col>
                </Row>

                <hr />

                <Form.Group className="mb-3">
                  <Form.Label>3D模型文件</Form.Label>
                  <Form.Control type="file" accept=".stp,.step,.iges,.igs" />
                  <Form.Text className="text-muted">
                    支持 STEP (.stp, .step) 和 IGES (.iges, .igs) 格式
                  </Form.Text>
                </Form.Group>
              </Tab>
            </Tabs>

            <div className="text-end mt-4">
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
          确定要删除夹具 <strong>{deletingFixture?.name}</strong> ({deletingFixture?.model_number}) 吗？此操作不可撤销。
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

export default FixturesPage