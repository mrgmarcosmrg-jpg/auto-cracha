from PIL import Image, ImageDraw

from app.cracha.utils.faixas import desenhar_zona_faixas
from app.cracha.utils.fontes import ajustar_fonte_para_largura, carregar_fonte, escrever_centralizado
from app.cracha.utils.foto import baixar_imagem, criar_circulo, processar_foto
from app.cracha.utils.qr import gerar_qr

LARGURA = 800
ALTURA = 500
DIVISORIA_X = 350


def renderizar(dados: dict) -> Image.Image:
    canvas = Image.new("RGB", (LARGURA, ALTURA), "white")
    draw = ImageDraw.Draw(canvas)

    cor_primaria = dados.get("cor_primaria") or "#0F172A"
    draw.rectangle([0, 0, DIVISORIA_X, ALTURA], fill=cor_primaria)

    _desenhar_lado_esquerdo(canvas, draw, dados)
    _desenhar_lado_direito(canvas, draw, dados)

    return canvas


def _desenhar_lado_esquerdo(canvas: Image.Image, draw: ImageDraw.ImageDraw, dados: dict) -> None:
    foto = processar_foto(dados.get("foto_url"), tamanho=180)
    foto_circular = criar_circulo(foto, tamanho=180, borda_px=5)
    x = (DIVISORIA_X - foto_circular.width) // 2
    canvas.paste(foto_circular, (x, 60), foto_circular)

    nome = (dados.get("nome") or "").upper()
    fonte_nome = ajustar_fonte_para_largura(draw, nome, DIVISORIA_X - 40, 26, 14)
    escrever_centralizado(draw, nome, 0, DIVISORIA_X, y=270, fonte=fonte_nome, cor="white")

    cargo = (dados.get("cargo") or "COLABORADOR").upper()
    escrever_centralizado(draw, cargo, 0, DIVISORIA_X, y=305, fonte=carregar_fonte(18), cor="white")


def _desenhar_lado_direito(canvas: Image.Image, draw: ImageDraw.ImageDraw, dados: dict) -> None:
    largura_direita = LARGURA - DIVISORIA_X
    centro_x = DIVISORIA_X + largura_direita // 2
    nome_empresa = (dados.get("nome_empresa") or "").strip()

    logo = baixar_imagem(dados.get("logo_url"))
    if logo:
        logo = _ajustar_logo(logo, max_largura=largura_direita - 40, max_altura=80)
        x = centro_x - logo.width // 2
        canvas.paste(logo, (x, 30), logo)
    else:
        escrever_centralizado(
            draw, nome_empresa.upper(), DIVISORIA_X, largura_direita, y=60, fonte=carregar_fonte(20), cor="#0F172A"
        )

    qr = gerar_qr(str(dados.get("qr_token")), tamanho=140)
    x_qr = centro_x - qr.width // 2
    canvas.paste(qr, (x_qr, 150))

    desenhar_zona_faixas(draw, dados, x_inicio=DIVISORIA_X, largura=largura_direita, y_inicio=410, altura_total=70)


def _ajustar_logo(logo: Image.Image, max_largura: int, max_altura: int) -> Image.Image:
    logo = logo.convert("RGBA")
    proporcao = min(max_largura / logo.width, max_altura / logo.height, 1)
    novo_tamanho = (max(1, int(logo.width * proporcao)), max(1, int(logo.height * proporcao)))
    return logo.resize(novo_tamanho, Image.LANCZOS)
