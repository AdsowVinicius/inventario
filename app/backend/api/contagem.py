from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Set, List
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.forms_contagem import FormsContagem
from schemas.contagem import (
    ContagemCreate,
    ContagemUpdate,
    ContagemResponse,
    ContagemListResponse,
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
    - 3 ou mais → limite atingido
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

    total = query.scalar() or 0
    
    # Sugerir próximo número (máximo 3)
    num_sugerido = min(total + 1, 3)
    limite_atingido = total >= 3
    
    return ContagemSugestaoResponse(
        num_contagem_sugerido=num_sugerido,
        total_contagens=total,
        limite_atingido=limite_atingido
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
    Limite máximo: 3 contagens por etiqueta/planta
    """
    try:
        etiqueta_variantes = get_code_variants(contagem.etiqueta_inventario)
        if not etiqueta_variantes:
            raise HTTPException(status_code=400, detail="Etiqueta inválida")

        etiqueta_normalizada = normalize_code(contagem.etiqueta_inventario) or contagem.etiqueta_inventario
        part_number_normalizado = normalize_code(contagem.part_number) or contagem.part_number

        # Verificar se já atingiu o limite de 3 contagens
        total_contagens = db.query(func.count(FormsContagem.id)).filter(
            FormsContagem.planta == contagem.planta,
            FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes))
        ).scalar() or 0
        
        if total_contagens >= 3:
            raise HTTPException(
                status_code=400,
                detail=f"Limite atingido! Esta etiqueta já foi contada 3 vezes. Não é possível realizar outra contagem."
            )

        # Calcular próximo número de contagem automaticamente
        max_contagem = db.query(func.max(FormsContagem.num_contagem)).filter(
            FormsContagem.planta == contagem.planta,
            FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes))
        ).scalar()

        proximo_numero = (max_contagem or 0) + 1
        numero_final = contagem.num_contagem or proximo_numero
        
        # Validar que o número não ultrapasse 3
        if numero_final > 3:
            raise HTTPException(
                status_code=400,
                detail=f"O número da contagem não pode ser maior que 3."
            )

        # Verificar se já existe contagem com este número para esta etiqueta/planta
        # SEMPRE verificar, independente se número foi informado ou calculado
        filtros = [
            FormsContagem.planta == contagem.planta,
            FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes)),
            FormsContagem.num_contagem == numero_final
        ]
        existente = db.query(FormsContagem).filter(*filtros).first()

        if existente:
            raise HTTPException(
                status_code=400,
                detail=f"Já existe uma contagem #{numero_final} para esta etiqueta nesta planta. Não é permitido duplicar."
            )
        
        # Criar novo registro com número definido
        nova_contagem = FormsContagem(
            planta=contagem.planta,
            num_contagem=numero_final,
            zona_inventario=contagem.zona_inventario,
            etiqueta_inventario=etiqueta_normalizada,
            part_number=part_number_normalizado,
            lote=contagem.lote,
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


@router.get("/listar", response_model=List[ContagemListResponse])
def listar_contagens(
    planta: Optional[str] = Query(None, description="Filtrar por planta"),
    zona_inventario: Optional[str] = Query(None, description="Filtrar por zona"),
    etiqueta: Optional[str] = Query(None, description="Filtrar por etiqueta"),
    part_number: Optional[str] = Query(None, description="Filtrar por part number"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lista contagens com filtros - Apenas ADMIN
    """
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = db.query(FormsContagem).join(User, FormsContagem.usuario_id == User.id)
    
    if planta:
        query = query.filter(FormsContagem.planta == planta)
    if zona_inventario:
        query = query.filter(FormsContagem.zona_inventario == zona_inventario)
    if etiqueta:
        etiqueta_variantes = get_code_variants(etiqueta)
        if etiqueta_variantes:
            query = query.filter(FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes)))
    if part_number:
        pn_variantes = get_code_variants(part_number)
        if pn_variantes:
            query = query.filter(FormsContagem.part_number.in_(list(pn_variantes)))
    
    contagens = query.order_by(FormsContagem.timestamp.desc()).offset(skip).limit(limit).all()
    
    result = []
    for c in contagens:
        result.append(ContagemListResponse(
            id=c.id,
            planta=c.planta,
            zona_inventario=c.zona_inventario,
            etiqueta_inventario=c.etiqueta_inventario,
            part_number=c.part_number,
            lote=c.lote,
            qtd=c.qtd,
            num_contagem=c.num_contagem,
            usuario_id=c.usuario_id,
            usuario_nome=c.usuario.user_name if c.usuario else "Desconhecido",
            timestamp=c.timestamp,
            updated_at=c.updated_at
        ))
    
    return result


