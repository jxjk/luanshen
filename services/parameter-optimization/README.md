# 参数优化服务

工艺数字孪生系统 - 参数优化微服务

## 功能特性

- 基于微生物遗传算法的智能参数优化
- 支持铣削、钻孔、镗孔、车削等多种加工方式
- RESTful API 接口
- 自动约束检查
- 多目标优化支持

## 快速开始

### 本地开发

1. 安装依赖：
```bash
cd services/parameter-optimization
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp ../../.env.example .env
# 编辑 .env 文件，配置数据库连接
```

3. 初始化数据库：
```bash
# 确保 MySQL 服务正在运行
# 执行初始化 SQL 脚本
mysql -u root -p < ../../00_刀具参数优化系统/ga_tools.sql
```

4. 启动服务：
```bash
python run.py
```

5. 访问 API 文档：
```
http://localhost:8000/docs
```

### Docker 部署

1. 使用 docker-compose 启动：
```bash
cd ..
docker-compose up -d
```

2. 查看日志：
```bash
docker-compose logs -f parameter-optimization
```

3. 停止服务：
```bash
docker-compose down
```

## API 使用示例

### 优化参数

```bash
curl -X POST "http://localhost:8000/api/v1/optimization/optimize" \
  -H "Content-Type: application/json" \
  -d '{
    "material_id": "P1",
    "tool_id": "1",
    "machine_id": "1",
    "strategy_id": "1"
  }'
```

### 获取材料列表

```bash
curl "http://localhost:8000/api/v1/materials/"
```

### 获取刀具信息

```bash
curl "http://localhost:8000/api/v1/tools/1"
```

## 项目结构

```
src/
├── api/              # API 层
│   ├── routes/       # 路由定义
│   └── schemas/      # 请求/响应模型
├── models/           # 数据模型
├── repositories/     # 数据访问层
├── algorithms/       # 算法模块
├── services/         # 业务逻辑层
├── config/           # 配置管理
└── main.py           # 应用入口
```

## 开发指南

### 添加新的加工方法

1. 在 `config/constants.py` 中添加新的加工方法枚举
2. 在 `algorithms/microbial_ga.py` 中实现相应的参数计算方法
3. 在数据库 `methods` 表中添加对应的策略记录

### 添加新的优化目标

1. 在 `algorithms/objectives.py` 中定义新的目标函数
2. 在 `MicrobialGeneticAlgorithm` 类中集成新目标

### 添加新的约束条件

1. 在 `algorithms/constraints.py` 中添加约束检查逻辑
2. 在 `OptimizationConstraints` 数据类中添加约束参数

## 测试

```bash
cd services/parameter-optimization
pytest tests/ -v --cov=src
```

## 配置说明

详见 `.env.example` 文件中的配置项说明。

## 技术栈

- FastAPI - Web 框架
- SQLAlchemy - ORM
- PyMySQL - MySQL 驱动
- NumPy - 数值计算
- Pydantic - 数据验证
- Uvicorn - ASGI 服务器

## 许可证

MIT License