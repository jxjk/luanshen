# 设备监控微服务

## 服务概述

设备监控微服务负责实时采集、存储和推送设备运行数据，支持 OPC UA、Modbus 等工业协议，为工艺数字孪生系统提供实时数据支撑。

## 核心功能

### 1. 实时数据采集
- 支持 OPC UA 协议采集
- 支持 Modbus 协议采集（待实现）
- 支持自定义传感器数据接入
- 高频数据采集（≥1kHz）

### 2. 设备状态管理
- 实时设备状态监控（运行/空闲/报警/维护）
- 设备坐标跟踪（X、Y、Z轴）
- 主轴转速、进给率监控
- 负载百分比监控

### 3. 时序数据存储
- 使用 InfluxDB 存储高频传感器数据
- 使用 MySQL 存储设备状态快照
- 支持历史数据查询和分析

### 4. 实时数据推送
- WebSocket 实时推送设备数据
- Redis 发布/订阅支持
- 消息队列异步处理

### 5. 报警检测
- 设备报警状态检测
- 阈值超限检测
- 自动触发报警服务

## 技术栈

- **Python 3.9+** - 主要开发语言
- **FastAPI** - 高性能 Web 框架
- **InfluxDB** - 时序数据库
- **MySQL** - 关系型数据库
- **Redis** - 缓存和消息订阅
- **RabbitMQ** - 消息队列
- **asyncua** - OPC UA 客户端
- **WebSocket** - 实时通信

## 项目结构

```
services/device-monitor/
├── src/
│   ├── main.py                 # FastAPI 应用入口
│   ├── config/
│   │   ├── settings.py         # Pydantic 配置
│   │   ├── database.py         # 数据库连接
│   │   └── constants.py        # 常量定义
│   ├── models/
│   │   ├── device_status.py    # 设备状态模型
│   │   └── sensor_data.py      # 传感器数据模型
│   ├── repositories/
│   │   ├── device_status_repository.py  # 设备状态仓储
│   │   └── sensor_data_repository.py    # 传感器数据仓储
│   ├── collectors/
│   │   ├── opcua_collector.py  # OPC UA 采集器
│   │   └── modbus_collector.py # Modbus 采集器（待实现）
│   ├── stores/
│   │   ├── influxdb_store.py   # InfluxDB 存储接口
│   │   └── redis_store.py      # Redis 存储接口
│   ├── websocket/
│   │   ├── manager.py          # WebSocket 连接管理器
│   │   └── broadcaster.py      # 数据广播器
│   ├── api/
│   │   └── routes/
│   │       ├── devices.py      # 设备管理路由
│   │       ├── monitoring.py   # 监控数据路由
│   │       └── ws.py           # WebSocket 路由
│   └── schemas/
│       ├── device.py           # 设备相关 Schema
│       └── monitoring.py       # 监控相关 Schema
├── tests/                      # 测试目录
├── requirements.txt            # Python 依赖
├── run.py                      # 服务启动脚本
├── .env.example                # 环境变量模板
└── README.md                   # 本文档
```

## 环境准备

### 1. 安装 Python 依赖

```bash
cd services/device-monitor
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件
# 配置数据库连接、InfluxDB、Redis、RabbitMQ 等参数
```

### 3. 初始化数据库

#### MySQL 数据库

```bash
# 执行数据库初始化脚本（在项目根目录）
mysql -u root -p < services/device-monitor/sql/init.sql
```

#### InfluxDB 数据库

```bash
# 创建 InfluxDB Bucket
# 使用 InfluxDB UI 或 CLI 创建名为 "device_data" 的 bucket
```

### 4. 启动依赖服务

使用 Docker Compose 启动所有依赖服务：

```bash
cd /path/to/工艺数字孪生
docker-compose up -d mysql influxdb redis rabbitmq
```

## 运行方式

### 方式一：直接运行

```bash
cd services/device-monitor
python run.py
```

### 方式二：使用 uvicorn

```bash
cd services/device-monitor
uvicorn src.main:app --host 0.0.0.0 --port 5008 --reload
```

### 方式三：Docker Compose

```bash
# 从项目根目录执行
docker-compose up -d device-monitor
```

## API 文档

服务启动后，访问以下地址查看 API 文档：

- Swagger UI: http://localhost:5008/docs
- ReDoc: http://localhost:5008/redoc
- OpenAPI Schema: http://localhost:5008/openapi.json

## 核心 API 端点

### 设备管理

- `GET /api/v1/devices` - 获取所有设备列表
- `GET /api/v1/devices/{device_id}` - 获取设备详情
- `POST /api/v1/devices/{device_id}/start` - 启动设备监控
- `POST /api/v1/devices/{device_id}/stop` - 停止设备监控
- `GET /api/v1/devices/{device_id}/status` - 获取设备当前状态

### 监控数据

- `GET /api/v1/monitoring/{device_id}/realtime` - 获取实时监控数据
- `GET /api/v1/monitoring/{device_id}/history` - 获取历史监控数据
- `GET /api/v1/monitoring/{device_id}/sensors` - 获取传感器数据列表

