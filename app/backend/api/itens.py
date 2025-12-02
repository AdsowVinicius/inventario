from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.itens import ItensInventario
from schemas.itens import ItensInventarioResponse, PartNumberResponse

router = APIRouter(prefix="/itens", tags=["Itens"])


@router.get("/", response_model=List[ItensInventarioResponse])
def listar_itens(
    planta: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os itens do inventário com filtros opcionais
    """
    query = db.query(ItensInventario)
    
    if planta:
        query = query.filter(ItensInventario.planta == planta)
    
    itens = query.offset(skip).limit(limit).all()
    return itens


@router.get("/part-numbers", response_model=List[PartNumberResponse])
def listar_part_numbers(
    planta: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista todos os part numbers únicos para dropdown
    """
    query = db.query(
        ItensInventario.num_material.label("part_number"),
        ItensInventario.txt_descrica_material.label("descricao"),
        ItensInventario.und_medida.label("und_medida")
    ).distinct()
    
    if planta:
        query = query.filter(ItensInventario.planta == planta)
    
    results = query.all()
    
    return [
        PartNumberResponse(
            part_number=r.part_number,
            descricao=r.descricao,
            und_medida=r.und_medida
        )
        for r in results
    ]
