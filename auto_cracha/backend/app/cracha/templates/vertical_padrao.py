import io
from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import urllib.request
from app.core.config import settings


class VerticalPadrao:
    """Template vertical 500x800px com suporte a logos dinâmicas, cores e nome de guerra."""
    
    CANVAS_WIDTH = 500
    CANVAS_HEIGHT = 800
    
    # Coordenadas em pixels (briefing GCenter + CrachApp)
    LOGO_GRUPO_Y = 15
    LOGO_FILIAL_Y = 15
    COMPANY_NAME_Y = 85
    FOTO_Y = 170
    INFO_Y = 480
    FAIXAS_Y_MIN = 635  # Zona injetável início
    FAIXAS_Y_MAX = 725  # Zona injetável fim
    QR_Y = 750
    
    def __init__(self, config_empresa: dict, config_filial: dict, colaborador: dict):
        self.config_empresa = config_empresa
        self.config_filial = config_filial
        self.colaborador = colaborador
        # Cor padrão roxo se não fornecida
        self.cor_primaria = config_filial.get('cor_primaria', '#7C3AED')
        self._hex_to_rgb(self.cor_primaria)
    
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Converte hex para RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _carregar_imagem_url(self, url: str, max_width: int, max_height: int) -> Optional[Image.Image]:
        """Carrega imagem de URL com tratamento de erro."""
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                img_bytes = response.read()
            img = Image.open(io.BytesIO(img_bytes))
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"Erro ao carregar imagem {url}: {e}")
            return None
    
    def renderizar(self, foto_circular: Optional[Image.Image], qr_code: Image.Image) -> Image.Image:
        """Renderiza o crachá completo com todas as features."""
        # Criar canvas branco
        canvas = Image.new('RGB', (self.CANVAS_WIDTH, self.CANVAS_HEIGHT), 'white')
        draw = ImageDraw.Draw(canvas)
        
        # ============ SEÇÃO 1: LOGOS (Grupo + Filial) ============
        logo_x_offset = 20
        
        # Logo do Grupo (esquerda)
        if self.config_filial.get('logo_grupo_url'):
            logo_grupo = self._carregar_imagem_url(
                self.config_filial['logo_grupo_url'], 
                max_width=70, 
                max_height=60
            )
            if logo_grupo:
                canvas.paste(logo_grupo, (logo_x_offset, self.LOGO_GRUPO_Y), logo_grupo if logo_grupo.mode == 'RGBA' else None)
        
        # Logo da Filial (direita)
        if self.config_filial.get('logo_filial_url'):
            logo_filial = self._carregar_imagem_url(
                self.config_filial['logo_filial_url'], 
                max_width=70, 
                max_height=60
            )
            if logo_filial:
                logo_x = self.CANVAS_WIDTH - logo_x_offset - (logo_filial.width if logo_filial else 70)
                canvas.paste(logo_filial, (logo_x, self.LOGO_FILIAL_Y), logo_filial if logo_filial.mode == 'RGBA' else None)
        
        # ============ SEÇÃO 2: NOME DA EMPRESA ============
        try:
            fonte_empresa_bold = ImageFont.truetype("arialbd.ttf", 18)
        except:
            fonte_empresa_bold = ImageFont.load_default()
        
        empresa_nome = self.config_empresa.get('nome_empresa', 'EMPRESA')
        bbox = draw.textbbox((0, 0), empresa_nome, font=fonte_empresa_bold)
        empresa_width = bbox[2] - bbox[0]
        empresa_x = (self.CANVAS_WIDTH - empresa_width) // 2
        
        # Usar cor_primaria para o nome
        cor_rgb = self._hex_to_rgb(self.cor_primaria)
        draw.text((empresa_x, self.COMPANY_NAME_Y), empresa_nome, fill=cor_rgb, font=fonte_empresa_bold)
        
        # ============ SEÇÃO 3: FOTO PROCESSADA (250x250px circular) ============
        if foto_circular:
            foto_x = (self.CANVAS_WIDTH - 250) // 2
            canvas.paste(foto_circular, (foto_x, self.FOTO_Y), foto_circular)
        
        # ============ SEÇÃO 4: NOME E CARGO (com lógica de nome_guerra) ============
        try:
            fonte_nome = ImageFont.truetype("arialbd.ttf", 20)
            fonte_cargo = ImageFont.truetype("arial.ttf", 14)
        except:
            fonte_nome = ImageFont.load_default()
            fonte_cargo = ImageFont.load_default()
        
        # ✅ REGRA: Se nome_guerra preenchido, usar; senão usar nome completo
        nome_exibicao = (self.colaborador.get('nome_guerra') or self.colaborador.get('nome', '')).upper()
        cargo = self.colaborador.get('cargo', '').upper()
        
        bbox_nome = draw.textbbox((0, 0), nome_exibicao, font=fonte_nome)
        nome_width = bbox_nome[2] - bbox_nome[0]
        nome_x = (self.CANVAS_WIDTH - nome_width) // 2
        draw.text((nome_x, self.INFO_Y), nome_exibicao, fill='black', font=fonte_nome)
        
        bbox_cargo = draw.textbbox((0, 0), cargo, font=fonte_cargo)
        cargo_width = bbox_cargo[2] - bbox_cargo[0]
        cargo_x = (self.CANVAS_WIDTH - cargo_width) // 2
        draw.text((cargo_x, self.INFO_Y + 35), cargo, fill='#666666', font=fonte_cargo)
        
        # ============ SEÇÃO 5: ZONAS INJETÁVEIS (Y=635 a Y=725, altura=90px) ============
        faixa_altura = self.FAIXAS_Y_MAX - self.FAIXAS_Y_MIN
        faixa_largura_unitaria = self.CANVAS_WIDTH // 2
        
        # ✅ Faixa 1: Em Treinamento (cor_primaria, esquerda)
        if self.colaborador.get('em_treinamento', False):
            self._desenhar_faixa(
                draw,
                x=10,
                y=self.FAIXAS_Y_MIN,
                largura=faixa_largura_unitaria - 15,
                altura=faixa_altura - 10,
                cor_bg=cor_rgb,  # ✅ Usa cor_primaria dinâmica
                texto="EM TREINAMENTO",
                fonte_size=14
            )
        
        # ✅ Faixa 2: PCD (azul, direita)
        if self.colaborador.get('pcd', False):
            self._desenhar_faixa(
                draw,
                x=self.CANVAS_WIDTH // 2 + 5,
                y=self.FAIXAS_Y_MIN,
                largura=faixa_largura_unitaria - 15,
                altura=faixa_altura - 10,
                cor_bg=(0, 102, 204),  # Azul fixo para PCD
                texto="PCD",
                fonte_size=14
            )
        
        # ============ SEÇÃO 6: QR CODE (centralizado) ============
        qr_resized = qr_code.resize((80, 80), Image.Resampling.LANCZOS)
        qr_x = (self.CANVAS_WIDTH - 80) // 2
        canvas.paste(qr_resized, (qr_x, self.QR_Y))
        
        return canvas
    
    def _desenhar_faixa(self, draw: ImageDraw.ImageDraw, x: int, y: int,
                       largura: int, altura: int, cor_bg: tuple,
                       texto: str, fonte_size: int = 14):
        """Desenha faixa com cantos arredondados 12px."""
        raio = 12
        
        # ✅ Cantos arredondados
        draw.rounded_rectangle(
            [x, y, x + largura, y + altura],
            radius=raio,
            fill=cor_bg
        )
        
        # Texto branco centralizado
        try:
            fonte = ImageFont.truetype("arialbd.ttf", fonte_size)
        except:
            fonte = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), texto, font=fonte)
        texto_width = bbox[2] - bbox[0]
        texto_height = bbox[3] - bbox[1]
        
        texto_x = x + (largura - texto_width) // 2
        texto_y = y + (altura - texto_height) // 2
        
        draw.text((texto_x, texto_y), texto, fill='white', font=fonte)
