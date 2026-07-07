import io

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_tenant_filter
from app.cracha.gerador_service import gerar_cracha
from app.models.colaborador import Colaborador
from app.models.tenant import Tenant
from app.schemas.cracha import PreviewRequest

router = APIRouter(prefix="/cracha", tags=["cracha"])


def _montar_dados_cracha(colaborador: Colaborador, tenant: Tenant, template_id: str) -> dict:
    return {
        "qr_token": str(colaborador.qr_token),
        "nome": colaborador.nome,
        "cargo": colaborador.cargo,
        "foto_url": colaborador.foto_url,
        "nome_empresa": tenant.nome_empresa,
        "logo_url": tenant.logo_url,
        "cor_primaria": tenant.cor_primaria,
        "cor_secundaria": tenant.cor_secundaria,
        "em_treinamento": colaborador.em_treinamento,
        "pcd": colaborador.pcd,
        "pcd_descricao": colaborador.pcd_descricao,
        "campos_adicionais": colaborador.campos_adicionais,
        "faixas_customizadas": tenant.faixas_customizadas,
        "template_id": template_id,
    }


@router.post("/preview")
def preview_cracha(
    payload: PreviewRequest,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    query = db.query(Colaborador).filter(Colaborador.id == payload.colaborador_id)
    for campo, valor in filtro.items():
        query = query.filter(getattr(Colaborador, campo) == valor)
    colaborador = query.first()
    if not colaborador:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Colaborador não encontrado")

    tenant = db.query(Tenant).filter(Tenant.id == colaborador.tenant_id).first()
    dados = _montar_dados_cracha(colaborador, tenant, payload.template_id)
    imagem = gerar_cracha(dados)

    buffer = io.BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="image/png")
