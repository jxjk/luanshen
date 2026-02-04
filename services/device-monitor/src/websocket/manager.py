"""
WebSocket 连接管理器
管理所有设备的 WebSocket 连接
"""
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime
import json
import asyncio

from ..config.settings import settings
from ..api.schemas.device import WSMessage


class WebSocketManager:
    """WebSocket 连接管理器"""
    
    def __init__(self):
        # 设备ID -> WebSocket连接集合
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        # WebSocket连接 -> 设备ID集合（一个连接可能订阅多个设备）
        self.connection_subscriptions: Dict[WebSocket, Set[int]] = {}
        # 心跳任务
        self.heartbeat_tasks: Dict[WebSocket, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, device_id: int):
        """连接 WebSocket"""
        await websocket.accept()
        
        # 添加到设备连接集合
        if device_id not in self.active_connections:
            self.active_connections[device_id] = set()
        self.active_connections[device_id].add(websocket)
        
        # 添加到订阅集合
        if websocket not in self.connection_subscriptions:
            self.connection_subscriptions[websocket] = set()
        self.connection_subscriptions[websocket].add(device_id)
        
        # 启动心跳
        self.heartbeat_tasks[websocket] = asyncio.create_task(
            self._heartbeat(websocket)
        )
        
        print(f"WebSocket 连接已建立: 设备 {device_id}, 当前连接数: {len(self.active_connections[device_id])}")
    
    async def disconnect(self, websocket: WebSocket):
        """断开 WebSocket 连接"""
        # 停止心跳
        if websocket in self.heartbeat_tasks:
            self.heartbeat_tasks[websocket].cancel()
            del self.heartbeat_tasks[websocket]
        
        # 从所有设备连接集合中移除
        if websocket in self.connection_subscriptions:
            for device_id in self.connection_subscriptions[websocket]:
                if device_id in self.active_connections:
                    self.active_connections[device_id].discard(websocket)
                    if not self.active_connections[device_id]:
                        del self.active_connections[device_id]
            
            del self.connection_subscriptions[websocket]
        
        print(f"WebSocket 连接已断开")
    
    async def broadcast_to_device(self, device_id: int, message: WSMessage):
        """向指定设备的所有连接广播消息"""
        if device_id not in self.active_connections:
            return
        
        disconnected = set()
        message_str = message.model_dump_json()
        
        for connection in self.active_connections[device_id]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"发送消息失败: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def broadcast_to_all(self, message: WSMessage):
        """向所有连接广播消息"""
        disconnected = set()
        message_str = message.model_dump_json()
        
        for device_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_text(message_str)
                except Exception as e:
                    print(f"发送消息失败: {e}")
                    disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def _heartbeat(self, websocket: WebSocket):
        """心跳检测"""
        while True:
            try:
                await asyncio.sleep(settings.ws_heartbeat_interval)
                heartbeat_message = WSMessage(
                    type="heartbeat",
                    device_id=0,  # 心跳消息不需要设备ID
                    data={"message": "heartbeat"},
                    timestamp=datetime.now()
                )
                await websocket.send_text(heartbeat_message.model_dump_json())
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"心跳发送失败: {e}")
                break
    
    def get_connection_count(self, device_id: int) -> int:
        """获取指定设备的连接数"""
        return len(self.active_connections.get(device_id, set()))
    
    def get_total_connection_count(self) -> int:
        """获取总连接数"""
        return sum(len(connections) for connections in self.active_connections.values())


# 全局 WebSocket 管理器实例
ws_manager = WebSocketManager()