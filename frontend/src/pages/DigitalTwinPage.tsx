import React, { useState } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Tabs,
  Tab,
  Table,
  Button,
  Badge,
  Form,
  Modal,
  Alert,
} from 'react-bootstrap'
import { theme } from '../theme'

const DigitalTwinPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('machines')
  const [showModal, setShowModal] = useState(false)
  const [showViewModal, setShowViewModal] = useState(false)
  const [modalType, setModalType] = useState<'machine' | 'tool' | 'fixture' | 'template'>('machine')
  const [viewingModel, setViewingModel] = useState<{ type: 'machine' | 'tool' | 'fixture'; name: string } | null>(null)

  // 模拟数据 - 机床数字孪生模型
  const [machineModels] = useState([
    {
      id: 1,
      name: 'FANUC-5AX',
      type: '五轴加工中心',
      manufacturer: 'FANUC',
      model: 'DMU-80',
      axes: 'X/Y/Z/A/B',
      xTravel: 800,
      yTravel: 600,
      zTravel: 500,
      maxSpindleSpeed: 12000,
      maxPower: 15,
      modelFile: 'model_fanuc.stp',
      status: 'active',
      createdAt: '2025-12-01',
    },
    {
      id: 2,
      name: 'SIEMENS-3AX',
      type: '三轴加工中心',
      manufacturer: 'SIEMENS',
      model: 'VMC-850',
      axes: 'X/Y/Z',
      xTravel: 850,
      yTravel: 500,
      zTravel: 550,
      maxSpindleSpeed: 8000,
      maxPower: 11,
      modelFile: 'model_siemens.stp',
      status: 'active',
      createdAt: '2025-11-15',
    },
  ])

  // 模拟数据 - 刀具库
  const [toolModels] = useState([
    {
      id: 1,
      name: '面铣刀-φ80',
      type: '面铣刀',
      diameter: 80,
      teeth: 6,
      material: '硬质合金',
      coating: 'TiN',
      modelFile: 'tool_face_mill.stp',
      status: 'active',
      createdAt: '2025-10-20',
    },
    {
      id: 2,
      name: '立铣刀-φ10',
      type: '立铣刀',
      diameter: 10,
      teeth: 4,
      material: '高速钢',
      coating: 'TiAlN',
      modelFile: 'tool_end_mill.stp',
      status: 'active',
      createdAt: '2025-10-22',
    },
  ])

  // 模拟数据 - 夹具库
  const [fixtureModels] = useState([
    {
      id: 1,
      name: '虎钳-100mm',
      type: '机用虎钳',
      clampingRange: '0-100',
      accuracy: 0.02,
      modelFile: 'fixture_vise.stp',
      status: 'active',
      createdAt: '2025-09-15',
    },
  ])

  // 模拟数据 - 工艺模板库
  const [templateModels] = useState([
    {
      id: 1,
      name: '铝合金铣削模板',
      material: '铝合金',
      operation: '粗加工/精加工',
      description: '适用于铝合金材料的铣削加工',
      parameters: {
        cuttingSpeed: '300-400 m/min',
        feedPerTooth: '0.1-0.2 mm',
        depthOfCut: '2-5 mm',
      },
      status: 'active',
      createdAt: '2025-08-10',
    },
  ])

  const handleAdd = (type: typeof modalType) => {
    setModalType(type)
    setShowModal(true)
  }

  const getStatusBadge = (status: string) => {
    return status === 'active' ? (
      <Badge bg="success">启用</Badge>
    ) : (
      <Badge bg="secondary">停用</Badge>
    )
  }

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className={`bi ${theme.icons.digitalTwin} me-2`}></i>
            数字孪生模型管理
          </h2>
          <p className="text-muted">
            管理机床数字孪生模型、刀具库、夹具库和工艺模板库
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="primary">
            <i className={`bi ${theme.icons.refresh} me-2`}></i>
            刷新数据
          </Button>
        </Col>
      </Row>

      <Card className="shadow-sm">
        <Card.Body className="p-0">
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k || 'machines')}
            className="border-0"
          >
            {/* 机床模型 */}
            <Tab eventKey="machines" title="机床模型">
              <div className="p-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div>
                    <h5 className="mb-1">机床数字孪生模型</h5>
                    <small className="text-muted">
                      管理机床的几何模型、运动学模型和动力学模型
                    </small>
                  </div>
                  <Button variant="primary" onClick={() => handleAdd('machine')}>
                    <i className={`bi ${theme.icons.add} me-2`}></i>
                    添加机床模型
                  </Button>
                </div>

                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>名称</th>
                      <th>类型</th>
                      <th>制造商</th>
                      <th>轴系</th>
                      <th>行程(X/Y/Z)</th>
                      <th>主轴转速</th>
                      <th>功率</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {machineModels.map((model) => (
                      <tr key={model.id}>
                        <td>{model.id}</td>
                        <td>
                          <strong>{model.name}</strong>
                          <br />
                          <small className="text-muted">{model.model}</small>
                        </td>
                        <td>{model.type}</td>
                        <td>{model.manufacturer}</td>
                        <td>{model.axes}</td>
                        <td>
                          {model.xTravel} / {model.yTravel} / {model.zTravel} mm
                        </td>
                        <td>{model.maxSpindleSpeed} r/min</td>
                        <td>{model.maxPower} kW</td>
                        <td>{getStatusBadge(model.status)}</td>
                        <td>
                          <Button 
                            size="sm" 
                            variant="outline-primary" 
                            className="me-1"
                            onClick={() => {
                              setViewingModel({ type: 'machine', name: model.name })
                              setShowViewModal(true)
                            }}
                          >
                            <i className={`bi ${theme.icons.view}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-secondary" className="me-1">
                            <i className={`bi ${theme.icons.edit}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-danger">
                            <i className={`bi ${theme.icons.delete}`}></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>

            {/* 刀具库 */}
            <Tab eventKey="tools" title="刀具库">
              <div className="p-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div>
                    <h5 className="mb-1">刀具库模型</h5>
                    <small className="text-muted">
                      管理刀具的3D模型、材质和参数
                    </small>
                  </div>
                  <Button variant="primary" onClick={() => handleAdd('tool')}>
                    <i className={`bi ${theme.icons.add} me-2`}></i>
                    添加刀具模型
                  </Button>
                </div>

                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>名称</th>
                      <th>类型</th>
                      <th>直径</th>
                      <th>齿数</th>
                      <th>材质</th>
                      <th>涂层</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {toolModels.map((model) => (
                      <tr key={model.id}>
                        <td>{model.id}</td>
                        <td>
                          <strong>{model.name}</strong>
                        </td>
                        <td>{model.type}</td>
                        <td>Φ{model.diameter} mm</td>
                        <td>{model.teeth} 齿</td>
                        <td>{model.material}</td>
                        <td>{model.coating}</td>
                        <td>{getStatusBadge(model.status)}</td>
                        <td>
                          <Button 
                            size="sm" 
                            variant="outline-primary" 
                            className="me-1"
                            onClick={() => {
                              setViewingModel({ type: 'tool', name: model.name })
                              setShowViewModal(true)
                            }}
                          >
                            <i className={`bi ${theme.icons.view}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-secondary" className="me-1">
                            <i className={`bi ${theme.icons.edit}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-danger">
                            <i className={`bi ${theme.icons.delete}`}></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>

            {/* 夹具库 */}
            <Tab eventKey="fixtures" title="夹具库">
              <div className="p-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div>
                    <h5 className="mb-1">夹具库模型</h5>
                    <small className="text-muted">
                      管理夹具的3D模型和定位参数
                    </small>
                  </div>
                  <Button variant="primary" onClick={() => handleAdd('fixture')}>
                    <i className={`bi ${theme.icons.add} me-2`}></i>
                    添加夹具模型
                  </Button>
                </div>

                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>名称</th>
                      <th>类型</th>
                      <th>夹持范围</th>
                      <th>精度</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {fixtureModels.map((model) => (
                      <tr key={model.id}>
                        <td>{model.id}</td>
                        <td>
                          <strong>{model.name}</strong>
                        </td>
                        <td>{model.type}</td>
                        <td>{model.clampingRange} mm</td>
                        <td>±{model.accuracy} mm</td>
                        <td>{getStatusBadge(model.status)}</td>
                        <td>
                          <Button 
                            size="sm" 
                            variant="outline-primary" 
                            className="me-1"
                            onClick={() => {
                              setViewingModel({ type: 'fixture', name: model.name })
                              setShowViewModal(true)
                            }}
                          >
                            <i className={`bi ${theme.icons.view}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-secondary" className="me-1">
                            <i className={`bi ${theme.icons.edit}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-danger">
                            <i className={`bi ${theme.icons.delete}`}></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>

            {/* 工艺模板 */}
            <Tab eventKey="templates" title="工艺模板">
              <div className="p-4">
                <div className="d-flex justify-content-between align-items-center mb-4">
                  <div>
                    <h5 className="mb-1">标准工艺模板</h5>
                    <small className="text-muted">
                      管理标准工艺模板和变体
                    </small>
                  </div>
                  <Button variant="primary" onClick={() => handleAdd('template')}>
                    <i className={`bi ${theme.icons.add} me-2`}></i>
                    添加工艺模板
                  </Button>
                </div>

                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>名称</th>
                      <th>材料</th>
                      <th>工序</th>
                      <th>说明</th>
                      <th>推荐参数</th>
                      <th>状态</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    {templateModels.map((model) => (
                      <tr key={model.id}>
                        <td>{model.id}</td>
                        <td>
                          <strong>{model.name}</strong>
                        </td>
                        <td>{model.material}</td>
                        <td>{model.operation}</td>
                        <td>{model.description}</td>
                        <td>
                          <small>
                            Vc: {model.parameters.cuttingSpeed}<br />
                            fz: {model.parameters.feedPerTooth}<br />
                            Ap: {model.parameters.depthOfCut}
                          </small>
                        </td>
                        <td>{getStatusBadge(model.status)}</td>
                        <td>
                          <Button size="sm" variant="outline-primary" className="me-1">
                            <i className={`bi ${theme.icons.view}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-secondary" className="me-1">
                            <i className={`bi ${theme.icons.edit}`}></i>
                          </Button>
                          <Button size="sm" variant="outline-danger">
                            <i className={`bi ${theme.icons.delete}`}></i>
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>

      {/* 添加模型模态框 */}
      <Modal show={showModal} onHide={() => setShowModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {modalType === 'machine' && '添加机床模型'}
            {modalType === 'tool' && '添加刀具模型'}
            {modalType === 'fixture' && '添加夹具模型'}
            {modalType === 'template' && '添加工艺模板'}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="info">
            <i className={`bi ${theme.icons.info} me-2`}></i>
            请上传 STEP/IGES 格式的3D模型文件，并填写相关参数信息。
          </Alert>
          <Form>
            <Form.Group className="mb-3">
              <Form.Label htmlFor="model-name">名称</Form.Label>
              <Form.Control 
                type="text" 
                id="model-name"
                name="model-name"
                placeholder="请输入名称" 
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label htmlFor="model-file">3D模型文件</Form.Label>
              <Form.Control 
                type="file" 
                id="model-file"
                name="model-file"
                accept=".stp,.step,.iges,.igs" 
              />
              <Form.Text className="text-muted">
                支持 STEP (.stp, .step) 和 IGES (.iges, .igs) 格式
              </Form.Text>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label htmlFor="model-description">说明</Form.Label>
              <Form.Control 
                as="textarea" 
                id="model-description"
                name="model-description"
                rows={3} 
                placeholder="请输入说明信息" 
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            取消
          </Button>
          <Button variant="primary">
            <i className={`bi ${theme.icons.save} me-2`}></i>
            保存
          </Button>
        </Modal.Footer>
      </Modal>

      {/* 3D查看模态框 */}
      <Modal show={showViewModal} onHide={() => setShowViewModal(false)} size="xl">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className={`bi ${theme.icons.digitalTwin} me-2`}></i>
            3D模型查看 - {viewingModel?.name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {viewingModel && (
            <>
              <Alert variant="secondary" className="mb-3">
                <i className="bi bi-info-circle me-2"></i>
                交互方式：左键旋转 | 右键平移 | 滚轮缩放
              </Alert>
              <div style={{
                width: '100%',
                height: '400px',
                background: '#1a202c',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                flexDirection: 'column'
              }}>
                <i className="bi bi-cube" style={{ fontSize: '4rem', marginBottom: '1rem' }}></i>
                <h4>3D 模型查看器</h4>
                <p className="text-muted mb-0">
                  {viewingModel.type === 'machine' && '机床模型'} 
                  {viewingModel.type === 'tool' && '刀具模型'} 
                  {viewingModel.type === 'fixture' && '夹具模型'}
                </p>
                <small className="text-muted mt-2">3D 功能正在维护中...</small>
              </div>
              <div className="mt-3">
                <h6>模型信息</h6>
                <Table bordered size="sm">
                  <tbody>
                    <tr>
                      <td width="30%">模型名称</td>
                      <td>{viewingModel.name}</td>
                    </tr>
                    <tr>
                      <td>模型类型</td>
                      <td>
                        {viewingModel.type === 'machine' && '机床模型'}
                        {viewingModel.type === 'tool' && '刀具模型'}
                        {viewingModel.type === 'fixture' && '夹具模型'}
                      </td>
                    </tr>
                    <tr>
                      <td>渲染引擎</td>
                      <td>Three.js + React Three Fiber</td>
                    </tr>
                    <tr>
                      <td>渲染模式</td>
                      <td>实时渲染 / 阴影支持</td>
                    </tr>
                  </tbody>
                </Table>
              </div>
            </>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowViewModal(false)}>
            关闭
          </Button>
          <Button variant="primary">
            <i className={`bi ${theme.icons.download} me-2`}></i>
            导出截图
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default DigitalTwinPage