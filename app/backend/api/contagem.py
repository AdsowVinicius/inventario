from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Set
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


def normalize_code(code: Optional[str]) -> Optional[str]:
    """Remove zeros à esquerda mantendo '0' quando valor inteiro é zero."""
    if code is None:
        return None
    text = str(code).strip()
    if text == "":
        return None
    normalized = text.lstrip("0")
    return normalized if normalized != "" else "0"


def get_code_variants(code: Optional[str]) -> Set[str]:
    """Retorna variações possíveis (original + normalizada) para consultas."""
    variants: Set[str] = set()
    if code is None:
        return variants
    text = str(code).strip()
    if text == "":
        return variants
    variants.add(text)
    normalized = normalize_code(text)
    if normalized and normalized != text:
        variants.add(normalized)
    return variants


@router.get("/sugerir", response_model=ContagemSugestaoResponse)
def sugerir_numero_contagem(
    pn: Optional[str] = Query(None, description="Part Number (opcional)"),
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
    etiqueta_variantes = get_code_variants(etiqueta)
    if not etiqueta_variantes:
        raise HTTPException(status_code=400, detail="Etiqueta inválida")

    query = db.query(func.count(FormsContagem.id)).filter(
        FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes)),
        FormsContagem.planta == planta
    )

    pn_variantes = get_code_variants(pn)
    if pn_variantes:
        query = query.filter(FormsContagem.part_number.in_(list(pn_variantes)))

    total = query.scalar()
    
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
        etiqueta_variantes = get_code_variants(contagem.etiqueta_inventario)
        if not etiqueta_variantes:
            raise HTTPException(status_code=400, detail="Etiqueta inválida")

        etiqueta_normalizada = normalize_code(contagem.etiqueta_inventario) or contagem.etiqueta_inventario
        part_number_normalizado = normalize_code(contagem.part_number) or contagem.part_number

        # Calcular próximo número de contagem automaticamente
        max_contagem = db.query(func.max(FormsContagem.num_contagem)).filter(
            FormsContagem.planta == contagem.planta,
            FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes))
        ).scalar()

        proximo_numero = (max_contagem or 0) + 1
        numero_final = contagem.num_contagem or proximo_numero

        # Evitar duplicar números manualmente informados
        if contagem.num_contagem:
            filtros = [
                FormsContagem.planta == contagem.planta,
                FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes)),
                FormsContagem.num_contagem == contagem.num_contagem
            ]
            existente = db.query(FormsContagem).filter(*filtros).first()

            if existente:
                raise HTTPException(
                    status_code=400,
                    detail=f"Já existe uma contagem #{contagem.num_contagem} para esta etiqueta nesta planta"
                )
        
        # Criar novo registro com número definido
        nova_contagem = FormsContagem(
            planta=contagem.planta,
            num_contagem=numero_final,
            zona_inventario=contagem.zona_inventario,
            etiqueta_inventario=etiqueta_normalizada,
            part_number=part_number_normalizado,
            campo=contagem.campo,
            qtd=contagem.qtd,
            usuario_id=current_user.id
        )
        
        db.add(nova_contagem)
        db.commit()
        db.refresh(nova_contagem)
        
        return MessageResponse(
            status="ok",
            mensagem=f"Contagem #{numero_final} salva com sucesso!"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar contagem: {str(e)}"
        )
