"""
数据库连接管理
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from .settings import settings


# 创建数据库 URL
db_url = (
    f"mysql+pymysql://{settings.db_user}:{settings.db_password}"
    f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    f"?charset={settings.db_charset}"
)

# 创建数据库引擎
engine = create_engine(
    db_url,
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_timeout=settings.db_pool_timeout,
    pool_recycle=settings.db_pool_recycle,
    pool_pre_ping=True,  # 连接前检查连接是否有效
    echo=False,  # 生产环境关闭 SQL 日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话的生成器函数（用于 FastAPI 依赖注入）
    
    使用示例:
        @app.get("/materials")
        def get_materials(db: Session = Depends(get_db)):
            repository = MaterialRepository(db)
            return repository.get_all()
    
    Yields:
        Session: 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    初始化数据库
    创建所有表（如果不存在）
    """
    from ..models import Base
    Base.metadata.create_all(bind=engine)


def close_db():
    """
    关闭数据库连接
    """
    engine.dispose()