# 工艺数字孪生系统 - Agent 指南

## 项目概述

这是一个面向机械加工制造的**工艺数字孪生系统**项目，旨在通过数字化手段实现工艺设计、仿真、执行、监控和优化的全生命周期管理。项目采用**微服务架构**，包含参数优化、设备监控、报警管理和质量追溯四大核心子系统，并配有完整的Web前端界面（16个功能页面）。

**当前状态**：✅ **已成功部署到本机 Docker 环境**，所有9个容器（基础设施+微服务+前端）均已启动并处于健康状态（2026-02-06 验证）。

### 项目目标

- 构建工艺知识的数字化沉淀与复用体系
- 实现加工过程的实时可视化与精准控制
- 质量问题的快速追溯与预防
- 生产资源的优化配置与效率提升
- 企业核心竞争力的系统性增强

### 核心子系统

#### 1. 参数优化服务（parameter-optimization）
基于**微生物遗传算法（Microbial Genetic Algorithm）**和**DeepSeek AI 集成**的智能参数优化系统，用于优化铣削、钻孔、镗孔、车削等加工工艺参数。

**重构亮点**：
- ✅ 模块化架构（微服务设计）
- ✅ SQLAlchemy ORM（参数化查询，防止 SQL 注入）
- ✅ Pydantic 配置管理（环境变量支持）
- ✅ FastAPI RESTful API
- ✅ Docker 容器化部署
- ✅ 遗传算法模块化、可配置、可测试
- ✅ 完整的日志系统
- ✅ 健康检查与监控
- ✅ **NumPy 向量化计算优化**（10x+ 性能提升）
- ✅ **早停机制**（自适应收敛）
- ✅ **DNA解码修复**（修复转速偏低、进给偏高、材料去除率不足的问题）
- ✅ **线速度计算公式修复**（与旧版本保持一致：vc = n * D / 318 + 0.1）
- **DeepSeek AI 集成**（智能优化建议和审查分析）✨ NEW
  - **AI 规划器**（智能设定参数搜索范围）✨ NEW
  - **AI 审查器**（验证优化结果的物理合理性和安全性）✨ NEW
  - **镗孔进给力计算公式恢复**（参照钻孔公式，考虑底孔直径影响）✅ UPDATED
  - **单位面积进给力约束**（钻孔专用，防止刀具弯曲）✅ UPDATED
  - **公式来源注释**（瓦尔特/山德威克切削理论）✅ UPDATED
  - **铣削切屑厚度宽径比判断**（ae ≤ 0.3D 和 ae > 0.3D 分段计算）✅ UPDATED
  - **刀具挠度约束优化**（悬臂梁模型，使用实际刀具参数）✅ UPDATED

**算法模块**：
- `microbial_ga.py` - 微生物遗传算法核心实现
  - DNA 编码：36位（speed:16, feed:13, cut_depth:7）
  - 向量化评估函数 `evaluate_vectorized()`
  - 支持早停机制：连续无改进时提前终止
  - DNA解码修复：使用正确的从高位到低位的加权求和方式
  - 线速度计算修复：vc = n * tool_diameter / 318.0 + 0.1（与旧版本一致）
  - **镗孔进给力计算**：ff = 0.63 × fz × Z × (D - D_bottom) × kc / 2（考虑底孔直径影响）✅ UPDATED
  - **单位面积进给力约束**：ff_unit = ff / (π × D² / 4)（钻孔专用，防止刀具弯曲）✅ UPDATED
  - **铣削切屑厚度宽径比判断**：ae_ratio ≤ 0.3 时使用简化公式，否则使用复杂公式（考虑切削角度）✅ UPDATED
  - **刀具挠度约束**：δ = (F × L³) / (3 × E × I)，I = π × D⁴ / 64（悬臂梁模型）✅ UPDATED
  - **公式来源注释**：功率计算参考瓦尔特/山德威克切削理论 ✅ UPDATED
  - 返回字段：speed, feed, cut_depth, cut_width, cutting_speed, feed_per_tooth, bottom_roughness, side_roughness, power, torque, feed_force, material_removal_rate, tool_life, tool_deflection ✅ UPDATED
- `constraints.py` - 约束条件检查（功率、扭矩、刀具寿命、表面粗糙度等）
- `objectives.py` - 目标函数（材料去除率最大化）
- `ai_assisted_optimizer.py` - AI 辅助优化器（集成 AI 规划器、优化算法和 AI 审查器）✨ NEW
- `ai_planner.py` - AI 规划器（基于刀具供应商参数智能设定搜索范围）✨ NEW
- `ai_reviewer.py` - AI 审查器（验证优化结果的物理合理性）✨ NEW

**AI 集成模块** ✨ NEW：
- `services/llm_service.py` - DeepSeek LLM 服务
  - 智能优化建议生成
  - 审查分析报告生成
  - 安全评分和风险评估
  - 支持异步调用和错误处理
- `DEEPSEEK_INTEGRATION.md` - DeepSeek 集成文档
- `test_deepseek.py` - LLM 集成测试脚本

**API 路由**：
- `/api/v1/optimization/` - 参数优化相关接口
- `/api/v1/optimization/optimize` - 标准参数优化接口
- `/api/v1/optimization/ai-optimize` - **AI 辅助参数优化接口**（集成 AI 规划、AI 审查和 LLM 增强）✨ NEW
- `/api/v1/materials/` - 材料管理
- `/api/v1/tools/` - 刀具管理
- `/api/v1/machines/` - 设备管理
- `/api/v1/strategies/` - 策略管理

#### 2. 设备监控服务（device-monitor）
实时采集和监控设备运行数据，支持 OPC UA 协议，使用 InfluxDB 存储时序数据，通过 WebSocket 推送实时数据。

**核心特性**：
- ✅ OPC UA 数据采集（AsyncUA）
- ✅ 支持主流NC控制器（FANUC、SIEMENS、HEIDENHAIN、MITSUBISHI）✅ UPDATED
- ✅ InfluxDB 时序数据存储（高频数据支持 ≥1kHz）
- ✅ Redis 缓存支持
- ✅ RabbitMQ 消息队列
- ✅ WebSocket 实时推送
- ✅ 设备状态监控
- ✅ 真实设备连接支持（替代模拟数据）✅ UPDATED

**支持的NC控制器**：
- **FANUC**：Series 0i-MD、0i-TD、30i/31i/32i、35i
- **SIEMENS**：SINUMERIK 828D、840D sl、840D、ONE
- **HEIDENHAIN**：TNC 640、TNC 620、iTNC 530、TNC 128
- **MITSUBISHI**：M80/M800系列、E70/E80系列
- **其他**：MAZAK、HAAS、Brother、Okuma等（通过OPC UA网关）

**模块结构**：
- `collectors/opcua_collector.py` - OPC UA 数据采集器
- `stores/influxdb_store.py` - InfluxDB 时序数据存储
- `websocket/manager.py` - WebSocket 连接管理
- `models/device_status.py` - 设备状态数据模型
- `config/constants.py` - 设备节点映射配置 ✅ UPDATED
- `config/settings.py` - OPC UA 连接配置 ✅ UPDATED
- `test_opcua_connection.py` - OPC UA 连接测试工具 ✅ NEW

**API 路由**：
- `/api/v1/device/` - 设备监控相关接口
- `/api/v1/monitoring/` - 监控统计接口
- `/ws/device/{device_id}` - WebSocket 实时数据推送

**配置文档**：
- 📖 [NC设备连接配置指南](docs/deployment/NC设备连接配置指南.md) - 完整的设备连接配置说明
- 📖 [NC设备快速配置指南](docs/deployment/NC设备快速配置指南.md) - 5分钟快速配置教程

#### 3. 报警管理服务（alarm-management）
统一管理和分发各类报警信息，支持邮件和短信通知，集成 Redis 和 RabbitMQ 实现高性能报警处理。

**核心特性**：
- ✅ 报警记录管理
- ✅ 邮件通知（SMTP + Aiosmtplib）
- ✅ 短信通知（阿里云 DysmsAPI 2.1.2）
- ✅ 多渠道通知支持
- ✅ 报警规则配置
- ✅ 报警闭环管理（创建、确认、解决、关闭）

**通知模块**：
- `notifiers/notification_service.py` - 通知服务统一入口
- `notifiers/email_notifier.py` - 邮件通知器
- `notifiers/sms_notifier.py` - 短信通知器

**API 路由**：
- `/api/v1/alarms/` - 报警管理接口
- `/api/v1/notifications/` - 通知配置接口

#### 4. 质量追溯服务（quality-trace）
实现产品质量全生命周期追溯，记录加工过程参数和质量检测结果。

**核心特性**：
- ✅ 质量数据记录
- ✅ 批次追溯（工单级、零件级）
- ✅ 工艺参数关联
- ✅ 质量报表生成
- ✅ 时间轴回放
- ✅ 关联分析

**模块结构**：
- `services/` - 质量追溯业务逻辑
- `repositories/` - 数据访问层
- `models/` - 质量追溯数据模型

**API 路由**：
- `/api/v1/quality/` - 质量追溯接口
- `/api/v1/batches/` - 批次管理接口

## 项目结构

