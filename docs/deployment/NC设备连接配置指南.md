# NC设备连接配置指南

## 目录

1. [概述](#概述)
2. [系统架构](#系统架构)
3. [支持的NC控制器](#支持的nc控制器)
4. [OPC UA服务器配置](#opc-ua服务器配置)
5. [设备节点配置](#设备节点配置)
6. [环境变量配置](#环境变量配置)
7. [真实设备连接步骤](#真实设备连接步骤)
8. [故障排除](#故障排除)
9. [配置示例](#配置示例)

---

## 概述

本指南详细说明如何将工艺数字孪生系统连接到真实的数控（NC）设备，替代当前的模拟数据。系统采用 **OPC UA** 协议作为标准工业通信协议，支持主流数控控制器的实时数据采集。

### 核心功能

- ✅ 实时数据采集（坐标、转速、进给率、负载等）
- ✅ 设备状态监控（运行、空闲、报警、维护、离线）
- ✅ 报警信息实时推送
- ✅ 历史数据存储（InfluxDB时序数据库）
- ✅ WebSocket实时数据推送
- ✅ 支持多设备并发监控

---

## 系统架构

```
┌─────────────────┐         OPC UA          ┌─────────────────┐
│  NC设备控制器    │ ◄────────────────────► │  OPC UA 服务器   │
│ (FANUC/SIEMENS) │  opc.tcp://host:4840   │  (Edge/Server)   │
└─────────────────┘                         └────────┬────────┘
                                                     │
                                                     │ AsyncUA
                                                     ▼
┌─────────────────┐                          ┌─────────────────┐
│  工艺数字孪生    │  ◄───────────────────► │ 设备监控微服务   │
│   Web前端       │   WebSocket (ws://)    │  (device-monitor)│
└─────────────────┘                          └────────┬────────┘
                                                     │
                              ┌──────────────────────┼──────────────────────┐
                              │                      │                      │
                              ▼                      ▼                      ▼
                    ┌───────────────┐      ┌───────────────┐      ┌───────────────┐
                    │   MySQL数据库  │      │ InfluxDB时序库 │      │   Redis缓存   │
                    │  (设备状态)    │      │  (历史数据)    │      │  (实时状态)   │
                    └───────────────┘      └───────────────┘      └───────────────┘
```

### 数据流

1. **数据采集**：OPC UA采集器从NC控制器获取实时数据（每秒1次，可配置）
2. **数据存储**：实时数据存入InfluxDB（历史数据）和Redis（实时缓存）
3. **数据推送**：通过WebSocket推送到前端，实现实时监控界面
4. **报警处理**：报警信息同步到报警管理服务和MySQL数据库

---

## 支持的NC控制器

### 1. FANUC系列

**支持的型号**：Series 0i-MD、Series 0i-TD、Series 30i/31i/32i、Series 35i

**OPC UA连接方式**：
- **直接连接**：FANUC i Series内置OPC UA服务器（需配置）
- **网关连接**：通过OPC UA网关（如Mitsubishi、Siemens网关）

**FANUC Focas Library**：
```python
# 示例：FANUC OPC UA节点配置
fanuc_node_mapping = {
    "status": "ns=2;s=Channel1.Stat.Mode",
    "x_position": "ns=2;s=AxisX.Act.Position",
    "y_position": "ns=2;s=AxisY.Act.Position",
    "z_position": "ns=2;s=AxisZ.Act.Position",
    "spindle_speed": "ns=2;s=Spindle.Act.Speed",
    "feed_rate": "ns=2;s=Channel1.Stat.Feed",
    "load": "ns=2;s=Spindle.Act.Load",
    "alarm_code": "ns=2;s=Alarm.Code",
    "alarm_message": "ns=2;s=Alarm.Message",
}
```

### 2. SIEMENS系列

**支持的型号**：SINUMERIK 828D、840D sl、840D、ONE

**OPC UA连接方式**：
- **SINUMERIK OPC UA Server**：SIEMENS官方OPC UA服务器
- **S7-1200/1500 PLC**：通过PLC作为OPC UA服务器

**SIEMENS OPC UA节点**：
```python
siemens_node_mapping = {
    "status": "ns=2;s=PLC.Blocks.DB10.OperatingState",
    "x_position": "ns=2;s=PLC.Blocks.DB10.AxisX.ActPos",
    "y_position": "ns=2;s=PLC.Blocks.DB10.AxisY.ActPos",
    "z_position": "ns=2;s=PLC.Blocks.DB10.AxisZ.ActPos",
    "spindle_speed": "ns=2;s=PLC.Blocks.DB10.Spindle.ActSpeed",
    "feed_rate": "ns=2;s=PLC.Blocks.DB10.Channel.ActFeed",
    "load": "ns=2;s=PLC.Blocks.DB10.Spindle.ActLoad",
    "alarm_code": "ns=2;s=PLC.Blocks.DB10.Alarm.Code",
    "alarm_message": "ns=2;s=PLC.Blocks.DB10.Alarm.Message",
}
```

### 3. HEIDENHAIN系列

**支持的型号**：TNC 640、TNC 620、iTNC 530、TNC 128

**OPC UA连接方式**：
- **Heidenhain OPC UA Server**：需要额外配置
- **DNC通讯**：通过DNC服务器转换为OPC UA

**HEIDENHAIN OPC UA节点**：
```python
heid enhain_node_mapping = {
    "status": "ns=2;s=Machine.Status",
    "x_position": "ns=2;s=AxisX.ActPosition",
    "y_position": "ns=2;s=AxisY.ActPosition",
    "z_position": "ns=2;s=AxisZ.ActPosition",
    "spindle_speed": "ns=2;s=Spindle.ActSpeed",
    "feed_rate": "ns=2;s=Path.ActFeed",
    "load": "ns=2;s=Spindle.ActLoad",
    "alarm_code": "ns=2;s=Alarm.Number",
    "alarm_message": "ns=2;s=Alarm.Text",
}
```

### 4. MITSUBISHI系列

**支持的型号**：M80/M800系列、E70/E80系列

**OPC UA连接方式**：
- **Mitsubishi OPC UA Server**：通过MELSOFT OPC UA Server
- **GX Works3**：配置PLC的OPC UA服务器

### 5. 其他品牌

- **MAZAK**：通过Mazak OPC UA网关
- **HAAS**：通过Haas NGC OPC UA接口
- **Brother**：通过Brother OPC UA网关
- **Okuma**：通过Okuma OSP-P300A OPC UA

---

## OPC UA服务器配置

### 方案一：NC控制器内置OPC UA服务器

#### FANUC配置

1. **启用OPC UA服务器**：
   - 进入系统设置 → 网络设置 → OPC UA
   - 启用OPC UA服务器功能
   - 设置端口（默认4840）

2. **配置节点**：
   - 使用FANUC OPC UA浏览器查看可用节点
   - 记录节点ID用于配置

#### SIEMENS配置

1. **安装SINUMERIK OPC UA Server**：
   ```bash
   # 在TIA Portal中配置
   # 1. 添加OPC UA服务器
   # 2. 配置访问权限
   # 3. 导出变量到OPC UA
   ```

2. **配置安全策略**：
   - 策略：None, Basic128Rsa15, Basic256
   - 加密：None, Sign, Sign&Encrypt

### 方案二：OPC UA网关/Edge网关

#### KEPServerEX配置

1. **安装KEPServerEX**：
   ```bash
   # 下载并安装KEPServerEX
   # 激活OPC UA驱动
   ```

2. **创建通道**：
   - 新建通道：选择NC控制器驱动（如FANUC Focas）
   - 配置设备：IP地址、端口、超时

3. **添加标签**：
   - 配置要采集的数据点
   - 设置采样间隔

4. **启用OPC UA**：
   - 右键工程 → 启用OPC UA
   - 设置端口（默认49380）

#### UAGateway配置

1. **安装UAGateway**：
   - 下载UAGateway（免费版支持3个连接）
   - 解压并运行

2. **配置OPC UA**：
   ```xml
   <!-- config.xml -->
   <UAGateway>
     <OPCUA>
       <Port>4840</Port>
       <Security>None</Security>
     </OPCUA>
   </UAGateway>
   ```

### 方案三：开源OPC UA服务器

#### Node-RED OPC UA

1. **安装Node-RED**：
   ```bash
   npm install -g node-red
   node-red
   ```

2. **安装OPC UA节点**：
   ```bash
   cd ~/.node-red
   npm install node-red-contrib-opcua
   ```

3. **配置流程**：
   - 添加`opc ua server`节点
   - 添加变量（变量地址、数据类型）
   - 部署流程

#### Python OPC UA服务器

```python
# opcua_server.py
from asyncua import Server, ua

async def main():
    server = Server()
    await server.init()
    
    # 配置服务器
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("NC Device OPC UA Server")
    
    # 设置命名空间
    uri = "http://examples.digitaltwin.org/ua/server/"
    idx = await server.register_namespace(uri)
    
    # 创建对象
    objects = server.get_objects_node()
    device = await objects.add_object(idx, "Device")
    
    # 添加变量
    await device.add_variable(idx, "Status", 2)
    await device.add_variable(idx, "X_Position", 100.5)
    await device.add_variable(idx, "Y_Position", 50.3)
    await device.add_variable(idx, "Z_Position", 25.1)
    await device.add_variable(idx, "Spindle_Speed", 3200)
    await device.add_variable(idx, "Feed_Rate", 640)
    await device.add_variable(idx, "Load", 45.2)
    
    # 启动服务器
    async with server:
        print(f"OPC UA Server started at {server.endpoint}")
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 设备节点配置

### 节点映射配置

在 `services/device-monitor/src/config/constants.py` 中配置节点映射：

```python
# OPC UA 节点配置
OPCUA_NODE_MAPPING = {
    # FANUC设备示例
    1: {
        "device_name": "FANUC_5AX_VM",
        "controller_type": "FANUC",
        "status": "ns=2;s=Channel1.Stat.Mode",
        "x_position": "ns=2;s=AxisX.Act.Position",
        "y_position": "ns=2;s=AxisY.Act.Position",
        "z_position": "ns=2;s=AxisZ.Act.Position",
        "spindle_speed": "ns=2;s=Spindle.Act.Speed",
        "feed_rate": "ns=2;s=Channel1.Stat.Feed",
        "load": "ns=2;s=Spindle.Act.Load",
        "alarm_code": "ns=2;s=Alarm.Code",
        "alarm_message": "ns=2;s=Alarm.Message",
    },
    
    # SIEMENS设备示例
    2: {
        "device_name": "SIEMENS_840D",
        "controller_type": "SIEMENS",
        "status": "ns=2;s=PLC.Blocks.DB10.OperatingState",
        "x_position": "ns=2;s=PLC.Blocks.DB10.AxisX.ActPos",
        "y_position": "ns=2;s=PLC.Blocks.DB10.AxisY.ActPos",
        "z_position": "ns=2;s=PLC.Blocks.DB10.AxisZ.ActPos",
        "spindle_speed": "ns=2;s=PLC.Blocks.DB10.Spindle.ActSpeed",
        "feed_rate": "ns=2;s=PLC.Blocks.DB10.Channel.ActFeed",
        "load": "ns=2;s=PLC.Blocks.DB10.Spindle.ActLoad",
        "alarm_code": "ns=2;s=PLC.Blocks.DB10.Alarm.Code",
        "alarm_message": "ns=2;s=PLC.Blocks.DB10.Alarm.Message",
    },
    
    # HEIDENHAIN设备示例
    3: {
        "device_name": "HEIDENHAIN_TNC640",
        "controller_type": "HEIDENHAIN",
        "status": "ns=2;s=Machine.Status",
        "x_position": "ns=2;s=AxisX.ActPosition",
        "y_position": "ns=2;s=AxisY.ActPosition",
        "z_position": "ns=2;s=AxisZ.ActPosition",
        "spindle_speed": "ns=2;s=Spindle.ActSpeed",
        "feed_rate": "ns=2;s=Path.ActFeed",
        "load": "ns=2;s=Spindle.ActLoad",
        "alarm_code": "ns=2;s=Alarm.Number",
        "alarm_message": "ns=2;s=Alarm.Text",
    },
}
```

### 状态码映射

设备状态码与系统状态枚举的映射关系：

```python
# FANUC状态码
FANUC_STATUS_MAP = {
    0: DeviceStatusEnum.OFFLINE,    # 未连接
    1: DeviceStatusEnum.IDLE,       # 空闲（手动模式）
    2: DeviceStatusEnum.RUNNING,    # 运行（自动模式）
    3: DeviceStatusEnum.ALARM,      # 报警
    4: DeviceStatusEnum.MAINTENANCE, # 维护
}

# SIEMENS状态码
SIEMENS_STATUS_MAP = {
    0: DeviceStatusEnum.OFFLINE,
    1: DeviceStatusEnum.IDLE,
    2: DeviceStatusEnum.RUNNING,
    3: DeviceStatusEnum.ALARM,
    4: DeviceStatusEnum.MAINTENANCE,
}
```

---

## 环境变量配置

### `.env`文件配置

在项目根目录创建或编辑 `.env` 文件：

```bash
# ========== OPC UA配置 ==========
# OPC UA服务器地址（设备监控服务连接的OPC UA服务器）
OPCUA_SERVER_URL=opc.tcp://192.168.1.100:4840

# 采集间隔（秒）
OPCUA_POLLING_INTERVAL=1.0

# ========== 数据库配置 ==========
DB_HOST=mysql
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456
DB_NAME=ga_tools

# ========== InfluxDB时序数据库 ==========
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=my-super-secret-auth-token
INFLUXDB_ORG=digital_twin
INFLUXDB_BUCKET=device_data

# ========== Redis缓存 ==========
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ========== RabbitMQ消息队列 ==========
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=rabbitmq123
```

### Docker Compose环境变量

在 `docker-compose.yml` 中配置：

```yaml
services:
  device-monitor:
    environment:
      # OPC UA服务器地址
      OPCUA_SERVER_URL: ${OPCUA_SERVER_URL:-opc.tcp://localhost:4840}
      OPCUA_POLLING_INTERVAL: ${OPCUA_POLLING_INTERVAL:-1.0}
      
      # 数据库连接
      DB_HOST: mysql
      DB_PORT: 3306
      DB_USER: root
      DB_PASSWORD: ${DB_PASSWORD:-123456}
      DB_NAME: ga_tools
      
      # InfluxDB连接
      INFLUXDB_URL: http://influxdb:8086
      INFLUXDB_TOKEN: ${INFLUXDB_TOKEN:-my-super-secret-auth-token}
      INFLUXDB_ORG: digital_twin
      INFLUXDB_BUCKET: device_data
      
      # Redis连接
      REDIS_HOST: redis
      REDIS_PORT: 6379
      
      # RabbitMQ连接
      RABBITMQ_HOST: rabbitmq
      RABBITMQ_PORT: 5672
      RABBITMQ_USER: ${RABBITMQ_USER:-admin}
      RABBITMQ_PASSWORD: ${RABBITMQ_PASSWORD:-rabbitmq123}
```

---

## 真实设备连接步骤

### 步骤1：准备工作

1. **确认网络连接**：
   ```bash
   # 测试设备IP连通性
   ping 192.168.1.100
   
   # 测试OPC UA端口
   telnet 192.168.1.100 4840
   ```

2. **获取设备信息**：
   - 设备IP地址
   - OPC UA服务器端口（默认4840）
   - 设备ID/节点名称
   - 安全策略（如None、Basic256）

3. **查看OPC UA节点**：
   - 使用UaExpert（免费OPC UA客户端）
   - 或使用Node-RED OPC UA浏览器
   - 或使用Python脚本：
     ```python
     from asyncua import Client
     
     async def browse_nodes():
         url = "opc.tcp://192.168.1.100:4840"
         async with Client(url=url) as client:
             root = client.get_root_node()
             children = await root.get_children()
             for child in children:
                 print(await child.read_browse_name())
     
     asyncio.run(browse_nodes())
     ```

### 步骤2：配置设备节点映射

编辑 `services/device-monitor/src/config/constants.py`：

```python
OPCUA_NODE_MAPPING = {
    1: {
        "device_name": "我的FANUC机床",
        "controller_type": "FANUC",
        "server_url": "opc.tcp://192.168.1.100:4840",
        "status": "ns=2;s=Channel1.Stat.Mode",
        "x_position": "ns=2;s=AxisX.Act.Position",
        "y_position": "ns=2;s=AxisY.Act.Position",
        "z_position": "ns=2;s=AxisZ.Act.Position",
        "spindle_speed": "ns=2;s=Spindle.Act.Speed",
        "feed_rate": "ns=2;s=Channel1.Stat.Feed",
        "load": "ns=2;s=Spindle.Act.Load",
        "alarm_code": "ns=2;s=Alarm.Code",
        "alarm_message": "ns=2;s=Alarm.Message",
    },
}
```

### 步骤3：更新数据库设备记录

在MySQL数据库中添加或更新设备记录：

```sql
-- 添加新设备
INSERT INTO `machines` (
    `id`, `name`, `type`, `manufacturer`, `model`, 
    `specifications`, `status`, `efficiency`
) VALUES (
    1, 
    'FANUC 5AX-VM', 
    '铣床', 
    'FANUC', 
    'Series 30i-MB', 
    '{"axes": 5, "max_speed": 12000, "max_feed": 15000}', 
    'RUNNING', 
    85.5
);

-- 更新设备OPC UA配置
UPDATE `machines` 
SET `specifications` = JSON_SET(
    `specifications`, 
    '$.opcua_url', 'opc.tcp://192.168.1.100:4840',
    '$.opcua_namespace', 2
)
WHERE `id` = 1;
```

### 步骤4：配置环境变量

创建 `.env` 文件：

```bash
OPCUA_SERVER_URL=opc.tcp://192.168.1.100:4840
OPCUA_POLLING_INTERVAL=1.0
```

### 步骤5：重启设备监控服务

```bash
# 停止服务
docker-compose stop device-monitor

# 重新构建（如需要）
docker-compose build device-monitor

# 启动服务
docker-compose up -d device-monitor

# 查看日志
docker-compose logs -f device-monitor
```

### 步骤6：启动设备监控

通过Web界面或API启动设备监控：

**Web界面**：
1. 访问 http://localhost:80
2. 进入设备监控页面
3. 点击"启动监控"按钮

**API调用**：
```bash
curl -X POST http://localhost:5008/api/v1/devices/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "opcua_url": "opc.tcp://192.168.1.100:4840"
  }'
```

**响应**：
```json
{
  "success": true,
  "message": "设备 1 监控已启动",
  "device_id": 1
}
```

### 步骤7：验证连接

1. **查看服务日志**：
   ```bash
   docker-compose logs device-monitor
   ```

2. **检查WebSocket连接**：
   ```bash
   # 使用wscat测试WebSocket连接
   wscat -c ws://localhost:5008/api/v1/ws/monitoring/1
   ```

3. **查看实时数据**：
   ```bash
   curl http://localhost:5008/api/v1/monitoring/1/realtime
   ```

4. **查看设备状态**：
   ```bash
   curl http://localhost:5008/api/v1/devices/1/status
   ```

---

## 故障排除

### 问题1：无法连接到OPC UA服务器

**症状**：
```
设备 1 OPC UA 连接失败: [Errno 111] Connection refused
```

**可能原因**：
1. OPC UA服务器未启动
2. 网络连接问题
3. 防火墙阻止连接
4. 端口号错误

**解决方案**：
```bash
# 1. 检查OPC UA服务器是否运行
ping 192.168.1.100
telnet 192.168.1.100 4840

# 2. 检查防火墙
# Windows
netsh advfirewall firewall add rule name="OPC UA" dir=in action=allow protocol=TCP localport=4840

# Linux
sudo ufw allow 4840/tcp

# 3. 检查OPC UA服务器配置
# 确认服务器监听地址为 0.0.0.0 而不是 127.0.0.1
```

### 问题2：节点ID错误

**症状**：
```
设备 1 采集失败: BadNodeIdUnknown
```

**可能原因**：
1. 节点ID拼写错误
2. 命名空间索引不正确
3. 节点不存在

**解决方案**：
```python
# 使用UaExpert查看正确的节点ID
# 或使用Python脚本浏览节点
from asyncua import Client

async def get_node_id():
    url = "opc.tcp://192.168.1.100:4840"
    async with Client(url=url) as client:
        # 测试节点
        node = client.get_node("ns=2;s=Channel1.Stat.Mode")
        value = await node.read_value()
        print(f"节点值: {value}")

asyncio.run(get_node_id())
```

### 问题3：数据类型不匹配

**症状**：
```
TypeError: 'NoneType' object is not subscriptable
```

**可能原因**：
1. 返回的数据类型与预期不符
2. 节点返回空值

**解决方案**：
```python
# 在opcua_collector.py中添加类型检查
async def _collect_data(self):
    try:
        # ... existing code ...
        
        # 添加类型转换和空值检查
        data = {}
        for key, node in self.nodes.items():
            value = await node.read_value()
            
            # 类型转换
            if value is not None:
                if isinstance(value, (int, float)):
                    data[key] = float(value)
                else:
                    data[key] = value
            else:
                data[key] = 0.0  # 默认值
        
        # ... rest of the code ...
```

### 问题4：WebSocket连接断开

**症状**：
```
WebSocket connection closed
```

**可能原因**：
1. 服务重启
2. 网络不稳定
3. 浏览器刷新

**解决方案**：
```typescript
// 在前端添加重连逻辑
const connectWebSocket = () => {
  if (wsRef.current) {
    wsRef.current.close()
  }

  wsRef.current = new WebSocket(`ws://localhost:5008/api/v1/ws/monitoring/${device_id}`)

  wsRef.current.onopen = () => {
    console.log('WebSocket connected')
    setWsConnected(true)
  }

  wsRef.current.onmessage = (event) => {
    const data = JSON.parse(event.data)
    setRealtimeData(data.data)
  }

  wsRef.current.onclose = () => {
    console.log('WebSocket disconnected, reconnecting...')
    setWsConnected(false)
    // 5秒后重连
    setTimeout(connectWebSocket, 5000)
  }

  wsRef.current.onerror = (error) => {
    console.error('WebSocket error:', error)
  }
}
```

### 问题5：InfluxDB写入失败

**症状**：
```
存储数据到 InfluxDB 失败: Unauthorized
```

**可能原因**：
1. Token错误
2. Bucket不存在
3. 权限不足

**解决方案**：
```bash
# 1. 检查InfluxDB配置
docker exec -it process_digital_twin_influxdb influx

# 2. 验证Token
auth
# 输入用户名和密码

# 3. 检查Bucket
use digital_twin
show buckets

# 4. 创建Bucket（如果不存在）
create bucket device_data
```

---

## 配置示例

### 示例1：单台FANUC设备

**环境变量**：
```bash
OPCUA_SERVER_URL=opc.tcp://192.168.1.100:4840
OPCUA_POLLING_INTERVAL=1.0
```

**节点映射**：
```python
OPCUA_NODE_MAPPING = {
    1: {
        "device_name": "FANUC_5AX_VM",
        "controller_type": "FANUC",
        "status": "ns=2;s=Channel1.Stat.Mode",
        "x_position": "ns=2;s=AxisX.Act.Position",
        "y_position": "ns=2;s=AxisY.Act.Position",
        "z_position": "ns=2;s=AxisZ.Act.Position",
        "spindle_speed": "ns=2;s=Spindle.Act.Speed",
        "feed_rate": "ns=2;s=Channel1.Stat.Feed",
        "load": "ns=2;s=Spindle.Act.Load",
        "alarm_code": "ns=2;s=Alarm.Code",
        "alarm_message": "ns=2;s=Alarm.Message",
    },
}
```

### 示例2：多台不同品牌设备

**环境变量**：
```bash
OPCUA_SERVER_URL=opc.tcp://192.168.1.200:4840
OPCUA_POLLING_INTERVAL=0.5
```

**节点映射**：
```python
OPCUA_NODE_MAPPING = {
    1: {
        "device_name": "FANUC_VM1",
        "controller_type": "FANUC",
        "server_url": "opc.tcp://192.168.1.100:4840",
        "status": "ns=2;s=Channel1.Stat.Mode",
        "x_position": "ns=2;s=AxisX.Act.Position",
        "y_position": "ns=2;s=AxisY.Act.Position",
        "z_position": "ns=2;s=AxisZ.Act.Position",
        "spindle_speed": "ns=2;s=Spindle.Act.Speed",
        "feed_rate": "ns=2;s=Channel1.Stat.Feed",
        "load": "ns=2;s=Spindle.Act.Load",
        "alarm_code": "ns=2;s=Alarm.Code",
        "alarm_message": "ns=2;s=Alarm.Message",
    },
    2: {
        "device_name": "SIEMENS_VM2",
        "controller_type": "SIEMENS",
        "server_url": "opc.tcp://192.168.1.101:4840",
        "status": "ns=2;s=PLC.Blocks.DB10.OperatingState",
        "x_position": "ns=2;s=PLC.Blocks.DB10.AxisX.ActPos",
        "y_position": "ns=2;s=PLC.Blocks.DB10.AxisY.ActPos",
        "z_position": "ns=2;s=PLC.Blocks.DB10.AxisZ.ActPos",
        "spindle_speed": "ns=2;s=PLC.Blocks.DB10.Spindle.ActSpeed",
        "feed_rate": "ns=2;s=PLC.Blocks.DB10.Channel.ActFeed",
        "load": "ns=2;s=PLC.Blocks.DB10.Spindle.ActLoad",
        "alarm_code": "ns=2;s=PLC.Blocks.DB10.Alarm.Code",
        "alarm_message": "ns=2;s=PLC.Blocks.DB10.Alarm.Message",
    },
    3: {
        "device_name": "HEIDENHAIN_VM3",
        "controller_type": "HEIDENHAIN",
        "server_url": "opc.tcp://192.168.1.102:4840",
        "status": "ns=2;s=Machine.Status",
        "x_position": "ns=2;s=AxisX.ActPosition",
        "y_position": "ns=2;s=AxisY.ActPosition",
        "z_position": "ns=2;s=AxisZ.ActPosition",
        "spindle_speed": "ns=2;s=Spindle.ActSpeed",
        "feed_rate": "ns=2;s=Path.ActFeed",
        "load": "ns=2;s=Spindle.ActLoad",
        "alarm_code": "ns=2;s=Alarm.Number",
        "alarm_message": "ns=2;s=Alarm.Text",
    },
}
```

### 示例3：通过OPC UA网关连接

**环境变量**：
```bash
OPCUA_SERVER_URL=opc.tcp://192.168.1.200:49380
OPCUA_POLLING_INTERVAL=1.0
```

**节点映射**（KEPServerEX）：
```python
OPCUA_NODE_MAPPING = {
    1: {
        "device_name": "FANUC_Via_KEPServer",
        "controller_type": "FANUC",
        "status": "ns=2;s=Channel1.Device1.Tag_Status",
        "x_position": "ns=2;s=Channel1.Device1.Tag_X",
        "y_position": "ns=2;s=Channel1.Device1.Tag_Y",
        "z_position": "ns=2;s=Channel1.Device1.Tag_Z",
        "spindle_speed": "ns=2;s=Channel1.Device1.Tag_SpindleSpeed",
        "feed_rate": "ns=2;s=Channel1.Device1.Tag_FeedRate",
        "load": "ns=2;s=Channel1.Device1.Tag_Load",
        "alarm_code": "ns=2;s=Channel1.Device1.Tag_AlarmCode",
        "alarm_message": "ns=2;s=Channel1.Device1.Tag_AlarmMessage",
    },
}
```

---

## 附录

### A. OPC UA工具推荐

| 工具名称 | 类型 | 用途 | 下载地址 |
|---------|------|------|---------|
| UaExpert | 客户端 | 浏览OPC UA节点 | https://www.unified-automation.com/products/development-tools/uaexpert.html |
| Node-RED | 开发工具 | 可视化配置 | https://nodered.org |
| KEPServerEX | 网关 | OPC DA到OPC UA转换 | https://www kepware.com |
| UAGateway | 网关 | 免费OPC UA网关 | https://www.uaexpert.com |

### B. 数据类型对照表

| NC控制器类型 | 状态值类型 | 位置类型 | 速度类型 |
|------------|-----------|---------|---------|
| FANUC | Int (0-4) | Float | Float |
| SIEMENS | Int (0-4) | Double | Double |
| HEIDENHAIN | Int (0-4) | Float | Float |
| MITSUBISHI | Int (0-4) | Float | Float |

### C. 安全策略配置

| 安全策略 | 描述 | 适用场景 |
|---------|------|---------|
| None | 无加密 | 内网、测试环境 |
| Basic128Rsa15 | 基本加密 | 生产环境 |
| Basic256 | 高级加密 | 高安全性要求 |

### D. 端口使用说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 4840 | OPC UA Server | 默认OPC UA端口 |
| 49380 | KEPServerEx | KEPServer OPC UA端口 |
| 5008 | device-monitor | 设备监控API |
| 5009 | alarm-management | 报警管理API |
| 5010 | quality-trace | 质量追溯API |

---

## 联系支持

如遇到连接问题，请：

1. 检查本文档的故障排除部分
2. 查看服务日志：`docker-compose logs device-monitor`
3. 提交Issue到项目仓库

---

**文档版本**：v1.0  
**最后更新**：2026-02-06  
**维护者**：工艺数字孪生项目团队