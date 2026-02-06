import React, { useState } from 'react'
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
  Table,
} from 'react-bootstrap'
import { theme } from '../theme'

interface ReportTemplate {
  id: number
  name: string
  type: 'production' | 'quality' | 'equipment' | 'efficiency'
  description: string
  lastGenerated: string
  icon: string
}

interface GeneratedReport {
  id: number
  name: string
  type: string
  generatedAt: string
  generatedBy: string
  fileSize: string
  status: 'completed' | 'generating' | 'failed'
}

const ReportsPage: React.FC = () => {
  const [showGenerateModal, setShowGenerateModal] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState<ReportTemplate | null>(null)
  const [dateRange, setDateRange] = useState({ start: '', end: '' })

  // 模拟数据 - 报告模板
  const [templates] = useState<ReportTemplate[]>([
    {
      id: 1,
      name: '生产报告',
      type: 'production',
      description: '包含生产进度、产量、合格率等关键指标',
      lastGenerated: '2025-12-14 18:00',
      icon: 'bi-bar-chart-line',
    },
    {
      id: 2,
      name: '质量报告',
      type: 'quality',
      description: '包含质量指标、缺陷分析、SPC统计等',
      lastGenerated: '2025-12-14 18:00',
      icon: 'bi-shield-check',
    },
    {
      id: 3,
      name: '设备效能报告',
      type: 'equipment',
      description: '包含OEE、设备运行率、停机分析等',
      lastGenerated: '2025-12-14 17:00',
      icon: 'bi-pc-display',
    },
    {
      id: 4,
      name: '效率分析报告',
      type: 'efficiency',
      description: '包含生产效率、瓶颈分析、改进建议等',
      lastGenerated: '2025-12-13 18:00',
      icon: 'bi-graph-up-arrow',
    },
    {
      id: 5,
      name: '优化记录报告',
      type: 'production',
      description: '记录所有参数优化任务及结果',
      lastGenerated: '2025-12-14 16:00',
      icon: 'bi-sliders',
    },
    {
      id: 6,
      name: '工艺追溯报告',
      type: 'quality',
      description: '追溯特定批次零件的完整工艺路径',
      lastGenerated: '2025-12-14 15:00',
      icon: 'bi-diagram-3',
    },
  ])

  // 模拟数据 - 已生成报告
  const [generatedReports] = useState<GeneratedReport[]>([
    {
      id: 1,
      name: '2025年12月生产日报',
      type: 'production',
      generatedAt: '2025-12-15 08:00',
      generatedBy: '系统自动',
      fileSize: '2.5 MB',
      status: 'completed',
    },
    {
      id: 2,
      name: '2025年12月质量周报',
      type: 'quality',
      generatedAt: '2025-12-14 18:00',
      generatedBy: '系统自动',
      fileSize: '3.2 MB',
      status: 'completed',
    },
    {
      id: 3,
      name: '2025年12月设备效能月报',
      type: 'equipment',
      generatedAt: '2025-12-14 17:00',
      generatedBy: '张工程师',
      fileSize: '4.8 MB',
      status: 'completed',
    },
    {
      id: 4,
      name: '批次 BATCH-001 工艺追溯报告',
      type: 'quality',
      generatedAt: '2025-12-15 10:30',
      generatedBy: '李质检',
      fileSize: '1.2 MB',
      status: 'completed',
    },
  ])

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      production: 'primary',
      quality: 'success',
      equipment: 'info',
      efficiency: 'warning',
    }
    return colors[type] || 'secondary'
  }

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      completed: { bg: 'success', text: '已完成' },
      generating: { bg: 'primary', text: '生成中' },
      failed: { bg: 'danger', text: '失败' },
    }
    const config = variants[status] || variants.completed
    return <Badge bg={config.bg}>{config.text}</Badge>
  }

  const handleGenerate = (template: ReportTemplate) => {
    setSelectedTemplate(template)
    setShowGenerateModal(true)
  }

  const handleDownload = (report: GeneratedReport) => {
    alert(`下载报告: ${report.name}`)
  }

  const handleDelete = (report: GeneratedReport) => {
    if (window.confirm(`确定要删除报告 "${report.name}" 吗？`)) {
      alert(`删除报告: ${report.name}`)
    }
  }

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className={`bi ${theme.icons.reports} me-2`}></i>
            报告生成与导出
          </h2>
          <p className="text-muted">
            自动生成各类生产、质量、设备报告，支持自定义模板
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="primary">
            <i className={`bi ${theme.icons.refresh} me-2`}></i>
            刷新列表
          </Button>
        </Col>
      </Row>

      {/* 报告模板 */}
      <Card className="mb-4 shadow-sm">
        <Card.Header>
          <i className={`bi ${theme.icons.templates} me-2`}></i>
          报告模板
        </Card.Header>
        <Card.Body>
          <Row>
            {templates.map((template) => (
              <Col md={4} lg={3} key={template.id} className="mb-4">
                <Card
                  className="h-100 shadow-sm hover-shadow cursor-pointer"
                  onClick={() => handleGenerate(template)}
                  style={{
                    transition: theme.transitions.duration.DEFAULT,
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)'
                    e.currentTarget.style.boxShadow = theme.shadows.lg
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)'
                    e.currentTarget.style.boxShadow = theme.shadows.sm
                  }}
                >
                  <Card.Body className="text-center">
                    <div
                      className="d-inline-flex align-items-center justify-content-center rounded-circle mb-3"
                      style={{
                        width: '64px',
                        height: '64px',
                        backgroundColor: theme.colors.primary[50],
                        color: theme.colors.primary[500],
                      }}
                    >
                      <i className={`bi ${template.icon}`} style={{ fontSize: theme.typography.fontSize['2xl'] }}></i>
                    </div>
                    <h5 className="mb-2">{template.name}</h5>
                    <Badge bg={getTypeColor(template.type)} className="mb-2">
                      {template.type === 'production' && '生产报告'}
                      {template.type === 'quality' && '质量报告'}
                      {template.type === 'equipment' && '设备报告'}
                      {template.type === 'efficiency' && '效率报告'}
                    </Badge>
                    <p className="text-muted small mb-2">{template.description}</p>
                    <small className="text-muted">
                      上次生成: {template.lastGenerated}
                    </small>
                  </Card.Body>
                </Card>
              </Col>
            ))}
          </Row>
        </Card.Body>
      </Card>

      {/* 已生成报告 */}
      <Card className="shadow-sm">
        <Card.Header>
          <i className={`bi ${theme.icons.history} me-2`}></i>
          已生成报告
        </Card.Header>
        <Card.Body>
          {generatedReports.length === 0 ? (
            <Alert variant="info">
              <i className={`bi ${theme.icons.info} me-2`}></i>
              暂无已生成的报告
            </Alert>
          ) : (
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>报告名称</th>
                  <th>类型</th>
                  <th>生成时间</th>
                  <th>生成者</th>
                  <th>文件大小</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                {generatedReports.map((report) => (
                  <tr key={report.id}>
                    <td>{report.id}</td>
                    <td>
                      <strong>{report.name}</strong>
                    </td>
                    <td>
                      <Badge bg={getTypeColor(report.type)}>
                        {report.type === 'production' && '生产'}
                        {report.type === 'quality' && '质量'}
                        {report.type === 'equipment' && '设备'}
                        {report.type === 'efficiency' && '效率'}
                      </Badge>
                    </td>
                    <td>{report.generatedAt}</td>
                    <td>{report.generatedBy}</td>
                    <td>{report.fileSize}</td>
                    <td>{getStatusBadge(report.status)}</td>
                    <td>
                      <div className="d-flex gap-1">
                        <Button
                          size="sm"
                          variant="outline-primary"
                          onClick={() => handleDownload(report)}
                          disabled={report.status !== 'completed'}
                        >
                          <i className={`bi ${theme.icons.download}`}></i>
                        </Button>
                        <Button size="sm" variant="outline-secondary">
                          <i className={`bi ${theme.icons.view}`}></i>
                        </Button>
                        <Button
                          size="sm"
                          variant="outline-danger"
                          onClick={() => handleDelete(report)}
                        >
                          <i className={`bi ${theme.icons.delete}`}></i>
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>

      {/* 生成报告模态框 */}
      <Modal show={showGenerateModal} onHide={() => setShowGenerateModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className={`bi bi-sliders me-2`}></i>
            生成报告 - {selectedTemplate?.name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedTemplate && (
            <>
              <Alert variant="info">
                <i className={`bi ${theme.icons.info} me-2`}></i>
                {selectedTemplate.description}
              </Alert>

              <Form>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label htmlFor="report-name">报告名称</Form.Label>
                      <Form.Control
                        type="text"
                        id="report-name"
                        name="report-name"
                        defaultValue={`${selectedTemplate.name} - ${new Date().toLocaleDateString('zh-CN')}`}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label htmlFor="report-format">报告格式</Form.Label>
                      <Form.Select id="report-format" name="report-format">
                        <option value="pdf">PDF</option>
                        <option value="excel">Excel</option>
                        <option value="word">Word</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>开始日期</Form.Label>
                      <Form.Control
                        type="date"
                        value={dateRange.start}
                        onChange={(e) =>
                          setDateRange({ ...dateRange, start: e.target.value })
                        }
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>结束日期</Form.Label>
                      <Form.Control
                        type="date"
                        value={dateRange.end}
                        onChange={(e) =>
                          setDateRange({ ...dateRange, end: e.target.value })
                        }
                      />
                    </Form.Group>
                  </Col>
                </Row>

                {selectedTemplate.type === 'production' && (
                  <Form.Group className="mb-3">
                    <Form.Label>包含内容</Form.Label>
                    <div>
                      <Form.Check type="checkbox" label="生产进度" defaultChecked />
                      <Form.Check type="checkbox" label="产量统计" defaultChecked />
                      <Form.Check type="checkbox" label="合格率分析" defaultChecked />
                      <Form.Check type="checkbox" label="人员绩效" />
                      <Form.Check type="checkbox" label="设备运行记录" defaultChecked />
                    </div>
                  </Form.Group>
                )}

                {selectedTemplate.type === 'quality' && (
                  <Form.Group className="mb-3">
                    <Form.Label>包含内容</Form.Label>
                    <div>
                      <Form.Check type="checkbox" label="质量指标" defaultChecked />
                      <Form.Check type="checkbox" label="缺陷分析" defaultChecked />
                      <Form.Check type="checkbox" label="SPC统计" defaultChecked />
                      <Form.Check type="checkbox" label="不合格品记录" defaultChecked />
                      <Form.Check type="checkbox" label="改进措施" />
                    </div>
                  </Form.Group>
                )}

                {selectedTemplate.type === 'equipment' && (
                  <Form.Group className="mb-3">
                    <Form.Label>包含内容</Form.Label>
                    <div>
                      <Form.Check type="checkbox" label="OEE分析" defaultChecked />
                      <Form.Check type="checkbox" label="设备运行率" defaultChecked />
                      <Form.Check type="checkbox" label="停机分析" defaultChecked />
                      <Form.Check type="checkbox" label="维护记录" defaultChecked />
                      <Form.Check type="checkbox" label="能耗分析" />
                    </div>
                  </Form.Group>
                )}

                {selectedTemplate.type === 'efficiency' && (
                  <Form.Group className="mb-3">
                    <Form.Label>包含内容</Form.Label>
                    <div>
                      <Form.Check type="checkbox" label="生产效率" defaultChecked />
                      <Form.Check type="checkbox" label="瓶颈分析" defaultChecked />
                      <Form.Check type="checkbox" label="改进建议" defaultChecked />
                      <Form.Check type="checkbox" label="资源利用率" defaultChecked />
                      <Form.Check type="checkbox" label="成本分析" />
                    </div>
                  </Form.Group>
                )}

                <Form.Group className="mb-3">
                  <Form.Label htmlFor="report-notes">备注说明</Form.Label>
                  <Form.Control
                    as="textarea"
                    id="report-notes"
                    name="report-notes"
                    rows={3}
                    placeholder="请输入备注说明（可选）"
                  />
                </Form.Group>
              </Form>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowGenerateModal(false)}>
            取消
          </Button>
          <Button variant="primary">
            <i className={`bi ${theme.icons.save} me-2`}></i>
            生成报告
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default ReportsPage