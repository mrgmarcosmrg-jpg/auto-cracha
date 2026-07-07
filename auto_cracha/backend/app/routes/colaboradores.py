import csv
import io
import urllib.parse
import uuid
from datetime import datetime
from typing import List, Optional

import openpyxl
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.dependencies import get_tenant_filter, montar_filtro_tenant, require_gestor_or_above
from app.core.encryption import gerar_cpf_hash
from app.models.colaborador import Colaborador, StatusColaborador
from app.models.consentimento_lgpd import ConsentimentoLgpd, StatusConsentimento
from app.models.filial import Filial
from app.models.usuario import PerfilUsuario, Usuario
from app.schemas.colaborador import (
    ColaboradorCreate,
    ColaboradorCriadoOut,
    ColaboradorOut,
    ColaboradorUpdate,
    ImportarResultado,
    LinkLgpdOut,
)

router = APIRouter(prefix="/colaboradores", tags=["colaboradores"])


def _limpar_digitos(valor: Optional[str]) -> str:
    return "".join(filter(str.isdigit, valor or ""))


def _aplicar_cpf(colaborador: Colaborador, cpf: str) -> None:
    cpf_limpo = _limpar_digitos(cpf)
    colaborador.cpf = cpf_limpo
    colaborador.cpf_hash = gerar_cpf_hash(cpf_limpo)


def _montar_link_lgpd(colaborador: Colaborador) -> LinkLgpdOut:
    link = f"{settings.APP_URL}/meu-cracha/{colaborador.qr_token}"
    texto = f"Olá {colaborador.nome}, acesse seu link de crachá: {link}"
    celular_limpo = _limpar_digitos(colaborador.celular)
    whatsapp_url = f"https://wa.me/55{celular_limpo}?text={urllib.parse.quote_plus(texto)}"
    return LinkLgpdOut(link=link, whatsapp_url=whatsapp_url)


def _obter_colaborador(db: Session, colaborador_id: uuid.UUID, filtro: dict) -> Colaborador:
    query = db.query(Colaborador).filter(Colaborador.id == colaborador_id)
    for campo, valor in filtro.items():
        query = query.filter(getattr(Colaborador, campo) == valor)
    colaborador = query.first()
    if not colaborador:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Colaborador não encontrado")
    return colaborador


def _validar_e_resolver_filial(db: Session, usuario: Usuario, filial_id_solicitado: Optional[uuid.UUID]) -> uuid.UUID:
    if usuario.perfil == PerfilUsuario.GESTOR_FILIAL:
        if filial_id_solicitado and filial_id_solicitado != usuario.filial_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Gestor de filial só pode usar a própria filial")
        return usuario.filial_id

    if not filial_id_solicitado:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "filial_id é obrigatório")

    filial = (
        db.query(Filial)
        .filter(Filial.id == filial_id_solicitado, Filial.tenant_id == usuario.tenant_id)
        .first()
    )
    if not filial:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Filial não encontrada")
    return filial.id


