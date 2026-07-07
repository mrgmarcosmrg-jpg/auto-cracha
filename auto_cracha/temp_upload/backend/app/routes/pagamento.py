from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import require_admin_tenant
from app.models.assinatura import Assinatura, PlanoAssinatura, StatusAssinatura
from app.models.usuario import Usuario
from app.schemas.pagamento import (
    AssinaturaOut,
    CreditosPixOut,
    CreditosPixRequest,
    CriarPreferenciaMercadoPagoRequest,
    PlanoOut,
    WebhookMercadoPagoBody,
)
from app.services.mercado_pago_service import (
    PLANOS,
    criar_preferencia_pagamento,
    obter_status_pagamento,
)

router = APIRouter(prefix="/pagamento", tags=["pagamento"])


@router.get("/planos", response_model=List[PlanoOut])
def listar_planos():
    """Lista todos os planos disponíveis."""
    return [
        PlanoOut(
            id=pid,
            nome=plano["nome"],
            descricao=plano["descricao"],
            preco_reais=plano["preco_reais"],
            max_colaboradores=plano["max_colaboradores"],
            recursos=plano["recursos"],
            destaque=plano["destaque"],
        )
        for pid, plano in PLANOS.items()
    ]


@router.post("/criar-preferencia")
def criar_preferencia(
    payload: CriarPreferenciaMercadoPagoRequest,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    """Cria uma preferência de pagamento no Mercado Pago."""
    try:
        resultado = criar_preferencia_pagamento(payload.plano_id, usuario.tenant_id, usuario.email)
        body = resultado.get("body", resultado)
        return {
            "init_point": body.get("init_point"),
            "sandbox_init_point": body.get("sandbox_init_point"),
        }
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(e))
    except Exception as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Erro ao criar preferência: {str(e)}")


@router.get("/assinatura", response_model=AssinaturaOut)
def obter_assinatura(
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    """Retorna os dados da assinatura atual do tenant."""
    assinatura = db.query(Assinatura).filter(Assinatura.tenant_id == usuario.tenant_id).first()
    if not assinatura:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assinatura não encontrada")

    return AssinaturaOut(
        status=assinatura.status.value,
        plano=assinatura.plano.value if assinatura.plano else "TRIAL",
        max_colaboradores=assinatura.max_colaboradores,
        creditos_pix=assinatura.creditos_pix,
        trial_expira_em=assinatura.trial_expira_em.isoformat() if assinatura.trial_expira_em else None,
        mp_payment_id=assinatura.mp_payment_id,
    )


@router.post("/webhook/mercado-pago")
def webhook_mercado_pago(payload: WebhookMercadoPagoBody, db: Session = Depends(get_db)):
    """Webhook para notificações de pagamento do Mercado Pago."""
    if payload.type == "payment":
        payment_id = payload.data.get("id") if payload.data else None
        if not payment_id:
            return {"status": "ok"}

        try:
            pagamento = obter_status_pagamento(payment_id)
        except Exception:
            return {"status": "ok"}

        external_reference = pagamento.get("external_reference")
        if not external_reference:
            return {"status": "ok"}

        assinatura = db.query(Assinatura).filter(Assinatura.tenant_id == external_reference).first()
        if not assinatura:
            return {"status": "ok"}

        status_mp = pagamento.get("status")
        if status_mp == "approved":
            assinatura.status = StatusAssinatura.ATIVO
            assinatura.mp_payment_id = payment_id

            items = pagamento.get("items", [])
            if items:
                title = items[0].get("title", "")
                parts = title.lower().split()
                plano = None
                for part in parts:
                    if part in ("bronze", "prata", "ouro"):
                        plano = part
                        break
                if plano and plano in PLANOS:
                    assinatura.plano = PlanoAssinatura(plano.upper())
                    assinatura.max_colaboradores = PLANOS[plano]["max_colaboradores"]

            db.commit()

    return {"status": "ok"}


@router.post("/creditos-pix", response_model=CreditosPixOut)
def comprar_creditos_pix(
    payload: CreditosPixRequest,
    usuario: Usuario = Depends(require_admin_tenant),
    db: Session = Depends(get_db),
):
    """Cria uma requisição de compra de créditos Pix (manual approval por agora)."""
    assinatura = db.query(Assinatura).filter(Assinatura.tenant_id == usuario.tenant_id).first()
    if not assinatura:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Assinatura não encontrada")

    valor_total = payload.quantidade * 0.50
    return {
        "quantidade": payload.quantidade,
        "valor_total_reais": valor_total,
        "status": "aguardando_pagamento",
        "mensagem": "Envie comprovante de transferência para pagamentos@crachapp.com.br",
    }
