import io
import urllib.request
from typing import Optional

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps


def baixar_imagem(url: Optional[str], timeout: int = 10) -> Optional[Image.Image]:
    if not url:
        return None
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resposta:
            conteudo = resposta.read()
        with Image.open(io.BytesIO(conteudo)) as img:
            img.load()
            return ImageOps.exif_transpose(img).convert("RGB")
    except Exception:
        return None


def processar_foto(url: Optional[str], tamanho: int = 250) -> Image.Image:
    """Baixa a foto, corrige EXIF, detecta rosto e recorta/redimensiona para um quadrado.

    Sem foto ou erro no download: usa um placeholder com ícone de pessoa.
    Foto sem rosto detectável: usa recorte central (fallback).
    """
    imagem = baixar_imagem(url)
    if imagem is None:
        return _placeholder(tamanho)

    recorte = _recortar_rosto(imagem) or _recorte_central(imagem)
    return recorte.resize((tamanho, tamanho), Image.LANCZOS)


def _placeholder(tamanho: int) -> Image.Image:
    img = Image.new("RGB", (tamanho, tamanho), "#CBD5E1")
    draw = ImageDraw.Draw(img)
    raio = tamanho // 3
    centro = tamanho // 2
    draw.ellipse([centro - raio // 2, centro - raio, centro + raio // 2, centro], fill="#94A3B8")
    draw.ellipse([centro - raio, centro + raio // 3, centro + raio, centro + raio * 2], fill="#94A3B8")
    return img


def _recortar_rosto(img: Image.Image) -> Optional[Image.Image]:
    try:
        cinza = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        detector = cv2.CascadeClassifier(cascade_path)
        rostos = detector.detectMultiScale(cinza, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
    except Exception:
        return None

    if len(rostos) == 0:
        return None

    x, y, w, h = max(rostos, key=lambda r: r[2] * r[3])
    cx, cy = x + w // 2, y + h // 2

    largura, altura = img.size
    lado = min(int(max(w, h) * 1.8), largura, altura)
    metade = lado // 2

    esquerda = max(0, min(cx - metade, largura - lado))
    topo = max(0, min(cy - metade, altura - lado))
    return img.crop((esquerda, topo, esquerda + lado, topo + lado))


def _recorte_central(img: Image.Image) -> Image.Image:
    largura, altura = img.size
    lado = min(largura, altura)
    esquerda = (largura - lado) // 2
    topo = (altura - lado) // 2
    return img.crop((esquerda, topo, esquerda + lado, topo + lado))


def criar_circulo(img: Image.Image, tamanho: int, borda_px: int = 6) -> Image.Image:
    """Aplica máscara circular com borda branca ao redor."""
    img = img.resize((tamanho, tamanho), Image.LANCZOS).convert("RGB")

    mascara = Image.new("L", (tamanho, tamanho), 0)
    ImageDraw.Draw(mascara).ellipse((0, 0, tamanho, tamanho), fill=255)

    tamanho_total = tamanho + borda_px * 2
    resultado = Image.new("RGBA", (tamanho_total, tamanho_total), (0, 0, 0, 0))
    ImageDraw.Draw(resultado).ellipse((0, 0, tamanho_total, tamanho_total), fill="white")

    circulo = Image.new("RGBA", (tamanho, tamanho))
    circulo.paste(img, (0, 0), mascara)
    resultado.paste(circulo, (borda_px, borda_px), circulo)

    return resultado