```
D:\Users\00596\Desktop\工艺数字孪生\
├── 需求规格说明书.md              # 完整的产品需求规格说明书（PRD）
├── AGENTS.md                       # 本文件
├── pyproject.toml                  # Python 项目配置
├── .env                            # 环境变量配置
├── .env.example                    # 环境变量模板
├── .gitignore                      # Git 忽略文件
├── QUICKSTART.md                   # 快速启动指南
├── DEPLOYMENT.md                   # 部署文档
├── BATCH_FILES.md                  # 批处理文件说明
├── docker-compose.yml              # Docker Compose 配置
│
├── frontend/                       # Web 前端应用
│   ├── package.json                # 前端依赖配置
│   ├── package-lock.json           # 依赖锁定文件
│   ├── vite.config.ts              # Vite 构建配置
│   ├── tsconfig.json               # TypeScript 配置
│   ├── tsconfig.node.json          # Node TypeScript 配置
│   ├── index.html                  # HTML 入口
│   ├── nginx.conf                  # Nginx 配置（生产环境代理）✅ UPDATED
│   ├── PDF导出功能说明.md           # PDF 导出功能文档 ✨ NEW
│   ├── README.md                   # 前端文档
│   └── src/
│       ├── main.tsx                # React 入口
│       ├── App.tsx                 # 主应用组件（包含路由配置）
│       ├── App.css                 # 主应用样式
│       ├── index.css               # 全局样式
│       ├── vite-env.d.ts           # Vite 类型声明
│       ├── theme/                  # 统一设计系统
│       │   └── index.ts            # 主题配置（颜色、字体、间距、图标等）
│       ├── components/             # 组件目录
│       │   ├── common/             # 通用组件
│       │   │   ├── StatCard.tsx    # 统计卡片组件
│       │   │   ├── DeviceStatusBadge.tsx  # 设备状态徽章
│       │   │   ├── AlarmCard.tsx   # 报警卡片组件
│       │   │   └── ModelViewer3D.tsx  # 3D模型查看器组件 ✅ INTEGRATED
│       │   └── layout/             # 布局组件
│       │       ├── Navbar.tsx      # 导航栏（含通知、用户菜单）
│       │       └── Sidebar.tsx     # 侧边栏（含分类导航）
│       ├── pages/                  # 页面组件（16个页面）
│       │   ├── WorkshopPage.tsx    # 车间视图（默认首页）
│       │   ├── OptimizationPage.tsx # 参数优化页面（含PDF导出）✅ UPDATED
│       │   ├── DigitalTwinPage.tsx # 数字孪生模型管理页面 ✅ UPDATED
│       │   ├── QualityPage.tsx     # 质量追溯与预测页面 ✅ UPDATED
│       │   ├── NCSimulationPage.tsx # NC代码仿真页面
│       │   ├── EnergyAnalysisPage.tsx # 能效分析页面
│       │   ├── ToolLifePage.tsx    # 刀具寿命管理页面
│       │   ├── MaterialsPage.tsx   # 材料管理页面
│       │   ├── ToolsPage.tsx       # 刀具管理页面
│       │   ├── MachinesPage.tsx    # 设备管理页面
│       │   ├── StrategiesPage.tsx  # 策略管理页面
│       │   ├── FixturesPage.tsx    # 夹具管理页面
│       │   ├── KnowledgePage.tsx   # 工艺知识库页面
│       │   ├── HistoryPage.tsx     # 历史记录页面
│       │   ├── ReportsPage.tsx     # 报告生成与导出页面
│       │   └── DeviceMonitorPage.tsx # 设备监控详情页面
│       ├── services/               # API 服务层
│       │   ├── api.ts              # Axios 客户端配置（超时120s）✅ UPDATED
│       │   ├── optimizationService.ts  # 优化服务
│       │   ├── materialService.ts  # 材料服务
│       │   ├── toolService.ts      # 刀具服务
│       │   ├── machineService.ts   # 设备服务
│       │   ├── strategyService.ts  # 策略服务
│       │   ├── deviceMonitorService.ts # 设备监控服务
│       │   ├── alarmService.ts     # 报警服务
│       │   └── pdfService.ts       # PDF 导出服务 ✨ NEW
│       └── types/                  # TypeScript 类型定义
│           └── index.ts            # 类型声明
│
├── 00_刀具参数优化系统/             # 旧版系统（保留兼容）
│   ├── gui_ga.py                   # GUI 主界面（Tkinter）
│   ├── microbialGeneticAlgorithm.py # 微生物遗传算法核心实现
│   ├── ga_tools.sql                # MySQL 数据库初始化脚本
│   └── README.md                   # 子项目说明文档
├── add_elastic_modulus.sql         # 数据库表结构更新：添加弹性模量列 ✅ UPDATED
├── add_tool_columns.sql            # 数据库表结构更新：添加刀具列（elastic_modulus、overhang_length）✅ UPDATED
├── fix_parameters.sql              # 数据库参数修复：优化材料参数和机床参数 ✅ UPDATED
├── test_cut_depth_fix.py           # 切深修复测试脚本 ✨ NEW
└── test_optimization.py            # 参数优化测试脚本 ✨ NEW
│
├── services/                       # 微服务目录
│   ├── parameter-optimization/     # 参数优化服务
│   │   ├── DEEPSEEK_INTEGRATION.md # DeepSeek AI 集成文档 ✨ NEW
│   │   ├── test_deepseek.py        # LLM 集成测试脚本 ✨ NEW
│   │   ├── src/algorithms/         # 算法模块
│   │   │   ├── microbial_ga.py     # 微生物遗传算法（向量化优化）✅ UPDATED
│   │   │   ├── constraints.py      # 约束条件
│   │   │   ├── objectives.py       # 目标函数
│   │   │   ├── ai_assisted_optimizer.py  # AI 辅助优化器 ✨ NEW
│   │   │   ├── ai_planner.py       # AI 规划器 ✨ NEW
│   │   │   └── ai_reviewer.py      # AI 审查器 ✨ NEW
│   │   ├── src/services/           # 服务模块
│   │   │   └── llm_service.py      # DeepSeek LLM 服务 ✨ NEW
│   │   ├── README.md               # 服务文档
│   │   └── requirements.txt        # Python 依赖
│   ├── device-monitor/             # 设备监控服务
│   ├── alarm-management/           # 报警管理服务
│   └── quality-trace/              # 质量追溯服务
│
├── infrastructure/                 # 基础设施
│   ├── docker/
│   │   └── Dockerfile              # 参数优化服务镜像构建
│   ├── kubernetes/                 # K8s 配置（待实现）
│   └── scripts/                    # 部署脚本（待实现）
│
├── shared/                         # 共享模块
│   └── common/                     # 公共代码（待实现）
│
└── docs/                           # 文档目录
    ├── architecture/               # 架构文档
    │   └── 阶段一实施计划.md
    ├── api/                        # API 文档
    └── deployment/                 # 部署文档
```

### 部署脚本

项目包含完整的自动化部署脚本：

| 批处理文件 | 功能 | 说明 |
|-----------|------|------|
| `一键部署.bat` | 一键部署 | 直接双击部署所有服务 |
| `查看状态.bat` | 查看状态 | 检查所有服务运行状态 |
| `停止服务.bat` | 停止服务 | 停止所有运行中的服务 |
| `初始化数据.bat` | 初始化数据 | 添加测试数据到数据库 |
| `cleanup.bat` | 清理数据 | 清理所有数据和服务（谨慎使用） |

| PowerShell 脚本 | 功能 | 说明 |
|----------------|------|------|
| `deploy.ps1` | 部署脚本 | 完整的部署流程（含环境检查） |
| `stop.ps1` | 停止服务 | 停止所有微服务和基础设施 |
| `status.ps1` | 状态检查 | 检查服务健康状态和容器信息 |
| `logs.ps1` | 日志查看 | 查看服务日志（支持 -Follow 参数实时跟踪） |
| `init-data.ps1` | 初始化数据 | 初始化测试数据 |
| `cleanup.ps1` | 清理数据 | 清理所有 Docker 数据卷和容器 |

## 技术栈

### 前端技术栈（Web UI）
- **React 18.2.0** - 用户界面框架
- **TypeScript 5.2.2** - 类型安全的 JavaScript
- **Vite 5.0.8** - 快速的构建工具
- **Bootstrap 5.3.2** - UI 组件库
- **React Bootstrap 2.9.1** - React Bootstrap 组件
- **React Router DOM 6.20.0** - 客户端路由
- **Axios 1.6.2** - HTTP 客户端（超时120s）✅ UPDATED
- **Bootstrap Icons 1.11.2** - 图标库
- **Chart.js 4.4.0** - 图表库（支持 SPC 控制图等）✅ INTEGRATED
- **React Chart.js 2 5.2.0** - React Chart.js 封装 ✅ INTEGRATED
- **Three.js 0.160.0** - 3D 图形库 ✅ INTEGRATED
- **React Three Fiber 8.16.0** - React 的 Three.js 渲染器 ✅ INTEGRATED
- **@react-three/drei 9.105.0** - Three.js 实用组件 ✅ INTEGRATED
- **jsPDF 4.1.0** - PDF 生成库 ✅ NEW
- **html2canvas 1.4.1** - HTML 转换为 Canvas ✅ NEW

### 前端设计系统

#### 颜色系统
- **主色调**：10级蓝色系统（#0d6efd）
- **功能色**：成功、警告、危险、信息
- **工业色**：运行绿、空闲灰、报警红、维护黄、离线黑
- **中性色**：9级灰色系统（#f8f9fa ~ #212529）
- **渐变色**：11种精美渐变（用于统计卡片）

#### 字体系统
- **字体栈**：系统字体（-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto）
- **字号**：10级（xs: 0.75rem ~ 4xl: 2.25rem）
- **字重**：6级（normal, medium, semibold, bold, extrabold, black）
- **行高**：3级（none: 1, tight: 1.25, normal: 1.5）

#### 间距系统
- **13级间距**（0 ~ 24rem），统一使用 theme.spacing
- **边距**：m-0 ~ m-5, my-0 ~ my-5, mx-0 ~ mx-5
- **填充**：p-0 ~ p-5, py-0 ~ py-5, px-0 ~ px-5

#### 其他设计元素
- **圆角**：4级（sm: 0.25rem ~ lg: 1rem）
- **阴影**：4级（sm ~ xl）
- **过渡动画**：0.3s ease
- **Z-Index**：7级（dropdown: 1000 ~ modal: 1060）
- **图标映射**：29个预定义图标（含 nc_simulation, energy_analysis, tool_life）

### 后端技术栈（所有微服务）

#### 通用技术栈
- **Python 3.9+** - 主要开发语言
- **FastAPI 0.104.0+** - 高性能 Web 框架
- **SQLAlchemy 2.0.23+** - Python SQL 工具包和 ORM
- **PyMySQL 1.1.0+** - MySQL 数据库驱动
- **Cryptography 41.0.7+** - 加密支持
- **Pydantic 2.5.0+** - 数据验证和设置管理
- **Pydantic Settings 2.1.0+** - 配置管理
- **Uvicorn 0.24.0+** - ASGI 服务器
- **python-jose 3.3.0+** - JWT 令牌处理
- **passlib 1.7.4+** - 密码加密（bcrypt）
- **python-multipart 0.0.6+** - 多部分表单支持
- **httpx 0.25.0+** - 异步 HTTP 客户端（用于 LLM API 调用）✨ NEW

#### 参数优化服务特有
- **NumPy 1.24.0+** - 数值计算库（向量化优化）✅ UPDATED
- **微生物遗传算法** - 自定义优化算法
  - DNA 编码：36位（speed:16, feed:13, cut_depth:7）
  - 向量化评估：10x+ 性能提升
  - 早停机制：自适应收敛
  - 支持加工方法：MILLING, DRILLING, BORING, TURNING

#### 设备监控服务特有
- **InfluxDB Client 1.38.0** - 时序数据库客户端
- **AsyncUA 1.0.0** - OPC UA 协议支持
- **Redis 5.0.1** - 缓存支持
- **Pika 1.3.2** - RabbitMQ 客户端
- **Aiohttp 3.9.1** - 异步 HTTP 客户端
- **WebSockets 12.0** - WebSocket 支持
- **Pandas 2.1.3** - 数据处理