### WebSocket

- `WS /api/v1/ws/monitoring/{device_id}` - 订阅设备实时数据

## WebSocket 使用示例

### JavaScript 客户端

```javascript
const ws = new WebSocket('ws://localhost:5008/api/v1/ws/monitoring/1');

ws.onopen = () => {
  console.log('WebSocket 连接已建立');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到实时数据:', data);
  // 更新 UI
};

ws.onerror = (error) => {
  console.error('WebSocket 错误:', error);
};

ws.onclose = () => {
  console.log('WebSocket 连接已关闭');
};
```

### Python 客户端

```python
import asyncio
import websockets
import json

async def monitor_device(device_id: int):
    uri = f"ws://localhost:5008/api/v1/ws/monitoring/{device_id}"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            print(f"收到数据: {data}")

asyncio.run(monitor_device(1))
```

## 数据模型

### 设备状态（DeviceStatus）

```json
{
  "id": 1,
  "device_id": 1,
  "status": "RUNNING",
  "current_x": 100.500,
  "current_y": 50.250,
  "current_z": 25.000,
  "spindle_speed": 3000.0,
  "feed_rate": 500.0,
  "load_percent": 65.5,
  "alarm_code": null,
  "alarm_message": null,
  "recorded_at": "2026-02-02T10:30:00Z"
}
```

### 传感器数据（SensorData）

```json
{
  "device_id": 1,
  "sensor_type": "VIBRATION",
  "value": 0.5,
  "unit": "mm/s",
  "timestamp": "2026-02-02T10:30:00.123456Z"
}
```

## 配置说明

### OPC UA 配置

在 `.env` 文件中配置 OPC UA 服务器：

```bash
OPCUA_SERVER_URL=opc.tcp://your-opcua-server:4840
OPCUA_POLLING_INTERVAL=1.0
```

### 数据采集配置

在代码中配置采集节点：

```python
# src/collectors/opcua_collector.py
NODE_IDS = {
    "device_1": {
        "status": "ns=2;s=Machine1.Status",
        "x_position": "ns=2;s=Machine1.AxisX.Position",
        "y_position": "ns=2;s=Machine1.AxisY.Position",
        "z_position": "ns=2;s=Machine1.AxisZ.Position",
        "spindle_speed": "ns=2;s=Machine1.Spindle.Speed",
        "feed_rate": "ns=2;s=Machine1.Feed.Rate",
        "load": "ns=2;s=Machine1.Load.Percent",
    }
}
```

## 监控和日志

### 健康检查

```bash
curl http://localhost:5008/api/v1/health
```

### 日志查看

日志级别可在 `.env` 文件中配置：

```bash
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 测试

运行单元测试：

```bash
cd services/device-monitor
pytest tests/ -v --cov=src --cov-report=html
```

## 故障排查

### 问题：无法连接 OPC UA 服务器

**解决方案**：
1. 检查 OPC UA 服务器地址是否正确
2. 检查网络连接和防火墙设置
3. 检查 OPC UA 服务器是否支持匿名访问

### 问题：InfluxDB 连接失败

**解决方案**：
1. 检查 InfluxDB 服务是否运行
2. 验证 URL、Token、Org、Bucket 配置是否正确
3. 检查 InfluxDB 版本兼容性

### 问题：WebSocket 连接断开

**解决方案**：
1. 实现自动重连机制
2. 检查心跳间隔设置
3. 验证网络稳定性

## 性能优化

### 1. 使用批量写入

```python
# InfluxDB 批量写入
batch = influxdb_client.write_api().write_bulk()
```

### 2. 异步处理

```python
# 使用异步 IO 提高性能
import asyncio
async def collect_data():
    # 异步采集逻辑
    pass
```

### 3. 数据压缩

```python
# 使用 Gzip 压缩 WebSocket 数据
websocket.send(json.dumps(data), compression="gzip")
```

## 安全建议

1. **传输加密**：生产环境使用 HTTPS 和 WSS
2. **认证授权**：集成 JWT 认证
3. **数据加密**：敏感数据加密存储
4. **访问控制**：基于角色的访问控制（RBAC）
5. **日志审计**：记录所有关键操作

## 未来扩展

- [ ] 支持 Modbus TCP 协议
- [ ] 支持 MTConnect 协议
- [ ] 支持 MQTT 协议
- [ ] 实现边缘计算功能
- [ ] 支持设备预测性维护
- [ ] 实现设备数字孪生模型

## 相关文档

- [阶段一实施计划](../../../docs/architecture/阶段一实施计划.md)
- [API 文档](http://localhost:5008/docs)
- [需求规格说明书](../../../需求规格说明书.md)

## 联系方式

- 项目团队：工艺数字孪生项目团队
- 技术支持：tech-support@example.com

---

**文档版本**：v1.0  
**创建日期**：2026-02-02  
**最后更新**：2026-02-02