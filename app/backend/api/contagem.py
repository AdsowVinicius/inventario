from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.forms_contagem import FormsContagem
from schemas.contagem import (
    ContagemCreate,
    ContagemResponse,
    ContagemSugestaoResponse,
    MessageResponse
)

router = APIRouter(prefix="/contagem", tags=["Contagem"])


@router.get("/sugerir", response_model=ContagemSugestaoResponse)
def sugerir_numero_contagem(
    pn: str = Query(..., description="Part Number"),
    etiqueta: str = Query(..., description="Etiqueta de Inventário"),
    planta: str = Query(..., description="Planta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Sugere o próximo número de contagem baseado em registros existentes
    
    Regras:
    - 0 registros → sugerir 1
    - 1 registro → sugerir 2
    - 2 registros → sugerir 3
    """
    # Contar registros existentes
    total = db.query(func.count(FormsContagem.id)).filter(
        FormsContagem.part_number == pn,
        FormsContagem.etiqueta_inventario == etiqueta,
        FormsContagem.planta == planta
    ).scalar()
    
    # Sugerir próximo número
    num_sugerido = (total or 0) + 1
    
    return ContagemSugestaoResponse(
        num_contagem_sugerido=num_sugerido,
        total_contagens=total or 0
    )


@router.post("/salvar", response_model=MessageResponse)
def salvar_contagem(
    contagem: ContagemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Salva uma nova contagem no banco de dados
    
    O número de contagem é gerado automaticamente baseado nas contagens existentes
    """
    try:
        # Calcular próximo número de contagem automaticamente
        max_contagem = db.query(func.max(FormsContagem.num_contagem)).filter(
            FormsContagem.etiqueta_inventario == contagem.etiqueta_inventario,
            FormsContagem.planta == contagem.planta
        ).scalar()
        
        proximo_numero = (max_contagem or 0) + 1
        
        # Criar novo registro com número automático
        nova_contagem = FormsContagem(
            planta=contagem.planta,
            num_contagem=proximo_numero,
            zona_inventario=contagem.zona_inventario,
            etiqueta_inventario=contagem.etiqueta_inventario,
            part_number=contagem.part_number,
            campo=contagem.campo,
            qtd=contagem.qtd,
            usuario_id=current_user.id
        )
        
        db.add(nova_contagem)
        db.commit()
        db.refresh(nova_contagem)
        
        return MessageResponse(
            status="ok",
            mensagem=f"Contagem #{proximo_numero} salva com sucesso!"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar contagem: {str(e)}"
        )
