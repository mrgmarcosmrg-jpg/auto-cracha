import hashlib
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.dependencies import get_tenant_filter, montar_filtro_tenant, require_gestor_or_above
from app.cracha.gerador_service import gerar_cracha
from app.cracha.utils.cloudinary_service import upload_pdf
from app.cracha.utils.pdf import cartoes_por_pagina_3x3, cartoes_por_pagina_3x3_por_template, gerar_pdf_a4_3x3, gerar_pdf_a4_unitario
from app.models.assinatura import Assinatura, StatusAssinatura
from app.models.colaborador import Colaborador, StatusColaborador
from app.models.config_empresa import ConfigEmpresa
from app.models.consentimento_lgpd import ConsentimentoLgpd
from app.models.filial import Filial
from app.models.lote import (
    HistoricoLote,
    LoteCracha,
    LoteImpressao,
    MiniloteReimpressao,
    ModoImpressao,
    PagoVia,
    StatusCracha,
    StatusLote,
    StatusMinilote,
    TipoEventoHistorico,
)
from app.models.tenant import Tenant
from app.models.usuario import PerfilUsuario, Usuario
from app.schemas.lote import (
    CriarLoteRequest,
    FalhaRegistradaOut,
    HistoricoLoteOut,
    LoteCrachaOut,
    LoteCriadoOut,
    LoteDetalheOut,
    LoteOut,
    MarcarFalhaRequest,
    PdfUrlOut,
)

router = APIRouter(prefix="/lotes", tags=["lotes"])


def _obter_lote(db: Session, lote_id: uuid.UUID, filtro: dict) -> LoteImpressao:
    query = db.query(LoteImpressao).filter(LoteImpressao.id == lote_id)
    for campo, valor in filtro.items():
        query = query.filter(getattr(LoteImpressao, campo) == valor)
    lote = query.first()
    if not lote:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lote não encontrado")
    return lote


def _registrar_historico(
    db: Session,
    lote_id: uuid.UUID,
    usuario_id: Optional[uuid.UUID],
    tipo: TipoEventoHistorico,
    quantidade: Optional[int] = None,
    descricao: Optional[str] = None,
) -> None:
    db.add(
        HistoricoLote(
            lote_id=lote_id,
            usuario_id=usuario_id,
            tipo_evento=tipo,
            quantidade_afetada=quantidade,
            descricao=descricao,
        )
    )


def _recalcular_status_lote(lote: LoteImpressao) -> None:
    total_processado = lote.quantidade_impressos + lote.quantidade_falhados
    if total_processado >= lote.quantidade_total:
        lote.status_lote = StatusLote.PARCIALMENTE_IMPRESSO if lote.quantidade_falhados > 0 else StatusLote.IMPRESSO
        lote.concluido_em = datetime.utcnow()
    else:
        lote.status_lote = StatusLote.IMPRIMINDO


def _verificar_permissao_lote(db: Session, tenant_id: uuid.UUID) -> Optional[str]:
    """Retorna o pago_via a registrar no lote (None quando coberto pela franquia do TRIAL)."""
    assinatura = db.query(Assinatura).filter(Assinatura.tenant_id == tenant_id).first()
    if not assinatura:
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "Assinatura não encontrada para o tenant")

    if assinatura.status == StatusAssinatura.ATIVO:
        return PagoVia.ASSINATURA.value

    if assinatura.status == StatusAssinatura.TRIAL:
        total_ativos = (
            db.query(Colaborador)
            .filter(Colaborador.tenant_id == tenant_id, Colaborador.status == StatusColaborador.ATIVO)
            .count()
        )
        if total_ativos <= assinatura.max_colaboradores:
            return None

    if assinatura.creditos_pix > 0:
        return PagoVia.PIX_AVULSO.value

    raise HTTPException(
        status.HTTP_402_PAYMENT_REQUIRED,
        detail={
            "mensagem": "Limite do plano atingido. Assine um plano ou compre créditos Pix para continuar.",
            "link_pagamento": f"{settings.APP_URL}/dashboard/plano",
        },
    )


