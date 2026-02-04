"""
材料管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...config.database import get_db
from ...repositories import MaterialRepository
from ..schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse

router = APIRouter(tags=["材料管理"])


@router.get("/", response_model=List[MaterialResponse])
async def get_materials(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有材料"""
    repo = MaterialRepository(db)
    materials = repo.get_all(skip=skip, limit=limit)
    return [MaterialResponse(**m.to_dict()) for m in materials]


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(material_id: str, db: Session = Depends(get_db)):
    """获取单个材料"""
    repo = MaterialRepository(db)
    material = repo.get_by_group(material_id)
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"材料 {material_id} 不存在"
        )
    return MaterialResponse(**material.to_dict())


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(material: MaterialCreate, db: Session = Depends(get_db)):
    """创建材料"""
    repo = MaterialRepository(db)

    # 检查是否已存在
    if repo.get_by_group(material.caiLiaoZu):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"材料 {material.caiLiaoZu} 已存在"
        )

    # 创建材料 - 映射字段名到数据库模型
    material_dict = material.dict()
    # 将 caiLiaoZu 映射到 cai_liao_zu
    if 'caiLiaoZu' in material_dict:
        material_dict['cai_liao_zu'] = material_dict.pop('caiLiaoZu')

    new_material = repo.create(material_dict)
    return MaterialResponse(**new_material.to_dict())


@router.put("/{material_id}", response_model=MaterialResponse)
async def update_material(material_id: str, material: MaterialUpdate, db: Session = Depends(get_db)):
    """更新材料"""
    repo = MaterialRepository(db)

    # 检查是否存在
    existing = repo.get_by_group(material_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"材料 {material_id} 不存在"
        )

    # 更新材料
    update_dict = material.dict(exclude_unset=True)
    updated_material = repo.update(material_id, update_dict)

    return MaterialResponse(**updated_material.to_dict())


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(material_id: str, db: Session = Depends(get_db)):
    """删除材料"""
    repo = MaterialRepository(db)
    
    if not repo.get_by_group(material_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"材料 {material_id} 不存在"
        )
    
    repo.delete(material_id)