import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_user, get_tenant_filter, montar_filtro_tenant
from app.models.colaborador import Colaborador
from app.models.usuario import Usuario
from app.models.config_empresa import ConfigEmpresa
from app.cracha.gerador_service import GeradorCracha


router = APIRouter(prefix="/cracha", tags=["cracha"])


@router.post("/preview")
def preview_cracha(
    colaborador_id: uuid.UUID = Query(...),
    template_id: str = Query("vertical_padrao"),
    usuario: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gera preview PNG de um crachá para um colaborador.
    
    Retorna o crachá renderizado como PNG stream para teste visual.
    """
    try:
        # Validar filtro multitenant
        filtro = montar_filtro_tenant(usuario)
        
        # Buscar colaborador
        query = db.query(Colaborador).filter(Colaborador.id == colaborador_id)
        for campo, valor in filtro.items():
            query = query.filter(getattr(Colaborador, campo) == valor)
        
        colaborador = query.first()
        if not colaborador:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Colaborador não encontrado")
        
        # Buscar configuração da empresa
        config = db.query(ConfigEmpresa).filter(
            ConfigEmpresa.tenant_id == usuario.tenant_id
        ).first()
        
        config_dict = {
            'nome_empresa': config.nome_empresa if config else 'Empresa',
            'logo_url': config.logo_url if config else None,
        }
        
        # Preparar dados do colaborador
        colaborador_dict = {
            'id': str(colaborador.id),
            'nome': colaborador.nome,
            'cargo': colaborador.cargo,
            'foto_url': colaborador.foto_url,
            'em_treinamento': colaborador.em_treinamento,
            'pcd': colaborador.pcd,
            'qr_token': colaborador.qr_token,
        }
        
        # Gerar crachá
        cracha_img = GeradorCracha.gerar(colaborador_dict, config_dict, template_id)
        
        if cracha_img is None:
            raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, "Erro ao gerar crachá")
        
        # Retornar como PNG
        from io import BytesIO
        img_bytes = BytesIO()
        cracha_img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return Response(
            content=img_bytes.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=cracha.png"}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Erro: {str(e)}")