@router.post("", response_model=LoteCriadoOut, status_code=status.HTTP_201_CREATED)
def criar_lote(
    payload: CriarLoteRequest,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    pago_via = _verificar_permissao_lote(db, usuario.tenant_id)

    filial_id = payload.filial_id or usuario.filial_id
    if not filial_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "filial_id é obrigatório")
    if usuario.perfil == PerfilUsuario.GESTOR_FILIAL and filial_id != usuario.filial_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Gestor de filial só pode criar lotes da própria filial")

    filial = db.query(Filial).filter(Filial.id == filial_id, Filial.tenant_id == usuario.tenant_id).first()
    if not filial:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Filial não encontrada")

    ids_unicos = list(dict.fromkeys(payload.colaborador_ids))
    colaboradores = (
        db.query(Colaborador)
        .filter(Colaborador.id.in_(ids_unicos), Colaborador.tenant_id == usuario.tenant_id)
        .all()
    )
    if len(colaboradores) != len(ids_unicos):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Um ou mais colaboradores não foram encontrados")

    nao_ativos = [c.nome for c in colaboradores if c.status != StatusColaborador.ATIVO]
    if nao_ativos:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Os colaboradores a seguir não estão ATIVOS: {', '.join(nao_ativos)}",
        )

    config_empresa = db.query(ConfigEmpresa).filter(ConfigEmpresa.tenant_id == usuario.tenant_id).first()
    template_id = config_empresa.template_id if config_empresa else "vertical_padrao"

    lote = LoteImpressao(
        tenant_id=usuario.tenant_id,
        filial_id=filial_id,
        usuario_criador_id=usuario.id,
        nome_lote=payload.nome_lote,
        status_lote=StatusLote.PENDENTE,
        quantidade_total=len(colaboradores),
        template_id=template_id,
        modo_impressao=payload.modo_impressao,
        pago_via=pago_via,
    )
    db.add(lote)
    db.flush()

    por_pagina = (
        cartoes_por_pagina_3x3_por_template(template_id) if payload.modo_impressao == ModoImpressao.A4_3X3 else 1
    )

    for indice, colaborador in enumerate(colaboradores):
        consentimento = (
            db.query(ConsentimentoLgpd)
            .filter(ConsentimentoLgpd.colaborador_id == colaborador.id)
            .order_by(ConsentimentoLgpd.criado_em.desc())
            .first()
        )
        filial_colaborador = db.query(Filial).filter(Filial.id == colaborador.filial_id).first()

        db.add(
            LoteCracha(
                lote_id=lote.id,
                colaborador_id=colaborador.id,
                status_cracha=StatusCracha.PENDENTE,
                posicao_na_pagina=(indice % por_pagina) + 1,
                numero_pagina=(indice // por_pagina) + 1,
                nome_snapshot=colaborador.nome,
                cargo_snapshot=colaborador.cargo,
                foto_url_snapshot=colaborador.foto_url,
                status_lgpd_snapshot=consentimento.status.value if consentimento else None,
                filial_nome_snapshot=filial_colaborador.nome if filial_colaborador else None,
            )
        )

    _registrar_historico(db, lote.id, usuario.id, TipoEventoHistorico.LOTE_CRIADO, quantidade=len(colaboradores))
    db.commit()

    total_paginas = (len(colaboradores) + por_pagina - 1) // por_pagina if colaboradores else 0
    return LoteCriadoOut(lote_id=lote.id, quantidade_total=len(colaboradores), total_paginas=total_paginas)


def _montar_dados_cracha_snapshot(lote: LoteImpressao, lote_cracha: LoteCracha, colaborador: Optional[Colaborador], tenant: Tenant) -> dict:
    return {
        "qr_token": str(colaborador.qr_token) if colaborador else "",
        "nome": lote_cracha.nome_snapshot,
        "cargo": lote_cracha.cargo_snapshot,
        "foto_url": lote_cracha.foto_url_snapshot,
        "nome_empresa": tenant.nome_empresa,
        "logo_url": tenant.logo_url,
        "cor_primaria": tenant.cor_primaria,
        "cor_secundaria": tenant.cor_secundaria,
        "em_treinamento": colaborador.em_treinamento if colaborador else False,
        "pcd": colaborador.pcd if colaborador else False,
        "pcd_descricao": colaborador.pcd_descricao if colaborador else None,
        "campos_adicionais": colaborador.campos_adicionais if colaborador else None,
        "faixas_customizadas": tenant.faixas_customizadas,
        "template_id": lote.template_id,
    }


@router.post("/{lote_id}/gerar-pdf", response_model=LoteOut)
def gerar_pdf_lote(
    lote_id: uuid.UUID,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, montar_filtro_tenant(usuario))
    if lote.status_lote != StatusLote.PENDENTE:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "O PDF deste lote já foi gerado")

    tenant = db.query(Tenant).filter(Tenant.id == lote.tenant_id).first()
    crachas = (
        db.query(LoteCracha)
        .filter(LoteCracha.lote_id == lote.id)
        .order_by(LoteCracha.numero_pagina, LoteCracha.posicao_na_pagina)
        .all()
    )
    colaboradores_por_id = {
        c.id: c
        for c in db.query(Colaborador).filter(Colaborador.id.in_([lc.colaborador_id for lc in crachas])).all()
    }

    imagens = [
        gerar_cracha(_montar_dados_cracha_snapshot(lote, lc, colaboradores_por_id.get(lc.colaborador_id), tenant))
        for lc in crachas
    ]

    if lote.modo_impressao == ModoImpressao.A4_3X3:
        pdf_bytes = gerar_pdf_a4_3x3(imagens)
        por_pagina = cartoes_por_pagina_3x3(imagens[0]) if imagens else 1
        total_paginas = (len(imagens) + por_pagina - 1) // por_pagina if imagens else 0
    else:
        pdf_bytes = gerar_pdf_a4_unitario(imagens)
        total_paginas = len(imagens)

    pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()
    pdf_url = upload_pdf(pdf_bytes, filename=f"lote_{lote.id}")

    lote.pdf_url = pdf_url
    lote.pdf_hash = pdf_hash
    lote.pdf_total_paginas = total_paginas
    lote.pdf_tamanho_kb = len(pdf_bytes) // 1024
    lote.pdf_gerado_em = datetime.utcnow()
    lote.status_lote = StatusLote.GERADO

    if lote.pago_via == PagoVia.PIX_AVULSO:
        db.query(Assinatura).filter(Assinatura.tenant_id == lote.tenant_id).update(
            {Assinatura.creditos_pix: Assinatura.creditos_pix - lote.quantidade_total}
        )

    _registrar_historico(db, lote.id, usuario.id, TipoEventoHistorico.PDF_GERADO, quantidade=len(imagens))
    db.commit()
    db.refresh(lote)
    return lote


