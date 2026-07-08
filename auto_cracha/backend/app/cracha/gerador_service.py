from typing import Optional
from PIL import Image
from app.cracha.templates.vertical_padrao import VerticalPadrao
from app.cracha.utils.foto import processar_foto
from app.cracha.utils.qr import gerar_qr


class GeradorCracha:
    """Factory para geração de crachás com diferentes templates."""
    
    TEMPLATES = {
        'vertical_padrao': VerticalPadrao,
        'horizontal_padrao': VerticalPadrao,  # MVP: usar vertical como padrão
    }
    
    @staticmethod
    def gerar(
        colaborador: dict,
        config_empresa: dict,
        config_filial: dict,
        template_id: str = 'vertical_padrao'
    ) -> Optional[Image.Image]:
        """
        Gera crachá para um colaborador com suporte a branding por filial.
        
        Args:
            colaborador: dict com id, nome, nome_guerra, cargo, foto_url, etc
            config_empresa: dict com nome_empresa, logo_url
            config_filial: dict com logo_filial_url, logo_grupo_url, cor_primaria
            template_id: identificador do template
        
        Returns:
            PIL Image do crachá, ou None se falhar
        """
        try:
            # Validar template
            if template_id not in GeradorCracha.TEMPLATES:
                raise ValueError(f"Template '{template_id}' não encontrado")
            
            # Processar foto
            foto_circular = None
            if colaborador.get('foto_url'):
                foto_circular = processar_foto(colaborador['foto_url'])
            
            # Gerar QR
            qr_code = gerar_qr(str(colaborador.get('qr_token', '')))
            
            # Instanciar template e renderizar
            classe_template = GeradorCracha.TEMPLATES[template_id]
            template = classe_template(config_empresa, config_filial, colaborador)
            cracha = template.renderizar(foto_circular, qr_code)
            
            return cracha
        
        except Exception as e:
            print(f"Erro ao gerar crachá: {e}")
            return None
