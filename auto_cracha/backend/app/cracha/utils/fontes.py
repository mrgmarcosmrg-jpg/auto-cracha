import os

from PIL import ImageDraw, ImageFont

_CAMINHOS_FONTE_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def carregar_fonte(tamanho: int):
    """Carrega uma fonte bold disponível no sistema (DejaVu no Docker, Arial no Windows).

    Sem nenhuma das duas, cai para a fonte escalável padrão do Pillow (>=10.1).
    """
    for caminho in _CAMINHOS_FONTE_BOLD:
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default(size=tamanho)


def ajustar_fonte_para_largura(draw: ImageDraw.ImageDraw, texto: str, largura_max: int, tamanho_inicial: int, tamanho_minimo: int):
    tamanho = tamanho_inicial
    while tamanho > tamanho_minimo:
        fonte = carregar_fonte(tamanho)
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        if bbox[2] - bbox[0] <= largura_max:
            return fonte
        tamanho -= 2
    return carregar_fonte(tamanho_minimo)


def escrever_centralizado(draw: ImageDraw.ImageDraw, texto: str, x_inicio: int, largura: int, y: int, fonte, cor: str) -> None:
    if not texto:
        return
    bbox = draw.textbbox((0, 0), texto, font=fonte)
    largura_texto = bbox[2] - bbox[0]
    x = x_inicio + (largura - largura_texto) / 2 - bbox[0]
    draw.text((x, y), texto, font=fonte, fill=cor)
