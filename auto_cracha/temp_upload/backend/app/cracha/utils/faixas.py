from typing import List

from PIL import ImageDraw

from app.cracha.utils.fontes import carregar_fonte


def desenhar_faixa(
    draw: ImageDraw.ImageDraw,
    y_inicio: int,
    altura: int,
    largura: int,
    cor: str,
    texto: str = "",
    fonte_tamanho: int = 20,
    raio: int = 12,
    x_inicio: int = 0,
) -> None:
    draw.rounded_rectangle([x_inicio, y_inicio, x_inicio + largura, y_inicio + altura], radius=raio, fill=cor)
    if not texto:
        return

    fonte = carregar_fonte(fonte_tamanho)
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    texto_largura = bbox[2] - bbox[0]
    texto_altura = bbox[3] - bbox[1]
    x = x_inicio + (largura - texto_largura) / 2 - bbox[0]
    y = y_inicio + (altura - texto_altura) / 2 - bbox[1]
    draw.text((x, y), texto, font=fonte, fill="white")


def resolver_faixas_ativas(dados: dict) -> List[dict]:
    """Decide quais faixas exibir, em ordem de prioridade (regra das 4 cenários + faixas
    customizadas do tenant + faixa neutra como último recurso)."""
    em_treinamento = bool(dados.get("em_treinamento"))
    pcd = bool(dados.get("pcd"))
    pcd_descricao = dados.get("pcd_descricao") or ""
    texto_pcd = f"PCD: {pcd_descricao}" if pcd_descricao else "PCD"

    if em_treinamento and pcd:
        return [
            {"proporcao": 0.5, "cor": "#EA580C", "texto": "EM TREINAMENTO", "fonte_tamanho": 18},
            {"proporcao": 0.5, "cor": "#2563EB", "texto": texto_pcd, "fonte_tamanho": 18},
        ]
    if em_treinamento:
        return [{"proporcao": 1.0, "cor": "#EA580C", "texto": "EM TREINAMENTO", "fonte_tamanho": 22}]
    if pcd:
        return [{"proporcao": 1.0, "cor": "#2563EB", "texto": texto_pcd, "fonte_tamanho": 22}]

    campos_adicionais = dados.get("campos_adicionais") or {}
    for faixa in dados.get("faixas_customizadas") or []:
        campo = faixa.get("campo_json")
        valor = campos_adicionais.get(campo) if campo else None
        if valor:
            return [
                {
                    "proporcao": 1.0,
                    "cor": faixa.get("cor", "#0F172A"),
                    "texto": str(faixa.get("label", valor)),
                    "fonte_tamanho": 20,
                }
            ]

    return [{"proporcao": 1.0, "cor": dados.get("cor_primaria") or "#0F172A", "texto": "", "fonte_tamanho": 20}]


def desenhar_zona_faixas(
    draw: ImageDraw.ImageDraw,
    dados: dict,
    x_inicio: int,
    largura: int,
    y_inicio: int,
    altura_total: int,
) -> None:
    y = y_inicio
    for faixa in resolver_faixas_ativas(dados):
        altura = int(altura_total * faixa["proporcao"])
        desenhar_faixa(
            draw,
            y,
            altura,
            largura,
            faixa["cor"],
            faixa["texto"],
            faixa["fonte_tamanho"],
            x_inicio=x_inicio,
        )
        y += altura
