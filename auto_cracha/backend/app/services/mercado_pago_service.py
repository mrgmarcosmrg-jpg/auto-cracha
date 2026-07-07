import os

import mercadopago

_mp_sdk = None


def _obter_cliente():
    global _mp_sdk
    if _mp_sdk is None:
        _mp_sdk = mercadopago.SDK(os.environ.get("MERCADOPAGO_ACCESS_TOKEN", ""))
    return _mp_sdk


PLANOS = {
    "bronze": {
        "nome": "Bronze",
        "descricao": "Até 50 colaboradores",
        "preco_reais": 99.90,
        "max_colaboradores": 50,
        "recursos": [
            "Geração de crachás",
            "QR Code dinâmico",
            "Até 50 colaboradores",
            "Suporte por e-mail",
        ],
        "destaque": False,
    },
    "prata": {
        "nome": "Prata",
        "descricao": "Até 200 colaboradores",
        "preco_reais": 299.90,
        "max_colaboradores": 200,
        "recursos": [
            "Tudo do Bronze",
            "Até 200 colaboradores",
            "Lotes de impressão ilimitados",
            "Suporte prioritário",
            "Integração com Mercado Pago",
        ],
        "destaque": True,
    },
    "ouro": {
        "nome": "Ouro",
        "descricao": "Ilimitado",
        "preco_reais": 999.90,
        "max_colaboradores": 9999,
        "recursos": [
            "Tudo da Prata",
            "Colaboradores ilimitados",
            "API customizada",
            "Suporte 24/7",
            "Consultor dedicado",
        ],
        "destaque": False,
    },
}


def criar_preferencia_pagamento(plano_id: str, tenant_id: str, email_tenant: str) -> dict:
    """Cria uma preferência de pagamento no Mercado Pago e retorna o link de checkout."""
    if plano_id not in PLANOS:
        raise ValueError(f"Plano inválido: {plano_id}")

    plano = PLANOS[plano_id]
    sdk = _obter_cliente()

    request_body = {
        "items": [
            {
                "title": f"Plano {plano['nome']} - CrachApp",
                "description": f"Assinatura mensal - {plano['descricao']}",
                "quantity": 1,
                "unit_price": plano["preco_reais"],
            }
        ],
        "payer": {
            "email": email_tenant,
        },
        "external_reference": str(tenant_id),
        "back_urls": {
            "success": f"https://crachapp.com.br/dashboard/plano?status=success&payment_id={{PAYMENT_ID}}",
            "failure": "https://crachapp.com.br/dashboard/plano?status=failure",
            "pending": "https://crachapp.com.br/dashboard/plano?status=pending",
        },
        "auto_return": "approved",
    }

    resultado = sdk.preference().create(request_body)
    return {"body": resultado["body"]} if resultado.get("status") == 201 else resultado


def obter_status_pagamento(payment_id: str) -> dict:
    """Obtém o status de um pagamento do Mercado Pago."""
    sdk = _obter_cliente()
    resultado = sdk.payment().get(payment_id)
    return resultado.get("body", resultado)
