# 工艺参数优化系统 - Web前端

基于 React + TypeScript + Bootstrap 5 构建的现代化工艺参数优化系统前端界面。

## 技术栈

- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5
- **UI库**: Bootstrap 5 + React Bootstrap
- **路由**: React Router DOM 6
- **HTTP客户端**: Axios
- **状态管理**: React Context API
- **图表**: Chart.js + React Chart.js 2

## 功能特性

### 核心功能

- ✅ **参数优化界面**: 直观的参数输入和优化结果展示
- ✅ **材料管理**: 材料的增删改查
- ✅ **刀具管理**: 刀具的增删改查
- ✅ **设备管理**: 设备的增删改查
- ✅ **策略管理**: 加工策略的增删改查
- ✅ **历史记录**: 优化历史记录查看（框架已搭建）

### 界面特性

- 🎨 现代化工业软件设计风格
- 📱 响应式布局，支持PC和平板
- 🌓 清晰的信息层级和视觉反馈
- ⚡ 流畅的用户交互体验
- 🔍 直观的数据展示和可视化

## 项目结构

```
frontend/
├── src/
│   ├── components/
│   │   └── layout/
│   │       ├── Navbar.tsx       # 导航栏组件
│   │       └── Sidebar.tsx      # 侧边栏组件
│   ├── pages/
│   │   ├── OptimizationPage.tsx  # 参数优化页面
│   │   ├── MaterialsPage.tsx     # 材料管理页面
│   │   ├── ToolsPage.tsx         # 刀具管理页面
│   │   ├── MachinesPage.tsx      # 设备管理页面
│   │   ├── StrategiesPage.tsx    # 策略管理页面
│   │   └── HistoryPage.tsx       # 历史记录页面
│   ├── services/
│   │   ├── api.ts                # API基础服务
│   │   ├── optimizationService.ts # 优化服务
│   │   ├── materialService.ts    # 材料服务
│   │   ├── toolService.ts        # 刀具服务
│   │   ├── machineService.ts     # 设备服务
│   │   └── strategyService.ts    # 策略服务
│   ├── types/
│   │   └── index.ts              # TypeScript类型定义
│   ├── App.tsx                   # 主应用组件
│   ├── App.css                   # 应用样式
│   ├── main.tsx                  # 应用入口
│   └── index.css                 # 全局样式
├── public/                       # 静态资源
├── index.html                    # HTML模板
├── package.json                  # 项目配置
├── tsconfig.json                 # TypeScript配置
├── vite.config.ts                # Vite配置
└── README.md                     # 项目文档
```

## 快速开始

### 环境要求

- Node.js >= 16.x
- npm >= 8.x 或 yarn >= 1.22.x

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 生产构建

```bash
npm run build
```

构建产物将输出到 `dist/` 目录。

### 预览生产构建

```bash
npm run preview
```

## 配置说明

### API代理配置

在 `vite.config.ts` 中配置了API代理，将 `/api` 请求转发到后端服务：

```typescript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:5007',
      changeOrigin: true,
    },
  },
}
```

确保后端服务在 `http://localhost:5007` 运行。

### 环境变量

如需配置其他环境变量，创建 `.env` 文件：

```bash
VITE_API_BASE_URL=/api/v1
VITE_API_TIMEOUT=30000
```

## 使用指南

### 参数优化流程

1. 选择材料（如：P1不锈钢）
2. 选择刀具（如：Φ25mm铣刀）
3. 选择设备（如：XK7132铣床）
4. 选择策略（如：粗铣）
5. 配置算法参数（可选）
6. 点击"开始优化"按钮
7. 查看优化结果

### 数据管理

- **材料管理**: 点击侧边栏"材料管理"，可查看、添加、编辑、删除材料
- **刀具管理**: 点击侧边栏"刀具管理"，可查看刀具列表
- **设备管理**: 点击侧边栏"设备管理"，可查看设备列表
- **策略管理**: 点击侧边栏"策略管理"，可查看策略列表

## 开发指南

### 添加新页面

1. 在 `src/pages/` 创建页面组件
2. 在 `src/App.tsx` 添加路由
3. 在 `Sidebar.tsx` 添加导航项

### 添加新API服务

1. 在 `src/types/index.ts` 定义类型
2. 在 `src/services/` 创建服务文件
3. 在页面组件中导入并使用

### 样式定制

- 全局样式: `src/index.css`
- 应用样式: `src/App.css`
- 组件样式: 使用 Bootstrap 类名或内联样式

## 技术特性

### TypeScript类型安全

所有组件和服务都使用TypeScript类型定义，确保类型安全。

### 响应式设计

使用Bootstrap 5的栅格系统和响应式工具类，适配不同屏幕尺寸。

### 组件化架构

采用模块化设计，组件职责单一，便于维护和扩展。

### API服务封装

统一的API客户端封装，支持请求/响应拦截器，便于添加认证、错误处理等。

## 已知问题

1. 历史记录功能正在开发中
2. 刀具、设备、策略的增删改查功能需要完善
3. 图表可视化功能待实现
4. 用户认证功能待实现

## 后续计划

- [ ] 完善数据管理的增删改查功能
- [ ] 实现历史记录的完整功能
- [ ] 添加图表可视化（Chart.js）
- [ ] 实现用户认证和权限管理
- [ ] 添加参数对比功能
- [ ] 优化移动端体验
- [ ] 添加国际化支持

## 浏览器支持

- Chrome >= 90
- Firefox >= 88
- Safari >= 14
- Edge >= 90

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系开发团队。