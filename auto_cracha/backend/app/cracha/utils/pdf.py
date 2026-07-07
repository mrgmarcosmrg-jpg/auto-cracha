from io import BytesIO
from typing import List, Tuple

from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

CARTAO_LARGURA_MM = 85.6
CARTAO_ALTURA_MM = 54.0
MARGEM_MM = 10.0
ESPACAMENTO_MM = 4.0
LARGURA_PAGINA_MM = 210.0
ALTURA_PAGINA_MM = 297.0


def _dimensoes_cartao_mm_por_proporcao(largura_px: int, altura_px: int) -> Tuple[float, float]:
    """CR80: 85.6x54mm. Crachás 'paisagem' (largura>=altura) usam a orientação
    landscape; crachás 'retrato' usam a orientação portrait do mesmo cartão."""
    if largura_px >= altura_px:
        return CARTAO_LARGURA_MM, CARTAO_ALTURA_MM
    return CARTAO_ALTURA_MM, CARTAO_LARGURA_MM


def _dimensoes_cartao_mm(imagem: Image.Image) -> Tuple[float, float]:
    return _dimensoes_cartao_mm_por_proporcao(imagem.width, imagem.height)


def _grade_3x3_por_proporcao(largura_px: int, altura_px: int) -> Tuple[int, int]:
    """Quantas colunas/linhas de um dado cartão cabem numa página A4 com as margens padrão."""
    cartao_largura_mm, cartao_altura_mm = _dimensoes_cartao_mm_por_proporcao(largura_px, altura_px)
    colunas = max(1, int((LARGURA_PAGINA_MM - 2 * MARGEM_MM + ESPACAMENTO_MM) // (cartao_largura_mm + ESPACAMENTO_MM)))
    linhas = max(1, int((ALTURA_PAGINA_MM - 2 * MARGEM_MM + ESPACAMENTO_MM) // (cartao_altura_mm + ESPACAMENTO_MM)))
    return colunas, linhas


def _grade_3x3(imagem: Image.Image) -> Tuple[int, int]:
    return _grade_3x3_por_proporcao(imagem.width, imagem.height)


def cartoes_por_pagina_3x3(imagem: Image.Image) -> int:
    colunas, linhas = _grade_3x3(imagem)
    return colunas * linhas


def cartoes_por_pagina_3x3_por_template(template_id: str) -> int:
    """Calcula quantos cartões cabem por página sem precisar renderizar nenhuma imagem
    (usa só as dimensões de canvas declaradas pelo módulo do template)."""
    from app.cracha.templates import horizontal_padrao, vertical_padrao

    modulo = {"vertical_padrao": vertical_padrao, "horizontal_padrao": horizontal_padrao}.get(
        template_id, vertical_padrao
    )
    colunas, linhas = _grade_3x3_por_proporcao(modulo.LARGURA, modulo.ALTURA)
    return colunas * linhas


def gerar_pdf_a4_3x3(imagens: List[Image.Image]) -> bytes:
    """Monta um PDF A4 com os crachás em grade, preenchendo o máximo de colunas/linhas
    que couberem na página (3x3 para o cartão retrato padrão, a 300 DPI)."""
    buffer = BytesIO()
    pagina = canvas.Canvas(buffer, pagesize=A4)

    if not imagens:
        pagina.showPage()
        pagina.save()
        return buffer.getvalue()

    cartao_largura_mm, cartao_altura_mm = _dimensoes_cartao_mm(imagens[0])
    colunas, linhas = _grade_3x3(imagens[0])
    por_pagina = colunas * linhas

    _, altura_pagina_pt = A4

    for indice, imagem in enumerate(imagens):
        posicao_na_pagina = indice % por_pagina
        if posicao_na_pagina == 0 and indice > 0:
            pagina.showPage()

        coluna = posicao_na_pagina % colunas
        linha = posicao_na_pagina // colunas

        x = (MARGEM_MM + coluna * (cartao_largura_mm + ESPACAMENTO_MM)) * mm
        y_topo_mm = MARGEM_MM + linha * (cartao_altura_mm + ESPACAMENTO_MM)
        y = altura_pagina_pt - (y_topo_mm + cartao_altura_mm) * mm

        pagina.drawImage(
            ImageReader(imagem),
            x,
            y,
            width=cartao_largura_mm * mm,
            height=cartao_altura_mm * mm,
        )

    pagina.showPage()
    pagina.save()
    return buffer.getvalue()


def gerar_pdf_a4_unitario(imagens: List[Image.Image]) -> bytes:
    """Um crachá centralizado por página (uma página para cada imagem da lista)."""
    buffer = BytesIO()
    pagina = canvas.Canvas(buffer, pagesize=A4)

    if not imagens:
        pagina.showPage()
        pagina.save()
        return buffer.getvalue()

    for indice, imagem in enumerate(imagens):
        if indice > 0:
            pagina.showPage()

        cartao_largura_mm, cartao_altura_mm = _dimensoes_cartao_mm(imagem)
        x = (LARGURA_PAGINA_MM - cartao_largura_mm) / 2 * mm
        y = (ALTURA_PAGINA_MM - cartao_altura_mm) / 2 * mm

        pagina.drawImage(
            ImageReader(imagem),
            x,
            y,
            width=cartao_largura_mm * mm,
            height=cartao_altura_mm * mm,
        )

    pagina.showPage()
    pagina.save()
    return buffer.getvalue()
