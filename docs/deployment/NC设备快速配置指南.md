# NC设备快速配置指南

> 5分钟快速连接真实NC设备到工艺数字孪生系统

---

## 前置条件

- ✅ NC设备已启用OPC UA服务器
- ✅ 设备IP地址和端口已知
- ✅ 网络连通性已验证
- ✅ 工艺数字孪生系统已部署

---

## 快速配置步骤

### 步骤1：获取设备信息（1分钟）

在NC设备控制器上获取以下信息：

```
设备IP：192.168.1.100
OPC UA端口：4840（默认）
控制器类型：FANUC
设备型号：Series 30i-MB
```

### 步骤2：测试网络连接（30秒）

```bash
# 测试网络连通性
ping 192.168.1.100

# 测试OPC UA端口
telnet 192.168.1.100 4840
```

### 步骤3：配置环境变量（1分钟）

编辑项目根目录的 `.env` 文件：

```bash
# 添加以下配置
OPCUA_SERVER_URL=opc.tcp://192.168.1.100:4840
OPCUA_POLLING_INTERVAL=1.0
```

### 步骤4：配置设备节点映射（2分钟）

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

### 步骤5：重启设备监控服务（30秒）

```bash
# 重启服务
docker-compose restart device-monitor

# 查看日志
docker-compose logs -f device-monitor
```

### 步骤6：启动设备监控（1分钟）

**方式1：Web界面**
1. 访问 http://localhost:80
2. 进入设备监控页面
3. 点击"启动监控"按钮

**方式2：API调用**
```bash
curl -X POST http://localhost:5008/api/v1/devices/1/start \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "opcua_url": "opc.tcp://192.168.1.100:4840"
  }'
```

### 步骤7：验证连接（1分钟）

```bash
# 查看实时数据
curl http://localhost:5008/api/v1/monitoring/1/realtime

# 查看设备状态
curl http://localhost:5008/api/v1/devices/1/status
```

---

## 常见NC控制器节点ID速查表

### FANUC

| 数据项 | 节点ID | 数据类型 |
|-------|--------|---------|
| 设备状态 | `ns=2;s=Channel1.Stat.Mode` | Int |
| X轴位置 | `ns=2;s=AxisX.Act.Position` | Float |
| Y轴位置 | `ns=2;s=AxisY.Act.Position` | Float |
| Z轴位置 | `ns=2;s=AxisZ.Act.Position` | Float |
| 主轴转速 | `ns=2;s=Spindle.Act.Speed` | Float |
| 进给率 | `ns=2;s=Channel1.Stat.Feed` | Float |
| 负载 | `ns=2;s=Spindle.Act.Load` | Float |
| 报警代码 | `ns=2;s=Alarm.Code` | String |
| 报警消息 | `ns=2;s=Alarm.Message` | String |

### SIEMENS

| 数据项 | 节点ID | 数据类型 |
|-------|--------|---------|
| 设备状态 | `ns=2;s=PLC.Blocks.DB10.OperatingState` | Int |
| X轴位置 | `ns=2;s=PLC.Blocks.DB10.AxisX.ActPos` | Double |
| Y轴位置 | `ns=2;s=PLC.Blocks.DB10.AxisY.ActPos` | Double |
| Z轴位置 | `ns=2;s=PLC.Blocks.DB10.AxisZ.ActPos` | Double |
| 主轴转速 | `ns=2;s=PLC.Blocks.DB10.Spindle.ActSpeed` | Double |
| 进给率 | `ns=2;s=PLC.Blocks.DB10.Channel.ActFeed` | Double |
| 负载 | `ns=2;s=PLC.Blocks.DB10.Spindle.ActLoad` | Double |
| 报警代码 | `ns=2;s=PLC.Blocks.DB10.Alarm.Code` | String |
| 报警消息 | `ns=2;s=PLC.Blocks.DB10.Alarm.Message` | String |

### HEIDENHAIN

| 数据项 | 节点ID | 数据类型 |
|-------|--------|---------|
| 设备状态 | `ns=2;s=Machine.Status` | Int |
| X轴位置 | `ns=2;s=AxisX.ActPosition` | Float |
| Y轴位置 | `ns=2;s=AxisY.ActPosition` | Float |
| Z轴位置 | `ns=2;s=AxisZ.ActPosition` | Float |
| 主轴转速 | `ns=2;s=Spindle.ActSpeed` | Float |
| 进给率 | `ns=2;s=Path.ActFeed` | Float |
| 负载 | `ns=2;s=Spindle.ActLoad` | Float |
| 报警代码 | `ns=2;s=Alarm.Number` | String |
| 报警消息 | `ns=2;s=Alarm.Text` | String |

---

## 快速故障排除

### 问题：无法连接到OPC UA服务器

**解决方案**：
```bash
# 1. 检查网络连通性
ping 192.168.1.100

# 2. 检查端口是否开放
telnet 192.168.1.100 4840

# 3. 检查防火墙
# Windows
netsh advfirewall firewall add rule name="OPC UA" dir=in action=allow protocol=TCP localport=4840

# Linux
sudo ufw allow 4840/tcp
```

### 问题：节点ID错误

**解决方案**：
```bash
# 使用测试脚本查看节点
cd services/device-monitor
python test_opcua_connection.py browse opc.tcp://192.168.1.100:4840
```

### 问题：设备状态显示为离线

**解决方案**：
```bash
# 检查服务日志
docker-compose logs device-monitor

# 重启监控
docker-compose restart device-monitor
```

---

## 使用测试工具验证连接

系统提供了OPC UA连接测试脚本：

```bash
cd services/device-monitor

# 测试FANUC设备
python test_opcua_connection.py fanuc

# 测试SIEMENS设备
python test_opcua_connection.py siemens

# 测试KEPServerEX网关
python test_opcua_connection.py kepserver

# 浏览服务器节点
python test_opcua_connection.py browse opc.tcp://192.168.1.100:4840
```

---

## 下一步

配置完成后：

1. ✅ 访问Web界面查看实时数据
2. ✅ 配置报警规则
3. ✅ 设置历史数据查询
4. ✅ 配置通知方式（邮件/短信）

详细配置请参考：[NC设备连接配置指南](./NC设备连接配置指南.md)

---

## 需要帮助？

- 📖 完整文档：[NC设备连接配置指南](./NC设备连接配置指南.md)
- 🔧 故障排除：查看服务日志 `docker-compose logs device-monitor`
- 💬 提交Issue：https://github.com/jxjk/luanshen/issues

---

**文档版本**：v1.0  
**最后更新**：2026-02-06  
**预计配置时间**：5分钟