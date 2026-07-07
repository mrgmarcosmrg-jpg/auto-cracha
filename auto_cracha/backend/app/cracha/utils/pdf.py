from io import BytesIO
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def compilar_pdf_empresa(imagens_crachá: list[Image.Image]) -> BytesIO:
    """
    Compila múltiplas imagens de crachás em layout A4 (3x3 = 9 crachás por página).
    Formato CR80: 85.6mm x 53.98mm
    """
    pdf_buffer = BytesIO()
    
    # Dimensões CR80 em pontos (1 inch = 72 pontos, 1 inch = 25.4mm)
    largura_cracha_mm = 85.6
    altura_cracha_mm = 53.98
    largura_cracha_pt = largura_cracha_mm * 72 / 25.4
    altura_cracha_pt = altura_cracha_mm * 72 / 25.4
    
    # Margens e espaçamento
    margem = 10 * mm
    espacamento = 5 * mm
    
    # Layout 3x3
    colunas = 3
    linhas = 3
    crachás_por_pagina = colunas * linhas
    
    # Criar PDF
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    largura_a4, altura_a4 = A4
    
    # Processar imagens em grupos de 9
    for idx_grupo, i in enumerate(range(0, len(imagens_crachá), crachás_por_pagina)):
        if idx_grupo > 0:
            c.showPage()
        
        grupo = imagens_crachá[i:i + crachás_por_pagina]
        
        for pos, img_pillow in enumerate(grupo):
            col = pos % colunas
            row = pos // colunas
            
            x = margem + col * (largura_cracha_pt + espacamento)
            y = altura_a4 - margem - (row + 1) * altura_cracha_pt - row * espacamento
            
            # Salvar imagem temporária
            img_bytes = BytesIO()
            img_pillow.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Desenhar no PDF
            c.drawImage(img_bytes, x, y, width=largura_cracha_pt, height=altura_cracha_pt)
    
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer


def compilar_pdf_unitario(imagem_cracha: Image.Image) -> BytesIO:
    """Compila uma única imagem de crachá em página A4 centralizada."""
    pdf_buffer = BytesIO()
    
    largura_cracha_mm = 85.6
    altura_cracha_mm = 53.98
    largura_cracha_pt = largura_cracha_mm * 72 / 25.4
    altura_cracha_pt = altura_cracha_mm * 72 / 25.4
    
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    largura_a4, altura_a4 = A4
    
    # Centralizar
    x = (largura_a4 - largura_cracha_pt) / 2
    y = (altura_a4 - altura_cracha_pt) / 2
    
    img_bytes = BytesIO()
    imagem_cracha.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    c.drawImage(img_bytes, x, y, width=largura_cracha_pt, height=altura_cracha_pt)
    c.save()
    
    pdf_buffer.seek(0)
    return pdf_buffer
