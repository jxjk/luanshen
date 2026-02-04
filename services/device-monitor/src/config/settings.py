"""
设备监控服务配置管理
基于 Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # FastAPI Configuration
    app_name: str = "Device Monitor Service"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # MySQL Database
    db_host: str = "localhost"
    db_port: int = 3306
    db_user: str = "root"
    db_password: str = ""
    db_name: str = "ga_tools"
    db_charset: str = "utf8mb4"
    
    @property
    def database_url(self) -> str:
        """MySQL 数据库连接 URL"""
        return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?charset={self.db_charset}"
    
    # InfluxDB Time Series Database
    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = ""
    influxdb_org: str = "your_org"
    influxdb_bucket: str = "device_data"
    
    # Redis Cache
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    @property
    def redis_url(self) -> str:
        """Redis 连接 URL"""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # RabbitMQ Message Queue
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    
    @property
    def rabbitmq_url(self) -> str:
        """RabbitMQ 连接 URL"""
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}/{self.rabbitmq_vhost}"
    
    # OPC UA Configuration
    opcua_server_url: str = "opc.tcp://localhost:4840"
    opcua_polling_interval: float = 1.0
    
    # WebSocket Configuration
    ws_heartbeat_interval: int = 30
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def cors_origins_list(self) -> list:
        """CORS 允许的源列表"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


settings = get_settings()