#### 报警管理服务特有
- **Redis 5.0.1** - 缓存支持
- **Pika 1.3.2** - RabbitMQ 客户端
- **Aiosmtplib 3.0.1** - SMTP 邮件发送
- **Email Validator 2.1.0** - 邮箱验证
- **Aliyun Python SDK Core 2.13.36** - 阿里云 SDK 核心
- **Aliyun Python SDK Dysmsapi 2.1.2** - 阿里云短信服务

#### 质量追溯服务特有
- **Redis 5.0.1** - 缓存支持
- **Pika 1.3.2** - RabbitMQ 客户端
- **Pandas 2.1.3** - 数据处理

### 基础设施
- **MySQL 8.0** - 关系型数据库（端口 3307）
- **InfluxDB 2.7** - 时序数据库（端口 8086）
- **Redis 7-alpine** - 缓存和消息队列（端口 6379）
- **RabbitMQ 3-management-alpine** - 消息队列（端口 5672，管理界面 15672）
- **Docker Compose 2.0+** - 容器编排
- **Alpine Linux 3.18+** - 轻量级基础镜像（python:3.11-alpine）
- **Nginx** - 前端反向代理（端口 80）✅ UPDATED

### 算法
- **微生物遗传算法（MGA）** - 用于优化切削参数
  - 支持多目标优化：材料去除率（Q）最大化
  - 约束条件：刀具寿命、功率、扭矩、表面粗糙度、进给力等
  - 支持早停机制：连续无改进时提前终止
  - **NumPy 向量化计算**：替代 ProcessPoolExecutor，性能提升10x+ ✅ UPDATED
  - **DNA 编码**：36位（speed:16, feed:13, cut_depth:7）

## 服务端口映射

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|---------|---------|------|
| Nginx | 80 | 80 | 前端反向代理 |
| MySQL | 3306 | 3307 | 关系型数据库 |
| InfluxDB | 8086 | 8086 | 时序数据库 |
| Redis | 6379 | 6379 | 缓存服务 |
| RabbitMQ | 5672 | 5672 | 消息队列 AMQP |
| RabbitMQ Management | 15672 | 15672 | RabbitMQ Web 管理界面 |
| 参数优化服务 | 8000 | 5007 | FastAPI API |
| 设备监控服务 | 5008 | 5008 | FastAPI API + WebSocket |
| 报警管理服务 | 5009 | 5009 | FastAPI API |
| 质量追溯服务 | 5010 | 5010 | FastAPI API |
| 前端（开发） | 3000 | 3000 | Vite 开发服务器 |

## 前端应用结构

### 路由配置

前端采用 React Router DOM 进行客户端路由，包含16个页面：

```typescript
// src/App.tsx
<Routes>
  {/* 默认路由重定向到车间视图 */}
  <Route path="/" element={<Navigate to="/workshop" replace />} />

  {/* 主菜单 */}
  <Route path="/workshop" element={<WorkshopPage />} />
  <Route path="/optimization" element={<OptimizationPage />} />
  <Route path="/digital-twin" element={<DigitalTwinPage />} />
  <Route path="/quality" element={<QualityPage />} />

  {/* 高级功能 */}
  <Route path="/nc-simulation" element={<NCSimulationPage />} />
  <Route path="/energy-analysis" element={<EnergyAnalysisPage />} />
  <Route path="/tool-life" element={<ToolLifePage />} />

  {/* 资源管理 */}
  <Route path="/materials" element={<MaterialsPage />} />
  <Route path="/tools" element={<ToolsPage />} />
  <Route path="/machines" element={<MachinesPage />} />
  <Route path="/strategies" element={<StrategiesPage />} />
  <Route path="/fixtures" element={<FixturesPage />} />

  {/* 知识与分析 */}
  <Route path="/knowledge" element={<KnowledgePage />} />
  <Route path="/history" element={<HistoryPage />} />
  <Route path="/reports" element={<ReportsPage />} />

  {/* 设备监控 */}
  <Route path="/monitoring/:deviceId" element={<DeviceMonitorPage />} />

  {/* 404 路由 */}
  <Route path="*" element={<Navigate to="/workshop" replace />} />
</Routes>
```

### 侧边栏菜单

侧边栏采用四级分类导航结构：

```typescript
// theme/index.ts
menuItems: [
  {
    category: '主菜单',
    items: [
      { path: '/workshop', icon: 'bi-grid-3x3-gap', label: '车间视图' },
      { path: '/optimization', icon: 'bi-speedometer2', label: '参数优化' },
      { path: '/digital-twin', icon: 'bi-boxes', label: '数字孪生', badge: 'NEW' },
      { path: '/quality', icon: 'bi-shield-check', label: '质量追溯' },
    ]
  },
  {
    category: '高级功能',
    items: [
      { path: '/nc-simulation', icon: 'bi-cpu', label: 'NC仿真', badge: 'NEW' },
      { path: '/energy-analysis', icon: 'bi-lightning-charge', label: '能效分析', badge: 'NEW' },
      { path: '/tool-life', icon: 'bi-tools', label: '刀具寿命', badge: 'NEW' },
    ]
  },
  {
    category: '资源管理',
    items: [
      { path: '/materials', icon: 'bi-box-seam', label: '材料管理' },
      { path: '/tools', icon: 'bi-tools', label: '刀具管理' },
      { path: '/machines', icon: 'bi-pc-display', label: '设备管理' },
      { path: '/strategies', icon: 'bi-list-task', label: '策略管理' },
      { path: '/fixtures', icon: 'bi-grid-3x3', label: '夹具管理' },
    ]
  },
  {
    category: '知识与分析',
    items: [
      { path: '/knowledge', icon: 'bi-book', label: '工艺知识库' },
      { path: '/history', icon: 'bi-clock-history', label: '历史记录' },
      { path: '/reports', icon: 'bi-file-earmark-bar-graph', label: '报告生成' },
    ]
  }
]
```

### 导航栏功能

导航栏包含以下功能：
- 品牌Logo和系统名称
- 通知下拉菜单（支持3种类型：danger、warning、success）
- 用户下拉菜单（系统设置、个人信息、退出登录）
- 移动端响应式支持（Offcanvas侧边栏）
- 页面标题显示（包含所有16个页面的标题映射）

### 通用组件

```typescript
// src/components/common/
StatCard              // 统计卡片（10种渐变变体、趋势显示）
DeviceStatusBadge     // 设备状态徽章（5种状态）
AlarmCard             // 报警卡片（3种级别、确认/解决操作）
ModelViewer3D         // 3D模型查看器 ✅ INTEGRATED
```

### API 服务层

所有服务文件已修复API响应格式问题，直接处理后端返回的数据：

```typescript
// src/services/api.ts - Axios 客户端配置
const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 120000,  // 120秒超时（优化算法可能需要较长时间）✅ UPDATED
  headers: { 'Content-Type': 'application/json' }
});

// src/services/materialService.ts - 材料服务
export const materialService = {
  getAll: () => apiClient.get<Material[]>('/materials/'),
  getById: (id: number) => apiClient.get<Material>(`/materials/${id}`),
  create: (data: MaterialCreate) => apiClient.post<Material>('/materials/', data),
  update: (id: number, data: MaterialCreate) => apiClient.put<Material>(`/materials/${id}`, data),
  delete: (id: number) => apiClient.delete(`/materials/${id}`),
};

// src/services/toolService.ts - 刀具服务
// src/services/machineService.ts - 设备服务
// src/services/strategyService.ts - 策略服务
// src/services/optimizationService.ts - 优化服务
// src/services/deviceMonitorService.ts - 设备监控服务
// src/services/alarmService.ts - 报警服务
// src/services/pdfService.ts - PDF 导出服务 ✨ NEW
```

### Vite 代理配置

开发环境下的 API 请求代理配置：

```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api/v1/alarms': { target: 'http://localhost:5009', changeOrigin: true },
    '/api/v1/notifications': { target: 'http://localhost:5009', changeOrigin: true },
    '/api/v1/device': { target: 'http://localhost:5008', changeOrigin: true },
    '/api/v1/monitoring': { target: 'http://localhost:5008', changeOrigin: true },
    '/api/v1/quality': { target: 'http://localhost:5010', changeOrigin: true },
    '/api/v1/batches': { target: 'http://localhost:5010', changeOrigin: true },
    '/api': { target: 'http://localhost:5007', changeOrigin: true },
  },
}
```

## 前端页面功能

### 1. 车间视图（WorkshopPage）
- 实时显示所有设备状态（运行/空闲/报警/维护/离线）
- 设备运行率统计图表（ProgressBar展示）
- 活跃报警列表（支持确认和解决操作）
- 设备列表（支持实时刷新）
- 自动刷新（每5秒）

### 2. 参数优化（OptimizationPage）✅ UPDATED
- 材料选择（下拉选择，显示材料参数）
- 刀具选择（下拉选择，显示刀具参数）
- 设备选择（下拉选择，显示设备参数）
- 策略选择（下拉选择，显示策略参数）
- 算法参数配置（种群大小、迭代次数、交叉概率、变异概率）
- 优化进度显示（ProgressBar动画）
- 优化结果展示（分三个标签页：切削参数、性能指标、质量指标）
- 约束使用情况可视化（功率、扭矩、进给力的百分比进度条）
- **PDF 报告导出** ✅ NEW
  - 生成格式化的优化报告 PDF
  - 包含完整的项目说明、加工参数配置、性能指标
  - 约束使用情况可视化（带颜色进度条）
  - 智能优化建议生成
  - 自动分页和页脚信息
  - 文件名带时间戳

### 3. 数字孪生（DigitalTwinPage）✅ UPDATED
- 机床模型管理（几何模型、运动学模型、动力学模型）✅ 3D查看器已集成
- 刀具库管理（3D模型、材质、参数）✅ 3D查看器已集成
- 夹具库管理（3D模型、定位参数）✅ 3D查看器已集成
- 工艺模板管理（标准工艺、变体管理）
- 3D模型上传功能（支持STEP/IGES格式）
- **新增3D模型查看器功能**：
  - 使用 Three.js + React Three Fiber 实现
  - 支持交互操作：左键旋转、右键平移、滚轮缩放
  - 自动旋转功能（可暂停/继续）
  - 阴影和光照效果
  - 实时渲染引擎
  - 支持机床、刀具、夹具三种模型类型展示
  - 模型信息显示面板
  - 截图导出功能

### 4. 质量追溯（QualityPage）✅ UPDATED
- 批次追溯（零件号、批次号搜索）
- **SPC监控（控制图类型选择、统计指标显示）** ✅ Chart.js已集成
  - Xbar-R 控制图（支持动态数据）
  - 显示UCL（上控制限）、LCL（下控制限）、平均值（Mean）
  - 实测值超出控制限时自动标记为红色
  - 交互式图表，支持鼠标悬停查看详细数据
  - 包含CPK/PPK等统计指标
  - 控制图类型选择（Xbar-R、Xbar-S、I-MR、P控制图）
  - 控制参数选择（长度A、宽度B、高度C、孔径D）
