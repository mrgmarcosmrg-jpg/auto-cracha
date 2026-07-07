from PIL import Image, ImageDraw, ImageFont
from typing import Optional
import textwrap


class VerticalPadrao:
    """Template vertical padrão para crachás (500x800px)."""
    
    CANVAS_WIDTH = 500
    CANVAS_HEIGHT = 800
    
    # Coordenadas em pixels (briefing)
    LOGO_Y = 30
    COMPANY_NAME_Y = 100
    FOTO_Y = 170
    INFO_Y = 480
    FAIXAS_Y_MIN = 635
    FAIXAS_Y_MAX = 725
    QR_Y = 750
    
    def __init__(self, config_empresa: dict, colaborador: dict):
        self.config = config_empresa
        self.colaborador = colaborador
    
    def renderizar(self, foto_circular: Optional[Image.Image], qr_code: Image.Image) -> Image.Image:
        """Renderiza o crachá completo."""
        # Criar canvas branco
        canvas = Image.new('RGB', (self.CANVAS_WIDTH, self.CANVAS_HEIGHT), 'white')
        draw = ImageDraw.Draw(canvas)
        
        # 1. Logo empresa (centralizada, 100x80px)
        if self.config.get('logo_url'):
            try:
                import urllib.request
                from io import BytesIO
                with urllib.request.urlopen(self.config['logo_url']) as response:
                    logo = Image.open(BytesIO(response.read()))
                    logo.thumbnail((100, 80), Image.Resampling.LANCZOS)
                    logo_x = (self.CANVAS_WIDTH - logo.width) // 2
                    canvas.paste(logo, (logo_x, self.LOGO_Y))
            except:
                pass
        
        # 2. Nome da empresa (Arial Bold, centralizado, Y=100)
        try:
            fonte_empresa = ImageFont.truetype("arial.ttf", 18)
            fonte_empresa_bold = ImageFont.truetype("arialbd.ttf", 18)
        except:
            fonte_empresa = ImageFont.load_default()
            fonte_empresa_bold = ImageFont.load_default()
        
        empresa_nome = self.config.get('nome_empresa', 'EMPRESA')
        bbox = draw.textbbox((0, 0), empresa_nome, font=fonte_empresa_bold)
        empresa_width = bbox[2] - bbox[0]
        empresa_x = (self.CANVAS_WIDTH - empresa_width) // 2
        draw.text((empresa_x, self.COMPANY_NAME_Y), empresa_nome, fill='black', font=fonte_empresa_bold)
        
        # 3. Foto circular (250x250px, centralizada)
        if foto_circular:
            foto_x = (self.CANVAS_WIDTH - 250) // 2
            canvas.paste(foto_circular, (foto_x, self.FOTO_Y), foto_circular)
        
        # 4. Nome do funcionário e cargo (caixa alta, centralizado, Y=480)
        try:
            fonte_nome = ImageFont.truetype("arialbd.ttf", 20)
            fonte_cargo = ImageFont.truetype("arial.ttf", 14)
        except:
            fonte_nome = ImageFont.load_default()
            fonte_cargo = ImageFont.load_default()
        
        nome = self.colaborador.get('nome', '').upper()
        cargo = self.colaborador.get('cargo', '').upper()
        
        bbox_nome = draw.textbbox((0, 0), nome, font=fonte_nome)
        nome_width = bbox_nome[2] - bbox_nome[0]
        nome_x = (self.CANVAS_WIDTH - nome_width) // 2
        draw.text((nome_x, self.INFO_Y), nome, fill='black', font=fonte_nome)
        
        bbox_cargo = draw.textbbox((0, 0), cargo, font=fonte_cargo)
        cargo_width = bbox_cargo[2] - bbox_cargo[0]
        cargo_x = (self.CANVAS_WIDTH - cargo_width) // 2
        draw.text((cargo_x, self.INFO_Y + 35), cargo, fill='#666666', font=fonte_cargo)
        
        # 5. Faixas injetáveis (Y=635 a Y=725, altura=90px)
        faixa_altura = self.FAIXAS_Y_MAX - self.FAIXAS_Y_MIN
        faixa_largura_unitaria = self.CANVAS_WIDTH // 2
        
        # Faixa 1: Em Treinamento (Laranja, esquerda)
        if self.colaborador.get('em_treinamento', False):
            self._desenhar_faixa(draw, 
                x=10, 
                y=self.FAIXAS_Y_MIN, 
                largura=faixa_largura_unitaria - 15, 
                altura=faixa_altura - 10,
                cor_bg=(255, 165, 0),  # Laranja
                texto="EM TREINAMENTO",
                fonte_size=14
            )
        
        # Faixa 2: PCD (Azul, direita)
        if self.colaborador.get('pcd', False):
            self._desenhar_faixa(draw,
                x=self.CANVAS_WIDTH // 2 + 5,
                y=self.FAIXAS_Y_MIN,
                largura=faixa_largura_unitaria - 15,
                altura=faixa_altura - 10,
                cor_bg=(0, 102, 204),  # Azul
                texto="PCD",
                fonte_size=14
            )
        
        # 6. QR Code (centralizado, Y=750)
        qr_resized = qr_code.resize((80, 80), Image.Resampling.LANCZOS)
        qr_x = (self.CANVAS_WIDTH - 80) // 2
        canvas.paste(qr_resized, (qr_x, self.QR_Y))
        
        return canvas
    
    def _desenhar_faixa(self, draw: ImageDraw.ImageDraw, x: int, y: int, 
                       largura: int, altura: int, cor_bg: tuple, 
                       texto: str, fonte_size: int = 14):
        """Desenha faixa com cantos arredondados e texto."""
        raio = 12
        
        # Desenhar fundo arredondado
        draw.rounded_rectangle(
            [x, y, x + largura, y + altura],
            radius=raio,
            fill=cor_bg
        )
        
        # Desenhar texto
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
