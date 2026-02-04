"""
报警管理服务配置管理
基于 Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """应用配置"""
    
    # FastAPI Configuration
    app_name: str = "Alarm Management Service"
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
    
    # Email Configuration
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_use_tls: bool = True
    
    # SMS Configuration (阿里云短信)
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_sms_sign_name: str = ""
    aliyun_sms_template_code: str = ""
    
    # WebSocket Configuration
    ws_heartbeat_interval: int = 30
    
    # Alarm Rules
    alarm_check_interval: int = 5
    alarm_auto_acknowledge_timeout: int = 300
    
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