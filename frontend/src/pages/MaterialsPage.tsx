import React, { useState, useEffect, useCallback } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Table,
  Modal,
  Form,
  Alert,
  Spinner,
  Badge,
  Pagination,
  ProgressBar,
} from 'react-bootstrap'
import { materialService } from '../services/materialService'
import { Material, MaterialCreate } from '../types'

const MaterialsPage: React.FC = () => {
  const [materials, setMaterials] = useState<Material[]>([])
  const [loading, setLoading] = useState(false)
  const [showModal, setShowModal] = useState(false)
  const [deletingMaterial, setDeletingMaterial] = useState<Material | null>(null)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [editingMaterial, setEditingMaterial] = useState<Material | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  
  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage] = useState(10)

  const [formData, setFormData] = useState<MaterialCreate>({
    caiLiaoZu: '',
    name: '',
    rm_min: 0,
    rm_max: 0,
    kc11: 0,
    mc: 0,
  })

  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadMaterials()
  }, [])

  const loadMaterials = async () => {
    try {
      setLoading(true)
      const data = await materialService.getAll()
      setMaterials(data)
    } catch (err) {
      setError('加载材料数据失败')
      console.error('Error loading materials:', err)
    } finally {
      setLoading(false)
    }
  }

  const validateForm = useCallback((): boolean => {
    const errors: Record<string, string> = {}

    if (!formData.caiLiaoZu.trim()) errors.caiLiaoZu = '材料组不能为空'
    if (!formData.name.trim()) errors.name = '材料名称不能为空'
    if (formData.rm_min <= 0) errors.rm_min = '最小抗拉强度必须大于0'
    if (formData.rm_max <= 0) errors.rm_max = '最大抗拉强度必须大于0'
    if (formData.rm_max < formData.rm_min) {
      errors.rm_max = '最大抗拉强度不能小于最小抗拉强度'
    }
    if (formData.kc11 <= 0) errors.kc11 = '切削力系数必须大于0'
    if (formData.mc < 0) errors.mc = '斜率不能为负数'

    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }, [formData])

  const handleAdd = () => {
    setEditingMaterial(null)
    setFormData({
      caiLiaoZu: '',
      name: '',
      rm_min: 0,
      rm_max: 0,
      kc11: 0,
      mc: 0,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleEdit = (material: Material) => {
    setEditingMaterial(material)
    setFormData({
      caiLiaoZu: material.caiLiaoZu,
      name: material.name,
      rm_min: material.rm_min,
      rm_max: material.rm_max,
      kc11: material.kc11,
      mc: material.mc,
    })
    setFormErrors({})
    setShowModal(true)
  }

  const handleDelete = (material: Material) => {
    setDeletingMaterial(material)
    setShowDeleteModal(true)
  }

  const confirmDelete = async () => {
    if (deletingMaterial) {
      try {
        await materialService.delete(deletingMaterial.id!)
        setSuccessMessage('材料删除成功')
        setShowDeleteModal(false)
        setDeletingMaterial(null)
        loadMaterials()
        setTimeout(() => setSuccessMessage(null), 3000)
      } catch (err) {
        setError('删除材料失败')
        console.error('Error deleting material:', err)
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
      if (editingMaterial) {
        await materialService.update(editingMaterial.id!, formData)
        setSuccessMessage('材料更新成功')
      } else {
        await materialService.create(formData)
        setSuccessMessage('材料添加成功')
      }
      setShowModal(false)
      loadMaterials()
      setTimeout(() => setSuccessMessage(null), 3000)
    } catch (err) {
      setError(editingMaterial ? '更新材料失败' : '添加材料失败')
      console.error('Error saving material:', err)
    }
  }

  // 搜索和分页
  const filteredMaterials = materials.filter(material =>
    material.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    material.caiLiaoZu.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const indexOfLastItem = currentPage * itemsPerPage
  const indexOfFirstItem = indexOfLastItem - itemsPerPage
  const currentItems = filteredMaterials.slice(indexOfFirstItem, indexOfLastItem)
  const totalPages = Math.ceil(filteredMaterials.length / itemsPerPage)

  const getMaterialGroupBadge = (group: string | undefined) => {
    if (!group || group.length === 0) {
      return 'secondary'
    }
    const variants: Record<string, string> = {
      'P': 'danger',      // 钢
      'M': 'warning',     // 不锈钢
      'K': 'success',     // 铸铁
      'N': 'info',        // 有色金属
    }
    return variants[group.charAt(0)] || 'secondary'
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-box-seam me-2"></i>
            材料管理
          </h2>
          <p className="text-muted">管理系统中的材料参数</p>
        </Col>
        <Col xs="auto" className="d-flex gap-2">
          <Form.Label htmlFor="material-search" className="visually-hidden">搜索材料</Form.Label>
          <Form.Control
            type="text"
            id="material-search"
            name="material-search"
            placeholder="搜索材料..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ width: '200px' }}
          />
          <Button variant="primary" onClick={handleAdd}>
            <i className="bi bi-plus-lg me-2"></i>
            添加材料
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
          ) : filteredMaterials.length === 0 ? (
            <Alert variant="info">
              <i className="bi bi-info-circle me-2"></i>
              {searchTerm ? '未找到匹配的材料' : '暂无材料数据，请点击"添加材料"按钮创建'}
            </Alert>
          ) : (
            <>
              <Table striped bordered hover responsive>
                <thead>
                  <tr>
                    <th>材料组</th>
                    <th>名称</th>
                    <th>抗拉强度 (MPa)</th>
                    <th>强度范围</th>
                    <th>切削力系数</th>
                    <th>斜率</th>
                    <th>操作</th>
                  </tr>
                </thead>
                <tbody>
                  {currentItems.map((material, index) => (
                    <tr key={material.id || material.caiLiaoZu || `material-${index}`}>
                      <td>
                        <Badge bg={getMaterialGroupBadge(material.caiLiaoZu)}>
                          {material.caiLiaoZu}
                        </Badge>
                      </td>
                      <td>
                        <strong>{material.name}</strong>
                      </td>
                      <td>
                        <Badge bg="primary">{material.rm_min} - {material.rm_max}</Badge>
                      </td>
                      <td>
                        <ProgressBar
                          now={(material.rm_max - material.rm_min)}
                          variant="info"
                          style={{ height: '20px' }}
                          label={`${material.rm_max - material.rm_min}`}
                        />
                      </td>
                      <td>
                        <span className="font-monospace">{material.kc11}</span>
                      </td>
                      <td>
                        <span className="font-monospace">{material.mc}</span>
                      </td>
                      <td>
                        <Button
                          variant="outline-primary"
                          size="sm"
                          className="me-1"
                          onClick={() => handleEdit(material)}
                        >
                          <i className="bi bi-pencil"></i>
                        </Button>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDelete(material)}
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
            {editingMaterial ? '编辑材料' : '添加材料'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    材料组 <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.caiLiaoZu}
                    onChange={(e) =>
                      setFormData({ ...formData, caiLiaoZu: e.target.value.toUpperCase() })
                    }
                    placeholder="例如: P1, M1, K1"
                    isInvalid={!!formErrors.caiLiaoZu}
                    disabled={!!editingMaterial}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.caiLiaoZu}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    P=钢, M=不锈钢, K=铸铁, N=有色金属
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>材料名称 <span className="text-danger">*</span></Form.Label>
                  <Form.Control
                    type="text"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    isInvalid={!!formErrors.name}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.name}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    最小抗拉强度 (MPa) <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.rm_min}
                    onChange={(e) =>
                      setFormData({ ...formData, rm_min: Number(e.target.value) })
                    }
                    isInvalid={!!formErrors.rm_min}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.rm_min}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    最大抗拉强度 (MPa) <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="number"
                    value={formData.rm_max}
                    onChange={(e) =>
                      setFormData({ ...formData, rm_max: Number(e.target.value) })
                    }
                    isInvalid={!!formErrors.rm_max}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.rm_max}
                  </Form.Control.Feedback>
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    切削力系数 <span className="text-danger">*</span>
                  </Form.Label>
                  <Form.Control
                    type="number"
                    step="0.1"
                    value={formData.kc11}
                    onChange={(e) =>
                      setFormData({ ...formData, kc11: Number(e.target.value) })
                    }
                    isInvalid={!!formErrors.kc11}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.kc11}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    单位: N/mm²
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>斜率</Form.Label>
                  <Form.Control
                    type="number"
                    step="0.01"
                    value={formData.mc}
                    onChange={(e) =>
                      setFormData({ ...formData, mc: Number(e.target.value) })
                    }
                    isInvalid={!!formErrors.mc}
                  />
                  <Form.Control.Feedback type="invalid">
                    {formErrors.mc}
                  </Form.Control.Feedback>
                  <Form.Text className="text-muted">
                    用于计算切削力
                  </Form.Text>
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
          确定要删除材料 <strong>{deletingMaterial?.name}</strong> ({deletingMaterial?.caiLiaoZu}) 吗？此操作不可撤销。
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

export default MaterialsPage