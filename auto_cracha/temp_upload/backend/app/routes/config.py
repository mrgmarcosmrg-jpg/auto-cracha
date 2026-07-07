from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import require_admin_tenant
from app.models.config_empresa import ConfigEmpresa
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.schemas.config import ConfigOut, ContatoUpdate, IdentidadeUpdate, SetorUpdate, TemplateUpdate
from app.services.cloudinary_service import upload_imagem

router = APIRouter(prefix="/config", tags=["config"])


def _obter_tenant_e_config(db: Session, tenant_id) -> tuple[Tenant, ConfigEmpresa]:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    config = db.query(ConfigEmpresa).filter(ConfigEmpresa.tenant_id == tenant_id).first()
    return tenant, config


def _montar_config_out(tenant: Tenant, config: ConfigEmpresa) -> ConfigOut:
    return ConfigOut(
        nome_empresa=tenant.nome_empresa,
        cnpj=tenant.cnpj,
        logo_url=tenant.logo_url,
        logo_grupo_url=tenant.logo_grupo_url,
        cor_primaria=tenant.cor_primaria,
        cor_secundaria=tenant.cor_secundaria,
        usar_faixa_treinamento=tenant.usar_faixa_treinamento,
        usar_faixa_pcd=tenant.usar_faixa_pcd,
        faixas_customizadas=tenant.faixas_customizadas,
        status=tenant.status.value,
        trial_expira_em=tenant.trial_expira_em,
        template_id=config.template_id,
        setor_sugerido=config.setor_sugerido,
        campos_adicionais_config=config.campos_adicionais_config,
        redes_sociais=config.redes_sociais,
        telefone=config.telefone,
        whatsapp=config.whatsapp,
        email_empresa=config.email_empresa,
        endereco_completo=config.endereco_completo,
        nome_fantasia=config.nome_fantasia,
        razao_social=config.razao_social,
    )


@router.get("", response_model=ConfigOut)
def obter_config(usuario: Usuario = Depends(require_admin_tenant), db: Session = Depends(get_db)):
    tenant, config = _obter_tenant_e_config(db, usuario.tenant_id)
    return _montar_config_out(tenant, config)


@router.put("/identidade", response_model=ConfigOut)
def atualizar_identidade(
    payload: IdentidadeUpdate,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    tenant, config = _obter_tenant_e_config(db, usuario.tenant_id)
    dados = payload.model_dump(exclude_unset=True)
    for campo in ("logo_url", "logo_grupo_url", "cor_primaria", "cor_secundaria"):
        if campo in dados:
            setattr(tenant, campo, dados[campo])
    for campo in ("nome_fantasia", "razao_social"):
        if campo in dados:
            setattr(config, campo, dados[campo])
    db.commit()
    return _montar_config_out(tenant, config)


@router.put("/contato", response_model=ConfigOut)
def atualizar_contato(
    payload: ContatoUpdate,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    tenant, config = _obter_tenant_e_config(db, usuario.tenant_id)
    for campo, valor in payload.model_dump(exclude_unset=True).items():
        setattr(config, campo, valor)
    db.commit()
    return _montar_config_out(tenant, config)


@router.put("/template", response_model=ConfigOut)
def atualizar_template(
    payload: TemplateUpdate,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    tenant, config = _obter_tenant_e_config(db, usuario.tenant_id)
    config.template_id = payload.template_id
    db.commit()
    return _montar_config_out(tenant, config)


@router.put("/setor", response_model=ConfigOut)
def atualizar_setor(
    payload: SetorUpdate,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    tenant, config = _obter_tenant_e_config(db, usuario.tenant_id)
    dados = payload.model_dump(exclude_unset=True)
    for campo in ("setor_sugerido", "campos_adicionais_config"):
        if campo in dados:
            setattr(config, campo, dados[campo])
    for campo in ("faixas_customizadas", "usar_faixa_treinamento", "usar_faixa_pcd"):
        if campo in dados:
            setattr(tenant, campo, dados[campo])
    db.commit()
    return _montar_config_out(tenant, config)


@router.post("/logo")
def upload_logo(
    arquivo: UploadFile = File(...),
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    tenant, _ = _obter_tenant_e_config(db, usuario.tenant_id)
    url = upload_imagem(arquivo.file.read(), folder=f"tenants/{tenant.id}/logo")
    tenant.logo_url = url
    db.commit()
    return {"logo_url": url}


@router.post("/logo-grupo")
def upload_logo_grupo(
    arquivo: UploadFile = File(...),
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    tenant, _ = _obter_tenant_e_config(db, usuario.tenant_id)
    url = upload_imagem(arquivo.file.read(), folder=f"tenants/{tenant.id}/logo-grupo")
    tenant.logo_grupo_url = url
    db.commit()
    return {"logo_grupo_url": url}
