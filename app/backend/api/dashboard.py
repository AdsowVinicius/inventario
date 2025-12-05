"""
API de Dashboard
- Fornece KPIs e análises para ADMIN e CONTROLADORIA
- Identifica contagens divergentes
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct, case, and_
from typing import Optional, List
from datetime import datetime, timedelta
from pydantic import BaseModel
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.forms_contagem import FormsContagem
from models.itens import ItensInventario

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# Schemas para o Dashboard
class KPIResponse(BaseModel):
    total_contagens: int
    total_etiquetas: int
    total_itens_base: int
    contagens_hoje: int
    contagens_semana: int
    usuarios_ativos: int
    zonas_ativas: int
    # Novos campos de porcentagem
    etiquetas_com_contagem_1: int
    etiquetas_com_contagem_2: int
    percentual_contagem_1: float
    percentual_contagem_2: float
    
    
class ContagemDivergenteResponse(BaseModel):
    etiqueta_inventario: str
    part_number: str
    planta: str
    zona_inventario: str
    contagem_1: Optional[float] = None
    contagem_2: Optional[float] = None
    contagem_3: Optional[float] = None
    usuario_1: Optional[str] = None
    usuario_2: Optional[str] = None
    usuario_3: Optional[str] = None
    status: str  # "divergente", "incompleta", "ok"
    diferenca_maxima: float
    

class ProgressoZonaResponse(BaseModel):
    zona: str
    planta: str
    etiquetas_contadas: int
    contagens_completas: int  # etiquetas com 1 e 2 sem divergência, ou 1, 2 e 3 com divergência resolvida
    contagens_parciais: int   # etiquetas que ainda precisam de contagens
    aguardando_3a: int        # etiquetas divergentes aguardando 3ª contagem
    percentual_completo: float
    

class ContagemPorUsuarioResponse(BaseModel):
    usuario_id: int
    usuario_nome: str
    total_contagens: int
    contagens_hoje: int
    

class ContagemPorPlantaResponse(BaseModel):
    planta: str
    total_contagens: int
    etiquetas_unicas: int
    contagens_completas: int  # 1+2 OK ou 1+2+3 resolvidas
    divergencias_pendentes: int  # divergências aguardando 3ª contagem
    divergencias_resolvidas: int  # divergências com 3ª contagem


class DashboardCompleto(BaseModel):
    kpis: KPIResponse
    divergentes: List[ContagemDivergenteResponse]
    progresso_zonas: List[ProgressoZonaResponse]
    contagens_por_usuario: List[ContagemPorUsuarioResponse]
    contagens_por_planta: List[ContagemPorPlantaResponse]
    resumo_divergencias: dict


def verificar_acesso_dashboard(current_user: User):
    """Verifica se o usuário tem acesso ao dashboard - Apenas ADMIN"""
    if current_user.role != 'ADMIN':
        raise HTTPException(status_code=403, detail="Acesso negado ao dashboard")


@router.get("/kpis", response_model=KPIResponse)
def obter_kpis(
    planta: Optional[str] = Query(None, description="Filtrar por planta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna os KPIs principais do sistema"""
    verificar_acesso_dashboard(current_user)
    
    hoje = datetime.utcnow().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    
    # Query base
    query = db.query(FormsContagem)
    if planta:
        query = query.filter(FormsContagem.planta == planta)
    
    # Total de contagens
    total_contagens = query.count()
    
    # Total de etiquetas únicas
    total_etiquetas = query.with_entities(
        func.count(distinct(FormsContagem.etiqueta_inventario))
    ).scalar() or 0
    
    # Total de itens na base
    itens_query = db.query(func.count(ItensInventario.id))
    if planta:
        itens_query = itens_query.filter(ItensInventario.planta == planta)
    total_itens_base = itens_query.scalar() or 0
    
    # Contagens hoje
    contagens_hoje = query.filter(
        func.date(FormsContagem.timestamp) == hoje
    ).count()
    
    # Contagens na semana
    contagens_semana = query.filter(
        func.date(FormsContagem.timestamp) >= inicio_semana
    ).count()
    
    # Usuários ativos (que fizeram contagem)
    usuarios_ativos = query.with_entities(
        func.count(distinct(FormsContagem.usuario_id))
    ).scalar() or 0
    
    # Zonas ativas
    zonas_ativas = query.with_entities(
        func.count(distinct(FormsContagem.zona_inventario))
    ).scalar() or 0
    
    # Contar etiquetas que têm contagem 1
    query_contagem_1 = db.query(
        func.count(distinct(FormsContagem.etiqueta_inventario))
    ).filter(FormsContagem.num_contagem == 1)
    if planta:
        query_contagem_1 = query_contagem_1.filter(FormsContagem.planta == planta)
    etiquetas_com_contagem_1 = query_contagem_1.scalar() or 0
    
    # Contar etiquetas que têm contagem 2
    query_contagem_2 = db.query(
        func.count(distinct(FormsContagem.etiqueta_inventario))
    ).filter(FormsContagem.num_contagem == 2)
    if planta:
        query_contagem_2 = query_contagem_2.filter(FormsContagem.planta == planta)
    etiquetas_com_contagem_2 = query_contagem_2.scalar() or 0
    
    # Calcular porcentagens com base nos itens cadastrados
    percentual_contagem_1 = round((etiquetas_com_contagem_1 / total_itens_base * 100), 2) if total_itens_base > 0 else 0.0
    percentual_contagem_2 = round((etiquetas_com_contagem_2 / total_itens_base * 100), 2) if total_itens_base > 0 else 0.0
    
    return KPIResponse(
        total_contagens=total_contagens,
        total_etiquetas=total_etiquetas,
        total_itens_base=total_itens_base,
        contagens_hoje=contagens_hoje,
        contagens_semana=contagens_semana,
        usuarios_ativos=usuarios_ativos,
        zonas_ativas=zonas_ativas,
        etiquetas_com_contagem_1=etiquetas_com_contagem_1,
        etiquetas_com_contagem_2=etiquetas_com_contagem_2,
        percentual_contagem_1=percentual_contagem_1,
        percentual_contagem_2=percentual_contagem_2
    )


