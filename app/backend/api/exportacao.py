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


@router.get("/preview")
def preview_dados(
    planta: Optional[str] = None,
    zona_inventario: Optional[str] = None,
    etiqueta_inventario: Optional[str] = None,
    part_number: Optional[str] = None,
    num_contagem: Optional[int] = None,
    limit: int = Query(default=100, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO"))
):
    """
    Preview dos dados que serão exportados
    
    Disponível apenas para: admin e encarregado
    """
    # Criar filtros
    filtros = ContagemFiltros(
        planta=planta,
        zona_inventario=zona_inventario,
        etiqueta_inventario=etiqueta_inventario,
        part_number=part_number,
        num_contagem=num_contagem
    )
    
    # Buscar contagens
    query = db.query(FormsContagem)
    query = aplicar_filtros(query, filtros)
    
    # Contar total
    total = query.count()
    
    # Limitar resultados para preview
    contagens = query.limit(limit).all()
    
    # Preparar dados
    data = [
        {
            'id': c.id,
            'planta': c.planta,
            'num_contagem': c.num_contagem,
            'zona_inventario': c.zona_inventario,
            'etiqueta_inventario': c.etiqueta_inventario,
            'part_number': c.part_number,
            'campo': c.campo or '',
            'qtd': c.qtd,
            'timestamp': c.timestamp.isoformat() if c.timestamp else None
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
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO"))
):
    """
    Exporta contagens para CSV
    
    Disponível apenas para: admin e encarregado
    """
    # Criar filtros
    filtros = ContagemFiltros(
        planta=planta,
        zona_inventario=zona_inventario,
        etiqueta_inventario=etiqueta_inventario,
        part_number=part_number,
        num_contagem=num_contagem
    )
    
    # Buscar contagens
    query = db.query(FormsContagem)
    query = aplicar_filtros(query, filtros)
    contagens = query.all()
    
    # Preparar dados
    columns = [
        'planta', 'num_contagem', 'zona_inventario',
        'etiqueta_inventario', 'part_number', 'campo', 'qtd'
    ]
    
    data = [
        {
            'planta': c.planta,
            'num_contagem': c.num_contagem,
            'zona_inventario': c.zona_inventario,
            'etiqueta_inventario': c.etiqueta_inventario,
            'part_number': c.part_number,
            'campo': c.campo or '',
            'qtd': c.qtd
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
    part_number: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("ADMIN", "ENCARREGADO"))
):
    """
    Exporta contagens para Excel
    
    Disponível apenas para: admin e encarregado
    """
    # Criar filtros
    filtros = ContagemFiltros(
        planta=planta,
        zona_inventario=zona_inventario,
        etiqueta_inventario=etiqueta_inventario,
        part_number=part_number,
        num_contagem=num_contagem
    )
    
    # Buscar contagens
    query = db.query(FormsContagem)
    query = aplicar_filtros(query, filtros)
    contagens = query.all()
    
    # Preparar dados
    columns = [
        'planta', 'num_contagem', 'zona_inventario',
        'etiqueta_inventario', 'part_number', 'campo', 'qtd'
    ]
    
    data = [
        {
            'planta': c.planta,
            'num_contagem': c.num_contagem,
            'zona_inventario': c.zona_inventario,
            'etiqueta_inventario': c.etiqueta_inventario,
            'part_number': c.part_number,
            'campo': c.campo or '',
            'qtd': c.qtd
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
