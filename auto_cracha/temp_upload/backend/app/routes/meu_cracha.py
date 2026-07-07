import hashlib
import json
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.encryption import criptografar_com_chave, descriptografar_com_chave
from app.core.security import hash_pin, verificar_pin
from app.cracha.utils.cloudinary_service import upload_foto
from app.models.colaborador import Colaborador, StatusColaborador
from app.models.consentimento_lgpd import ConsentimentoLgpd, StatusConsentimento
from app.schemas.meu_cracha import (
    AlterarPinRequest,
    AtualizarDadosMedicosRequest,
    ContatoVisivelRequest,
    CriarDadosMedicosRequest,
    DadosMedicosCampos,
    MeuCrachaOut,
)

router = APIRouter(prefix="/meu-cracha", tags=["meu-cracha"])


def _obter_colaborador(db: Session, qr_token: uuid.UUID) -> Colaborador:
    colaborador = db.query(Colaborador).filter(Colaborador.qr_token == qr_token).first()
    if not colaborador:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Link inválido")
    return colaborador


def _derivar_chave(pin: str, colaborador_id: uuid.UUID) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), str(colaborador_id).encode("utf-8"), 100_000)


def _montar_meu_cracha_out(colaborador: Colaborador) -> MeuCrachaOut:
    return MeuCrachaOut(
        nome=colaborador.nome,
        cargo=colaborador.cargo,
        foto_url=colaborador.foto_url,
        exibir_contato_pessoal=colaborador.exibir_contato_pessoal,
        status=colaborador.status.value,
        tem_dados_medicos=colaborador.dados_medicos_crypto is not None,
        data_nascimento=colaborador.data_nascimento,
        contato_emergencia_nome=colaborador.contato_emergencia_nome,
        contato_emergencia_tel=colaborador.contato_emergencia_tel,
    )


def _montar_json_medico(payload: DadosMedicosCampos) -> str:
    return json.dumps(
        {
            "tipo_sanguineo": payload.tipo_sanguineo,
            "comorbidades": payload.comorbidades,
            "remedios_eventuais": payload.remedios_eventuais,
            "remedios_continuos": payload.remedios_continuos,
            "plano_saude": payload.plano_saude,
            "alergenicos": payload.alergenicos,
        }
    )


@router.get("/{qr_token}", response_model=MeuCrachaOut)
def obter_meu_cracha(qr_token: uuid.UUID, db: Session = Depends(get_db)):
    return _montar_meu_cracha_out(_obter_colaborador(db, qr_token))


def _registrar_resposta_consentimento(db: Session, colaborador: Colaborador, request: Request, status_novo: StatusConsentimento) -> None:
    consentimento = (
        db.query(ConsentimentoLgpd)
        .filter(ConsentimentoLgpd.colaborador_id == colaborador.id)
        .order_by(ConsentimentoLgpd.criado_em.desc())
        .first()
    )
    if consentimento:
        consentimento.status = status_novo
        consentimento.respondido_em = datetime.utcnow()
        consentimento.ip_resposta = request.client.host if request.client else None


@router.post("/{qr_token}/autorizar")
def autorizar_dados(qr_token: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)
    _registrar_resposta_consentimento(db, colaborador, request, StatusConsentimento.AUTORIZADO)
    if colaborador.status == StatusColaborador.PENDENTE_LGPD:
        colaborador.status = StatusColaborador.ATIVO
    db.commit()
    return {"status": colaborador.status.value}


@router.post("/{qr_token}/recusar")
def recusar_dados(qr_token: uuid.UUID, request: Request, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)
    _registrar_resposta_consentimento(db, colaborador, request, StatusConsentimento.RECUSADO)
    db.commit()
    return {"status": "RECUSADO"}


@router.patch("/{qr_token}/foto", response_model=MeuCrachaOut)
def atualizar_foto(qr_token: uuid.UUID, arquivo: UploadFile = File(...), db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)
    colaborador.foto_url = upload_foto(arquivo.file.read(), folder=f"colaboradores/{colaborador.id}/foto")
    db.commit()
    db.refresh(colaborador)
    return _montar_meu_cracha_out(colaborador)


@router.patch("/{qr_token}/contato-visivel")
def atualizar_contato_visivel(qr_token: uuid.UUID, payload: ContatoVisivelRequest, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)
    colaborador.exibir_contato_pessoal = payload.exibir_contato_pessoal
    db.commit()
    return {"exibir_contato_pessoal": colaborador.exibir_contato_pessoal}


@router.post("/{qr_token}/dados-medicos", status_code=status.HTTP_201_CREATED)
def criar_dados_medicos(qr_token: uuid.UUID, payload: CriarDadosMedicosRequest, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)

    chave = _derivar_chave(payload.pin, colaborador.id)
    colaborador.dados_medicos_crypto = criptografar_com_chave(_montar_json_medico(payload), chave)
    colaborador.pin_emergencia_hash = hash_pin(payload.pin)
    colaborador.data_nascimento = payload.data_nascimento
    colaborador.contato_emergencia_nome = payload.contato_emergencia_nome
    colaborador.contato_emergencia_tel = payload.contato_emergencia_tel

    db.commit()
    return {"detail": "Dados de emergência cadastrados."}


@router.patch("/{qr_token}/dados-medicos")
def atualizar_dados_medicos(qr_token: uuid.UUID, payload: AtualizarDadosMedicosRequest, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)
    if not colaborador.pin_emergencia_hash:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nenhum PIN cadastrado ainda")
    if not verificar_pin(payload.pin_atual, colaborador.pin_emergencia_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "PIN incorreto")

    chave = _derivar_chave(payload.pin_atual, colaborador.id)
    colaborador.dados_medicos_crypto = criptografar_com_chave(_montar_json_medico(payload), chave)
    colaborador.data_nascimento = payload.data_nascimento
    colaborador.contato_emergencia_nome = payload.contato_emergencia_nome
    colaborador.contato_emergencia_tel = payload.contato_emergencia_tel

    db.commit()
    return {"detail": "Dados de emergência atualizados."}


@router.patch("/{qr_token}/pin")
def alterar_pin(qr_token: uuid.UUID, payload: AlterarPinRequest, db: Session = Depends(get_db)):
    colaborador = _obter_colaborador(db, qr_token)
    if not colaborador.pin_emergencia_hash or not colaborador.dados_medicos_crypto:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Nenhum PIN cadastrado ainda")
    if not verificar_pin(payload.pin_atual, colaborador.pin_emergencia_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "PIN atual incorreto")

    chave_atual = _derivar_chave(payload.pin_atual, colaborador.id)
    dados_json = descriptografar_com_chave(colaborador.dados_medicos_crypto, chave_atual)

    chave_nova = _derivar_chave(payload.pin_novo, colaborador.id)
    colaborador.dados_medicos_crypto = criptografar_com_chave(dados_json, chave_nova)
    colaborador.pin_emergencia_hash = hash_pin(payload.pin_novo)

    db.commit()
    return {"detail": "PIN atualizado."}