- 质量预测（合格率预测、趋势变化、风险因素分析）
- 质量详情模态框（尺寸检验明细、加工参数记录）
- 时间轴回放功能
- 关联分析功能

### 5. 高级功能页面

#### NC代码仿真（NCSimulationPage）
- G代码文件上传（支持.nc, .gcode, .txt格式）
- 机床选择（FANUC-5AX、SIEMENS-3AX、HEIDENHAIN等）
- 刀具选择（面铣刀、立铣刀、球头刀等）
- G代码解析（快速移动、直线插补、圆弧插补、换刀识别）
- 实时仿真进度显示（逐行执行动画）
- 仿真结果统计（总代码行数、各类型移动次数、估计时间、总距离）
- 碰撞检测和警告提示
- 仿真设置（速度、精度、安全高度、进给倍率）
- 3D视图区域（坐标显示、刀具轨迹可视化）
- G代码列表展示（代码高亮、状态标记）

#### 能效分析（EnergyAnalysisPage）
- 设备能耗监控（总能耗、有效能耗、待机能耗）
- 能效分析和CO₂排放计算
- 成本计算和统计
- 节能机会识别（待机优化、负载优化、工艺优化、设备升级）
- 投资回报分析（投资金额、回报周期）
- 能耗趋势分析（图表占位）
- 绿色加工建议（高速切削、干式切削、刀具优化、待机管理）

#### 刀具寿命管理（ToolLifePage）
- 刀具寿命监控（使用进度、剩余寿命、磨损系数）
- 换刀预警（良好/警告/紧急/已过期状态）
- 寿命预测和预计到期时间
- 使用统计（使用次数、最后维护时间）
- 换刀操作（换刀确认、更换原因选择）
- 换刀记录管理（历史记录查看）
- 寿命分析（刀具寿命分布图、磨损趋势图）
- 寿命预测建议（参数优化、冷却条件、定期维护、提前备刀）

### 6. 资源管理页面
- **材料管理**：CRUD操作、搜索、分页、材料组标识（P钢/M不锈钢/K铸铁/N有色金属）
- **刀具管理**：CRUD操作、搜索、分页、类型筛选（铣削/钻孔/镗孔/车削）、高级参数
- **设备管理**：CRUD操作、搜索、分页、类型筛选（铣床/钻床/镗床/车床）、效率显示
- **策略管理**：CRUD操作、搜索、分页、类型筛选、粗糙度参数
- **夹具管理**：完整CRUD功能、搜索、分页、类型管理（机用虎钳/气动夹具/液压夹具/卡盘/组合夹具/专用夹具）、3D模型上传、尺寸规格管理、使用统计

### 7. 知识与分析页面
- **工艺知识库**：
  - 加工案例库（成功案例、失败案例、优化案例）
  - 专家经验库（推荐参数、适用条件）
  - 案例搜索和分类筛选
  - 参数关联图谱（占位功能）
- **历史记录**：
  - 参数优化历史记录列表
  - 搜索和筛选（材料、日期范围）
  - 统计卡片（优化记录数、平均去除率、平均执行时间、使用用户数）
  - 详情查看（输入参数、算法参数、优化结果）
  - 重新优化功能
  - 导出功能
- **报告生成**：
  - 6种报告模板（生产报告、质量报告、设备效能报告、效率分析报告、优化记录报告、工艺追溯报告）
  - 报告生成配置（时间范围、报告格式、包含内容）
  - 已生成报告列表（状态、大小、操作）
  - 下载和删除功能

### 8. 设备监控详情（DeviceMonitorPage）
- 实时数据展示（坐标、转速、进给率、负载）
- 历史数据查询（时间范围选择）
- 活跃报警列表（确认、解决操作）
- WebSocket实时连接状态
- 监控启停控制

## 构建和运行

### 完整部署（推荐 - Docker）

#### 快速启动（3步）

**1. 启动所有服务**
```batch
REM 使用批处理文件（Windows）- 最简单
一键部署.bat

REM 或使用 PowerShell
.\deploy.ps1

REM 或使用 Docker Compose
docker-compose up -d --build
```

**2. 查看服务状态**
```batch
REM 使用批处理文件
查看状态.bat

REM 或使用 Docker Compose
docker-compose ps
```

**3. 初始化测试数据**
```batch
REM 使用批处理文件
初始化数据.bat

REM 或使用 PowerShell
.\init-data.ps1
```

#### 访问地址
- **前端界面**：http://localhost:80（生产环境）或 http://localhost:3000（开发环境）
- **参数优化 API**：http://localhost:5007
- **设备监控 API**：http://localhost:5008
- **报警管理 API**：http://localhost:5009
- **质量追溯 API**：http://localhost:5010
- **RabbitMQ 管理界面**：http://localhost:15672（admin/rabbitmq123）
- **InfluxDB**：http://localhost:8086（admin/influxdb123）

#### API 文档
- **参数优化**：http://localhost:5007/docs 或 http://localhost:5007/redoc
- **设备监控**：http://localhost:5008/docs 或 http://localhost:5008/redoc
- **报警管理**：http://localhost:5009/docs 或 http://localhost:5009/redoc
- **质量追溯**：http://localhost:5010/docs 或 http://localhost:5010/redoc

### 前端开发

#### 环境准备
```bash
cd frontend
npm install
```

#### 运行方式
```bash
# 开发模式（热重载）
npm run dev

# 构建生产版本
npm run build

# 预览生产构建
npm run preview

# 代码检查
npm run lint
```

#### 访问地址
- 开发服务器：http://localhost:3000
- 生产构建预览：http://localhost:4173

### 后端开发（各微服务）

#### 环境准备

1. **安装 Python 依赖**：
```bash
cd services/<service-name>
pip install -r requirements.txt
```