@router.patch("/{lote_id}/crachas/{cracha_id}/impresso", response_model=LoteCrachaOut)
def marcar_cracha_impresso(
    lote_id: uuid.UUID,
    cracha_id: uuid.UUID,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, montar_filtro_tenant(usuario))
    cracha = db.query(LoteCracha).filter(LoteCracha.id == cracha_id, LoteCracha.lote_id == lote.id).first()
    if not cracha:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Crachá não encontrado neste lote")

    cracha.status_cracha = StatusCracha.IMPRESSO
    cracha.marcado_impresso_em = datetime.utcnow()

    db.query(LoteImpressao).filter(LoteImpressao.id == lote.id).update(
        {LoteImpressao.quantidade_impressos: LoteImpressao.quantidade_impressos + 1}
    )
    db.commit()
    db.refresh(lote)

    _recalcular_status_lote(lote)
    _registrar_historico(db, lote.id, usuario.id, TipoEventoHistorico.CRACHA_IMPRESSO, quantidade=1)
    db.commit()
    db.refresh(cracha)
    return cracha


@router.patch("/{lote_id}/crachas/{cracha_id}/falhou", response_model=FalhaRegistradaOut)
def marcar_cracha_falhou(
    lote_id: uuid.UUID,
    cracha_id: uuid.UUID,
    payload: MarcarFalhaRequest,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, montar_filtro_tenant(usuario))
    cracha = db.query(LoteCracha).filter(LoteCracha.id == cracha_id, LoteCracha.lote_id == lote.id).first()
    if not cracha:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Crachá não encontrado neste lote")

    cracha.status_cracha = StatusCracha.FALHOU
    cracha.motivo_falha = payload.motivo_falha
    cracha.marcado_falha_em = datetime.utcnow()

    db.query(LoteImpressao).filter(LoteImpressao.id == lote.id).update(
        {LoteImpressao.quantidade_falhados: LoteImpressao.quantidade_falhados + 1}
    )
    db.commit()
    db.refresh(lote)
    _recalcular_status_lote(lote)

    minilote = (
        db.query(MiniloteReimpressao)
        .filter(
            MiniloteReimpressao.lote_original_id == lote.id,
            MiniloteReimpressao.status == StatusMinilote.AGUARDANDO,
        )
        .first()
    )
    if minilote:
        minilote.crachas_falhados_ids = [*minilote.crachas_falhados_ids, str(cracha.id)]
    else:
        minilote = MiniloteReimpressao(
            lote_original_id=lote.id,
            crachas_falhados_ids=[str(cracha.id)],
            status=StatusMinilote.AGUARDANDO,
        )
        db.add(minilote)

    _registrar_historico(
        db, lote.id, usuario.id, TipoEventoHistorico.CRACHA_FALHOU, quantidade=1, descricao=payload.motivo_falha
    )
    db.commit()
    db.refresh(minilote)
    return FalhaRegistradaOut(minilote_id=minilote.id)


