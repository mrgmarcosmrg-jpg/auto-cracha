import hashlib
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.encryption import descriptografar_com_chave
from app.core.rate_limit import JANELA_SEGUNDOS, bloqueado_por_segundos, limpar, registrar_tentativa, tentativas_restantes
from app.core.security import verificar_pin
from app.models.colaborador import Colaborador, StatusColaborador
from app.models.config_empresa import ConfigEmpresa
from app.models.tenant import Tenant
from app.schemas.publico import ColaboradorPublicoOut, EmpresaPublicaOut, PaginaPublicaOut, SosRequest

router = APIRouter(tags=["publico"])


def _obter_colaborador_por_token(db: Session, qr_token: uuid.UUID) -> Colaborador:
    colaborador = db.query(Colaborador).filter(Colaborador.qr_token == qr_token).first()
    if not colaborador:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Crachá não encontrado")
    return colaborador


@router.get("/p/{qr_token}", response_model=PaginaPublicaOut)
def pagina_publica(qr_token: uuid.UUID, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador_por_token(db, qr_token)
    tenant = db.query(Tenant).filter(Tenant.id == colaborador.tenant_id).first()
    config = db.query(ConfigEmpresa).filter(ConfigEmpresa.tenant_id == colaborador.tenant_id).first()

    empresa = EmpresaPublicaOut(
        nome_fantasia=(config.nome_fantasia if config else None) or tenant.nome_empresa,
        razao_social=config.razao_social if config else None,
        logo_url=tenant.logo_url,
        endereco_completo=config.endereco_completo if config else None,
        telefone=config.telefone if config else None,
        whatsapp=config.whatsapp if config else None,
        email_empresa=config.email_empresa if config else None,
        redes_sociais=config.redes_sociais if config else None,
    )

    acesso_expirado = (
        colaborador.status == StatusColaborador.VISITANTE
        and colaborador.visitante_expira_em is not None
        and colaborador.visitante_expira_em < datetime.utcnow()
    )

    colaborador_out = ColaboradorPublicoOut(
        status=colaborador.status,
        nome=colaborador.nome,
        acesso_expirado=acesso_expirado,
    )

    pode_exibir_dados_completos = not acesso_expirado and colaborador.status in (
        StatusColaborador.ATIVO,
        StatusColaborador.VISITANTE,
    )

    if colaborador.status == StatusColaborador.DESLIGADO:
        colaborador_out.cargo = colaborador.cargo
        colaborador_out.foto_url = colaborador.foto_url
        colaborador_out.data_desligamento = colaborador.data_desligamento
    elif pode_exibir_dados_completos:
        colaborador_out.cargo = colaborador.cargo
        colaborador_out.foto_url = colaborador.foto_url
        colaborador_out.exibir_contato_pessoal = colaborador.exibir_contato_pessoal
        if colaborador.exibir_contato_pessoal:
            colaborador_out.celular = colaborador.celular
            colaborador_out.email_colaborador = colaborador.email_colaborador
        colaborador_out.contato_emergencia_nome = colaborador.contato_emergencia_nome
        colaborador_out.contato_emergencia_tel = colaborador.contato_emergencia_tel
        colaborador_out.tem_sos = colaborador.pin_emergencia_hash is not None
    # PENDENTE_LGPD e acesso_expirado: só nome + status, já preenchidos acima.

    return PaginaPublicaOut(empresa=empresa, colaborador=colaborador_out)


@router.post("/p/{qr_token}/sos")
def consultar_sos(qr_token: uuid.UUID, payload: SosRequest, request: Request, db: Session = Depends(get_db)):
    chave_rate = f"sos:{request.client.host if request.client else 'desconhecido'}"

    segundos = bloqueado_por_segundos(chave_rate)
    if segundos > 0:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail={"bloqueado_por_segundos": segundos})

    colaborador = _obter_colaborador_por_token(db, qr_token)
    if not colaborador.pin_emergencia_hash or not colaborador.dados_medicos_crypto:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dados de emergência não cadastrados")

    if not verificar_pin(payload.pin, colaborador.pin_emergencia_hash):
        registrar_tentativa(chave_rate)
        restantes = tentativas_restantes(chave_rate)
        if restantes == 0:
            raise HTTPException(
                status.HTTP_429_TOO_MANY_REQUESTS, detail={"bloqueado_por_segundos": JANELA_SEGUNDOS}
            )
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail={"tentativas_restantes": restantes})

    limpar(chave_rate)
    chave_aes = hashlib.pbkdf2_hmac("sha256", payload.pin.encode("utf-8"), str(colaborador.id).encode("utf-8"), 100_000)
    dados_json = descriptografar_com_chave(colaborador.dados_medicos_crypto, chave_aes)
    return json.loads(dados_json)
