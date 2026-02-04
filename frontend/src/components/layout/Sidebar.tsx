import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Badge } from 'react-bootstrap'
import { theme } from '../../theme'

const Sidebar: React.FC = () => {
  const location = useLocation()

  return (
    <nav
      className="sidebar shadow-sm d-none"
      style={{
        width: theme.layout.sidebar.width,
        backgroundColor: theme.layout.sidebar.backgroundColor,
        borderRight: `1px solid ${theme.colors.gray[200]}`,
        position: 'fixed',
        top: theme.layout.navbar.height,
        left: 0,
        bottom: 0,
        overflowY: 'auto',
        zIndex: theme.zIndex.sticky,
      }}
    >
      <div className="py-3">
        {theme.menuItems.map((category, categoryIndex) => (
          <div key={category.category} className={categoryIndex > 0 ? 'mt-4' : ''}>
            <small
              className="text-uppercase fw-bold px-4 mb-2 d-block"
              style={{
                fontSize: theme.typography.fontSize.xs,
                color: theme.colors.gray[500],
                letterSpacing: '0.5px',
              }}
            >
              {category.category}
            </small>
            <ul className="sidebar-nav" style={{ listStyle: 'none', padding: 0, margin: 0 }}>
              {category.items.map((item) => {
                const isActive = location.pathname === item.path
                return (
                  <li key={item.path} style={{ marginBottom: theme.spacing[1] }}>
                    <Link
                      to={item.path}
                      className={`sidebar-nav-link d-flex align-items-center px-4 ${
                        isActive ? 'active' : ''
                      }`}
                      style={{
                        padding: `${theme.spacing[3]} ${theme.spacing[4]}`,
                        color: isActive ? theme.colors.primary[500] : theme.colors.gray[600],
                        textDecoration: 'none',
                        borderLeft: `3px solid ${
                          isActive ? theme.colors.primary[500] : 'transparent'
                        }`,
                        transition: theme.transitions.duration.DEFAULT,
                        backgroundColor: isActive
                          ? theme.colors.primary[50]
                          : 'transparent',
                      }}
                    >
                      <i
                        className={`bi ${item.icon} me-3`}
                        style={{
                          fontSize: theme.typography.fontSize.lg,
                          width: '20px',
                          textAlign: 'center',
                        }}
                      ></i>
                      <span
                        style={{
                          fontSize: theme.typography.fontSize.base,
                          fontWeight: isActive ? theme.typography.fontWeight.medium : theme.typography.fontWeight.normal,
                        }}
                      >
                        {item.label}
                      </span>
                      {item.badge && (
                        <Badge
                          bg="warning"
                          text="dark"
                          className="ms-auto"
                          style={{
                            fontSize: theme.typography.fontSize.xs,
                            padding: '2px 6px',
                            fontWeight: theme.typography.fontWeight.bold,
                          }}
                        >
                          {item.badge}
                        </Badge>
                      )}
                    </Link>
                  </li>
                )
              })}
            </ul>
          </div>
        ))}

        {/* 底部信息 */}
        <div className="mt-5 px-4">
          <div
            className="p-3 rounded"
            style={{
              backgroundColor: theme.colors.primary[50],
              border: `1px solid ${theme.colors.primary[200]}`,
            }}
          >
            <div className="d-flex align-items-center gap-2 mb-2">
              <i className={`bi ${theme.icons.info}`} style={{ color: theme.colors.primary[500] }}></i>
              <small className="fw-bold" style={{ color: theme.colors.primary[700] }}>
                系统信息
              </small>
            </div>
            <small className="text-muted d-block mb-1" style={{ fontSize: theme.typography.fontSize.xs }}>
              版本: v1.0.0
            </small>
            <small className="text-muted" style={{ fontSize: theme.typography.fontSize.xs }}>
              状态: <span style={{ color: theme.colors.success.DEFAULT }}>正常运行</span>
            </small>
          </div>

          <div className="mt-3 text-center">
            <small className="text-muted" style={{ fontSize: theme.typography.fontSize.xs }}>
              © 2026 工艺数字孪生系统
            </small>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Sidebar