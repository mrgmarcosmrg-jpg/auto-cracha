from PIL import Image, ImageDraw

from app.cracha.utils.cores import escurecer, gradiente_vertical
from app.cracha.utils.faixas import desenhar_zona_faixas
from app.cracha.utils.fontes import ajustar_fonte_para_largura, carregar_fonte, escrever_centralizado
from app.cracha.utils.foto import baixar_imagem, criar_circulo, processar_foto
from app.cracha.utils.qr import gerar_qr

LARGURA = 500
ALTURA = 800


def renderizar(dados: dict) -> Image.Image:
    canvas = Image.new("RGB", (LARGURA, ALTURA), "white")
    draw = ImageDraw.Draw(canvas)

    cor_primaria = dados.get("cor_primaria") or "#0F172A"
    nome_empresa = (dados.get("nome_empresa") or "").strip()

    _desenhar_cabecalho(canvas, draw, dados, cor_primaria, nome_empresa)
    _desenhar_foto(canvas, dados)
    _desenhar_nome_e_cargo(draw, dados)
    _desenhar_qrcode(canvas, dados)
    desenhar_zona_faixas(draw, dados, x_inicio=0, largura=LARGURA, y_inicio=635, altura_total=90)

    return canvas


def _desenhar_cabecalho(canvas: Image.Image, draw: ImageDraw.ImageDraw, dados: dict, cor_primaria: str, nome_empresa: str) -> None:
    gradiente = gradiente_vertical(LARGURA, 210, cor_primaria, escurecer(cor_primaria, 0.15))
    canvas.paste(gradiente, (0, 0))

    logo = baixar_imagem(dados.get("logo_url"))
    if logo:
        logo = _ajustar_logo(logo, max_largura=312, max_altura=90)
        x = (LARGURA - logo.width) // 2
        canvas.paste(logo, (x, 20), logo)
    else:
        escrever_centralizado(draw, nome_empresa, 0, LARGURA, y=55, fonte=carregar_fonte(28), cor="white")

    fonte_nome_empresa = ajustar_fonte_para_largura(draw, nome_empresa.upper(), 480, 31, 14)
    escrever_centralizado(draw, nome_empresa.upper(), 0, LARGURA, y=115, fonte=fonte_nome_empresa, cor="white")


def _ajustar_logo(logo: Image.Image, max_largura: int, max_altura: int) -> Image.Image:
    logo = logo.convert("RGBA")
    proporcao = min(max_largura / logo.width, max_altura / logo.height, 1)
    novo_tamanho = (max(1, int(logo.width * proporcao)), max(1, int(logo.height * proporcao)))
    return logo.resize(novo_tamanho, Image.LANCZOS)


def _desenhar_foto(canvas: Image.Image, dados: dict) -> None:
    foto = processar_foto(dados.get("foto_url"), tamanho=250)
    foto_circular = criar_circulo(foto, tamanho=250, borda_px=6)
    x = (LARGURA - foto_circular.width) // 2
    canvas.paste(foto_circular, (x, 148), foto_circular)


def _desenhar_nome_e_cargo(draw: ImageDraw.ImageDraw, dados: dict) -> None:
    nome = (dados.get("nome") or "").upper()
    fonte_nome = ajustar_fonte_para_largura(draw, nome, 480, 42, 18)
    escrever_centralizado(draw, nome, 0, LARGURA, y=400, fonte=fonte_nome, cor="#0F172A")

    cargo = (dados.get("cargo") or "COLABORADOR").upper()
    escrever_centralizado(draw, cargo, 0, LARGURA, y=440, fonte=carregar_fonte(28), cor="#0F172A")


def _desenhar_qrcode(canvas: Image.Image, dados: dict) -> None:
    qr = gerar_qr(str(dados.get("qr_token")), tamanho=160)
    x = (LARGURA - qr.width) // 2
    canvas.paste(qr, (x, 468))
