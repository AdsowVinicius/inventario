from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import io
from core.database import get_db
from core.security import get_current_user, require_role
from models.user import User
from models.forms_contagem import FormsContagem
from schemas.contagem import ContagemFiltros
from utils.excel_export import generate_csv, generate_excel

router = APIRouter(prefix="/exportacao", tags=["Exportação"])

# Mapeamento de zonas por planta com descrição
ZONAS_POR_PLANTA = {
    'PS01': {
        'A': 'Acabado',
        'B': 'Semi-Acabado',
        'C': 'Matéria-Prima/Embalagens',
        'D': 'Almoxarifado',
        'E': 'Câmara-Fria',
        'F': 'Qualidade',
        'G': 'Engenharia'
    },
    'PS02': {
        'A': 'G2',
        'B': 'Qualidade',
        'C': 'Sala de Tintas',
        'D': 'Almoxarifado de Tintas',
        'E': 'Almoxarifado',
        'F': 'Almox/Manutenção',
        'G': 'Polimento/Retoque',
        'H': 'Montagem',
        'I': 'Estoque Acabado'
    },
    'PS03': {
        'A': 'Acabado',
        'B': 'Semi-Acabado',
        'C': 'Componentes/Embalagens',
        'D': 'Sala de Tintas',
        'E': 'Almoxarifado'
    },
    'PS05': {
        'A': 'Almoxarifado',
        'B': 'Estoque Acabado',
        'C': 'Montagem',
        'D': 'Colagem',
        'E': 'Semi-Acabado',
        'F': 'Sala de Materiais',
        'G': 'G2',
        'H': 'Obsoleto',
        'I': 'Engenharia/Qualidade'
    },
    'PB82': {
        'A': 'Almoxarifado',
        'B': 'Estoque',
        'C': 'Produção'
    }
}

def obter_zona_completa(planta: str, zona: str) -> str:
    """Retorna a zona no formato 'Zona (A) - Descrição'"""
    descricao = ZONAS_POR_PLANTA.get(planta, {}).get(zona, '')
    if descricao:
        return f"Zona ({zona}) - {descricao}"
    return f"Zona ({zona})"


@router.get("/preview")
def preview_dados(
    planta: Optional[str] = None,
    zona_inventario: Optional[str] = None,
    etiqueta_inventario: Optional[str] = None,
    part_number: Optional[str] = None,
    num_contagem: Optional[int] = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "CONTROLADORIA"))
):
    """
    Preview dos dados que serão exportados
    
    Disponível apenas para: admin e controladoria
    """
    # Criar filtros
    filtros = ContagemFiltros(
        planta=planta,
        zona_inventario=zona_inventario,
        etiqueta_inventario=etiqueta_inventario,
        part_number=part_number,
        num_contagem=num_contagem
    )
    
    # Buscar contagens com join do usuário
    query = db.query(FormsContagem).join(User, FormsContagem.usuario_id == User.id)
    query = aplicar_filtros(query, filtros)
    
    # Contar total
    total = query.count()
    
    # Limitar resultados para preview
    contagens = query.limit(limit).all()
    
    # Preparar dados com nomes compatíveis com o frontend
    data = [
        {
            'id': c.id,
            'etiqueta_inventario': f"{c.num_contagem}ª CONTAGEM",
            'inventario_cod_texto': c.etiqueta_inventario,
            'part_number': c.part_number,
            'part_number_text': c.part_number,
            'planta': c.planta,
            'planta_text': c.planta,
            'qtd': c.qtd,
            'quantidade': c.qtd,
            'zona_inventario': c.zona_inventario,
            'zona_invent_no_text': obter_zona_completa(c.planta, c.zona_inventario),
            'num_contagem': c.num_contagem,
            'created_date': c.timestamp.strftime('%b %d, %Y %I:%M %p') if c.timestamp else '',
            'modified_date': c.updated_at.strftime('%b %d, %Y %I:%M %p') if c.updated_at else '',
            'created_by': c.usuario.user_name if c.usuario else '',
            'created_by_email': c.usuario.email if c.usuario and c.usuario.email else f"{c.usuario.user_name}@inventario.com" if c.usuario else '',
            'lote': c.lote or ''
        }
        for c in contagens
    ]
    
    return {
        "total": total,
        "exibindo": len(data),
        "dados": data
    }


