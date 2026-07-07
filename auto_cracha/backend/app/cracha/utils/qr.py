import io
import qrcode
from PIL import Image
from app.core.config import settings


def gerar_qr(qr_token: str) -> Image.Image:
    """Gera QR Code apontando para o link público do crachá."""
    url = f"{settings.APP_URL}/p/{qr_token}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    return img.convert('RGB')
