"""
基础仓储类
提供通用的数据访问方法
"""
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """基础仓储类"""

    def __init__(self, model: Type[ModelType], db: Session):
        """
        初始化仓储
        
        Args:
            model: SQLAlchemy 模型类
            db: 数据库会话
        """
        self.model = model
        self.db = db

    def get(self, id: str) -> Optional[ModelType]:
        """
        根据ID获取单个对象
        
        Args:
            id: 对象ID
            
        Returns:
            找到的对象，不存在则返回 None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        获取所有对象（分页）
        
        Args:
            skip: 跳过记录数
            limit: 返回记录数
            
        Returns:
            对象列表
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        创建新对象
        
        Args:
            obj_in: 对象数据字典
            
        Returns:
            创建的对象
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, id: str, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        更新对象
        
        Args:
            id: 对象ID
            obj_in: 更新数据字典
            
        Returns:
            更新后的对象，不存在则返回 None
        """
        db_obj = self.get(id)
        if db_obj:
            for field, value in obj_in.items():
                setattr(db_obj, field, value)
            self.db.commit()
            self.db.refresh(db_obj)
        return db_obj

    def delete(self, id: str) -> bool:
        """
        删除对象
        
        Args:
            id: 对象ID
            
        Returns:
            删除成功返回 True，否则返回 False
        """
        db_obj = self.get(id)
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False

    def count(self) -> int:
        """
        获取对象总数
        
        Returns:
            对象总数
        """
        return self.db.query(self.model).count()

    def exists(self, id: str) -> bool:
        """
        检查对象是否存在
        
        Args:
            id: 对象ID
            
        Returns:
            存在返回 True，否则返回 False
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None