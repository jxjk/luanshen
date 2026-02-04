"""
策略管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...config.database import get_db
from ...repositories import StrategyRepository
from ..schemas.strategy import StrategyCreate, StrategyUpdate, StrategyResponse

router = APIRouter(tags=["策略管理"])


@router.get("/", response_model=List[StrategyResponse])
async def get_strategies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有策略"""
    repo = StrategyRepository(db)
    strategies = repo.get_all(skip=skip, limit=limit)
    return [StrategyResponse(**s.to_dict()) for s in strategies]


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """获取单个策略"""
    repo = StrategyRepository(db)
    strategy = repo.get(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略 {strategy_id} 不存在"
        )
    return StrategyResponse(**strategy.to_dict())


@router.post("/", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(strategy: StrategyCreate, db: Session = Depends(get_db)):
    """创建策略"""
    repo = StrategyRepository(db)

    # 创建策略 - 映射字段名到数据库模型
    strategy_dict = strategy.dict()
    # 生成策略ID
    import random
    if 'id' not in strategy_dict or not strategy_dict['id']:
        strategy_dict['id'] = f"ST{random.randint(1000, 9999)}"

    # 将 moSunXiShu 映射到 mo_sun_xi_shu
    if 'moSunXiShu' in strategy_dict:
        strategy_dict['mo_sun_xi_shu'] = strategy_dict.pop('moSunXiShu')

    new_strategy = repo.create(strategy_dict)
    return StrategyResponse(**new_strategy.to_dict())


@router.put("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(strategy_id: str, strategy: StrategyUpdate, db: Session = Depends(get_db)):
    """更新策略"""
    repo = StrategyRepository(db)

    # 检查是否存在
    if not repo.get(strategy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略 {strategy_id} 不存在"
        )

    # 更新策略
    update_dict = strategy.dict(exclude_unset=True)
    # 将 moSunXiShu 映射到 mo_sun_xi_shu
    if 'moSunXiShu' in update_dict:
        update_dict['mo_sun_xi_shu'] = update_dict.pop('moSunXiShu')

    updated_strategy = repo.update(strategy_id, update_dict)

    return StrategyResponse(**updated_strategy.to_dict())


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(strategy_id: str, db: Session = Depends(get_db)):
    """删除策略"""
    repo = StrategyRepository(db)
    
    if not repo.get(strategy_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"策略 {strategy_id} 不存在"
        )
    
    repo.delete(strategy_id)