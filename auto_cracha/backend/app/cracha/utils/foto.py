import io
from typing import Optional
import cv2
import numpy as np
from PIL import Image, ImageDraw

FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)


def processar_foto(url_ou_bytes: str | bytes) -> Optional[Image.Image]:
    """Processa foto com face detection e crop circular."""
    try:
        if isinstance(url_ou_bytes, str):
            import urllib.request
            with urllib.request.urlopen(url_ou_bytes) as response:
                image_data = response.read()
        else:
            image_data = url_ou_bytes

        nparr = np.frombuffer(image_data, np.uint8)
        img_cv2 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img_cv2 is None:
            return _fallback_crop_central(image_data)

        gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
        faces = FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=4, minSize=(100, 100))

        if len(faces) > 0:
            x, y, w, h = faces[0]
            expansion = max(w, h) * 0.2
            x = max(0, int(x - expansion))
            y = max(0, int(y - expansion))
            w = int(w + expansion * 2)
            h = int(h + expansion * 2)
            size = max(w, h)
            x_center = x + w // 2
            y_center = y + h // 2
            x = max(0, x_center - size // 2)
            y = max(0, y_center - size // 2)
            cropped = img_cv2[y:y+size, x:x+size]
        else:
            return _fallback_crop_central(image_data)

        img_pil = Image.fromarray(cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB))
        img_pil = img_pil.resize((250, 250), Image.Resampling.LANCZOS)

        return _criar_circular_com_borda(img_pil)

    except Exception as e:
        print(f"Erro ao processar foto: {e}")
        return _fallback_crop_central(url_ou_bytes) if isinstance(url_ou_bytes, bytes) else None


def _fallback_crop_central(image_data: bytes) -> Optional[Image.Image]:
    """Fallback: crop central sem face detection."""
    try:
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail((300, 300), Image.Resampling.LANCZOS)
        left = (img.width - 250) // 2
        top = (img.height - 250) // 2
        right = left + 250
        bottom = top + 250
        img_cropped = img.crop((left, top, right, bottom))
        return _criar_circular_com_borda(img_cropped)
    except Exception as e:
        print(f"Erro no fallback: {e}")
        return None


def _criar_circular_com_borda(img: Image.Image, tamanho: int = 250, borda_px: int = 6) -> Image.Image:
    """Cria versão circular da imagem com borda branca."""
    img = img.resize((tamanho, tamanho), Image.Resampling.LANCZOS)
    tamanho_com_borda = tamanho + (borda_px * 2)
    img_com_borda = Image.new('RGBA', (tamanho_com_borda, tamanho_com_borda), (255, 255, 255, 255))
    img_com_borda.paste(img, (borda_px, borda_px))

    mask = Image.new('L', (tamanho_com_borda, tamanho_com_borda), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse([0, 0, tamanho_com_borda - 1, tamanho_com_borda - 1], fill=255)
    img_com_borda.putalpha(mask)

    return img_com_borda