@router.get("", response_model=List[ColaboradorOut])
def listar_colaboradores(
    filial_id: Optional[uuid.UUID] = None,
    status_colaborador: Optional[StatusColaborador] = Query(None, alias="status"),
    em_treinamento: Optional[bool] = None,
    pcd: Optional[bool] = None,
    busca: Optional[str] = None,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    query = db.query(Colaborador)
    for campo, valor in filtro.items():
        query = query.filter(getattr(Colaborador, campo) == valor)
    if filial_id:
        query = query.filter(Colaborador.filial_id == filial_id)
    if status_colaborador:
        query = query.filter(Colaborador.status == status_colaborador)
    if em_treinamento is not None:
        query = query.filter(Colaborador.em_treinamento == em_treinamento)
    if pcd is not None:
        query = query.filter(Colaborador.pcd == pcd)
    if busca:
        digitos = _limpar_digitos(busca)
        if len(digitos) == 11:
            query = query.filter(Colaborador.cpf_hash == gerar_cpf_hash(digitos))
        else:
            query = query.filter(Colaborador.nome.ilike(f"%{busca}%"))
    return query.order_by(Colaborador.nome).all()


@router.get("/template-csv")
def baixar_template_csv(usuario: Usuario = Depends(require_gestor_or_above)):
    conteudo = "nome,cargo,celular,email,cpf,filial_nome\n"
    return Response(
        content=conteudo,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=colaboradores_template.csv"},
    )


def _ler_linhas_arquivo(filename: str, conteudo: bytes) -> List[dict]:
    nome_arquivo = filename.lower()
    if nome_arquivo.endswith(".csv"):
        texto = conteudo.decode("utf-8-sig")
        return [dict(linha) for linha in csv.DictReader(io.StringIO(texto))]

    if nome_arquivo.endswith(".xlsx"):
        planilha = openpyxl.load_workbook(io.BytesIO(conteudo), read_only=True).active
        linhas_iter = planilha.iter_rows(values_only=True)
        cabecalho = [str(c).strip().lower() if c else "" for c in next(linhas_iter)]
        linhas = []
        for linha in linhas_iter:
            linhas.append({cabecalho[i]: linha[i] for i in range(len(cabecalho)) if i < len(linha)})
        return linhas

    raise HTTPException(status.HTTP_400_BAD_REQUEST, "Formato não suportado. Envie .csv ou .xlsx")


@router.post("/importar", response_model=ImportarResultado)
def importar_colaboradores(
    arquivo: UploadFile = File(...),
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    linhas = _ler_linhas_arquivo(arquivo.filename or "", arquivo.file.read())
    filiais_por_nome = {
        f.nome.strip().lower(): f for f in db.query(Filial).filter(Filial.tenant_id == usuario.tenant_id).all()
    }

    importados = 0
    erros = []
    for indice, linha in enumerate(linhas, start=2):  # linha 1 é o cabeçalho
        nome = str(linha.get("nome") or "").strip()
        cargo = str(linha.get("cargo") or "").strip()
        celular = str(linha.get("celular") or "").strip()
        if not nome or not cargo or not celular:
            erros.append({"linha": indice, "motivo": "nome, cargo e celular são obrigatórios"})
            continue

        if usuario.perfil == PerfilUsuario.GESTOR_FILIAL:
            filial_id = usuario.filial_id
        else:
            filial_nome = str(linha.get("filial_nome") or "").strip().lower()
            filial = filiais_por_nome.get(filial_nome)
            if not filial:
                erros.append({"linha": indice, "motivo": f"filial '{linha.get('filial_nome')}' não encontrada"})
                continue
            filial_id = filial.id

        colaborador = Colaborador(
            tenant_id=usuario.tenant_id,
            filial_id=filial_id,
            nome=nome,
            cargo=cargo,
            celular=celular,
            email_colaborador=str(linha.get("email") or "").strip() or None,
            status=StatusColaborador.PENDENTE_LGPD,
        )
        cpf = str(linha.get("cpf") or "").strip()
        if cpf:
            _aplicar_cpf(colaborador, cpf)

        db.add(colaborador)
        db.flush()
        db.add(ConsentimentoLgpd(colaborador_id=colaborador.id, status=StatusConsentimento.PENDENTE))
        importados += 1

    db.commit()
    return ImportarResultado(importados=importados, erros=erros)


@router.post("", response_model=ColaboradorCriadoOut, status_code=status.HTTP_201_CREATED)
def criar_colaborador(
    payload: ColaboradorCreate,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    filial_id = _validar_e_resolver_filial(db, usuario, payload.filial_id)

    colaborador = Colaborador(
        tenant_id=usuario.tenant_id,
        filial_id=filial_id,
        nome=payload.nome,
        cargo=payload.cargo,
        celular=payload.celular,
        email_colaborador=payload.email_colaborador,
        em_treinamento=payload.em_treinamento,
        pcd=payload.pcd,
        pcd_descricao=payload.pcd_descricao,
        campos_adicionais=payload.campos_adicionais,
        status=StatusColaborador.PENDENTE_LGPD,
    )
    if payload.cpf:
        _aplicar_cpf(colaborador, payload.cpf)

    db.add(colaborador)
    db.flush()
    db.add(ConsentimentoLgpd(colaborador_id=colaborador.id, status=StatusConsentimento.PENDENTE))
    db.commit()
    db.refresh(colaborador)

    base = ColaboradorOut.model_validate(colaborador, from_attributes=True)
    return ColaboradorCriadoOut(**base.model_dump(), link_lgpd=_montar_link_lgpd(colaborador))


@router.get("/{colaborador_id}", response_model=ColaboradorOut)
def obter_colaborador(
    colaborador_id: uuid.UUID,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    return _obter_colaborador(db, colaborador_id, filtro)


@router.put("/{colaborador_id}", response_model=ColaboradorOut)
def atualizar_colaborador(
    colaborador_id: uuid.UUID,
    payload: ColaboradorUpdate,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    colaborador = _obter_colaborador(db, colaborador_id, montar_filtro_tenant(usuario))
    dados = payload.model_dump(exclude_unset=True)

    if "filial_id" in dados:
        dados["filial_id"] = _validar_e_resolver_filial(db, usuario, dados["filial_id"])
    if "cpf" in dados:
        cpf = dados.pop("cpf")
        if cpf:
            _aplicar_cpf(colaborador, cpf)

    for campo, valor in dados.items():
        setattr(colaborador, campo, valor)

    db.commit()
    db.refresh(colaborador)
    return colaborador


@router.post("/{colaborador_id}/desligar", response_model=ColaboradorOut)
def desligar_colaborador(
    colaborador_id: uuid.UUID,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    colaborador = _obter_colaborador(db, colaborador_id, montar_filtro_tenant(usuario))
    colaborador.status = StatusColaborador.DESLIGADO
    colaborador.data_desligamento = datetime.utcnow()
    db.commit()
    db.refresh(colaborador)
    return colaborador


@router.post("/{colaborador_id}/reativar", response_model=ColaboradorOut)
def reativar_colaborador(
    colaborador_id: uuid.UUID,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    colaborador = _obter_colaborador(db, colaborador_id, montar_filtro_tenant(usuario))
    colaborador.status = StatusColaborador.PENDENTE_LGPD
    colaborador.data_desligamento = None
    db.add(ConsentimentoLgpd(colaborador_id=colaborador.id, status=StatusConsentimento.PENDENTE))
    db.commit()
    db.refresh(colaborador)
    return colaborador


@router.get("/{colaborador_id}/link-lgpd", response_model=LinkLgpdOut)
def obter_link_lgpd(
    colaborador_id: uuid.UUID,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    colaborador = _obter_colaborador(db, colaborador_id, filtro)
    consentimento = (
        db.query(ConsentimentoLgpd)
        .filter(ConsentimentoLgpd.colaborador_id == colaborador.id)
        .order_by(ConsentimentoLgpd.criado_em.desc())
        .first()
    )
    if consentimento and not consentimento.link_enviado_em:
        consentimento.link_enviado_em = datetime.utcnow()
        db.commit()
    return _montar_link_lgpd(colaborador)
