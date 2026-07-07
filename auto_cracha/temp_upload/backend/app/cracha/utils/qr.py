import qrcode
from PIL import Image


def gerar_qr(qr_token: str, tamanho: int = 160) -> Image.Image:
    url = f"https://crachapp.com.br/p/{qr_token}"
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=4,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    imagem = qr.make_image(fill_color="#1E293B", back_color="white").convert("RGB")
    return imagem.resize((tamanho, tamanho), Image.LANCZOS)
