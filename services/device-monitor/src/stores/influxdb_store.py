"""
InfluxDB 时序数据存储接口
"""
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, ASYNCHRONOUS
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ..config.database import get_influxdb_client
from ..config.settings import settings


class InfluxDBStore:
    """InfluxDB 存储类"""
    
    def __init__(self):
        self.client = get_influxdb_client()
        self.write_api = self.client.write_api(write_options=ASYNCHRONOUS)
        self.query_api = self.client.query_api()
        self.bucket = settings.influxdb_bucket
        self.org = settings.influxdb_org
    
    def write_point(
        self,
        measurement: str,
        tags: Dict[str, str],
        fields: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ) -> bool:
        """写入单个数据点"""
        try:
            point = Point(measurement)
            
            # 添加 tags
            for key, value in tags.items():
                point.tag(key, str(value))
            
            # 添加 fields
            for key, value in fields.items():
                point.field(key, value)
            
            # 设置时间戳
            if timestamp:
                point.time(timestamp)
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=point)
            return True
        except Exception as e:
            print(f"写入 InfluxDB 失败: {e}")
            return False
    
    def write_batch(
        self,
        measurement: str,
        points_data: List[Dict[str, Any]]
    ) -> bool:
        """批量写入数据点"""
        try:
            points = []
            for data in points_data:
                point = Point(measurement)
                
                # 添加 tags
                tags = data.get("tags", {})
                for key, value in tags.items():
                    point.tag(key, str(value))
                
                # 添加 fields
                fields = data.get("fields", {})
                for key, value in fields.items():
                    point.field(key, value)
                
                # 设置时间戳
                timestamp = data.get("timestamp")
                if timestamp:
                    point.time(timestamp)
                
                points.append(point)
            
            self.write_api.write(bucket=self.bucket, org=self.org, record=points)
            return True
        except Exception as e:
            print(f"批量写入 InfluxDB 失败: {e}")
            return False
    
    def query_data(
        self,
        measurement: str,
        time_range: tuple,
        filters: Optional[Dict[str, str]] = None,
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """查询数据"""
        try:
            start_time, end_time = time_range
            
            # 构建 Flux 查询
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
              |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            '''
            
            # 添加标签过滤
            if filters:
                for key, value in filters.items():
                    query += f'|> filter(fn: (r) => r["{key}"] == "{value}")\n'
            
            # 添加字段过滤
            if fields:
                fields_str = ', '.join([f'"{f}"' for f in fields])
                query += f'|> filter(fn: (r) => r["_field"] =~ /^({fields_str})$/)\n'
            
            # 添加限制
            if limit:
                query += f'|> limit(n: {limit})\n'
            
            # 执行查询
            result = self.query_api.query(org=self.org, query=query)
            
            # 解析结果
            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        "time": record.get_time(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        "measurement": record.get_measurement(),
                        **record.values
                    })
            
            return data
        except Exception as e:
            print(f"查询 InfluxDB 失败: {e}")
            return []
    
    def query_aggregated(
        self,
        measurement: str,
        time_range: tuple,
        window: str,
        filters: Optional[Dict[str, str]] = None,
        agg_func: str = "mean"
    ) -> List[Dict[str, Any]]:
        """查询聚合数据"""
        try:
            start_time, end_time = time_range
            
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: {start_time.isoformat()}, stop: {end_time.isoformat()})
              |> filter(fn: (r) => r["_measurement"] == "{measurement}")
            '''
            
            if filters:
                for key, value in filters.items():
                    query += f'|> filter(fn: (r) => r["{key}"] == "{value}")\n'
            
            query += f'|> aggregateWindow(every: {window}, fn: {agg_func})\n'
            
            result = self.query_api.query(org=self.org, query=query)
            
            data = []
            for table in result:
                for record in table.records:
                    data.append({
                        "time": record.get_time(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        **record.values
                    })
            
            return data
        except Exception as e:
            print(f"查询聚合数据失败: {e}")
            return []
    
    def get_latest_value(
        self,
        measurement: str,
        field: str,
        filters: Dict[str, str]
    ) -> Optional[Dict[str, Any]]:
        """获取最新值"""
        try:
            query = f'''
            from(bucket: "{self.bucket}")
              |> range(start: -1h)
              |> filter(fn: (r) => r["_measurement"] == "{measurement}")
              |> filter(fn: (r) => r["_field"] == "{field}")
            '''
            
            for key, value in filters.items():
                query += f'|> filter(fn: (r) => r["{key}"] == "{value}")\n'
            
            query += '|> last()\n'
            
            result = self.query_api.query(org=self.org, query=query)
            
            for table in result:
                for record in table.records:
                    return {
                        "time": record.get_time(),
                        "field": record.get_field(),
                        "value": record.get_value(),
                        **record.values
                    }
            
            return None
        except Exception as e:
            print(f"获取最新值失败: {e}")
            return None
    
    def delete_data(
        self,
        measurement: str,
        time_range: tuple,
        filters: Optional[Dict[str, str]] = None
    ) -> bool:
        """删除数据（慎用）"""
        try:
            start_time, end_time = time_range
            
            # 构建删除 predicate
            predicate = f'_measurement="{measurement}"'
            if filters:
                for key, value in filters.items():
                    predicate += f' AND {key}="{value}"'
            
            self.client.delete_api().delete(
                start=start_time,
                stop=end_time,
                predicate=predicate,
                bucket=self.bucket,
                org=self.org
            )
            return True
        except Exception as e:
            print(f"删除数据失败: {e}")
            return False
    
    def close(self):
        """关闭客户端"""
        self.write_api.close()
