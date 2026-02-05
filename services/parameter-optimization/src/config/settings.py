"""
配置管理系统
使用 Pydantic Settings 进行配置管理，支持环境变量和配置文件
"""
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """数据库配置"""
    host: str = Field(default="localhost", description="数据库主机")
    port: int = Field(default=3306, description="数据库端口")
    user: str = Field(..., description="数据库用户名")
    password: str = Field(..., description="数据库密码")
    database: str = Field(default="ga_tools", description="数据库名称")
    charset: str = Field(default="utf8mb4", description="字符集")
    pool_size: int = Field(default=5, description="连接池大小")
    max_overflow: int = Field(default=10, description="连接池最大溢出数")
    pool_timeout: int = Field(default=30, description="连接池超时时间(秒)")
    pool_recycle: int = Field(default=3600, description="连接回收时间(秒)")

    class Config:
        env_prefix = "DB_"

    @property
    def url(self) -> str:
        """生成数据库连接 URL"""
        return (
            f"mysql+pymysql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
            f"?charset={self.charset}"
        )


class AlgorithmSettings(BaseSettings):
    """遗传算法配置"""
    population_size: int = Field(default=10240, description="种群大小", ge=100, le=100000)
    generations: int = Field(default=200, description="迭代次数", ge=10, le=1000)
    crossover_rate: float = Field(default=0.6, description="交叉概率", ge=0.0, le=1.0)
    mutation_rate: float = Field(default=0.3, description="变异概率", ge=0.0, le=1.0)
    dna_size: int = Field(default=36, description="DNA 长度", ge=16)
    early_stop_generations: int = Field(default=50, description="早停连续无改进代数")

    class Config:
        env_prefix = "ALGO_"


class APISettings(BaseSettings):
    """API 服务配置"""
    host: str = Field(default="0.0.0.0", description="服务监听地址")
    port: int = Field(default=8000, description="服务端口", ge=1024, le=65535)
    reload: bool = Field(default=True, description="开发模式热重载")
    workers: int = Field(default=4, description="工作进程数", ge=1)
    cors_origins: list[str] = Field(default=["*"], description="CORS 允许的源")
    api_prefix: str = Field(default="/api/v1", description="API 路由前缀")

    class Config:
        env_prefix = "API_"


class SecuritySettings(BaseSettings):
    """安全配置"""
    secret_key: str = Field(..., description="JWT 密钥")
    algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    bcrypt_rounds: int = Field(default=12, description="bcrypt 加密轮数")

    class Config:
        env_prefix = ""


class LogSettings(BaseSettings):
    """日志配置"""
    level: str = Field(default="INFO", description="日志级别")
    file: Optional[str] = Field(default=None, description="日志文件路径")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="日志格式"
    )
    max_bytes: int = Field(default=10485760, description="日志文件最大大小(10MB)")
    backup_count: int = Field(default=5, description="日志文件备份数量")

    class Config:
        env_prefix = "LOG_"


class Settings(BaseSettings):
    """应用总配置"""
    environment: str = Field(default="development", description="运行环境")
    app_name: str = Field(default="工艺参数优化系统", description="应用名称")
    app_version: str = Field(default="1.0.0", description="应用版本")
    
    # 直接继承所有配置
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": False}
    
    # 数据库配置（使用 Field 设置默认值）
    db_host: str = Field(default="localhost", description="数据库主机")
    db_port: int = Field(default=3306, description="数据库端口")
    db_user: str = Field(default="root", description="数据库用户名")
    db_password: str = Field(default="123456", description="数据库密码")
    db_name: str = Field(default="ga_tools", description="数据库名称")
    db_charset: str = Field(default="utf8mb4", description="字符集")
    db_pool_size: int = Field(default=5, description="连接池大小")
    db_max_overflow: int = Field(default=10, description="连接池最大溢出数")
    db_pool_timeout: int = Field(default=30, description="连接池超时时间(秒)")
    db_pool_recycle: int = Field(default=3600, description="连接回收时间(秒)")
    
    # 算法配置
    algo_population_size: int = Field(default=10240, description="种群大小")
    algo_generations: int = Field(default=200, description="迭代次数")
    algo_crossover_rate: float = Field(default=0.6, description="交叉概率")
    algo_mutation_rate: float = Field(default=0.3, description="变异概率")
    algo_dna_size: int = Field(default=36, description="DNA 长度")
    algo_early_stop_generations: int = Field(default=50, description="早停连续无改进代数")
    
    # API 配置
    api_host: str = Field(default="0.0.0.0", description="服务监听地址")
    api_port: int = Field(default=8000, description="服务端口")
    api_reload: bool = Field(default=True, description="开发模式热重载")
    api_workers: int = Field(default=4, description="工作进程数")
    api_cors_origins: list[str] = Field(default=["*"], description="CORS 允许的源")
    api_api_prefix: str = Field(default="/api/v1", description="API 路由前缀")
    
    # 安全配置
    secret_key: str = Field(default="change-me-in-production", description="JWT 密钥")
    algorithm: str = Field(default="HS256", description="JWT 算法")
    access_token_expire_minutes: int = Field(default=30, description="访问令牌过期时间(分钟)")
    bcrypt_rounds: int = Field(default=12, description="bcrypt 加密轮数")
    
    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", description="日志格式")
    log_max_bytes: int = Field(default=10485760, description="日志文件最大大小(10MB)")
    log_backup_count: int = Field(default=5, description="日志文件备份数量")
    
    # DeepSeek LLM 配置
    deepseek_api_key: Optional[str] = Field(default=None, description="DeepSeek API Key")
    deepseek_base_url: str = Field(default="https://api.deepseek.com/v1", description="DeepSeek API 基础 URL")
    deepseek_model: str = Field(default="deepseek-chat", description="DeepSeek 模型名称")
    deepseek_temperature: float = Field(default=0.7, description="DeepSeek 温度参数")
    deepseek_max_tokens: int = Field(default=2000, description="DeepSeek 最大令牌数")
    deepseek_timeout: int = Field(default=30, description="DeepSeek 请求超时时间(秒)")
    deepseek_enabled: bool = Field(default=True, description="是否启用 DeepSeek LLM")


# 全局配置实例
settings = Settings()