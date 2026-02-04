"""
OPC UA 数据采集器
用于从 OPC UA 服务器采集设备数据
"""
from typing import Dict, Optional, Callable
from datetime import datetime
import asyncio

from asyncua import Client, ua

from ..config.settings import settings
from ..config.constants import OPCUA_NODE_MAPPING, DeviceStatusEnum
from ..stores.influxdb_store import InfluxDBStore
from ..websocket.manager import ws_manager
from ..api.schemas.device import WSMessage


class OPCUACollector:
    """OPC UA 采集器"""
    
    def __init__(self, device_id: int, server_url: str):
        self.device_id = device_id
        self.server_url = server_url
        self.client: Optional[Client] = None
        self.nodes: Dict[str, ua.Node] = {}
        self.is_running = False
        self.collect_task: Optional[asyncio.Task] = None
        
        # 存储和 WebSocket
        self.store = InfluxDBStore()
    
    async def connect(self) -> bool:
        """连接 OPC UA 服务器"""
        try:
            self.client = Client(url=self.server_url)
            await self.client.connect()
            
            # 获取节点
            node_mapping = OPCUA_NODE_MAPPING.get(self.device_id, {})
            for key, node_id in node_mapping.items():
                self.nodes[key] = self.client.get_node(node_id)
            
            print(f"设备 {self.device_id} OPC UA 连接成功")
            return True
        except Exception as e:
            print(f"设备 {self.device_id} OPC UA 连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开 OPC UA 连接"""
        if self.client:
            await self.client.disconnect()
            self.client = None
        self.is_running = False
    
    async def start_collection(self, interval: float = None):
        """开始数据采集"""
        if self.is_running:
            print(f"设备 {self.device_id} 采集已在运行中")
            return
        
        self.is_running = True
        interval = interval or settings.opcua_polling_interval
        
        self.collect_task = asyncio.create_task(self._collect_loop(interval))
        print(f"设备 {self.device_id} 开始采集数据，间隔: {interval}秒")
    
    async def stop_collection(self):
        """停止数据采集"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.collect_task:
            self.collect_task.cancel()
            try:
                await self.collect_task
            except asyncio.CancelledError:
                pass
            self.collect_task = None
        
        print(f"设备 {self.device_id} 停止采集数据")
    
    async def _collect_loop(self, interval: float):
        """采集循环"""
        while self.is_running:
            try:
                await self._collect_data()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"设备 {self.device_id} 采集失败: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_data(self):
        """采集单次数据"""
        try:
            if not self.client or not self.nodes:
                return
            
            timestamp = datetime.now()
            data = {}
            
            # 读取所有节点值
            for key, node in self.nodes.items():
                value = await node.read_value()
                data[key] = value
            
            # 提取设备状态
            status = self._parse_status(data.get("status"))
            
            # 构建实时数据
            realtime_data = {
                "device_id": self.device_id,
                "status": status,
                "coordinates": {
                    "x": data.get("x_position"),
                    "y": data.get("y_position"),
                    "z": data.get("z_position"),
                },
                "parameters": {
                    "spindle_speed": data.get("spindle_speed"),
                    "feed_rate": data.get("feed_rate"),
                    "load": data.get("load"),
                },
                "alarm": {
                    "code": data.get("alarm_code"),
                    "message": data.get("alarm_message"),
                },
                "timestamp": timestamp,
            }
            
            # 存储到 InfluxDB
            await self._store_to_influxdb(data, timestamp)
            
            # 推送到 WebSocket
            await self._broadcast_to_websocket(realtime_data)
            
        except Exception as e:
            print(f"设备 {self.device_id} 采集数据失败: {e}")
    
    def _parse_status(self, status_value: any) -> str:
        """解析设备状态"""
        if status_value is None:
            return DeviceStatusEnum.OFFLINE
        
        # 根据实际 OPC UA 服务器返回的值进行映射
        if isinstance(status_value, int):
            status_map = {
                0: DeviceStatusEnum.OFFLINE,
                1: DeviceStatusEnum.IDLE,
                2: DeviceStatusEnum.RUNNING,
                3: DeviceStatusEnum.ALARM,
                4: DeviceStatusEnum.MAINTENANCE,
            }
            return status_map.get(status_value, DeviceStatusEnum.OFFLINE)
        
        return str(status_value)
    
    async def _store_to_influxdb(self, data: dict, timestamp: datetime):
        """存储数据到 InfluxDB"""
        try:
            # 写入设备传感器数据
            self.store.write_point(
                measurement="device_sensor_data",
                tags={"device_id": str(self.device_id)},
                fields={
                    "x_position": float(data.get("x_position", 0)) or 0,
                    "y_position": float(data.get("y_position", 0)) or 0,
                    "z_position": float(data.get("z_position", 0)) or 0,
                    "spindle_speed": float(data.get("spindle_speed", 0)) or 0,
                    "feed_rate": float(data.get("feed_rate", 0)) or 0,
                    "load": float(data.get("load", 0)) or 0,
                },
                timestamp=timestamp
            )
            
            # 如果有报警，写入报警数据
            if data.get("alarm_code"):
                self.store.write_point(
                    measurement="device_alarms",
                    tags={
                        "device_id": str(self.device_id),
                        "alarm_code": str(data.get("alarm_code")),
                    },
                    fields={
                        "alarm_message": str(data.get("alarm_message", "")),
                    },
                    timestamp=timestamp
                )
            
        except Exception as e:
            print(f"存储数据到 InfluxDB 失败: {e}")
    
    async def _broadcast_to_websocket(self, data: dict):
        """广播数据到 WebSocket"""
        try:
            message = WSMessage(
                type="device_status",
                device_id=self.device_id,
                data=data,
                timestamp=data["timestamp"]
            )
            await ws_manager.broadcast_to_device(self.device_id, message)
        except Exception as e:
            print(f"广播数据到 WebSocket 失败: {e}")


# 全局采集器管理
active_collectors: Dict[int, OPCUACollector] = {}


async def get_or_create_collector(
    device_id: int,
    server_url: str = None
) -> OPCUACollector:
    """获取或创建采集器"""
    if device_id in active_collectors:
        return active_collectors[device_id]
    
    server_url = server_url or settings.opcua_server_url
    collector = OPCUACollector(device_id, server_url)
    active_collectors[device_id] = collector
    return collector


async def remove_collector(device_id: int):
    """移除采集器"""
    if device_id in active_collectors:
        await active_collectors[device_id].disconnect()
        del active_collectors[device_id]