@router.get("/divergentes", response_model=List[ContagemDivergenteResponse])
def obter_contagens_divergentes(
    planta: Optional[str] = Query(None, description="Filtrar por planta"),
    zona: Optional[str] = Query(None, description="Filtrar por zona"),
    limite: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Identifica contagens divergentes.
    
    Lógica de contagem:
    - Contagem 1 e 2 são OBRIGATÓRIAS
    - Se contagem 1 e 2 são IGUAIS → etiqueta OK (não precisa 3ª)
    - Se contagem 1 e 2 são DIFERENTES → precisa 3ª contagem para desempate
    
    Status:
    - "aguardando_contagem_1": só precisa da 1ª contagem
    - "aguardando_contagem_2": tem 1ª, precisa da 2ª
    - "aguardando_contagem_3": 1ª e 2ª divergentes, precisa da 3ª para desempate
    - "ok": 1ª e 2ª iguais, OU 1ª, 2ª e 3ª finalizadas
    - "divergente_resolvida": tinha divergência mas 3ª contagem resolveu
    """
    verificar_acesso_dashboard(current_user)
    
    # Buscar todas as contagens agrupadas por etiqueta/planta
    query = db.query(
        FormsContagem.etiqueta_inventario,
        FormsContagem.part_number,
        FormsContagem.planta,
        FormsContagem.zona_inventario
    ).distinct()
    
    if planta:
        query = query.filter(FormsContagem.planta == planta)
    if zona:
        query = query.filter(FormsContagem.zona_inventario == zona)
    
    etiquetas = query.all()
    
    divergentes = []
    
    for etq in etiquetas:
        # Buscar as contagens desta etiqueta
        contagens = db.query(FormsContagem).filter(
            FormsContagem.etiqueta_inventario == etq.etiqueta_inventario,
            FormsContagem.planta == etq.planta
        ).order_by(FormsContagem.num_contagem).all()
        
        if len(contagens) == 0:
            continue
            
        # Organizar contagens por número
        contagem_map = {c.num_contagem: c for c in contagens}
        
        c1 = contagem_map.get(1)
        c2 = contagem_map.get(2)
        c3 = contagem_map.get(3)
        
        qtd1 = c1.qtd if c1 else None
        qtd2 = c2.qtd if c2 else None
        qtd3 = c3.qtd if c3 else None
        
        # Determinar status baseado na nova lógica
        if qtd1 is None:
            status = "aguardando_contagem_1"
            diferenca = 0
        elif qtd2 is None:
            status = "aguardando_contagem_2"
            diferenca = 0
        elif qtd1 == qtd2:
            # Contagem 1 e 2 são iguais - OK, não precisa 3ª
            status = "ok"
            diferenca = 0
        else:
            # Contagem 1 e 2 são diferentes
            diferenca = abs(qtd1 - qtd2)
            if qtd3 is None:
                # Precisa da 3ª contagem para desempate
                status = "aguardando_contagem_3"
            else:
                # Tem 3ª contagem - divergência resolvida
                status = "divergente_resolvida"
        
        # Adicionar apenas os que precisam de ação
        if status in ["aguardando_contagem_1", "aguardando_contagem_2", "aguardando_contagem_3"]:
            divergentes.append(ContagemDivergenteResponse(
                etiqueta_inventario=etq.etiqueta_inventario,
                part_number=etq.part_number,
                planta=etq.planta,
                zona_inventario=etq.zona_inventario,
                contagem_1=qtd1,
                contagem_2=qtd2,
                contagem_3=qtd3,
                usuario_1=c1.usuario.user_name if c1 and c1.usuario else None,
                usuario_2=c2.usuario.user_name if c2 and c2.usuario else None,
                usuario_3=c3.usuario.user_name if c3 and c3.usuario else None,
                status=status,
                diferenca_maxima=diferenca
            ))
    
    # Ordenar: primeiro os que precisam da 3ª (divergentes), depois por diferença
    status_ordem = {"aguardando_contagem_3": 0, "aguardando_contagem_2": 1, "aguardando_contagem_1": 2}
    divergentes.sort(key=lambda x: (status_ordem.get(x.status, 99), -x.diferenca_maxima))
    
    return divergentes[:limite]


@router.get("/progresso-zonas", response_model=List[ProgressoZonaResponse])
def obter_progresso_zonas(
    planta: Optional[str] = Query(None, description="Filtrar por planta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna o progresso de contagem por zona.
    
    Uma etiqueta é considerada "completa" quando:
    - Tem contagem 1 e 2 com valores IGUAIS (não precisa 3ª), OU
    - Tem contagem 1, 2 e 3 (divergência resolvida)
    """
    verificar_acesso_dashboard(current_user)
    
    # Buscar zonas únicas
    query = db.query(
        FormsContagem.zona_inventario,
        FormsContagem.planta
    ).distinct()
    
    if planta:
        query = query.filter(FormsContagem.planta == planta)
    
    zonas = query.all()
    
    resultado = []
    
    for zona in zonas:
        # Contagens desta zona
        contagens = db.query(FormsContagem).filter(
            FormsContagem.zona_inventario == zona.zona_inventario,
            FormsContagem.planta == zona.planta
        ).all()
        
        # Agrupar por etiqueta
        etiquetas_contagens = {}
        for c in contagens:
            key = c.etiqueta_inventario
            if key not in etiquetas_contagens:
                etiquetas_contagens[key] = {}
            etiquetas_contagens[key][c.num_contagem] = c.qtd
        
        etiquetas_contadas = len(etiquetas_contagens)
        contagens_completas = 0
        contagens_parciais = 0
        aguardando_3a = 0
        
        for etq, nums in etiquetas_contagens.items():
            qtd1 = nums.get(1)
            qtd2 = nums.get(2)
            qtd3 = nums.get(3)
            
            if qtd1 is None or qtd2 is None:
                # Falta contagem 1 ou 2 - parcial
                contagens_parciais += 1
            elif qtd1 == qtd2:
                # 1 e 2 iguais - completa, não precisa 3ª
                contagens_completas += 1
            elif qtd3 is not None:
                # 1 e 2 diferentes mas tem 3ª - completa (resolvida)
                contagens_completas += 1
            else:
                # 1 e 2 diferentes sem 3ª - aguardando 3ª contagem
                aguardando_3a += 1
        
        percentual = (contagens_completas / etiquetas_contadas * 100) if etiquetas_contadas > 0 else 0
        
        resultado.append(ProgressoZonaResponse(
            zona=zona.zona_inventario,
            planta=zona.planta,
            etiquetas_contadas=etiquetas_contadas,
            contagens_completas=contagens_completas,
            contagens_parciais=contagens_parciais,
            aguardando_3a=aguardando_3a,
            percentual_completo=round(percentual, 1)
        ))
    
    # Ordenar por percentual
    resultado.sort(key=lambda x: x.percentual_completo, reverse=True)
    
    return resultado


@router.get("/contagens-usuario", response_model=List[ContagemPorUsuarioResponse])
def obter_contagens_por_usuario(
    planta: Optional[str] = Query(None, description="Filtrar por planta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna contagens agrupadas por usuário"""
    verificar_acesso_dashboard(current_user)
    
    hoje = datetime.utcnow().date()
    
    query = db.query(
        FormsContagem.usuario_id,
        User.user_name,
        func.count(FormsContagem.id).label('total'),
        func.sum(case((func.date(FormsContagem.timestamp) == hoje, 1), else_=0)).label('hoje')
    ).join(User, FormsContagem.usuario_id == User.id)
    
    if planta:
        query = query.filter(FormsContagem.planta == planta)
    
    resultados = query.group_by(
        FormsContagem.usuario_id,
        User.user_name
    ).order_by(func.count(FormsContagem.id).desc()).all()
    
    return [
        ContagemPorUsuarioResponse(
            usuario_id=r.usuario_id,
            usuario_nome=r.user_name,
            total_contagens=r.total,
            contagens_hoje=r.hoje or 0
        )
        for r in resultados
    ]


@router.get("/contagens-planta", response_model=List[ContagemPorPlantaResponse])
def obter_contagens_por_planta(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retorna contagens agrupadas por planta com análise de divergências.
    
    Lógica:
    - Completa: 1+2 iguais OU 1+2+3 (divergência resolvida)
    - Divergência pendente: 1+2 diferentes sem 3ª
    - Divergência resolvida: 1+2 diferentes com 3ª
    """
    verificar_acesso_dashboard(current_user)
    
    # Plantas únicas
    plantas = db.query(distinct(FormsContagem.planta)).all()
    
    resultado = []
    
    for (planta,) in plantas:
        contagens = db.query(FormsContagem).filter(FormsContagem.planta == planta).all()
        
        total = len(contagens)
        
        # Etiquetas únicas
        etiquetas = set(c.etiqueta_inventario for c in contagens)
        etiquetas_unicas = len(etiquetas)
        
        # Agrupar por etiqueta para calcular status
        etiqueta_map = {}
        for c in contagens:
            key = c.etiqueta_inventario
            if key not in etiqueta_map:
                etiqueta_map[key] = {}
            etiqueta_map[key][c.num_contagem] = c.qtd
        
        contagens_completas = 0
        divergencias_pendentes = 0
        divergencias_resolvidas = 0
        
        for etq, nums in etiqueta_map.items():
            qtd1 = nums.get(1)
            qtd2 = nums.get(2)
            qtd3 = nums.get(3)
            
            if qtd1 is None or qtd2 is None:
                # Ainda não tem 1 e 2 - não conta como nada ainda
                pass
            elif qtd1 == qtd2:
                # 1 e 2 iguais - completa
                contagens_completas += 1
            elif qtd3 is not None:
                # 1 e 2 diferentes com 3ª - resolvida
                contagens_completas += 1
                divergencias_resolvidas += 1
            else:
                # 1 e 2 diferentes sem 3ª - pendente
                divergencias_pendentes += 1
        
        resultado.append(ContagemPorPlantaResponse(
            planta=planta,
            total_contagens=total,
            etiquetas_unicas=etiquetas_unicas,
            contagens_completas=contagens_completas,
            divergencias_pendentes=divergencias_pendentes,
            divergencias_resolvidas=divergencias_resolvidas
        ))
    
    resultado.sort(key=lambda x: x.total_contagens, reverse=True)
    
    return resultado


@router.get("/completo", response_model=DashboardCompleto)
def obter_dashboard_completo(
    planta: Optional[str] = Query(None, description="Filtrar por planta"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retorna todos os dados do dashboard em uma única chamada"""
    verificar_acesso_dashboard(current_user)
    
    # KPIs
    kpis = obter_kpis(planta, db, current_user)
    
    # Divergentes
    divergentes = obter_contagens_divergentes(planta, None, 50, db, current_user)
    
    # Progresso por zona
    progresso_zonas = obter_progresso_zonas(planta, db, current_user)
    
    # Contagens por usuário
    contagens_usuario = obter_contagens_por_usuario(planta, db, current_user)
    
    # Contagens por planta
    contagens_planta = obter_contagens_por_planta(db, current_user)
    
    # Resumo de divergências com nova lógica
    aguardando_1 = len([d for d in divergentes if d.status == "aguardando_contagem_1"])
    aguardando_2 = len([d for d in divergentes if d.status == "aguardando_contagem_2"])
    aguardando_3 = len([d for d in divergentes if d.status == "aguardando_contagem_3"])
    
    resumo_divergencias = {
        "aguardando_contagem_1": aguardando_1,
        "aguardando_contagem_2": aguardando_2,
        "aguardando_contagem_3": aguardando_3,
        "total_pendentes": aguardando_1 + aguardando_2 + aguardando_3,
        "percentual_pendentes": round(
            (aguardando_1 + aguardando_2 + aguardando_3) / kpis.total_etiquetas * 100, 1
        ) if kpis.total_etiquetas > 0 else 0
    }
    
    return DashboardCompleto(
        kpis=kpis,
        divergentes=divergentes,
        progresso_zonas=progresso_zonas,
        contagens_por_usuario=contagens_usuario,
        contagens_por_planta=contagens_planta,
        resumo_divergencias=resumo_divergencias
    )