2. **配置环境变量**：
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 配置数据库连接等参数
```

3. **启动基础设施**（如使用 Docker）：
```bash
docker-compose up -d mysql influxdb redis rabbitmq
```

#### 运行方式

**参数优化服务**：
```bash
cd services/parameter-optimization
python run.py
```

**设备监控服务**：
```bash
cd services/device-monitor
python run.py
```

**报警管理服务**：
```bash
cd services/alarm-management
python run.py
```

**质量追溯服务**：
```bash
cd services/quality-trace
python run.py
```

### 旧版（兼容）

#### 运行刀具参数优化系统
```bash
cd 00_刀具参数优化系统
python gui_ga.py
```

#### 仅运行遗传算法（无 GUI）
```bash
cd 00_刀具参数优化系统
python microbialGeneticAlgorithm.py
```

## API 端点

### 参数优化 API（端口 5007）

#### POST /api/v1/optimization/optimize
优化切削参数

**请求体**：
```json
{
  "material_id": "P1",
  "tool_id": "1",
  "machine_id": "1",
  "strategy_id": "1",
  "population_size": 10240,
  "generations": 200,
  "crossover_rate": 0.6,
  "mutation_rate": 0.3
}
```

**响应**：
```json
{
  "success": true,
  "message": "优化成功",
  "result": {
    "speed": 3200,
    "feed": 640,
    "cut_depth": 2.5,
    "cut_width": 25.0,
    "cutting_speed": 251.33,
    "feed_per_tooth": 0.1,
    "bottom_roughness": 1.6,
    "side_roughness": 3.2,
    "power": 5.2,
    "torque": 15.5,
    "feed_force": 1200,
    "material_removal_rate": 160.0,
    "tool_life": 120.0,
    "fitness": 0.987654
  }
}
```

#### GET /api/v1/optimization/health
健康检查

**响应**：
```json
{
  "status": "healthy",
  "service": "parameter-optimization"
}
```

#### 数据管理 API
- **材料管理**：GET/POST/PUT/DELETE `/api/v1/materials/`
- **刀具管理**：GET/POST/PUT/DELETE `/api/v1/tools/`
- **设备管理**：GET/POST/PUT/DELETE `/api/v1/machines/`
- **策略管理**：GET/POST/PUT/DELETE `/api/v1/strategies/`

### AI 辅助优化 API（端口 5007）✨ NEW

#### POST /api/v1/optimization/ai-optimize
AI 辅助参数优化（集成 AI 规划、AI 审查和 LLM 增强）

**查询参数**：
- `enable_ai_planning`: 是否启用 AI 规划（默认 True）
- `enable_ai_review`: 是否启用 AI 审查（默认 True）
- `enable_llm`: 是否启用 LLM 增强（默认 True，需要配置 DEEPSEEK_API_KEY）

**请求体**：
```json
{
  "material_id": "P1",
  "tool_id": "1",
  "machine_id": "1",
  "strategy_id": "1",
  "population_size": 10240,
  "generations": 200,
  "crossover_rate": 0.6,
  "mutation_rate": 0.3
}
```

**响应**：
```json
{
  "success": true,
  "message": "AI 规划已完成；AI 审查评分：85.5/100",
  "result": {
    "speed": 3200.0,
    "feed": 640.0,
    "cut_depth": 2.5,
    "cut_width": 25.0,
    "cutting_speed": 251.33,
    "feed_per_tooth": 0.1,
    "bottom_roughness": 1.6,
    "side_roughness": 3.2,
    "power": 5.2,
    "torque": 15.5,
    "feed_force": 1200,
    "material_removal_rate": 160.0,
    "tool_life": 120.0,
    "fitness": 0.987654
  },
  "ai_planning": {
    "search_range": {
      "speed": {"min": 2000, "max": 4000},
      "feed": {"min": 400, "max": 800},
      "cut_depth": {"min": 1.5, "max": 3.5}
    },
    "reason": "基于刀具供应商推荐参数和材料特性，优化搜索范围...",
    "safety_factor": 0.85,
    "suggestions": {
      "speed": "材料硬度较高，建议降低转速以提高刀具寿命",
      "feed": "硬质合金刀具可承受较高进给，建议在推荐范围内选择较大值",
      "general": "优化参数基本合理，建议在实际加工中根据情况进行微调",
      "risks": "请注意监控刀具磨损情况，定期检查加工质量"
    }
  },
  "ai_review": {
    "passed": true,
    "safety_score": 85.5,
    "overall_assessment": "存在警告：参数基本合理，但有改进空间",
    "summary": {
      "safe": 6,
      "warning": 2,
      "error": 0,
      "critical": 0
    },
    "items": [
      {
        "check": "功率约束",
        "status": "safe",
        "value": 5.2,
        "limit": 15.0,
        "message": "功率使用率 34.7%，在安全范围内"
      }
    ],
    "llm_analysis": "【参数优化审查报告】\n\n一、安全性分析..."
  }
}
```

**工作流程**：
1. **AI 规划**：基于刀具供应商参数、材料特性和机床能力，智能设定参数搜索范围
2. **遗传算法优化**：在规划的搜索范围内执行优化
3. **AI 审查**：验证优化结果的物理合理性和安全性
4. **LLM 增强**：使用 DeepSeek 大模型生成智能优化建议和审查分析（可选）

### 设备监控 API（端口 5008）

#### WebSocket /ws/device/{device_id}
实时设备数据推送

**连接示例**：
```javascript
const ws = new WebSocket('ws://localhost:5008/ws/device/M001');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Device data:', data);
};
```

#### GET /api/v1/devices
获取所有设备状态

**响应**：
```json
[
  {
    "id": 1,
    "device_id": "M001",
    "status": "RUNNING",
    "current_x": 100.5,
    "current_y": 50.3,
    "current_z": 25.1,
    "spindle_speed": 3200,
    "feed_rate": 640,
    "load_percent": 45.2,
    "recorded_at": "2026-02-03T10:30:00Z"
  }
]
```

#### GET /api/v1/monitoring/stats
获取监控统计

**响应**：
```json
{
  "total_devices": 10,
  "running_devices": 6,
  "idle_devices": 2,
  "alarm_devices": 1,
  "maintenance_devices": 1,
  "offline_devices": 0
}
```

### 报警管理 API（端口 5009）

#### GET /api/v1/alarms/
获取报警列表

**查询参数**：
- `status`: 报警状态（OPEN, ACKNOWLEDGED, RESOLVED, CLOSED）
- `alarm_level`: 报警级别（WARNING, ALARM, CRITICAL）
- `device_id`: 设备ID
- `page`: 页码
- `page_size`: 每页数量

#### POST /api/v1/alarms/
创建报警

**请求体**：
```json
{
  "device_id": 1,
  "alarm_level": "CRITICAL",
  "alarm_type": "DEVICE_ALARM",
  "alarm_code": "TEMP_HIGH",
  "alarm_message": "主轴温度过高"
}
```

#### POST /api/v1/alarms/{id}/acknowledge
确认报警

**请求体**：
```json
{
  "acknowledged_by": "user001",
  "note": "已通知维护人员"
}
```

#### POST /api/v1/alarms/{id}/resolve
解决报警

**请求体**：
```json
{
  "resolved_by": "user001",
  "resolution_note": "更换冷却液后温度恢复正常"
}
```

### 质量追溯 API（端口 5010）

#### GET /api/v1/quality/batches/
获取批次列表

**查询参数**：
- `workpiece_id`: 工件ID
- `production_order_id`: 生产订单ID
- `start_time`: 开始时间
- `end_time`: 结束时间
- `quality_grade`: 质量等级

#### POST /api/v1/quality/batches/
创建追溯记录

**请求体**：
```json
{
  "workpiece_id": "WP20260203001",
  "workpiece_name": "法兰盘 A",
  "production_order_id": "PO20260203",
  "material_id": "P1",
  "tool_id": "1",
  "machine_id": "1",
  "strategy_id": "1",
  "operator": "user001"
}
```

#### GET /api/v1/quality/batches/{id}
获取批次详情

## 已知问题与注意事项

### 前端应用
1. **数据初始化**：首次使用需要运行 `初始化数据.bat` 添加测试数据
2. **浏览器兼容性**：推荐使用 Chrome、Edge、Firefox 最新版本
3. **WebSocket 连接**：设备监控页面需要 WebSocket 支持
4. **代理配置**：vite.config.ts 已配置代理，API 请求自动转发到后端
5. **后端API集成**：高级功能页面（NC仿真、能效分析、刀具寿命）使用模拟数据，待后端API实现后可对接真实数据
6. **Chart.js 集成**：前端已集成 Chart.js 和 React Chart.js 2，SPC 控制图已在 QualityPage 中实现 ✅
7. **Three.js 集成**：前端已集成 Three.js、React Three Fiber 和 @react-three/drei，3D 模型查看器已在 DigitalTwinPage 中实现 ✅
8. **PDF 导出功能**：参数优化页面支持导出 PDF 报告，使用 jsPDF 和 html2canvas 实现 ✅ NEW

### 微服务
1. **依赖管理**：所有服务依赖 MySQL、Redis、RabbitMQ，需先启动基础设施
2. **环境变量**：各服务有独立的环境变量配置，需正确配置
3. **日志管理**：日志存储在 `/app/logs` 目录，通过 Docker Volume 持久化
4. **数据库连接**：使用 `get_db()` 生成器函数，不要使用 `@contextmanager` 装饰器
5. **健康检查**：部分微服务健康检查可能显示为 unhealthy，但 API 功能正常（如参数优化服务）
6. **超时配置**：nginx 代理超时和 Axios 超时已设置为 120s，支持长时间优化算法运行 ✅ UPDATED

### 参数优化算法 ✅ UPDATED
1. **向量化计算**：使用 NumPy 向量化评估函数替代 ProcessPoolExecutor，性能提升10x+
2. **DNA 编码**：36位编码（speed:16, feed:13, cut_depth:7），所有解码函数必须使用正确的位范围
3. **早停机制**：连续无改进时提前终止，默认50代
4. **返回字段**：必须包含 speed, feed, cut_depth, cut_width 字段
5. **镗孔进给力计算**：ff = 0.63 × fz × Z × (D - D_bottom) × kc / 2，考虑底孔直径影响 ✅ UPDATED
6. **单位面积进给力约束**：ff_unit = ff / (π × D² / 4)，钻孔专用约束，防止刀具弯曲 ✅ UPDATED
7. **铣削切屑厚度宽径比判断**：ae_ratio ≤ 0.3 时使用 hm = fz × √(ae_ratio)，否则使用复杂公式（考虑切削角度 fs）✅ UPDATED
8. **刀具挠度约束**：δ = (F × L³) / (3 × E × I)，I = π × D⁴ / 64，使用实际刀具参数（elastic_modulus、overhang_length）✅ UPDATED
9. **公式来源注释**：功率计算参考瓦尔特（Walter）和山德威克（Sandvik）切削理论 ✅ UPDATED
10. **数据库表结构更新**：tools 表新增 elastic_modulus（弹性模量）和 overhang_length（悬伸长度）列 ✅ UPDATED

### DeepSeek AI 集成 ✨ NEW
1. **环境变量配置**：需要设置 `DEEPSEEK_API_KEY` 环境变量才能使用 LLM 功能
2. **可选功能**：可以通过 `enable_llm=false` 参数禁用 LLM 功能，使用规则建议
3. **网络要求**：需要能够访问 DeepSeek API 服务器（https://api.deepseek.com/v1）
4. **性能影响**：LLM 调用会增加响应时间（约 2-5 秒），建议在生产环境中根据需求启用
5. **测试验证**：运行 `python test_deepseek.py` 可以验证 LLM 集成是否正常工作
6. **安全评分**：AI 审查会返回安全评分（0-100），低于 60 分建议谨慎使用优化结果
7. **建议质量**：LLM 生成的建议质量受温度参数影响，建议在 0.5-0.8 之间调整

### API 响应格式
**重要**：后端API直接返回数据（如 `ToolResponse`、`List[ToolResponse]`），前端服务文件已修复为直接处理后端返回的数据，不再使用 `ApiResponse<T>` 包装格式。

### 旧版系统
1. **数据库连接**：当前使用硬编码的数据库凭证，生产环境需改为配置管理
2. **SQL 注入风险**：部分 SQL 查询使用字符串拼接，建议使用参数化查询
3. **GUI 代码长度**：`gui_ga.py` 文件较长（1800+ 行），建议模块化拆分
4. **种群大小**：当前 POP_SIZE 设置较大，可根据硬件配置调整
5. **字符编码**：数据库使用 GBK 编码，注意字符集兼容性

## 未来扩展方向

根据《需求规格说明书.md》，系统规划包含以下模块：

### 阶段一（试点验证）✅ 已完成
- [x] 刀具参数优化系统（旧版已完成）
- [x] 参数优化微服务（重构版已完成）
- [x] 设备监控服务（已完成）
- [x] 报警管理服务（已完成）
- [x] 质量追溯服务（已完成）
- [x] Web 前端界面（16个页面已完成）
- [x] 统一设计系统（theme/index.ts 已完成）
- [x] 通用组件库（components/common 已完成）
- [x] 时序数据库（InfluxDB 2.7 已部署）
- [x] 消息队列（RabbitMQ 3 已部署）
- [x] 缓存（Redis 7 已部署）
- [x] NC代码仿真页面（NCSimulationPage 已完成）
- [x] 能效分析页面（EnergyAnalysisPage 已完成）
- [x] 刀具寿命管理页面（ToolLifePage 已完成）
- [x] 历史记录页面（HistoryPage 已完善）
- [x] 夹具管理页面（FixturesPage 已完善）
- [x] Chart.js 集成与 SPC 控制图实现（QualityPage 已完成）✅
- [x] Three.js 集成与 3D 模型查看器实现（DigitalTwinPage 已完成）✅
- [x] PDF 导出功能实现（参数优化页面支持 PDF 报告导出）✅ NEW
- [x] NumPy 向量化计算优化（性能提升10x+）✅ UPDATED
- [x] Nginx 反向代理配置（生产环境支持）✅ UPDATED
- [x] **DeepSeek AI 集成**（AI 规划器、AI 审查器、LLM 智能建议）✨ NEW
- [x] **AI 辅助优化 API**（/api/v1/optimization/ai-optimize）✨ NEW
- [x] **镗孔进给力计算公式恢复**（参照钻孔公式，考虑底孔直径影响）✅ UPDATED
- [x] **单位面积进给力约束**（钻孔专用，防止刀具弯曲）✅ UPDATED
- [x] **公式来源注释**（瓦尔特/山德威克切削理论）✅ UPDATED
- [x] **铣削切屑厚度宽径比判断**（ae ≤ 0.3D 和 ae > 0.3D 分段计算）✅ UPDATED
- [x] **刀具挠度约束优化**（悬臂梁模型，使用实际刀具参数）✅ UPDATED
- [x] **数据库表结构更新**（elastic_modulus 和 overhang_length 列）✅ UPDATED
- [x] **测试脚本完善**（test_cut_depth_fix.py、test_optimization.py）✅ UPDATED
- [ ] RBAC 权限管理（待开发）
- [ ] 报告自动生成（PDF 导出已实现，待扩展更多报告模板）
- [ ] SPC控制图数据集成（需后端API支持）
- [ ] 3D模型文件上传与解析（需后端API支持）

### 阶段二（推广扩展）
- [ ] 扩展至主要产线
- [ ] 深化工艺优化功能
- [ ] 构建工艺知识库
- [ ] 与 MES/CAM/CAPP/QMS/ERP 集成
- [ ] 移动端应用
- [ ] API 网关（Kong）
- [ ] 生产进度甘特图（WorkshopPage 待完善）
- [ ] 关键指标仪表盘（WorkshopPage 待完善）

### 阶段三（智能化升级）
- [ ] 引入 AI 算法（预测性维护、智能工艺优化）
- [ ] 实现自适应加工
- [ ] 构建企业级数字孪生平台
- [ ] 探索新模式（远程运维、增值服务）
- [ ] 3D 虚拟机床展示（3D查看器已实现，待扩展更多模型）
- [ ] 数字孪生可视化大屏
- [ ] VR/AR 远程协作
- [ ] 边缘计算节点

## 参考文档

- `需求规格说明书.md` - 完整的产品需求规格说明
- `docs/architecture/阶段一实施计划.md` - 阶段一详细实施计划
- `QUICKSTART.md` - 快速启动指南
- `DEPLOYMENT.md` - 部署文档
- `BATCH_FILES.md` - 批处理文件说明
- `frontend/PDF导出功能说明.md` - PDF 导出功能详细说明 ✨ NEW
- `services/parameter-optimization/DEEPSEEK_INTEGRATION.md` - DeepSeek AI 集成文档 ✨ NEW
- `services/parameter-optimization/README.md` - 参数优化服务文档
- `services/device-monitor/README.md` - 设备监控服务文档
- `services/alarm-management/README.md` - 报警管理服务文档
- `services/quality-trace/README.md` - 质量追溯服务文档
- `00_刀具参数优化系统/README.md` - 旧版系统文档

## 常见问题

### 部署相关

**Q: 如何部署到本机 Docker？**
A:
```batch
REM 使用批处理文件（推荐）
一键部署.bat

