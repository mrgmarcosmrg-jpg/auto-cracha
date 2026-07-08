from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas


def compilar_pdf_empresa(imagens_cracha: list[Image.Image]) -> BytesIO:
    """
    Compila múltiplas imagens de crachás em layout A4 (3x3 = 9 crachás por página).
    Calibração 300DPI: CR80 = 85.6mm x 53.98mm = 1010px x 638px @ 300DPI
    Mantém PNG intermediário em 500x800px e redimensiona para CR80 no PDF.
    """
    pdf_buffer = BytesIO()
    
    # Dimensões CR80 em mm (padrão internacional)
    largura_cracha_mm = 85.6
    altura_cracha_mm = 53.98
    
    # Converter para pontos (1 inch = 72pt, 1 inch = 25.4mm)
    # Para 300DPI em PDF (que usa 72DPI):
    # CR80 em 300DPI = 85.6mm = 1010px
    # Convertendo para 72DPI: 1010 * 72 / 300 = 242pt
    largura_cracha_pt = largura_cracha_mm * mm
    altura_cracha_pt = altura_cracha_mm * mm
    
    # Margens e espaçamento
    margem = 10 * mm
    espacamento = 3 * mm
    
    # Layout 3x3
    colunas = 3
    linhas = 3
    crachás_por_pagina = colunas * linhas
    
    # Criar PDF
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    largura_a4, altura_a4 = A4
    
    # Processar imagens em grupos de 9
    for idx_grupo, i in enumerate(range(0, len(imagens_cracha), crachás_por_pagina)):
        if idx_grupo > 0:
            c.showPage()
        
        grupo = imagens_cracha[i:i + crachás_por_pagina]
        
        for pos, img_pillow in enumerate(grupo):
            col = pos % colunas
            row = pos // colunas
            
            x = margem + col * (largura_cracha_pt + espacamento)
            y = altura_a4 - margem - (row + 1) * altura_cracha_pt - row * espacamento
            
            # Salvar imagem temporária em memória
            img_bytes = BytesIO()
            img_pillow.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Desenhar no PDF com dimensões exatas CR80
            c.drawImage(
                img_bytes,
                x, y,
                width=largura_cracha_pt,
                height=altura_cracha_pt,
                preserveAspectRatio=True
            )
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def compilar_pdf_unitario(imagem_cracha: Image.Image) -> BytesIO:
    """
    Compila uma única imagem de crachá em página A4 centralizada (300DPI).
    Redimensiona a imagem PNG 500x800px para tamanho CR80 exato (85.6mm x 53.98mm).
    """
    pdf_buffer = BytesIO()
    
    largura_cracha_mm = 85.6
    altura_cracha_mm = 53.98
    largura_cracha_pt = largura_cracha_mm * mm
    altura_cracha_pt = altura_cracha_mm * mm
    
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    largura_a4, altura_a4 = A4
    
    # Centralizar na página
    x = (largura_a4 - largura_cracha_pt) / 2
    y = (altura_a4 - altura_cracha_pt) / 2
    
    img_bytes = BytesIO()
    imagem_cracha.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    c.drawImage(
        img_bytes,
        x, y,
        width=largura_cracha_pt,
        height=altura_cracha_pt,
        preserveAspectRatio=True
    )
    c.save()
    
    pdf_buffer.seek(0)
    return pdf_buffer


def obter_dimensoes_300dpi() -> dict:
    """Retorna dimensões CR80 em diferentes unidades para referência."""
    return {
        'cr80_mm': {'largura': 85.6, 'altura': 53.98},
        'cr80_pt': {'largura': 85.6 * mm, 'altura': 53.98 * mm},
        'cr80_px_300dpi': {'largura': 1010, 'altura': 638},
        'cr80_inches': {'largura': 85.6 / 25.4, 'altura': 53.98 / 25.4},
    }
