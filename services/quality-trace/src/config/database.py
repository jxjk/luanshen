"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from redis import Redis
import pika
from typing import Generator

from .settings import settings

# MySQL Database
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator:
    """获取 MySQL 数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Redis Client
redis_client: Redis = None


def get_redis_client() -> Redis:
    """获取 Redis 客户端"""
    global redis_client
    if redis_client is None:
        redis_client = Redis.from_url(
            settings.redis_url,
            decode_responses=True
        )
    return redis_client


def close_redis_client():
    """关闭 Redis 客户端"""
    global redis_client
    if redis_client:
        redis_client.close()
        redis_client = None


# RabbitMQ Connection
rabbitmq_connection: pika.BlockingConnection = None


def get_rabbitmq_connection() -> pika.BlockingConnection:
    """获取 RabbitMQ 连接"""
    global rabbitmq_connection
    if rabbitmq_connection is None or rabbitmq_connection.is_closed:
        parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            virtual_host=settings.rabbitmq_vhost,
            credentials=pika.PlainCredentials(
                settings.rabbitmq_user,
                settings.rabbitmq_password
            )
        )
        rabbitmq_connection = pika.BlockingConnection(parameters)
    return rabbitmq_connection


def close_rabbitmq_connection():
    """关闭 RabbitMQ 连接"""
    global rabbitmq_connection
    if rabbitmq_connection and not rabbitmq_connection.is_closed:
        rabbitmq_connection.close()
        rabbitmq_connection = None


# 初始化函数
def init_db():
    """初始化数据库连接"""
    # MySQL 自动创建表（使用现有ga_tools数据库）
    from ..models.trace_record import QualityTraceRecord, QualityTraceParameter
    Base.metadata.create_all(bind=engine)
    print("MySQL 数据库初始化完成")
    
    # Redis 测试连接
    redis = get_redis_client()
    if redis.ping():
        print("Redis 连接成功")
    
    # RabbitMQ 测试连接
    try:
        conn = get_rabbitmq_connection()
        if conn.is_open:
            print("RabbitMQ 连接成功")
    except Exception as e:
        print(f"RabbitMQ 连接失败: {e}")


def close_db():
    """关闭所有数据库连接"""
    close_redis_client()
    close_rabbitmq_connection()
    print("所有数据库连接已关闭")