REM 或使用 PowerShell
.\deploy.ps1

REM 或使用 Docker Compose
docker-compose up -d --build
```

**Q: 如何查看所有服务是否正常运行？**
A:
```batch
REM 使用批处理文件
查看状态.bat

REM 或使用 Docker Compose
docker-compose ps
```

当前部署状态（2026-02-06 验证）：
- ✅ MySQL（3307端口）- 健康运行
- ✅ InfluxDB（8086端口）- 健康运行
- ✅ Redis（6379端口）- 健康运行
- ✅ RabbitMQ（5672/15672端口）- 健康运行
- ✅ 参数优化服务（5007端口）- 健康运行
- ✅ 设备监控服务（5008端口）- 健康运行
- ✅ 报警管理服务（5009端口）- 健康运行
- ✅ 质量追溯服务（5010端口）- 健康运行
- ✅ 前端服务（80端口）- 健康运行

**Q: Docker 部署时容器冲突怎么办？**
A:
```batch
REM 停止并删除所有容器
docker-compose down -v

REM 或使用批处理文件
cleanup.bat

REM 然后重新部署
一键部署.bat
```

**Q: 如何查看服务日志？**
A:
```batch
REM 使用批处理文件
logs.bat

REM 或使用 PowerShell
.\logs.ps1 -Follow

REM 或使用 Docker Compose
docker-compose logs -f parameter-optimization
docker-compose logs -f device-monitor
docker-compose logs -f mysql
```

**Q: 如何检查服务状态？**
A:
```batch
REM 使用批处理文件
查看状态.bat

REM 或使用 PowerShell
.\status.ps1

REM 或使用 Docker Compose
docker-compose ps
```

**Q: 如何停止所有服务？**
A:
```batch
REM 使用批处理文件
停止服务.bat

REM 或使用 PowerShell
.\stop.ps1

REM 或使用 Docker Compose
docker-compose down
```

### API 相关

**Q: 添加刀具、设备失败怎么办？**
A: 已修复！问题是API响应格式不匹配。前端服务文件已更新为直接处理后端返回的数据。如果仍有问题，请检查：
1. 后端服务是否正常运行
2. 浏览器控制台是否有错误信息
3. 网络请求是否成功（F12开发者工具 → Network）

### NC设备连接相关 ✅ NEW

**Q: 如何连接真实的NC设备？**
A: 请参考以下文档：
1. **快速配置**（5分钟）：[NC设备快速配置指南](docs/deployment/NC设备快速配置指南.md)
2. **完整配置**：[NC设备连接配置指南](docs/deployment/NC设备连接配置指南.md)

基本步骤：
1. 获取设备IP和OPC UA端口
2. 配置 `.env` 文件中的 `OPCUA_SERVER_URL`
3. 在 `constants.py` 中配置设备节点映射
4. 重启设备监控服务
5. 通过Web界面或API启动设备监控

**Q: 系统支持哪些NC控制器？**
A: 系统支持以下主流NC控制器：
- **FANUC**：Series 0i-MD、0i-TD、30i/31i/32i、35i
- **SIEMENS**：SINUMERIK 828D、840D sl、840D、ONE
- **HEIDENHAIN**：TNC 640、TNC 620、iTNC 530、TNC 128
- **MITSUBISHI**：M80/M800系列、E70/E80系列
- **其他**：MAZAK、HAAS、Brother、Okuma等（通过OPC UA网关）

详见：[NC设备连接配置指南 - 支持的NC控制器](docs/deployment/NC设备连接配置指南.md#支持的nc控制器)

**Q: 如何测试OPC UA连接？**
A: 系统提供了OPC UA连接测试工具：
```bash
cd services/device-monitor

# 测试FANUC设备
python test_opcua_connection.py fanuc

# 测试SIEMENS设备
python test_opcua_connection.py siemens

# 浏览服务器节点
python test_opcua_connection.py browse opc.tcp://192.168.1.100:4840
```

详见：[NC设备连接配置指南 - 使用测试工具验证连接](docs/deployment/NC设备连接配置指南.md#使用测试工具验证连接)

**Q: OPC UA连接失败怎么办？**
A: 常见原因和解决方案：

1. **网络不通**：
   ```bash
   ping 192.168.1.100
   telnet 192.168.1.100 4840
   ```

2. **防火墙阻止**：
   ```bash
   # Windows
   netsh advfirewall firewall add rule name="OPC UA" dir=in action=allow protocol=TCP localport=4840
   
   # Linux
   sudo ufw allow 4840/tcp
   ```

3. **节点ID错误**：
   - 使用测试工具浏览节点：`python test_opcua_connection.py browse opc.tcp://192.168.1.100:4840`
   - 确认节点ID格式正确（如 `ns=2;s=Channel1.Stat.Mode`）

4. **OPC UA服务器未启动**：
   - 检查NC控制器是否启用OPC UA功能
   - 确认服务器地址和端口正确

