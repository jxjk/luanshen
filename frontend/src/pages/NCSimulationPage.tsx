import React, { useState } from 'react'
import {
  Container,
  Row,
  Col,
  Card,
  Button,
  Alert,
  Form,
  Tabs,
  Tab,
  Badge,
  ProgressBar,
  Spinner,
  Modal,
} from 'react-bootstrap'
import { theme } from '../theme'

interface GCodeBlock {
  line: number
  code: string
  type: 'rapid' | 'linear' | 'circular' | 'tool_change' | 'comment' | 'other'
  x?: number
  y?: number
  z?: number
  feed?: number
  spindle?: number
}

interface SimulationResult {
  totalBlocks: number
  rapidMoves: number
  linearMoves: number
  circularMoves: number
  toolChanges: number
  estimatedTime: number
  totalDistance: number
  collisions: Collision[]
  warnings: Warning[]
}

interface Collision {
  type: 'tool_part' | 'tool_fixture' | 'tool_machine' | 'tool_tool'
  block: number
  description: string
  severity: 'critical' | 'warning'
}

interface Warning {
  block: number
  type: string
  description: string
}

const NCSimulationPage: React.FC = () => {
  const [gcodeFile, setGcodeFile] = useState<File | null>(null)
  const [gcodeContent, setGcodeContent] = useState<string>('')
  const [parsedBlocks, setParsedBlocks] = useState<GCodeBlock[]>([])
  const [simulating, setSimulating] = useState(false)
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null)
  const [currentBlock, setCurrentBlock] = useState(0)
  const [selectedMachine, setSelectedMachine] = useState('FANUC-5AX')
  const [selectedTool, setSelectedTool] = useState('T1')
  const [showSettings, setShowSettings] = useState(false)
  const [simulationSpeed, setSimulationSpeed] = useState(1.0)
  const [error, setError] = useState<string | null>(null)

  const machines = [
    { id: 'FANUC-5AX', name: 'FANUC五轴加工中心', type: '5-axis' },
    { id: 'SIEMENS-3AX', name: 'SIEMENS三轴加工中心', type: '3-axis' },
    { id: 'HEIDENHAIN', name: 'HEIDENHAIN五轴加工中心', type: '5-axis' },
  ]

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setGcodeFile(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        const content = event.target?.result as string
        setGcodeContent(content)
        parseGCode(content)
      }
      reader.readAsText(file)
    }
  }

  const parseGCode = (content: string): void => {
    const lines = content.split('\n')
    const blocks: GCodeBlock[] = []

    lines.forEach((line, index) => {
      const trimmedLine = line.trim()
      if (!trimmedLine || trimmedLine.startsWith('(') || trimmedLine.startsWith(';')) {
        blocks.push({
          line: index + 1,
          code: trimmedLine,
          type: 'comment',
        })
        return
      }

      const block: GCodeBlock = {
        line: index + 1,
        code: trimmedLine,
        type: 'other',
      }

      // 解析G代码
      if (trimmedLine.includes('G00') || trimmedLine.includes('G0')) {
        block.type = 'rapid'
      } else if (trimmedLine.includes('G01') || trimmedLine.includes('G1')) {
        block.type = 'linear'
      } else if (trimmedLine.includes('G02') || trimmedLine.includes('G03') || trimmedLine.includes('G2') || trimmedLine.includes('G3')) {
        block.type = 'circular'
      } else if (trimmedLine.includes('M06') || trimmedLine.includes('T')) {
        block.type = 'tool_change'
      }

      // 解析坐标
      const xMatch = trimmedLine.match(/X(-?\d+\.?\d*)/i)
      const yMatch = trimmedLine.match(/Y(-?\d+\.?\d*)/i)
      const zMatch = trimmedLine.match(/Z(-?\d+\.?\d*)/i)
      const fMatch = trimmedLine.match(/F(-?\d+\.?\d*)/i)
      const sMatch = trimmedLine.match(/S(-?\d+\.?\d*)/i)

      if (xMatch) block.x = parseFloat(xMatch[1])
      if (yMatch) block.y = parseFloat(yMatch[1])
      if (zMatch) block.z = parseFloat(zMatch[1])
      if (fMatch) block.feed = parseFloat(fMatch[1])
      if (sMatch) block.spindle = parseFloat(sMatch[1])

      blocks.push(block)
    })

    setParsedBlocks(blocks)
  }

  const handleSimulate = async () => {
    if (!gcodeContent) {
      setError('请先上传G代码文件')
      return
    }

    setSimulating(true)
    setError(null)
    setCurrentBlock(0)

    // 模拟仿真过程
    for (let i = 0; i < parsedBlocks.length; i++) {
      await new Promise(resolve => setTimeout(resolve, 50 / simulationSpeed))
      setCurrentBlock(i + 1)
    }

    // 生成仿真结果
    const result: SimulationResult = {
      totalBlocks: parsedBlocks.length,
      rapidMoves: parsedBlocks.filter(b => b.type === 'rapid').length,
      linearMoves: parsedBlocks.filter(b => b.type === 'linear').length,
      circularMoves: parsedBlocks.filter(b => b.type === 'circular').length,
      toolChanges: parsedBlocks.filter(b => b.type === 'tool_change').length,
      estimatedTime: 45.5,
      totalDistance: 12580.5,
      collisions: [],
      warnings: [
        {
          block: 15,
          type: 'fast_move',
          description: '快速移动时Z轴高度不足，建议提升安全高度',
        },
      ],
    }

    setSimulationResult(result)
    setSimulating(false)
  }

  const handleStopSimulation = () => {
    setSimulating(false)
  }

  const getBlockTypeBadge = (type: string) => {
    const variants: Record<string, { bg: string; text: string }> = {
      rapid: { bg: 'warning', text: '快速移动' },
      linear: { bg: 'success', text: '直线插补' },
      circular: { bg: 'info', text: '圆弧插补' },
      tool_change: { bg: 'secondary', text: '换刀' },
      comment: { bg: 'light', text: '注释' },
      other: { bg: 'dark', text: '其他' },
    }
    return variants[type] || variants.other
  }

  return (
    <Container fluid className="fade-in">
      <Row className="mb-4">
        <Col>
          <h2 className="fw-bold">
            <i className="bi bi-cpu me-2"></i>
            NC代码仿真
          </h2>
          <p className="text-muted">
            G代码解析、三维材料去除仿真、碰撞检测和加工时间估算
          </p>
        </Col>
        <Col xs="auto">
          <Button variant="outline-secondary" onClick={() => setShowSettings(true)}>
            <i className="bi bi-gear me-2"></i>
            仿真设置
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
        {/* 左侧控制面板 */}
        <Col lg={4}>
          <Card className="mb-4 shadow-sm">
            <Card.Header>
              <i className="bi bi-upload me-2"></i>
              上传G代码
            </Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>选择文件</Form.Label>
                <Form.Control
                  type="file"
                  accept=".nc,.gcode,.txt"
                  onChange={handleFileUpload}
                />
                <Form.Text className="text-muted">
                  支持 .nc, .gcode, .txt 格式
                </Form.Text>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>选择机床</Form.Label>
                <Form.Select
                  value={selectedMachine}
                  onChange={(e) => setSelectedMachine(e.target.value)}
                >
                  {machines.map(m => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>刀具</Form.Label>
                <Form.Select
                  value={selectedTool}
                  onChange={(e) => setSelectedTool(e.target.value)}
                >
                  <option value="T1">T1 - 面铣刀 Φ80</option>
                  <option value="T2">T2 - 立铣刀 Φ10</option>
                  <option value="T3">T3 - 球头刀 Φ6</option>
                </Form.Select>
              </Form.Group>

              <div className="d-grid gap-2">
                <Button
                  variant="primary"
                  onClick={handleSimulate}
                  disabled={!gcodeContent || simulating}
                  size="lg"
                >
                  {simulating ? (
                    <>
                      <Spinner animation="border" size="sm" className="me-2" />
                      仿真中...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-play-fill me-2"></i>
                      开始仿真
                    </>
                  )}
                </Button>
                {simulating && (
                  <Button variant="danger" onClick={handleStopSimulation}>
                    <i className="bi bi-stop-fill me-2"></i>
                    停止
                  </Button>
                )}
              </div>
            </Card.Body>
          </Card>

          {/* 仿真进度 */}
          {simulating && (
            <Card className="mb-4 shadow-sm">
              <Card.Header>
                <i className="bi bi-activity me-2"></i>
                仿真进度
              </Card.Header>
              <Card.Body>
                <div className="mb-3">
                  <div className="d-flex justify-content-between mb-1">
                    <small>代码行数</small>
                    <small>{currentBlock} / {parsedBlocks.length}</small>
                  </div>
                  <ProgressBar 
                    now={(currentBlock / parsedBlocks.length) * 100} 
                    variant="primary"
                    animated
                  />
                </div>
                <div className="text-center">
                  <small className="text-muted">
                    当前: {parsedBlocks[currentBlock - 1]?.code || ''}
                  </small>
                </div>
              </Card.Body>
            </Card>
          )}

          {/* 仿真结果 */}
          {simulationResult && !simulating && (
            <Card className="shadow-sm">
              <Card.Header>
                <i className="bi bi-check-circle-fill text-success me-2"></i>
                仿真结果
              </Card.Header>
              <Card.Body>
                <Alert variant={simulationResult.collisions.length > 0 ? 'danger' : 'success'}>
                  {simulationResult.collisions.length > 0 ? (
                    <>
                      <i className="bi bi-exclamation-triangle-fill me-2"></i>
                      检测到 {simulationResult.collisions.length} 个碰撞！
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle-fill me-2"></i>
                      仿真完成，未检测到碰撞
                    </>
                  )}
                </Alert>

                <Table striped bordered hover size="sm">
                  <tbody>
                    <tr>
                      <td><strong>总代码行数</strong></td>
                      <td>{simulationResult.totalBlocks}</td>
                    </tr>
                    <tr>
                      <td><strong>快速移动</strong></td>
                      <td>{simulationResult.rapidMoves}</td>
                    </tr>
                    <tr>
                      <td><strong>直线插补</strong></td>
                      <td>{simulationResult.linearMoves}</td>
                    </tr>
                    <tr>
                      <td><strong>圆弧插补</strong></td>
                      <td>{simulationResult.circularMoves}</td>
                    </tr>
                    <tr>
                      <td><strong>换刀次数</strong></td>
                      <td>{simulationResult.toolChanges}</td>
                    </tr>
                    <tr>
                      <td><strong>估计加工时间</strong></td>
                      <td>
                        <Badge bg="primary">{simulationResult.estimatedTime.toFixed(1)} 分钟</Badge>
                      </td>
                    </tr>
                    <tr>
                      <td><strong>总移动距离</strong></td>
                      <td>{simulationResult.totalDistance.toFixed(1)} mm</td>
                    </tr>
                  </tbody>
                </Table>

                {simulationResult.warnings.length > 0 && (
                  <div className="mt-3">
                    <h6 className="mb-2">
                      <i className="bi bi-exclamation-triangle text-warning me-2"></i>
                      警告
                    </h6>
                    {simulationResult.warnings.map((warning, idx) => (
                      <Alert key={idx} variant="warning" className="mb-2">
                        <small>行 {warning.block}: {warning.description}</small>
                      </Alert>
                    ))}
                  </div>
                )}
              </Card.Body>
            </Card>
          )}
        </Col>

        {/* 右侧显示区域 */}
        <Col lg={8}>
          <Card className="shadow-sm" style={{ minHeight: '600px' }}>
            <Card.Header>
              <Tabs
                activeKey="viewer"
                className="border-0"
                style={{ marginBottom: '-15px' }}
              >
                <Tab eventKey="viewer" title="3D视图">
                  <span className="ms-2">
                    <Badge bg="success">实时</Badge>
                  </span>
                </Tab>
                <Tab eventKey="code" title="代码编辑器">
                  <span className="ms-2">
                    <Badge bg="secondary">{parsedBlocks.length} 行</Badge>
                  </span>
                </Tab>
                <Tab eventKey="analysis" title="分析报告" />
              </Tabs>
            </Card.Header>
            <Card.Body className="p-0">
              <Tabs.Content>
                <Tabs.Pane active>
                  {/* 3D视图区域 */}
                  <div
                    style={{
                      height: '550px',
                      backgroundColor: '#1e1e1e',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                    }}
                  >
                    {!gcodeContent ? (
                      <div className="text-center text-white">
                        <i className="bi bi-boxes display-1 text-secondary mb-3"></i>
                        <h4 className="text-muted">等待G代码</h4>
                        <p className="text-muted">请上传G代码文件开始仿真</p>
                      </div>
                    ) : simulating ? (
                      <div className="text-center text-white">
                        <Spinner animation="border" variant="primary" />
                        <p className="mt-2">仿真中...</p>
                      </div>
                    ) : (
                      <div className="text-center text-white">
                        <i className="bi bi-check-circle display-1 text-success mb-3"></i>
                        <h4>仿真完成</h4>
                        <p className="text-muted">3D视图将在此显示仿真结果</p>
                      </div>
                    )}

                    {/* 坐标显示 */}
                    {gcodeContent && (
                      <div
                        style={{
                          position: 'absolute',
                          bottom: '10px',
                          left: '10px',
                          backgroundColor: 'rgba(0, 0, 0, 0.7)',
                          padding: '10px',
                          borderRadius: '4px',
                          color: 'white',
                        }}
                      >
                        <div>X: {parsedBlocks[currentBlock - 1]?.x?.toFixed(3) || '---'}</div>
                        <div>Y: {parsedBlocks[currentBlock - 1]?.y?.toFixed(3) || '---'}</div>
                        <div>Z: {parsedBlocks[currentBlock - 1]?.z?.toFixed(3) || '---'}</div>
                        <div>F: {parsedBlocks[currentBlock - 1]?.feed || '---'}</div>
                        <div>S: {parsedBlocks[currentBlock - 1]?.spindle || '---'}</div>
                      </div>
                    )}
                  </div>
                </Tabs.Pane>
              </Tabs.Content>
            </Card.Body>
          </Card>

          {/* G代码列表 */}
          {parsedBlocks.length > 0 && (
            <Card className="mt-4 shadow-sm">
              <Card.Header>
                <i className="bi bi-code me-2"></i>
                G代码
              </Card.Header>
              <Card.Body style={{ maxHeight: '300px', overflowY: 'auto' }}>
                <Table striped bordered hover size="sm">
                  <thead>
                    <tr>
                      <th width="60">行号</th>
                      <th width="100">类型</th>
                      <th>代码</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parsedBlocks.map((block, idx) => (
                      <tr
                        key={idx}
                        style={{
                          backgroundColor: idx < currentBlock ? 'rgba(40, 167, 69, 0.1)' : '',
                        }}
                      >
                        <td>{block.line}</td>
                        <td>
                          <Badge {...getBlockTypeBadge(block.type)}>
                            {getBlockTypeBadge(block.type).text}
                          </Badge>
                        </td>
                        <td>
                          <code style={{ fontSize: '0.875rem' }}>
                            {block.code}
                          </code>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>

      {/* 仿真设置模态框 */}
      <Modal show={showSettings} onHide={() => setShowSettings(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="bi bi-gear me-2"></i>
            仿真设置
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>仿真速度</Form.Label>
                  <Form.Select
                    value={simulationSpeed}
                    onChange={(e) => setSimulationSpeed(Number(e.target.value))}
                  >
                    <option value={0.5}>0.5x 慢速</option>
                    <option value={1.0}>1.0x 正常</option>
                    <option value={2.0}>2.0x 快速</option>
                    <option value={5.0}>5.0x 极速</option>
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>碰撞检测精度</Form.Label>
                  <Form.Select>
                    <option>高精度</option>
                    <option>中精度</option>
                    <option>低精度（快速）</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>安全高度</Form.Label>
              <Form.Control type="number" defaultValue="50" />
              <Form.Text className="text-muted">
                快速移动时的最小Z轴高度（mm）
              </Form.Text>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>进给速度倍率</Form.Label>
              <Form.RangeInput min={10} max={150} defaultValue={100} />
              <div className="d-flex justify-content-between">
                <small>10%</small>
                <small>150%</small>
              </div>
            </Form.Group>

            <Form.Check
              type="checkbox"
              label="启用碰撞检测"
              defaultChecked
            />
            <Form.Check
              type="checkbox"
              label="启用过切检测"
              defaultChecked
            />
            <Form.Check
              type="checkbox"
              label="显示刀具轨迹"
              defaultChecked
            />
            <Form.Check
              type="checkbox"
              label="显示材料去除"
              defaultChecked
            />
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowSettings(false)}>
            取消
          </Button>
          <Button variant="primary">
            <i className="bi bi-check-lg me-2"></i>
            应用
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  )
}

export default NCSimulationPage