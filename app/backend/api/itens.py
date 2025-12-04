from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import distinct, func
from typing import List, Optional
from core.database import get_db
from core.security import get_current_user
from models.user import User, RoleEnum
from models.itens import ItensInventario
from schemas.itens import ItensInventarioResponse, PartNumberResponse, ItensInventarioCreate, ItensInventarioUpdate

router = APIRouter(prefix="/itens", tags=["Itens"])


def verificar_permissao_edicao(current_user: User):
    """Verifica se o usuário tem permissão para editar itens"""
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.CONTROLADORIA]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores e controladoria podem gerenciar itens"
        )


@router.get("/", response_model=List[ItensInventarioResponse])
def listar_itens(
    planta: Optional[str] = None,
    busca: Optional[str] = None,
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
    
    if busca:
        termo = busca.strip()
        query = query.filter(
            (ItensInventario.num_material.ilike(f"%{termo}%")) |
            (ItensInventario.txt_descrica_material.ilike(f"%{termo}%"))
        )
    
    total = query.count()
    itens = query.order_by(ItensInventario.num_material).offset(skip).limit(limit).all()
    return itens


@router.get("/total")
def contar_itens(
    planta: Optional[str] = None,
    busca: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Conta o total de itens para paginação
    """
    query = db.query(func.count(ItensInventario.id))
    
    if planta:
        query = query.filter(ItensInventario.planta == planta)
    
    if busca:
        termo = busca.strip()
        query = query.filter(
            (ItensInventario.num_material.ilike(f"%{termo}%")) |
            (ItensInventario.txt_descrica_material.ilike(f"%{termo}%"))
        )
    
    total = query.scalar()
    return {"total": total}


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


@router.get("/buscar", response_model=List[PartNumberResponse])
def buscar_part_numbers(
    q: str = Query(..., min_length=1, description="Termo de busca (part number ou descrição)"),
    planta: Optional[str] = None,
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca part numbers por código ou descrição (autocomplete)
    Aceita letras e números
    """
    termo = q.strip()
    
    query = db.query(
        ItensInventario.num_material.label("part_number"),
        ItensInventario.txt_descrica_material.label("descricao"),
        ItensInventario.und_medida.label("und_medida")
    ).distinct()
    
    if planta:
        query = query.filter(ItensInventario.planta == planta)
    
    # Busca SEQUENCIAL - apenas itens que COMEÇAM com o termo digitado
    query = query.filter(
        (ItensInventario.num_material.ilike(f"{termo}%")) |
        (ItensInventario.txt_descrica_material.ilike(f"{termo}%"))
    )
    
    results = query.limit(limit).all()
    
    return [
        PartNumberResponse(
            part_number=r.part_number,
            descricao=r.descricao,
            und_medida=r.und_medida
        )
        for r in results
    ]


@router.get("/detalhes/{part_number}")
def obter_detalhes_part_number(
    part_number: str,
    planta: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém detalhes de um part number específico
    Retorna 404 se não encontrar
    """
    query = db.query(
        ItensInventario.num_material.label("part_number"),
        ItensInventario.txt_descrica_material.label("descricao"),
        ItensInventario.und_medida.label("und_medida")
    )
    
    if planta:
        query = query.filter(ItensInventario.planta == planta)
    
    # Busca exata ou normalizada (sem zeros à esquerda)
    termo_normalizado = part_number.lstrip('0') or '0'
    result = query.filter(
        (ItensInventario.num_material == part_number) |
        (ItensInventario.num_material == termo_normalizado)
    ).first()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Part Number '{part_number}' não encontrado"
        )
    
    return PartNumberResponse(
        part_number=result.part_number,
        descricao=result.descricao,
        und_medida=result.und_medida
    )


@router.get("/{item_id}", response_model=ItensInventarioResponse)
def obter_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtém um item específico pelo ID
    """
    item = db.query(ItensInventario).filter(ItensInventario.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    return item


@router.post("/", response_model=ItensInventarioResponse, status_code=status.HTTP_201_CREATED)
def criar_item(
    item_data: ItensInventarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria um novo item no inventário (apenas ADMIN e CONTROLADORIA)
    """
    verificar_permissao_edicao(current_user)
    
    # Verificar se já existe item com mesmo part number na mesma planta
    existente = db.query(ItensInventario).filter(
        ItensInventario.num_material == item_data.num_material,
        ItensInventario.planta == item_data.planta
    ).first()
    
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Já existe um item com o Part Number '{item_data.num_material}' na planta '{item_data.planta}'"
        )
    
    novo_item = ItensInventario(**item_data.model_dump())
    db.add(novo_item)
    db.commit()
    db.refresh(novo_item)
    
    return novo_item


@router.put("/{item_id}", response_model=ItensInventarioResponse)
def atualizar_item(
    item_id: int,
    item_data: ItensInventarioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Atualiza um item existente (apenas ADMIN e CONTROLADORIA)
    """
    verificar_permissao_edicao(current_user)
    
    item = db.query(ItensInventario).filter(ItensInventario.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    
    # Verificar duplicidade se estiver alterando part number ou planta
    dados = item_data.model_dump(exclude_unset=True)
    novo_pn = dados.get('num_material', item.num_material)
    nova_planta = dados.get('planta', item.planta)
    
    if novo_pn != item.num_material or nova_planta != item.planta:
        existente = db.query(ItensInventario).filter(
            ItensInventario.num_material == novo_pn,
            ItensInventario.planta == nova_planta,
            ItensInventario.id != item_id
        ).first()
        
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Já existe um item com o Part Number '{novo_pn}' na planta '{nova_planta}'"
            )
    
    # Atualizar campos
    for campo, valor in dados.items():
        setattr(item, campo, valor)
    
    db.commit()
    db.refresh(item)
    
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Exclui um item do inventário (apenas ADMIN)
    """
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem excluir itens"
        )
    
    item = db.query(ItensInventario).filter(ItensInventario.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item não encontrado"
        )
    
    db.delete(item)
    db.commit()
    
    return None
