# 自动化部署指南

本指南介绍如何使用PowerShell脚本自动化部署和管理工艺参数优化系统。

## 脚本列表

### PowerShell脚本

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| `deploy.ps1` | 一键部署所有服务 | 首次部署或重新部署 |
| `stop.ps1` | 停止所有服务 | 停止运行中的服务 |
| `status.ps1` | 检查服务状态 | 诊断问题或查看状态 |
| `logs.ps1` | 查看服务日志 | 调试和故障排查 |
| `cleanup.ps1` | 清理所有数据 | 完全重置系统 |
| `init-data.ps1` | 初始化测试数据 | 首次部署后添加测试数据 |

### 批处理文件（推荐）

| 文件 | 功能 | 说明 |
|------|------|------|
| `deploy.bat` | 部署服务 | 双击即可部署所有服务 |
| `stop.bat` | 停止服务 | 双击即可停止所有服务 |
| `status.bat` | 查看状态 | 双击即可查看服务状态 |
| `init.bat` | 初始化数据 | 双击即可添加测试数据 |
| `logs.bat` | 查看日志 | 双击即可查看服务日志 |
| `cleanup.bat` | 清理数据 | 双击即可清理所有数据 |

> **注意**：批处理文件使用UTF-8编码，避免中文字符导致的编码问题。详细信息请查看 [BATCH_FILES.md](BATCH_FILES.md)。

## 快速开始

### 1. 首次部署

```powershell
# 以管理员身份运行PowerShell
.\deploy.ps1
```

脚本会自动完成以下任务：
- ✓ 检查Docker环境
- ✓ 检查Docker Compose
- ✓ 检查端口占用
- ✓ 创建环境变量配置
- ✓ 启动MySQL数据库
- ✓ 启动后端服务
- ✓ 等待服务就绪

### 2. 初始化测试数据

```powershell
.\init-data.ps1
```

### 3. 启动前端

```powershell
cd frontend
npm install
npm run dev
```

访问 http://localhost:3000

## 脚本详解

### deploy.ps1 - 部署脚本

**功能**：一键部署所有Docker服务

**使用方法**：
```powershell
.\deploy.ps1
```

**执行步骤**：
1. 检查Docker是否安装
2. 检查Docker服务是否运行
3. 检查Docker Compose是否可用
4. 检查端口占用（3307, 5007）
5. 创建.env文件（如果不存在）
6. 启动Docker Compose服务
7. 等待MySQL数据库就绪

**输出信息**：
- 服务访问地址
- 常用命令提示
- 下一步操作指引

### stop.ps1 - 停止脚本

**功能**：停止所有运行中的服务

**使用方法**：
```powershell
.\stop.ps1
```

**说明**：
- 停止所有Docker容器
- 保留数据卷（不会删除数据）
- 可以通过 `.\deploy.ps1` 重新启动

### status.ps1 - 状态检查脚本

**功能**：检查系统和服务的运行状态

**使用方法**：
```powershell
.\status.ps1
```

**检查项目**：
- Docker服务状态
- 容器运行状态
- 端口占用情况
- 数据卷状态
- 服务健康检查

**输出示例**：
```
[1] Docker服务状态
✓ Docker服务: 运行中

[2] 容器状态
NAME                                STATUS    PORTS
process_digital_twin_mysql         Up        0.0.0.0:3307->3306/tcp
process_digital_twin_optimization  Up        0.0.0.0:5007->8000/tcp

[3] 端口占用
✓ 端口3307 (MySQL): 已占用
✓ 端口5007 (API): 已占用

[4] 数据卷状态
✓ 数据卷:
  - process_digital_twin_mysql_data
  - process_digital_twin_optimization_logs

[5] 服务健康检查
✓ 后端服务: 健康
```

### logs.ps1 - 日志查看脚本

**功能**：查看服务日志

**使用方法**：

```powershell
# 查看所有服务日志
.\logs.ps1

# 实时跟踪所有服务日志
.\logs.ps1 -Follow

# 查看特定服务日志
.\logs.ps1 -Service mysql

# 实时跟踪特定服务日志
.\logs.ps1 -Service parameter-optimization -Follow
```

**参数**：
- `-Service`: 指定服务名称（mysql, parameter-optimization）
- `-Follow`: 实时跟踪日志输出

### cleanup.ps1 - 清理脚本

**功能**：清理所有数据和服务

**使用方法**：
```powershell
.\cleanup.ps1
```

**警告**：
- 此操作将删除所有数据
- 需要输入 "YES" 确认
- 不可逆操作

