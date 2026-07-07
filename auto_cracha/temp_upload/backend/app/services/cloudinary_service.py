import os

import cloudinary
import cloudinary.uploader

cloudinary.config(cloudinary_url=os.environ.get("CLOUDINARY_URL", ""))


def upload_imagem(conteudo: bytes, folder: str) -> str:
    resultado = cloudinary.uploader.upload(conteudo, folder=folder, resource_type="image")
    return resultado["secure_url"]


def upload_pdf(conteudo: bytes, filename: str, folder: str = "lotes") -> str:
    resultado = cloudinary.uploader.upload(
        conteudo, folder=folder, resource_type="raw", public_id=filename, overwrite=True
    )
    return resultado["secure_url"]