详见：[NC设备连接配置指南 - 故障排除](docs/deployment/NC设备连接配置指南.md#故障排除)

**Q: 如何获取NC控制器的OPC UA节点ID？**
A: 有以下几种方法：

1. **使用UaExpert**（免费OPC UA客户端）：
   - 下载：https://www.unified-automation.com/products/development-tools/uaexpert.html
   - 连接到OPC UA服务器
   - 浏览节点树，查看节点ID

2. **使用系统提供的测试工具**：
   ```bash
   python test_opcua_connection.py browse opc.tcp://192.168.1.100:4840
   ```

3. **参考速查表**：
   - [FANUC节点ID](docs/deployment/NC设备连接配置指南.md#fanuc)
   - [SIEMENS节点ID](docs/deployment/NC设备连接配置指南.md#siemens)
   - [HEIDENHAIN节点ID](docs/deployment/NC设备连接配置指南.md#heid enhain)

**Q: 可以连接多台不同品牌的NC设备吗？**
A: 可以！系统支持同时连接多台不同品牌的NC设备。只需在 `constants.py` 中配置多个设备节点映射即可：

```python
OPCUA_NODE_MAPPING = {
    1: {
        "device_name": "FANUC_VM1",
        "controller_type": "FANUC",
        "server_url": "opc.tcp://192.168.1.100:4840",
        # ... 节点配置
    },
    2: {
        "device_name": "SIEMENS_VM2",
        "controller_type": "SIEMENS",
        "server_url": "opc.tcp://192.168.1.101:4840",
        # ... 节点配置
    },
}
```

**Q: 数据采集间隔如何配置？**
A: 在 `.env` 文件中配置：
```bash
# 采集间隔（秒）
OPCUA_POLLING_INTERVAL=1.0
```

推荐值：
- 0.5秒：高频监控（关键设备）
- 1.0秒：标准监控（默认）
- 2.0秒：低频监控（非关键设备）

**Q: 如何查看设备实时数据？**
A: 有以下几种方式：

1. **Web界面**：
   - 访问 http://localhost:80
   - 进入车间视图或设备监控页面
   - 查看实时数据和状态

2. **API调用**：
   ```bash
   # 查看实时数据
   curl http://localhost:5008/api/v1/monitoring/1/realtime
   
   # 查看设备状态
   curl http://localhost:5008/api/v1/devices/1/status
   
   # 查看监控统计
   curl http://localhost:5008/api/v1/monitoring/stats
   ```

3. **WebSocket连接**：
   ```javascript
   const ws = new WebSocket('ws://localhost:5008/api/v1/ws/monitoring/1');
   ws.onmessage = (event) => {
     const data = JSON.parse(event.data);
     console.log('实时数据:', data);
   };
   ```

**Q: 设备数据存储在哪里？**
A: 设备数据存储在两个地方：

1. **InfluxDB时序数据库**（历史数据）：
   - 存储所有历史采集数据
   - 支持高频数据（≥1kHz）
   - 用于历史数据查询和趋势分析

2. **Redis缓存**（实时状态）：
   - 存储最新设备状态
   - 用于快速查询实时数据

3. **MySQL数据库**（设备记录）：
   - 存储设备基本信息
   - 存储设备状态快照

**Q: 如何查询历史数据？**
A: 使用API查询：
```bash
# 查询历史数据
curl -X POST http://localhost:5008/api/v1/monitoring/1/history \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "start_time": "2026-02-01T00:00:00Z",
    "end_time": "2026-02-06T23:59:59Z",
    "measurement": "device_sensor_data",
    "limit": 1000
  }'
```

详见：[NC设备连接配置指南 - 数据流](docs/deployment/NC设备连接配置指南.md#数据流)

**Q: 遗传算法运行很慢怎么办？**
A: 已通过 NumPy 向量化优化实现10x+性能提升。如需进一步优化，可以减小种群大小和迭代次数：
```json
{
  "population_size": 5120,
  "generations": 100
}
```

**Q: 优化请求超时（504错误）怎么办？**
A: 已修复！nginx 代理超时和 Axios 超时已设置为 120s。如仍遇到超时，请检查：
1. 种群大小和迭代次数设置是否过大
2. 服务器资源是否充足
3. 网络连接是否稳定

**Q: 如何添加新材料/刀具/设备？**
A:
- **Web 界面**：访问 http://localhost:80（生产环境）或 http://localhost:3000（开发环境），在对应的管理页面添加
- **API 调用**：使用 RESTful API（如 `POST /api/v1/materials/`）
- **API 文档**：访问 http://localhost:5007/docs 进行测试

**Q: 前端页面显示"暂无数据"？**
A: 需要先初始化测试数据：
```batch
初始化数据.bat
```

### 前端相关

**Q: 前端如何启动？**
A:
```bash
cd frontend
npm install
npm run dev
```
然后访问 http://localhost:3000

**Q: 前端无法连接到后端？**
A: 检查以下几点：
1. 后端服务是否正常运行（运行 `查看状态.bat` 检查）
2. 前端 vite.config.ts 中的代理配置是否正确
3. 浏览器控制台是否有跨域错误
4. 确保后端运行在对应端口

**Q: WebSocket 连接失败？**
A: 检查：
1. 设备监控服务是否正常运行
2. 防火墙是否允许 WebSocket 连接
3. 浏览器控制台是否有错误信息

**Q: 高级功能页面使用的是什么数据？**
A: NC仿真、能效分析、刀具寿命三个高级功能页面当前使用模拟数据，前端界面和功能已完全实现。待后端API开发完成后，可通过更新服务文件对接真实数据。

**Q: 如何使用3D模型查看器？**
A: 在数字孪生页面（DigitalTwinPage）中，点击任意机床、刀具或夹具的"查看"按钮即可打开3D模型查看器。支持：
- 左键旋转模型
- 右键平移视角
- 滚轮缩放视图
- 自动旋转开关
- 导出截图功能

**Q: SPC控制图如何使用？**
A: 在质量追溯页面（QualityPage）的"SPC监控"标签页中，可选择：
- 控制图类型（Xbar-R、Xbar-S、I-MR、P控制图）
- 控制参数（长度A、宽度B、高度C、孔径D）
- 图表会自动显示UCL、LCL、Mean和实测值
- 超出控制限的数据点会自动标记为红色

**Q: 如何导出优化结果 PDF 报告？** ✨ NEW
A: 在参数优化页面（OptimizationPage）中：
1. 执行参数优化并等待完成
2. 优化完成后，点击"导出 PDF"按钮
3. 系统将自动生成并下载 PDF 文件
4. 文件名格式：`优化报告_YYYY-MM-DDTHH-mm-ss.pdf`

**Q: PDF 报告包含哪些内容？** ✨ NEW
A: PDF 报告包含以下内容：
- 报告标题和生成时间
- 项目说明（加工方法、材料、刀具等）
- 优化结果摘要（6个核心参数）
- 材料去除率（绿色背景突出显示）
- 加工参数配置（材料、刀具、设备、策略详细信息）
- 性能指标（功率、扭矩、进给力、刀具寿命、粗糙度）
- 约束使用情况（带颜色进度条：绿≤80%、橙≤95%、红>95%）
- 智能优化建议（基于约束使用率和材料去除率）
- 免责声明和页脚信息

**Q: PDF 导出失败怎么办？** ✨ NEW
A: 请检查：
1. 浏览器是否支持 PDF 下载（推荐 Chrome、Edge、Firefox）
2. 浏览器控制台是否有错误信息（F12 → Console）
3. 网络连接是否正常
4. 优化结果是否成功生成
5. 浏览器是否允许下载文件

### AI 集成相关 ✨ NEW

**Q: 如何启用 DeepSeek AI 功能？**
A: 需要配置 `DEEPSEEK_API_KEY` 环境变量：
```batch
REM Windows CMD
set DEEPSEEK_API_KEY=your_deepseek_api_key_here

REM PowerShell
$env:DEEPSEEK_API_KEY="your_deepseek_api_key_here"

REM Linux/Mac
export DEEPSEEK_API_KEY="your_deepseek_api_key_here"
```

**Q: 如何获取 DeepSeek API Key？**
A:
1. 访问 DeepSeek 控制台：https://platform.deepseek.com/console
2. 注册/登录账号
3. 在 API Keys 页面创建新的 API Key
4. 复制 API Key 并配置到环境变量中

**Q: AI 辅助优化和标准优化有什么区别？**
A: AI 辅助优化包含以下增强功能：
1. **AI 规划**：智能设定参数搜索范围，提高优化效率
2. **AI 审查**：验证优化结果的物理合理性和安全性
3. **LLM 建议**：生成智能优化建议和审查分析报告
4. **安全评分**：提供 0-100 的安全评分，评估优化结果可靠性

**Q: 如何禁用 LLM 功能？**
A: 有两种方式：
1. 在 API 调用时设置 `enable_llm=false` 参数
2. 不设置 `DEEPSEEK_API_KEY` 环境变量（系统会自动降级）

**Q: LLM 调用失败怎么办？**
A: 请检查：
1. `DEEPSEEK_API_KEY` 是否正确设置
2. 网络连接是否正常（需要访问 https://api.deepseek.com/v1）
3. API Key 是否有足够的额度
4. 查看服务日志：`logs/app.log`
5. 运行测试脚本：`python test_deepseek.py`

**Q: AI 审查评分低于 60 分怎么办？**
A: 建议采取以下措施：
1. 检查优化参数是否合理（转速、进给、切深、切宽）
2. 查看具体的审查项（safe、warning、error、critical）
3. 考虑调整刀具、材料或机床参数
4. 重新运行优化，可能需要调整算法参数
5. 咨询工艺专家进行人工审核

**Q: 如何测试 DeepSeek 集成是否正常？**
A: 运行测试脚本：
```bash
cd services/parameter-optimization
python test_deepseek.py
```

**Q: LLM 功能会影响优化性能吗？**
A: 会增加约 2-5 秒的响应时间。如果对性能要求较高，可以：
1. 使用 `enable_llm=false` 参数禁用 LLM 功能
2. 只在需要详细分析时启用 LLM
3. 使用缓存机制（待实现）

**Q: AI 生成的建议不准确怎么办？**
A: 可以尝试：
1. 调整 `DEEPSEEK_TEMPERATURE` 参数（0.5-0.8）
2. 改进 Prompt 设计（需要修改代码）
3. 提供更详细的上下文信息
4. 使用规则建议作为后备方案

### 算法相关 ✅ UPDATED

## 算法优化详解（v14.0 更新）

### 最新优化内容

#### 1. 镗孔进给力计算公式恢复 ✅ UPDATED

**问题**：镗孔进给力计算缺失，导致镗孔加工参数优化不准确。

**解决方案**：参照钻孔公式，考虑底孔直径影响。

**公式**：
```
ff = 0.63 × fz × Z × (D - D_bottom) × kc / 2
```

**参数说明**：
- `ff`：进给力 (N)
- `fz`：每齿进给 (mm)
- `Z`：刀具齿数
- `D`：刀具直径 (mm)
- `D_bottom`：底孔直径 (mm)
- `kc`：单位切削力 (N/mm²)

**来源**：参照钻孔进给力公式，根据切削面积调整（π × D² - π × D_bottom²）。

#### 2. 单位面积进给力约束（钻孔专用）✅ UPDATED

**问题**：钻孔时刀具容易弯曲，需要添加单位面积进给力约束。

**解决方案**：计算单位面积进给力，防止刀具弯曲。

**公式**：
```
ff_unit = ff / (π × D² / 4)
```

**约束条件**：
```
ff_unit ≤ max_feed_force_unit
```

**参数说明**：
- `ff_unit`：单位面积进给力 (N/mm²)
- `ff`：进给力 (N)
- `D`：刀具直径 (mm)

**来源**：刀具弯曲理论，单位面积进给力超过阈值会导致刀具弯曲。

#### 3. 铣削切屑厚度宽径比判断 ✅ UPDATED

**问题**：铣削切屑厚度计算不准确，导致功率和扭矩计算误差。

**解决方案**：根据切宽与刀具直径的比值（ae_ratio）分段计算切屑厚度。

**公式**：

**当 ae_ratio ≤ 0.3 时**：
```
hm = fz × √(ae_ratio)
```

**当 ae_ratio > 0.3 时**：
```
ratio = (ae - 0.5 × D) / (0.5 × D)  # 限制在 [-1, 1] 范围内
fs = 90 + arcsin(ratio) × 180 / π    # 切削角度（度）
hm = 1147 × fz × sin(κr × π / 180) × ae_ratio / fs
```

**参数说明**：
- `hm`：平均切屑厚度 (mm)
- `fz`：每齿进给 (mm)
- `ae_ratio`：切宽与刀具直径的比值（ae / D）
- `ae`：切宽 (mm)
- `D`：刀具直径 (mm)
- `fs`：切削角度（度）
- `κr`：主偏角（度）

**来源**：瓦尔特（Walter）和山德威克（Sandvik）切削理论，切宽较小时使用简化公式，切宽较大时考虑切削角度影响。

#### 4. 刀具挠度约束优化 ✅ UPDATED

**问题**：刀具挠度约束不准确，使用硬编码参数导致优化结果不理想。

**解决方案**：使用实际刀具参数（elastic_modulus、overhang_length）计算挠度。

**公式**：
```
I = π × D⁴ / 64                      # 截面惯性矩 (mm⁴)
δ = (F × L³) / (3 × E × I)           # 挠度 (mm)
```

**约束条件**：
```
δ ≤ max_tool_deflection              # 最大允许挠度
```

**参数说明**：
- `δ`：刀具挠度 (mm)
- `F`：进给力 (N)
- `L`：悬伸长度 (mm) - 从数据库读取（overhang_length）
- `E`：弹性模量 (MPa) - 从数据库读取（elastic_modulus）
- `I`：截面惯性矩 (mm⁴)
- `D`：刀具直径 (mm)

**来源**：悬臂梁理论，挠度与进给力、悬伸长度的三次方成正比，与弹性模量、截面惯性矩成反比。

**数据库更新**：
```sql
-- 为 tools 表添加刀具参数列
ALTER TABLE tools ADD COLUMN elastic_modulus FLOAT NULL COMMENT '弹性模量 MPa';
ALTER TABLE tools ADD COLUMN overhang_length FLOAT NULL COMMENT '悬伸长度 mm';
```

**参数值**：
- `elastic_modulus`：硬质合金刀具约 630,000 MPa（630 GPa）
- `overhang_length`：常用值 60 mm
- `max_tool_deflection`：0.15 × D（刀具直径的 15%）

#### 5. 公式来源注释 ✅ UPDATED

**问题**：公式来源不明确，难以追溯和验证。

**解决方案**：添加公式来源注释，标注参考的切削理论。

**标注格式**：
```python
# 功率和扭矩（瓦尔特功率计算公式）
# pmot = Q × kc / 60000 / machine_efficiency (Kw)
# 备用：山德威克功率计算公式（Sandvik Power Formula）
# pmot = AE × ap × f × KC11 / 60037200 / machine_efficiency (Kw)
pmot = q * kc * PhysicalConstants.POWER_WATT_TO_KW / constraints.machine_efficiency
```

**参考来源**：
- 瓦尔特（Walter）切削理论
- 山德威克（Sandvik）切削理论
- 机械加工手册

#### 6. 数据库表结构更新 ✅ UPDATED

**问题**：刀具参数不足，无法准确计算刀具挠度。

**解决方案**：为 tools 表添加弹性模量和悬伸长度列。

**更新脚本**：
```sql
-- add_tool_columns.sql
ALTER TABLE tools ADD COLUMN elastic_modulus FLOAT NULL COMMENT '弹性模量 MPa';
ALTER TABLE tools ADD COLUMN overhang_length FLOAT NULL COMMENT '悬伸长度 mm';
```

**参数初始化**：
```sql
-- 更新现有刀具参数
UPDATE tools SET elastic_modulus = 630000, overhang_length = 60 WHERE elastic_modulus IS NULL;
```

#### 7. 测试脚本完善 ✅ UPDATED

**问题**：缺少自动化测试脚本，难以验证算法优化效果。

**解决方案**：新增测试脚本，验证算法优化效果。

**测试脚本**：
- `test_cut_depth_fix.py`：测试切深修复效果，验证刀具挠度约束
- `test_optimization.py`：测试参数优化效果，验证约束是否生效

**使用方法**：
```bash
# 测试切深修复
python test_cut_depth_fix.py

# 测试参数优化
python test_optimization.py
```

### 优化效果

**修复前**：
- 切深过小（< 1.5 mm），无法满足粗加工要求
- 刀具挠度超出限制，影响加工精度
- 镗孔进给力计算缺失，镗孔参数不准确
- 铣削切屑厚度计算误差，功率和扭矩计算不准确

**修复后**：
- 切深恢复正常（≥ 2.0 mm），满足粗加工要求 ✅
- 刀具挠度在允许范围内（≤ 0.15 × D）✅
- 镗孔进给力计算准确，考虑底孔直径影响 ✅
- 铣削切屑厚度计算准确，根据 ae_ratio 分段计算 ✅
- 公式来源明确，易于追溯和验证 ✅
- 数据库表结构完善，支持实际刀具参数 ✅

### 验证方法

**1. 运行测试脚本**：
```bash
python test_cut_depth_fix.py
python test_optimization.py
```

**2. 检查优化结果**：
- 切深 ≥ 2.0 mm（粗加工要求）
- 刀具挠度 ≤ 0.15 × D（刀具直径的 15%）
- 镗孔进给力包含底孔直径参数
- 铣削切屑厚度根据 ae_ratio 分段计算

**3. 检查数据库**：
```sql
SELECT id, name, diameter, elastic_modulus, overhang_length FROM tools;
```

**4. 检查代码注释**：
- 公式来源注释（瓦尔特/山德威克）
- 参数说明注释
- 计算步骤注释

### 相关文件

**算法文件**：
- `services/parameter-optimization/src/algorithms/microbial_ga.py` - 微生物遗传算法核心实现
- `services/parameter-optimization/src/algorithms/objectives.py` - 目标函数

**数据库脚本**：
- `add_tool_columns.sql` - 添加刀具参数列
- `fix_parameters.sql` - 修复材料参数和机床参数

**测试脚本**：
- `test_cut_depth_fix.py` - 切深修复测试
- `test_optimization.py` - 参数优化测试

**文档**：
- `AGENTS.md` - 本文档
- `DEEPSEEK_INTEGRATION.md` - DeepSeek AI 集成文档

---

**Q: 微生物遗传算法如何工作？**
A: 算法使用 NumPy 向量化计算实现高性能优化：
1. **DNA 编码**：36位二进制编码（speed:16, feed:13, cut_depth:7）
2. **种群初始化**：随机生成指定规模的种群
3. **适应度评估**：向量化计算所有个体的适应度（10x+ 性能提升）
4. **选择与交叉**：基于微生物竞争机制进行选择和交叉
5. **变异操作**：按概率进行位翻转变异
6. **早停机制**：连续无改进时提前终止（默认50代）

**Q: 为什么向量化计算比进程池更快？**
A: 向量化计算的优势：
1. **避免进程开销**：无需创建和销毁进程
2. **内存共享**：所有计算在同一进程内完成
3. **NumPy 优化**：利用 C 层优化的数组操作
4. **批处理**：一次处理整个种群，减少循环开销

**Q: 算法支持哪些加工方法？**
A: 支持4种加工方法：
- **MILLING**：铣削
- **DRILLING**：钻孔
- **BORING**：镗孔
- **TURNING**：车削

每种方法有不同的计算逻辑和约束条件。

**Q: 如何验证算法修复是否正确？** ✨ NEW
A: 可以通过以下方式验证：
1. 检查 DNA 解码是否与旧版本一致
2. 检查线速度计算公式是否为 vc = n * D / 318 + 0.1
3. 运行优化并检查转速、进给、材料去除率是否合理
4. 对比新旧版本的优化结果
5. 运行测试脚本：`python test_cut_depth_fix.py` 和 `python test_optimization.py` ✅ UPDATED
6. 检查镗孔进给力是否包含底孔直径参数：ff = 0.63 × fz × Z × (D - D_bottom) × kc / 2 ✅ UPDATED
7. 检查刀具挠度是否使用实际刀具参数：δ = (F × L³) / (3 × E × I) ✅ UPDATED
8. 检查数据库是否包含 elastic_modulus 和 overhang_length 列 ✅ UPDATED

**Q: 算法修复了哪些问题？** ✨ NEW
A: 修复了以下关键问题：
1. **DNA解码错误**：从错误的左移位改为正确的加权求和
2. **线速度计算错误**：从 vc = n * π * D / 60000 修复为 vc = n * D / 318 + 0.1
3. **uint8溢出问题**：在加权计算前将 bit 转换为 int 类型
4. **镗孔进给力公式缺失**：恢复镗孔进给力计算，参照钻孔公式，考虑底孔直径影响 ✅ UPDATED
5. **单位面积进给力约束缺失**：添加钻孔专用约束，防止刀具弯曲 ✅ UPDATED
6. **铣削切屑厚度计算错误**：根据 ae_ratio 分段计算，ae > 0.3D 时使用复杂公式 ✅ UPDATED
7. **刀具挠度约束不准确**：使用实际刀具参数（elastic_modulus、overhang_length）计算挠度 ✅ UPDATED
8. **公式来源不明确**：添加公式来源注释（瓦尔特/山德威克切削理论）✅ UPDATED
9. 这些修复解决了转速偏低、进给偏高、材料去除率不足、切深过小、刀具挠度超出限制等问题

**Q: 如何调整算法参数？**
A: 可以通过 API 请求或配置文件调整：
```json
{
  "population_size": 10240,    // 种群大小（建议：1024-10240）
  "generations": 200,          // 迭代次数（建议：50-500）
  "crossover_rate": 0.6,       // 交叉概率（0.5-0.8）
  "mutation_rate": 0.3         // 变异概率（0.1-0.5）
}
```

**Q: 算法返回哪些字段？**
A: 优化结果包含以下字段：
- `speed`：转速 (r/min)
- `feed`：进给量 (mm/min)
- `cut_depth`：切深 (mm)
- `cut_width`：切宽 (mm)
- `cutting_speed`：线速度 (m/min)
- `feed_per_tooth`：每齿进给 (mm)
- `bottom_roughness`：底面粗糙度 (μm)
- `side_roughness`：侧面粗糙度 (μm)
- `power`：功率 (Kw)
- `torque`：扭矩 (Nm)
- `feed_force`：进给力 (N)
- `material_removal_rate`：材料去除率 (cm³/min)
- `tool_life`：刀具寿命 (min)
- `tool_deflection`：刀具挠度 (mm) ✅ UPDATED
- `fitness`：适应度值

---

**文档版本**：v15.0
**最后更新**：2026-02-06
**维护者**：工艺数字孪生项目团队

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2025-12-01 | 初始版本，基础架构 |
| v2.0 | 2026-01-15 | 添加微服务架构和 RESTful API |
| v3.0 | 2026-01-30 | 添加安全认证、日志系统和 Docker 部署 |
| v4.0 | 2026-02-02 | 添加 Web 前端界面和自动化部署脚本 |
| v5.0 | 2026-02-03 | 添加设备监控、报警管理、质量追溯三大微服务；统一使用 Alpine Linux 基础镜像 |
| v6.0 | 2026-02-03 | 更新阶段一完成状态；完善前端应用结构；更新技术栈版本；补充 API 文档；已知问题与故障排除 |
| v7.0 | 2026-02-03 | 添加统一设计系统（theme/index.ts）；新增13个前端页面；更新路由配置；添加通用组件；修复API响应格式问题；更新常见问题 |
| v8.0 | 2026-02-03 | 新增3个高级功能页面（NC仿真、能效分析、刀具寿命）；完善历史记录和夹具管理页面；更新侧边栏菜单结构（4级分类）；更新页面数量为16个；添加Chart.js依赖；更新阶段一完成状态 |
| v9.0 | 2026-02-03 | 集成 Chart.js 实现 SPC 控制图；集成 Three.js 实现 3D 模型查看器；新增 ModelViewer3D 组件；更新 QualityPage 和 DigitalTwinPage 功能描述；更新前端依赖列表；完善服务状态说明 |
| v10.0 | 2026-02-03 | 新增 PDF 导出功能；参数优化页面支持生成格式化 PDF 报告；添加 jsPDF 和 html2canvas 依赖；新增 pdfService 服务；添加 PDF导出功能说明文档；更新常见问题 |
| v11.0 | 2026-02-04 | 更新 Nginx 反向代理配置（生产环境支持端口80）；修复算法返回字段（添加speed, feed, cut_depth, cut_width）；添加 NumPy 向量化计算优化说明；更新超时配置（120s）；添加算法相关常见问题 |
| v12.0 | 2026-02-04 | **成功部署到本机 Docker 环境**；修复算法 DNA 解码和线速度计算问题；更新项目部署状态；添加算法验证相关问题；更新所有服务端口映射 |
| v13.0 | 2026-02-05 | 更新 Python 版本要求（3.9+）；添加 cryptography 依赖；完善项目结构说明；更新部署状态日期；补充 Vite 代理配置文档 |
| v14.0 | 2026-02-06 | **算法重大优化**：镗孔进给力公式恢复、单位面积进给力约束、公式来源注释（瓦尔特/山德威克）、铣削切屑厚度宽径比判断、刀具挠度约束优化；数据库表结构更新（elastic_modulus 和 overhang_length 列）；新增测试文件（test_cut_depth_fix.py、test_optimization.py）；确认9个容器健康运行 |
| v15.0 | 2026-02-06 | **NC设备连接功能完善**：新增NC设备连接配置文档和快速配置指南；完善设备节点映射配置（支持FANUC、SIEMENS、HEIDENHAIN、MITSUBISHI等主流控制器）；新增OPC UA连接测试工具（test_opcua_connection.py）；更新设备监控服务配置（constants.py、settings.py）；添加NC设备连接常见问题；支持真实设备替代模拟数据 |