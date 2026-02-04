"""
设备管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...config.database import get_db
from ...repositories import MachineRepository
from ..schemas.machine import MachineCreate, MachineUpdate, MachineResponse

router = APIRouter(tags=["设备管理"])


@router.get("/", response_model=List[MachineResponse])
async def get_machines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有设备"""
    repo = MachineRepository(db)
    machines = repo.get_all(skip=skip, limit=limit)
    return [MachineResponse(**m.to_dict()) for m in machines]


@router.get("/{machine_id}", response_model=MachineResponse)
async def get_machine(machine_id: str, db: Session = Depends(get_db)):
    """获取单个设备"""
    repo = MachineRepository(db)
    machine = repo.get(machine_id)
    if not machine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {machine_id} 不存在"
        )
    return MachineResponse(**machine.to_dict())


@router.post("/", response_model=MachineResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    """创建设备"""
    repo = MachineRepository(db)

    # 检查是否已存在
    if repo.get(machine.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"设备 {machine.id} 已存在"
        )

    # 创建设备 - 映射字段名到数据库模型
    machine_dict = machine.dict()
    # 将 xiaoLv 映射到 xiao_lv
    if 'xiaoLv' in machine_dict:
        machine_dict['xiao_lv'] = machine_dict.pop('xiaoLv')
    new_machine = repo.create(machine_dict)
    return MachineResponse(**new_machine.to_dict())


@router.put("/{machine_id}", response_model=MachineResponse)
async def update_machine(machine_id: str, machine: MachineUpdate, db: Session = Depends(get_db)):
    """更新设备"""
    repo = MachineRepository(db)

    # 检查是否存在
    if not repo.get(machine_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {machine_id} 不存在"
        )

    # 更新设备 - 映射字段名到数据库模型
    update_dict = machine.dict(exclude_unset=True)
    # 将 xiaoLv 映射到 xiao_lv
    if 'xiaoLv' in update_dict:
        update_dict['xiao_lv'] = update_dict.pop('xiaoLv')
    updated_machine = repo.update(machine_id, update_dict)

    return MachineResponse(**updated_machine.to_dict())


@router.delete("/{machine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_machine(machine_id: str, db: Session = Depends(get_db)):
    """删除设备"""
    repo = MachineRepository(db)
    
    if not repo.get(machine_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"设备 {machine_id} 不存在"
        )
    
    repo.delete(machine_id)