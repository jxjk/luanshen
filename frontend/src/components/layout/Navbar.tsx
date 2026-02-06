import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Navbar as BSNavbar, Container, Offcanvas, Badge, Nav, Dropdown, Button } from 'react-bootstrap'
import { theme } from '../../theme'

const AppNavbar: React.FC = () => {
  const [showMenu, setShowMenu] = useState(false)
  const location = useLocation()

  const pageTitle = React.useMemo(() => {
    const pageTitles: Record<string, string> = {
      '/workshop': '车间视图',
      '/optimization': '参数优化',
      '/digital-twin': '数字孪生',
      '/quality': '质量追溯',
      '/nc-simulation': 'NC代码仿真',
      '/energy-analysis': '能效分析',
      '/tool-life': '刀具寿命管理',
      '/materials': '材料管理',
      '/tools': '刀具管理',
      '/machines': '设备管理',
      '/strategies': '策略管理',
      '/fixtures': '夹具管理',
      '/knowledge': '工艺知识库',
      '/history': '历史记录',
      '/reports': '报告生成',
    }
    return pageTitles[location.pathname] || '工艺数字孪生系统'
  }, [location.pathname])

  const mockNotifications = [
    { id: 1, message: '设备 CNC-001 出现报警', type: 'danger', time: '2分钟前' },
    { id: 2, message: '刀具 T-123 寿命即将到期', type: 'warning', time: '15分钟前' },
    { id: 3, message: '优化任务已完成', type: 'success', time: '1小时前' },
  ]

  return (
    <BSNavbar
      bg="primary"
      variant="dark"
      expand={false}
      className="app-header shadow-sm"
      style={{
        height: theme.layout.navbar.height,
        backgroundColor: theme.colors.primary[500],
      }}
      sticky="top"
    >
      <Container fluid>
        {/* 品牌Logo */}
        <BSNavbar.Brand as={Link} to="/" className="d-flex align-items-center">
          <i className={`bi ${theme.icons.dashboard} me-2`} style={{ fontSize: theme.typography.fontSize.lg }}></i>
          <span className="fw-bold">工艺数字孪生系统</span>
        </BSNavbar.Brand>

        {/* 汉堡菜单按钮 - 所有设备统一使用 */}
        <BSNavbar.Toggle
          aria-controls="offcanvasNavbar"
          onClick={() => setShowMenu(true)}
          className="border-0"
        />

        {/* 侧边栏 - 包含通知、菜单和用户信息 */}
        <BSNavbar.Offcanvas
          id="offcanvasNavbar"
          aria-labelledby="offcanvasNavbarLabel"
          placement="end"
          show={showMenu}
          onHide={() => setShowMenu(false)}
        >
          <Offcanvas.Header closeButton>
            <Offcanvas.Title id="offcanvasNavbarLabel">
              <i className={`bi ${theme.icons.dashboard} me-2`}></i>
              工艺数字孪生系统
            </Offcanvas.Title>
          </Offcanvas.Header>
          <Offcanvas.Body>
            {/* 通知部分 */}
            <div className="mb-4">
              <div className="d-flex align-items-center justify-content-between mb-2">
                <h6 className="mb-0">通知</h6>
                <Badge bg="danger" style={{ fontSize: theme.typography.fontSize.xs }}>
                  {mockNotifications.length}
                </Badge>
              </div>
              {mockNotifications.length === 0 ? (
                <div className="text-center text-muted py-3">
                  <i className={`bi ${theme.icons.success} display-4 text-success mb-2`}></i>
                  <p className="mb-0">暂无通知</p>
                </div>
              ) : (
                <div>
                  {mockNotifications.map((notification) => (
                    <div
                      key={notification.id}
                      className="p-3 border rounded mb-2"
                      style={{ cursor: 'pointer' }}
                    >
                      <div className="d-flex align-items-start gap-2">
                        {notification.type === 'danger' && (
                          <i className="bi bi-exclamation-triangle-fill text-danger"></i>
                        )}
                        {notification.type === 'warning' && (
                          <i className="bi bi-exclamation-circle-fill text-warning"></i>
                        )}
                        {notification.type === 'success' && (
                          <i className="bi bi-check-circle-fill text-success"></i>
                        )}
                        <div className="flex-grow-1">
                          <p className="mb-1" style={{ fontSize: theme.typography.fontSize.sm }}>
                            {notification.message}
                          </p>
                          <small className="text-muted">{notification.time}</small>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button variant="link" className="text-primary w-100 p-0">
                    查看全部
                  </Button>
                </div>
              )}
            </div>

            <hr className="my-3" />

            {/* 菜单导航 */}
            <Nav className="flex-column gap-2">
              {theme.menuItems.map((category) => (
                <div key={category.category}>
                  <small className="text-muted text-uppercase fw-bold ps-3 mb-2 d-block" style={{ fontSize: theme.typography.fontSize.xs }}>
                    {category.category}
                  </small>
                  {category.items.map((item) => (
                    <Nav.Link
                      key={item.path}
                      as={Link}
                      to={item.path}
                      className={`text-start ${
                        location.pathname === item.path ? 'active' : ''
                      }`}
                      onClick={() => setShowMenu(false)}
                    >
                      <i className={`bi ${item.icon} me-2`}></i>
                      {item.label}
                      {item.badge && (
                        <Badge bg="warning" text="dark" className="ms-2">
                          {item.badge}
                        </Badge>
                      )}
                    </Nav.Link>
                  ))}
                </div>
              ))}
            </Nav>

            <hr className="my-3" />

            {/* 用户信息和设置 */}
            <div className="d-flex align-items-center gap-3 mb-3">
              <div
                className="rounded-circle d-flex align-items-center justify-content-center"
                style={{
                  width: '40px',
                  height: '40px',
                  backgroundColor: theme.colors.primary[100],
                  color: theme.colors.primary[500],
                }}
              >
                <i className={`bi ${theme.icons.user}`}></i>
              </div>
              <div>
                <div className="fw-bold">管理员</div>
                <small className="text-muted">admin@example.com</small>
              </div>
            </div>

            <Nav className="flex-column gap-2 mb-3">
              <Nav.Link as={Link} to="/settings" onClick={() => setShowMenu(false)}>
                <i className={`bi ${theme.icons.settings} me-2`}></i>
                系统设置
              </Nav.Link>
              <Nav.Link as={Link} to="/profile" onClick={() => setShowMenu(false)}>
                <i className={`bi ${theme.icons.user} me-2`}></i>
                个人信息
              </Nav.Link>
            </Nav>

            <Button variant="outline-danger" className="w-100" as="button">
              <i className={`bi bi-box-arrow-right me-2`}></i>
              退出登录
            </Button>
          </Offcanvas.Body>
        </BSNavbar.Offcanvas>
      </Container>

      {/* 页面标题栏 - 可选，根据需要显示 */}
      <div
        className="border-top"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.1)',
          padding: `${theme.spacing[2]} 0`,
        }}
      >
        <Container fluid>
          <h6 className="mb-0 text-white">{pageTitle}</h6>
        </Container>
      </div>
    </BSNavbar>
  )
}

export default AppNavbar