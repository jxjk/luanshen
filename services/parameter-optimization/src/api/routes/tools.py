"""
刀具管理 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ...config.database import get_db
from ...repositories import ToolRepository
from ..schemas.tool import ToolCreate, ToolUpdate, ToolResponse

router = APIRouter(tags=["刀具管理"])


@router.get("/", response_model=List[ToolResponse])
async def get_tools(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有刀具"""
    repo = ToolRepository(db)
    tools = repo.get_all(skip=skip, limit=limit)
    return [ToolResponse(**t.to_dict()) for t in tools]


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(tool_id: str, db: Session = Depends(get_db)):
    """获取单个刀具"""
    repo = ToolRepository(db)
    tool = repo.get(tool_id)
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"刀具 {tool_id} 不存在"
        )
    return ToolResponse(**tool.to_dict())


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(tool: ToolCreate, db: Session = Depends(get_db)):
    """创建刀具"""
    repo = ToolRepository(db)

    # 检查是否已存在
    if repo.get(tool.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"刀具 {tool.id} 已存在"
        )

    # 创建刀具 - 映射字段名到数据库模型
    tool_dict = tool.dict()
    # 生成刀具ID（如果需要）
    if 'id' not in tool_dict or not tool_dict['id']:
        tool_dict['id'] = str(int(hash(tool.name + tool.type)) % 1000000).zfill(8)

    new_tool = repo.create(tool_dict)
    return ToolResponse(**new_tool.to_dict())


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(tool_id: str, tool: ToolUpdate, db: Session = Depends(get_db)):
    """更新刀具"""
    repo = ToolRepository(db)

    # 检查是否存在
    if not repo.get(tool_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"刀具 {tool_id} 不存在"
        )

    # 更新刀具
    update_dict = tool.dict(exclude_unset=True)
    updated_tool = repo.update(tool_id, update_dict)

    return ToolResponse(**updated_tool.to_dict())


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: str, db: Session = Depends(get_db)):
    """删除刀具"""
    repo = ToolRepository(db)
    
    if not repo.get(tool_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"刀具 {tool_id} 不存在"
        )
    
    repo.delete(tool_id)