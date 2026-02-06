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
  Tabs,
  Tab,
  Table,
  InputGroup,
} from 'react-bootstrap'
import { theme } from '../theme'

interface KnowledgeCase {
  id: number
  title: string
  category: string
  material: string
  operation: string
  description: string
  result: 'success' | 'failure' | 'optimization'
  tags: string[]
  createdAt: string
  author: string
}

interface ExpertKnowledge {
  id: number
  title: string
  category: string
  description: string
  parameters: Record<string, string>
  conditions: string[]
  createdAt: string
  author: string
}

const KnowledgePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('cases')
  const [showModal, setShowModal] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  // 模拟数据 - 加工案例库
  const [cases] = useState<KnowledgeCase[]>([
    {
      id: 1,
      title: '铝合金薄壁件加工优化案例',
      category: '铣削',
      material: '6061铝合金',
      operation: '精加工',
      description: '通过调整切削参数和路径，成功解决薄壁件变形问题',
      result: 'success',
      tags: ['薄壁件', '变形控制', '铝合金'],
      createdAt: '2025-12-01',
      author: '张工程师',
    },
    {
      id: 2,
      title: '不锈钢钻孔钻头断裂分析',
      category: '钻孔',
      material: '304不锈钢',
      operation: '钻孔',
      description: '分析钻头断裂原因，提出改进方案',
      result: 'failure',
      tags: ['钻头断裂', '不锈钢', '失效分析'],
      createdAt: '2025-11-28',
      author: '李工程师',
    },
    {
      id: 3,
      title: '钛合金加工效率提升方案',
      category: '铣削',
      material: 'TC4钛合金',
      operation: '粗加工',
      description: '优化切削参数，材料去除率提升30%',
      result: 'optimization',
      tags: ['钛合金', '效率提升', '参数优化'],
      createdAt: '2025-11-25',
      author: '王工程师',
    },
  ])

  // 模拟数据 - 专家经验库
  const [expertKnowledge] = useState<ExpertKnowledge[]>([
    {
      id: 1,
      title: '铝合金铣削切削参数推荐',
      category: '铣削',
      description: '基于多年经验总结的铝合金铣削最佳参数范围',
      parameters: {
        '线速度': '300-400 m/min',
        '每齿进给': '0.1-0.2 mm',
        '切深': '2-5 mm',
        '切宽': '0.5-1.5 D',
      },
      conditions: [
        '材料硬度：HB 60-100',
        '刀具材质：硬质合金',
        '冷却方式：乳化液冷却',
      ],
      createdAt: '2025-10-15',
      author: '资深工艺师',
    },
    {
      id: 2,
      title: '不锈钢深孔加工注意事项',
      category: '钻孔',
      description: '不锈钢深孔加工的关键要点和常见问题解决方案',
      parameters: {
        '钻头类型': '枪钻',
        '切削速度': '15-25 m/min',
        '进给量': '0.05-0.1 mm/rev',
        '冷却压力': '≥5 MPa',
      },
      conditions: [
        '孔深径比：≥10:1',
        '材料：不锈钢',
        '精度要求：H7',
      ],
      createdAt: '2025-10-10',
      author: '钻孔专家',
    },
  ])

  const categories = ['all', '铣削', '钻孔', '镗孔', '车削']

  const getResultBadge = (result: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      success: { bg: 'success', text: '成功案例' },
      failure: { bg: 'danger', text: '失败案例' },
      optimization: { bg: 'primary', text: '优化案例' },
    }
    const config = variants[result] || variants.success
    return <Badge bg={config.bg}>{config.text}</Badge>
  }

  const filteredCases = cases.filter(
    (item) =>
      (selectedCategory === 'all' || item.category === selectedCategory) &&
      (searchTerm === '' ||
        item.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase())))
  )

  return (
    <Container fluid>
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className={`bi ${theme.icons.knowledge} me-2`}></i>
            工艺知识库
          </h2>
          <p className="text-muted">
            沉淀和复用工艺知识，智能检索相似工艺案例
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="primary">
            <i className={`bi ${theme.icons.add} me-2`}></i>
            添加知识
          </Button>
        </Col>
      </Row>

      {/* 统计卡片 */}
      <Row className="mb-4">
        <Col md={3}>
          <Card className="stat-card stat-card-primary border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{cases.length}</h3>
              <p className="mb-0">加工案例</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-success border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">{expertKnowledge.length}</h3>
              <p className="mb-0">专家经验</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-warning border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">12</h3>
              <p className="mb-0">工艺模板</p>
            </Card.Body>
          </Card>
        </Col>
        <Col md={3}>
          <Card className="stat-card stat-card-info border-0">
            <Card.Body className="text-center">
              <h3 className="mb-1">98%</h3>
              <p className="mb-0">覆盖率</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="shadow-sm">
        <Card.Body className="p-0">
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k || 'cases')}
            className="border-0"
          >
            {/* 加工案例库 */}
            <Tab eventKey="cases" title="加工案例库">
              <div className="p-4">
                {/* 搜索和筛选 */}
                <Row className="mb-4">
                  <Col md={6}>
                    <InputGroup>
                      <InputGroup.Text>
                        <i className={`bi ${theme.icons.search}`}></i>
                      </InputGroup.Text>
                      <Form.Label htmlFor="knowledge-search" className="visually-hidden">搜索案例</Form.Label>
                      <Form.Control
                        type="text"
                        id="knowledge-search"
                        name="knowledge-search"
                        placeholder="搜索案例标题或标签..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                      />
                    </InputGroup>
                  </Col>
                  <Col md={6}>
                    <div className="d-flex gap-2">
                      {categories.map((cat) => (
                        <Button
                          key={cat}
                          variant={selectedCategory === cat ? 'primary' : 'outline-secondary'}
                          size="sm"
                          onClick={() => setSelectedCategory(cat)}
                        >
                          {cat === 'all' ? '全部' : cat}
                        </Button>
                      ))}
                    </div>
                  </Col>
                </Row>

                {filteredCases.length === 0 ? (
                  <Alert variant="info">
                    <i className={`bi ${theme.icons.info} me-2`}></i>
                    未找到匹配的案例
                  </Alert>
                ) : (
                  <Row>
                    {filteredCases.map((item) => (
                      <Col md={6} lg={4} key={item.id} className="mb-4">
                        <Card className="h-100 shadow-sm hover-shadow">
                          <Card.Body>
                            <div className="d-flex justify-content-between align-items-start mb-2">
                              {getResultBadge(item.result)}
                              <small className="text-muted">{item.createdAt}</small>
                            </div>
                            <h5 className="mb-2">{item.title}</h5>
                            <div className="mb-2">
                              <Badge bg="secondary" className="me-1">
                                {item.category}
                              </Badge>
                              <Badge bg="info">{item.material}</Badge>
                            </div>
                            <p className="text-muted small mb-3" style={{ minHeight: '48px' }}>
                              {item.description}
                            </p>
                            <div className="d-flex flex-wrap gap-1 mb-3">
                              {item.tags.map((tag) => (
                                <Badge
                                  key={tag}
                                  bg="light"
                                  text="dark"
                                  style={{ fontSize: theme.typography.fontSize.xs }}
                                >
                                  #{tag}
                                </Badge>
                              ))}
                            </div>
                            <div className="d-flex justify-content-between align-items-center pt-2 border-top">
                              <small className="text-muted">
                                <i className={`bi ${theme.icons.user} me-1`}></i>
                                {item.author}
                              </small>
                              <Button size="sm" variant="outline-primary">
                                查看详情
                              </Button>
                            </div>
                          </Card.Body>
                        </Card>
                      </Col>
                    ))}
                  </Row>
                )}
              </div>
            </Tab>

            {/* 专家经验库 */}
            <Tab eventKey="expert" title="专家经验">
              <div className="p-4">
                <div className="mb-4">
                  <InputGroup>
                    <InputGroup.Text>
                      <i className={`bi ${theme.icons.search}`}></i>
                    </InputGroup.Text>
                    <Form.Control
                      type="text"
                      placeholder="搜索专家经验..."
                    />
                  </InputGroup>
                </div>

                {expertKnowledge.map((item) => (
                  <Card key={item.id} className="mb-4 shadow-sm">
                    <Card.Header className="d-flex justify-content-between align-items-center">
                      <div>
                        <h5 className="mb-0">{item.title}</h5>
                        <small className="text-muted">
                          <Badge bg="secondary" className="me-2">{item.category}</Badge>
                          <i className={`bi ${theme.icons.user} me-1`}></i>
                          {item.author} · {item.createdAt}
                        </small>
                      </div>
                      <div>
                        <Button size="sm" variant="outline-primary">
                          应用到工艺
                        </Button>
                      </div>
                    </Card.Header>
                    <Card.Body>
                      <p>{item.description}</p>

                      <Row>
                        <Col md={6}>
                          <h6 className="mb-2">
                            <i className={`bi bi-sliders me-2`}></i>
                            推荐参数
                          </h6>
                          <Table bordered responsive size="sm">
                            <tbody>
                              {Object.entries(item.parameters).map(([key, value]) => (
                                <tr key={key}>
                                  <td width="40%">{key}</td>
                                  <td>
                                    <strong>{value}</strong>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </Table>
                        </Col>
                        <Col md={6}>
                          <h6 className="mb-2">
                            <i className={`bi bi-list-check me-2`}></i>
                            适用条件
                          </h6>
                          <ul className="mb-0">
                            {item.conditions.map((cond, idx) => (
                              <li key={idx}>{cond}</li>
                            ))}
                          </ul>
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                ))}
              </div>
            </Tab>

            {/* 工艺参数关联 */}
            <Tab eventKey="relations" title="参数关联">
              <div className="p-4">
                <Alert variant="info">
                  <i className={`bi ${theme.icons.info} me-2`}></i>
                  展示材料、刀具、工艺参数之间的关联关系
                </Alert>
                <div className="text-center py-5">
                  <i className={`bi ${theme.icons.knowledge} display-1 text-muted mb-3`}></i>
                  <h4 className="text-muted">参数关联图谱</h4>
                  <p className="text-muted">
                    可视化展示材料-刀具-参数-质量之间的关联关系
                  </p>
                </div>
              </div>
            </Tab>
          </Tabs>
        </Card.Body>
      </Card>
    </Container>
  )
}

export default KnowledgePage