@router.post("/{lote_id}/arquivar", response_model=LoteOut)
def arquivar_lote(
    lote_id: uuid.UUID,
    usuario: Usuario = Depends(require_gestor_or_above),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, montar_filtro_tenant(usuario))
    if lote.status_lote not in (StatusLote.IMPRESSO, StatusLote.PARCIALMENTE_IMPRESSO):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Só é possível arquivar lotes IMPRESSO ou PARCIALMENTE_IMPRESSO"
        )

    lote.status_lote = StatusLote.ARQUIVADO
    lote.arquivado_em = datetime.utcnow()
    _registrar_historico(db, lote.id, usuario.id, TipoEventoHistorico.LOTE_ARQUIVADO)
    db.commit()
    db.refresh(lote)
    return lote


@router.get("", response_model=List[LoteOut])
def listar_lotes(
    filial_id: Optional[uuid.UUID] = None,
    status_lote: Optional[StatusLote] = Query(None, alias="status"),
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    query = db.query(LoteImpressao)
    for campo, valor in filtro.items():
        query = query.filter(getattr(LoteImpressao, campo) == valor)
    if filial_id:
        query = query.filter(LoteImpressao.filial_id == filial_id)
    if status_lote:
        query = query.filter(LoteImpressao.status_lote == status_lote)
    return query.order_by(LoteImpressao.criado_em.desc()).all()


@router.get("/{lote_id}", response_model=LoteDetalheOut)
def obter_lote(
    lote_id: uuid.UUID,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, filtro)
    crachas = (
        db.query(LoteCracha)
        .filter(LoteCracha.lote_id == lote.id)
        .order_by(LoteCracha.numero_pagina, LoteCracha.posicao_na_pagina)
        .all()
    )
    base = LoteOut.model_validate(lote, from_attributes=True)
    crachas_out = [LoteCrachaOut.model_validate(c, from_attributes=True) for c in crachas]
    return LoteDetalheOut(**base.model_dump(), crachas=crachas_out)


@router.get("/{lote_id}/historico", response_model=List[HistoricoLoteOut])
def historico_lote(
    lote_id: uuid.UUID,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, filtro)
    return db.query(HistoricoLote).filter(HistoricoLote.lote_id == lote.id).order_by(HistoricoLote.ocorrido_em).all()


@router.get("/{lote_id}/pdf", response_model=PdfUrlOut)
def baixar_pdf_lote(
    lote_id: uuid.UUID,
    filtro: dict = Depends(get_tenant_filter),
    db: Session = Depends(get_db),
):
    lote = _obter_lote(db, lote_id, filtro)
    if not lote.pdf_url:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "PDF ainda não foi gerado para este lote")

    if not lote.pdf_baixado_em:
        lote.pdf_baixado_em = datetime.utcnow()
        _registrar_historico(db, lote.id, None, TipoEventoHistorico.PDF_BAIXADO)
        db.commit()

    return PdfUrlOut(pdf_url=lote.pdf_url)