**清理内容**：
- 停止所有服务
- 删除所有数据卷
- 清理未使用的镜像

### init-data.ps1 - 初始化数据脚本

**功能**：初始化测试数据

**使用方法**：
```powershell
.\init-data.ps1
```

**添加的数据**：
- 材料：45号钢 (P1)
  - 抗拉强度：600-750 MPa
  - 切削力系数：1800
- 刀具：硬质合金立铣刀
  - 直径：25mm
  - 齿数：2
  - 最大线速度：150 m/min
- 设备：XK7132铣床
  - 最大功率：7.5 Kw
  - 最大转速：3000 r/min
- 策略：粗铣策略
  - 最小表面粗糙度：12.5 um

## 常见使用场景

### 场景1：首次部署

```powershell
# 1. 部署服务
.\deploy.ps1

# 2. 初始化数据
.\init-data.ps1

# 3. 启动前端
cd frontend
npm install
npm run dev
```

### 场景2：服务异常重启

```powershell
# 1. 查看服务状态
.\status.ps1

# 2. 查看日志排查问题
.\logs.ps1 -Follow

# 3. 重启服务
docker-compose restart

# 或停止后重新部署
.\stop.ps1
.\deploy.ps1
```

### 场景3：完全重置系统

```powershell
# 1. 停止服务
.\stop.ps1

# 2. 清理所有数据
.\cleanup.ps1

# 3. 重新部署
.\deploy.ps1

# 4. 初始化数据
.\init-data.ps1
```

### 场景4：查看服务日志

```powershell
# 查看所有服务日志
.\logs.ps1

# 实时跟踪后端服务日志
.\logs.ps1 -Service parameter-optimization -Follow

# 查看MySQL日志
.\logs.ps1 -Service mysql
```

## 故障排查

### 问题1：Docker未安装

**症状**：执行脚本时提示"Docker未安装"

**解决方案**：
1. 下载并安装 Docker Desktop
2. 启动 Docker Desktop
3. 重新运行脚本

### 问题2：端口被占用

**症状**：脚本提示端口3307或5007已被占用

**解决方案**：
```powershell
# 查看端口占用
netstat -ano | findstr :3307
netstat -ano | findstr :5007

# 终止占用端口的进程
taskkill /PID <进程ID> /F

# 或修改docker-compose.yml中的端口映射
```

### 问题3：MySQL启动失败

**症状**：MySQL容器无法启动或健康检查失败

**解决方案**：
```powershell
# 查看MySQL日志
.\logs.ps1 -Service mysql

# 检查数据卷是否损坏
docker volume ls

# 重新创建数据卷
.\cleanup.ps1
.\deploy.ps1
```

### 问题4：后端服务无法连接

**症状**：无法访问 http://localhost:5007

**解决方案**：
```powershell
# 检查服务状态
.\status.ps1

# 查看后端日志
.\logs.ps1 -Service parameter-optimization -Follow

# 检查数据库连接
docker exec -it process_digital_twin_mysql mysql -u root -p123456
```

## 高级配置

### 修改环境变量

编辑 `.env` 文件：

```bash
# 数据库配置
DB_HOST=localhost
DB_PORT=3307
DB_USER=root
DB_PASSWORD=123456
DB_NAME=ga_tools

# 算法配置
ALGO_POPULATION_SIZE=1024
ALGO_GENERATIONS=50
ALGO_CROSSOVER_RATE=0.6
ALGO_MUTATION_RATE=0.3

# API配置
API_HOST=0.0.0.0
API_PORT=5007

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
```

修改后重启服务：
```powershell
.\stop.ps1
.\deploy.ps1
```

### 修改端口映射

编辑 `docker-compose.yml`：

```yaml
services:
  mysql:
    ports:
      - "3308:3306"  # 修改MySQL端口为3308

  parameter-optimization:
    ports:
      - "5008:8000"  # 修改API端口为5008
```

修改后重启服务：
```powershell
.\stop.ps1
.\deploy.ps1
```

## 注意事项

1. **权限要求**：所有脚本需要以管理员身份运行PowerShell
2. **防火墙设置**：确保防火墙允许Docker和端口访问
3. **数据备份**：定期备份重要数据
4. **生产环境**：修改默认密码和密钥
5. **资源监控**：监控CPU、内存和磁盘使用情况

## 获取帮助

如有问题，请查看：
- 项目文档：AGENTS.md
- 快速启动：QUICKSTART.md
- API文档：http://localhost:5007/docs
- 前端文档：frontend/README.md