@router.get("/total")
def contar_total_contagens(
    planta: Optional[str] = Query(None),
    zona_inventario: Optional[str] = Query(None),
    etiqueta: Optional[str] = Query(None),
    part_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna o total de contagens com os filtros aplicados"""
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    query = db.query(func.count(FormsContagem.id))
    
    if planta:
        query = query.filter(FormsContagem.planta == planta)
    if zona_inventario:
        query = query.filter(FormsContagem.zona_inventario == zona_inventario)
    if etiqueta:
        etiqueta_variantes = get_code_variants(etiqueta)
        if etiqueta_variantes:
            query = query.filter(FormsContagem.etiqueta_inventario.in_(list(etiqueta_variantes)))
    if part_number:
        pn_variantes = get_code_variants(part_number)
        if pn_variantes:
            query = query.filter(FormsContagem.part_number.in_(list(pn_variantes)))
    
    return {"total": query.scalar() or 0}


@router.get("/{contagem_id}", response_model=ContagemListResponse)
def obter_contagem(
    contagem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtém uma contagem específica pelo ID"""
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    contagem = db.query(FormsContagem).filter(FormsContagem.id == contagem_id).first()
    
    if not contagem:
        raise HTTPException(status_code=404, detail="Contagem não encontrada")
    
    return ContagemListResponse(
        id=contagem.id,
        planta=contagem.planta,
        zona_inventario=contagem.zona_inventario,
        etiqueta_inventario=contagem.etiqueta_inventario,
        part_number=contagem.part_number,
        lote=contagem.lote,
        qtd=contagem.qtd,
        num_contagem=contagem.num_contagem,
        usuario_id=contagem.usuario_id,
        usuario_nome=contagem.usuario.user_name if contagem.usuario else "Desconhecido",
        timestamp=contagem.timestamp,
        updated_at=contagem.updated_at
    )


@router.put("/{contagem_id}", response_model=MessageResponse)
def atualizar_contagem(
    contagem_id: int,
    dados: ContagemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza uma contagem existente - Apenas ADMIN"""
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Apenas administradores podem editar contagens")
    
    contagem = db.query(FormsContagem).filter(FormsContagem.id == contagem_id).first()
    
    if not contagem:
        raise HTTPException(status_code=404, detail="Contagem não encontrada")
    
    try:
        if dados.etiqueta_inventario is not None:
            contagem.etiqueta_inventario = normalize_code(dados.etiqueta_inventario) or dados.etiqueta_inventario
        if dados.part_number is not None:
            contagem.part_number = normalize_code(dados.part_number) or dados.part_number
        if dados.zona_inventario is not None:
            contagem.zona_inventario = dados.zona_inventario
        if dados.lote is not None:
            contagem.lote = dados.lote
        if dados.qtd is not None:
            contagem.qtd = dados.qtd
        if dados.num_contagem is not None:
            contagem.num_contagem = dados.num_contagem
        
        db.commit()
        
        return MessageResponse(
            status="ok",
            mensagem=f"Contagem #{contagem_id} atualizada com sucesso!"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao atualizar contagem: {str(e)}"
        )


@router.delete("/{contagem_id}", response_model=MessageResponse)
def excluir_contagem(
    contagem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exclui uma contagem - Apenas ADMIN"""
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Apenas administradores podem excluir contagens")
    
    contagem = db.query(FormsContagem).filter(FormsContagem.id == contagem_id).first()
    
    if not contagem:
        raise HTTPException(status_code=404, detail="Contagem não encontrada")
    
    try:
        info = f"Etiqueta: {contagem.etiqueta_inventario}, PN: {contagem.part_number}"
        db.delete(contagem)
        db.commit()
        
        return MessageResponse(
            status="ok",
            mensagem=f"Contagem excluída com sucesso! ({info})"
        )
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao excluir contagem: {str(e)}"
        )
