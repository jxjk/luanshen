# 快速启动指南

本指南将帮助您快速启动工艺参数优化系统的前后端服务。

## 前置要求

- Node.js >= 16.x
- Python >= 3.9
- MySQL 8.0+
- Docker（可选，用于容器化部署）

## 启动步骤

### 方式一：自动化部署（Windows推荐）⭐

#### 方法1：双击运行批处理文件（最简单）

直接双击以下批处理文件：

- **deploy.bat**：部署所有服务
- **stop.bat**：停止所有服务
- **status.bat**：检查服务状态
- **init.bat**：添加测试数据
- **logs.bat**：查看服务日志
- **cleanup.bat**：清理所有数据

#### 方法2：PowerShell脚本

```powershell
# 在PowerShell中运行（以管理员身份）
.\deploy.ps1
```

该脚本会自动：
- ✓ 检查Docker环境
- ✓ 检查端口占用
- ✓ 创建环境变量配置
- ✓ 启动MySQL数据库
- ✓ 启动后端服务
- ✓ 等待服务就绪

部署完成后，初始化测试数据：

```powershell
.\init-data.ps1
```

然后启动前端：

```powershell
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

#### 其他自动化脚本

```powershell
# 查看服务状态
.\status.ps1

# 查看实时日志
.\logs.ps1 -Follow

# 停止服务
.\stop.ps1

# 清理所有数据（谨慎使用）
.\cleanup.ps1
```

详细使用说明请查看 [DEPLOYMENT.md](DEPLOYMENT.md)

### 方式二：Docker Compose手动部署

```bash
# 1. 启动所有服务（MySQL + 后端）
docker-compose up -d

# 2. 安装前端依赖
cd frontend
npm install

# 3. 启动前端开发服务器
npm run dev
```

访问 http://localhost:3000

### 方式二：手动启动

#### 1. 启动MySQL数据库

```bash
# 使用Docker启动MySQL
docker run -d \
  --name mysql \
  -e MYSQL_ROOT_PASSWORD=123456 \
  -e MYSQL_DATABASE=ga_tools \
  -p 3307:3306 \
  -v $(pwd)/00_刀具参数优化系统/ga_tools.sql:/docker-entrypoint-initdb.d/init.sql \
  mysql:8.0

# 等待MySQL初始化完成（约30秒）
```

#### 2. 启动后端服务

```bash
cd services/parameter-optimization

# 安装Python依赖
pip install -r requirements.txt

# 配置环境变量（.env文件已配置好）
# 确保.env文件中的数据库配置正确：
# DB_HOST=localhost
# DB_PORT=3307
# DB_USER=root
# DB_PASSWORD=123456
# DB_NAME=ga_tools

# 启动服务
python run.py
```

后端服务将在 http://localhost:5007 运行

#### 3. 启动前端服务

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端服务将在 http://localhost:3000 运行

## 验证服务

### 检查后端服务

访问 http://localhost:5007/docs 查看API文档

### 检查前端服务

访问 http://localhost:3000 查看前端界面

### 健康检查

```bash
# 后端健康检查
curl http://localhost:5007/api/v1/optimization/health

# 应该返回：
# {"status":"healthy","service":"parameter-optimization"}
```

## 使用流程

1. **登录系统**（未来功能）
2. **选择材料**：在参数优化页面选择要加工的材料
3. **选择刀具**：选择合适的刀具
4. **选择设备**：选择使用的设备
5. **选择策略**：选择加工策略（粗铣、精铣等）
6. **配置算法参数**（可选）：调整种群大小、迭代次数等
7. **开始优化**：点击"开始优化"按钮
8. **查看结果**：在右侧查看优化结果

## 常见问题

### Q: 前端无法连接到后端？

A: 检查以下几点：
1. 后端服务是否正常运行（运行 `.\status.ps1` 检查）
2. 前端vite.config.ts中的代理配置是否正确
3. 浏览器控制台是否有跨域错误

### Q: 部署脚本执行失败？

A: 检查以下几点：
1. 是否以管理员身份运行PowerShell
2. Docker Desktop是否已启动
3. 端口3307和5007是否被占用

### Q: 数据库连接失败？

A: 检查以下几点：
1. MySQL服务是否正在运行（运行 `.\status.ps1` 查看）
2. .env文件中的数据库配置是否正确
3. 数据库端口是否被占用（默认3307）

### Q: 如何查看服务日志？

A: 使用日志脚本：
```powershell
# 查看所有服务日志
.\logs.ps1

# 实时跟踪日志
.\logs.ps1 -Follow
```

### Q: 优化功能无法使用？

A: 检查以下几点：
1. 数据库中是否有材料、刀具、设备、策略数据（运行 `.\init-data.ps1` 初始化）
2. 可以访问 http://localhost:5007/docs 手动添加测试数据
3. 查看后端日志是否有错误信息（运行 `.\logs.ps1`）

## 测试数据

如果数据库为空，可以通过以下方式添加测试数据：

### 方式一：自动化脚本（推荐）⭐

```powershell
# 在PowerShell中运行
.\init-data.ps1
```

该脚本会自动添加：
- 材料：45号钢 (P1)
- 刀具：硬质合金立铣刀 (Φ25mm, 2齿)
- 设备：XK7132铣床
- 策略：粗铣策略

### 方式二：使用API文档

1. 访问 http://localhost:5007/docs
2. 使用Swagger UI添加材料、刀具、设备、策略数据

### 方式三：使用旧版GUI

```bash
cd 00_刀具参数优化系统
python gui_ga.py
```

通过旧版GUI界面添加数据。

## 项目结构

```
工艺数字孪生/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── components/          # 组件
│   │   ├── pages/               # 页面
│   │   ├── services/            # API服务
│   │   └── types/               # 类型定义
│   └── package.json
├── services/
│   └── parameter-optimization/  # 后端服务
│       ├── src/
│       │   ├── api/             # API路由
│       │   ├── models/          # 数据模型
│       │   ├── repositories/    # 数据访问层
│       │   └── algorithms/      # 算法模块
│       └── requirements.txt
├── 00_刀具参数优化系统/         # 旧版系统
│   ├── gui_ga.py
│   └── ga_tools.sql
└── docker-compose.yml           # Docker编排
```

## 下一步

- 添加用户认证功能
- 完善历史记录功能
- 添加图表可视化
- 实现实时监控功能
- 集成MES/CAM系统

## 获取帮助

如有问题，请查看：
- 批处理文件指南：[BATCH_FILES.md](BATCH_FILES.md)
- 部署指南：[DEPLOYMENT.md](DEPLOYMENT.md)
- 后端API文档：http://localhost:5007/docs
- 前端README：frontend/README.md
- 项目文档：AGENTS.md