"""
OPC UA连接测试脚本
用于验证OPC UA服务器连接和节点读取
"""
import asyncio
from asyncua import Client, ua
from typing import Dict, Any


class OPCUATester:
    """OPC UA连接测试器"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.client: Client = None
    
    async def test_connection(self) -> bool:
        """测试连接"""
        try:
            print(f"正在连接到: {self.server_url}")
            self.client = Client(url=self.server_url, timeout=10)
            await self.client.connect()
            print("✅ OPC UA连接成功")
            return True
        except Exception as e:
            print(f"❌ OPC UA连接失败: {e}")
            return False
    
    async def test_node_read(self, node_id: str) -> Any:
        """测试节点读取"""
        try:
            if not self.client:
                print("❌ 未连接到OPC UA服务器")
                return None
            
            print(f"正在读取节点: {node_id}")
            node = self.client.get_node(node_id)
            value = await node.read_value()
            print(f"✅ 节点值: {value}")
            return value
        except Exception as e:
            print(f"❌ 读取节点失败: {e}")
            return None
    
    async def test_node_write(self, node_id: str, value: Any) -> bool:
        """测试节点写入"""
        try:
            if not self.client:
                print("❌ 未连接到OPC UA服务器")
                return False
            
            print(f"正在写入节点: {node_id}, 值: {value}")
            node = self.client.get_node(node_id)
            await node.write_value(value)
            print("✅ 节点写入成功")
            return True
        except Exception as e:
            print(f"❌ 写入节点失败: {e}")
            return False
    
    async def browse_nodes(self, node_id: str = None, max_depth: int = 3):
        """浏览节点树"""
        try:
            if not self.client:
                print("❌ 未连接到OPC UA服务器")
                return
            
            if node_id:
                node = self.client.get_node(node_id)
            else:
                node = self.client.get_root_node()
            
            print(f"\n正在浏览节点: {node_id or 'Root'}")
            await self._browse_recursive(node, 0, max_depth)
        except Exception as e:
            print(f"❌ 浏览节点失败: {e}")
    
    async def _browse_recursive(self, node, depth: int, max_depth: int):
        """递归浏览节点"""
        if depth >= max_depth:
            return
        
        try:
            name = await node.read_browse_name()
            node_id = node.nodeid
            
            indent = "  " * depth
            print(f"{indent}+ {name.Name} [{node_id}]")
            
            children = await node.get_children()
            for child in children:
                await self._browse_recursive(child, depth + 1, max_depth)
        except Exception as e:
            print(f"  {'  ' * depth}! 错误: {e}")
    
    async def test_device_mapping(self, device_mapping: Dict[str, str]):
        """测试设备节点映射"""
        print("\n=== 测试设备节点映射 ===")
        
        if not self.client:
            print("❌ 未连接到OPC UA服务器")
            return
        
        results = {}
        for key, node_id in device_mapping.items():
            if key in ["device_name", "controller_type", "server_url", "description"]:
                continue
            
            value = await self.test_node_read(node_id)
            results[key] = value
        
        print("\n=== 测试结果汇总 ===")
        for key, value in results.items():
            status = "✅" if value is not None else "❌"
            print(f"{status} {key}: {value}")
        
        return results
    
    async def disconnect(self):
        """断开连接"""
        if self.client:
            await self.client.disconnect()
            print("已断开OPC UA连接")


async def test_fanuc_device():
    """测试FANUC设备"""
    print("\n" + "="*60)
    print("测试 FANUC 设备")
    print("="*60)
    
    tester = OPCUATester("opc.tcp://192.168.1.100:4840")
    
    try:
        if await tester.test_connection():
            # 测试节点映射
            fanuc_mapping = {
                "device_name": "FANUC_5AX_VM",
                "controller_type": "FANUC",
                "server_url": "opc.tcp://192.168.1.100:4840",
                "description": "FANUC Series 30i-MB 五轴加工中心",
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
            
            await tester.test_device_mapping(fanuc_mapping)
    finally:
        await tester.disconnect()


async def test_siemens_device():
    """测试SIEMENS设备"""
    print("\n" + "="*60)
    print("测试 SIEMENS 设备")
    print("="*60)
    
    tester = OPCUATester("opc.tcp://192.168.1.101:4840")
    
    try:
        if await tester.test_connection():
            siemens_mapping = {
                "device_name": "SIEMENS_840D",
                "controller_type": "SIEMENS",
                "server_url": "opc.tcp://192.168.1.101:4840",
                "description": "SIEMENS SINUMERIK 840D sl 五轴加工中心",
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
            
            await tester.test_device_mapping(siemens_mapping)
    finally:
        await tester.disconnect()


async def test_kepserver_gateway():
    """测试KEPServerEX网关"""
    print("\n" + "="*60)
    print("测试 KEPServerEX 网关")
    print("="*60)
    
    tester = OPCUATester("opc.tcp://192.168.1.200:49380")
    
    try:
        if await tester.test_connection():
            kepserver_mapping = {
                "device_name": "FANUC_Via_KEPServer",
                "controller_type": "FANUC",
                "server_url": "opc.tcp://192.168.1.200:49380",
                "description": "通过KEPServerEX网关连接的FANUC设备",
                "status": "ns=2;s=Channel1.Device1.Tag_Status",
                "x_position": "ns=2;s=Channel1.Device1.Tag_X",
                "y_position": "ns=2;s=Channel1.Device1.Tag_Y",
                "z_position": "ns=2;s=Channel1.Device1.Tag_Z",
                "spindle_speed": "ns=2;s=Channel1.Device1.Tag_SpindleSpeed",
                "feed_rate": "ns=2;s=Channel1.Device1.Tag_FeedRate",
                "load": "ns=2;s=Channel1.Device1.Tag_Load",
                "alarm_code": "ns=2;s=Channel1.Device1.Tag_AlarmCode",
                "alarm_message": "ns=2;s=Channel1.Device1.Tag_AlarmMessage",
            }
            
            await tester.test_device_mapping(kepserver_mapping)
    finally:
        await tester.disconnect()


async def test_custom_device(server_url: str, node_mapping: Dict[str, str]):
    """测试自定义设备"""
    print("\n" + "="*60)
    print(f"测试自定义设备: {server_url}")
    print("="*60)
    
    tester = OPCUATester(server_url)
    
    try:
        if await tester.test_connection():
            await tester.test_device_mapping(node_mapping)
    finally:
        await tester.disconnect()


async def browse_server(server_url: str, max_depth: int = 3):
    """浏览OPC UA服务器节点"""
    print("\n" + "="*60)
    print(f"浏览OPC UA服务器: {server_url}")
    print("="*60)
    
    tester = OPCUATester(server_url)
    
    try:
        if await tester.test_connection():
            await tester.browse_nodes(max_depth=max_depth)
    finally:
        await tester.disconnect()


async def main():
    """主函数"""
    import sys
    
    print("="*60)
    print("OPC UA 连接测试工具")
    print("="*60)
    print()
    print("使用方法:")
    print("  python test_opcua_connection.py fanuc          # 测试FANUC设备")
    print("  python test_opcua_connection.py siemens        # 测试SIEMENS设备")
    print("  python test_opcua_connection.py kepserver      # 测试KEPServerEX网关")
    print("  python test_opcua_connection.py browse <url>   # 浏览服务器节点")
    print("  python test_opcua_connection.py custom <url>   # 测试自定义设备")
    print()
    
    if len(sys.argv) < 2:
        print("❌ 请指定测试类型")
        return
    
    test_type = sys.argv[1].lower()
    
    if test_type == "fanuc":
        await test_fanuc_device()
    elif test_type == "siemens":
        await test_siemens_device()
    elif test_type == "kepserver":
        await test_kepserver_gateway()
    elif test_type == "browse" and len(sys.argv) >= 3:
        server_url = sys.argv[2]
        await browse_server(server_url)
    elif test_type == "custom" and len(sys.argv) >= 3:
        server_url = sys.argv[2]
        # 这里可以添加自定义节点映射
        await test_custom_device(server_url, {})
    else:
        print(f"❌ 未知的测试类型: {test_type}")


if __name__ == "__main__":
    asyncio.run(main())