def aplicar_filtros(query, filtros: ContagemFiltros):
    """Aplica filtros à query de contagem"""
    if filtros.planta:
        query = query.filter(FormsContagem.planta == filtros.planta)
    
    if filtros.zona_inventario:
        query = query.filter(FormsContagem.zona_inventario == filtros.zona_inventario)
    
    if filtros.etiqueta_inventario:
        query = query.filter(FormsContagem.etiqueta_inventario == filtros.etiqueta_inventario)
    
    if filtros.part_number:
        query = query.filter(FormsContagem.part_number == filtros.part_number)
    
    if filtros.num_contagem:
        query = query.filter(FormsContagem.num_contagem == filtros.num_contagem)
    
    return query


@router.get("/csv")
def exportar_csv(
    planta: Optional[str] = None,
    zona_inventario: Optional[str] = None,
    etiqueta_inventario: Optional[str] = None,
    part_number: Optional[str] = None,
    num_contagem: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "CONTROLADORIA"))
):
    """
    Exporta contagens para CSV
    
    Disponível apenas para: admin e controladoria
    """
    # Criar filtros
    filtros = ContagemFiltros(
        planta=planta,
        zona_inventario=zona_inventario,
        etiqueta_inventario=etiqueta_inventario,
        part_number=part_number,
        num_contagem=num_contagem
    )
    
    # Buscar contagens com join do usuário
    query = db.query(FormsContagem).join(User, FormsContagem.usuario_id == User.id)
    query = aplicar_filtros(query, filtros)
    contagens = query.all()
    
    # Preparar dados
    columns = [
        'etiqueta_inventario', 'inventario_cod_texto', 'part_number_text',
        'planta_text', 'quantidade', 'zona_invent_no_text',
        'created_date', 'modified_date', 'created_by', 'created_by_email', 'lote'
    ]
    
    data = [
        {
            'etiqueta_inventario': f"{c.num_contagem}ª CONTAGEM",
            'inventario_cod_texto': c.etiqueta_inventario,
            'part_number_text': c.part_number,
            'planta_text': c.planta,
            'quantidade': c.qtd,
            'zona_invent_no_text': obter_zona_completa(c.planta, c.zona_inventario),
            'created_date': c.timestamp.strftime('%b %d, %Y %I:%M %p') if c.timestamp else '',
            'modified_date': c.updated_at.strftime('%b %d, %Y %I:%M %p') if c.updated_at else '',
            'created_by': c.usuario.user_name if c.usuario else '',
            'created_by_email': c.usuario.email if c.usuario and c.usuario.email else f"{c.usuario.user_name}@inventario.com" if c.usuario else '',
            'lote': c.lote or ''
        }
        for c in contagens
    ]
    
    # Gerar CSV
    csv_content = generate_csv(data, columns)
    
    # Retornar como arquivo
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=contagens.csv"
        }
    )


@router.get("/excel")
def exportar_excel(
    planta: Optional[str] = None,
    zona_inventario: Optional[str] = None,
    etiqueta_inventario: Optional[str] = None,
    part_number: Optional[str] = None,
    num_contagem: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "CONTROLADORIA"))
):
    """
    Exporta contagens para Excel
    
    Disponível apenas para: admin e controladoria
    """
    # Criar filtros
    filtros = ContagemFiltros(
        planta=planta,
        zona_inventario=zona_inventario,
        etiqueta_inventario=etiqueta_inventario,
        part_number=part_number,
        num_contagem=num_contagem
    )
    
    # Buscar contagens com join do usuário
    query = db.query(FormsContagem).join(User, FormsContagem.usuario_id == User.id)
    query = aplicar_filtros(query, filtros)
    contagens = query.all()
    
    # Preparar dados
    columns = [
        'etiqueta_inventario', 'inventario_cod_texto', 'part_number_text',
        'planta_text', 'quantidade', 'zona_invent_no_text',
        'created_date', 'modified_date', 'created_by', 'created_by_email', 'lote'
    ]
    
    data = [
        {
            'etiqueta_inventario': f"{c.num_contagem}ª CONTAGEM",
            'inventario_cod_texto': c.etiqueta_inventario,
            'part_number_text': c.part_number,
            'planta_text': c.planta,
            'quantidade': c.qtd,
            'zona_invent_no_text': obter_zona_completa(c.planta, c.zona_inventario),
            'created_date': c.timestamp.strftime('%b %d, %Y %I:%M %p') if c.timestamp else '',
            'modified_date': c.updated_at.strftime('%b %d, %Y %I:%M %p') if c.updated_at else '',
            'created_by': c.usuario.user_name if c.usuario else '',
            'created_by_email': c.usuario.email if c.usuario and c.usuario.email else f"{c.usuario.user_name}@inventario.com" if c.usuario else '',
            'lote': c.lote or ''
        }
        for c in contagens
    ]
    
    # Gerar Excel
    excel_bytes = generate_excel(data, columns)
    
    # Retornar como arquivo
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=contagens.xlsx"
        }
    )
