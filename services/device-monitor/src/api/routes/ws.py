"""
WebSocket API 路由
用于实时数据推送
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional

from ...websocket.manager import ws_manager

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/monitoring/{device_id}")
async def websocket_monitoring(
    websocket: WebSocket,
    device_id: int
):
    """
    WebSocket 实时监控端点
    
    连接后将持续接收设备的实时数据
    
    消息格式:
    ```json
    {
      "type": "device_status",
      "device_id": 1,
      "data": {
        "status": "RUNNING",
        "coordinates": { "x": 100.5, "y": 50.25, "z": 25.0 },
        "parameters": { "spindle_speed": 3000, "feed_rate": 500, "load": 65.5 },
        "alarm": { "code": null, "message": null },
        "timestamp": "2026-02-02T10:30:00"
      },
      "timestamp": "2026-02-02T10:30:00"
    }
    ```
    
    心跳消息:
    ```json
    {
      "type": "heartbeat",
      "device_id": 0,
      "data": { "message": "heartbeat" },
      "timestamp": "2026-02-02T10:30:00"
    }
    ```
    """
    await ws_manager.connect(websocket, device_id)
    
    try:
        # 连接成功后发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "device_id": device_id,
            "message": f"已连接到设备 {device_id} 的实时监控",
            "timestamp": ws_manager.get_total_connection_count()
        })
        
        # 保持连接，等待服务器推送数据
        while True:
            # 接收客户端消息（可用于控制命令）
            data = await websocket.receive_json()
            
            # 处理客户端消息
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "device_id": device_id,
                    "timestamp": data.get("timestamp")
                })
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket 错误: {e}")
        await ws_manager.disconnect(websocket)


@router.get("/stats")
async def get_websocket_stats():
    """
    获取 WebSocket 连接统计
    """
    return {
        "total_connections": ws_manager.get_total_connection_count(),
        "devices": [
            {
                "device_id": device_id,
                "connections": len(connections)
            }
            for device_id, connections in ws_manager.active_connections.items()
        ]
    }