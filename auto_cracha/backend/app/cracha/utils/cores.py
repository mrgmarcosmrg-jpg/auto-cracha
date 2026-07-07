from PIL import Image


def hex_para_rgb(cor_hex: str) -> tuple[int, int, int]:
    cor_hex = cor_hex.lstrip("#")
    return tuple(int(cor_hex[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore[return-value]


def escurecer(cor_hex: str, fator: float = 0.15) -> str:
    r, g, b = hex_para_rgb(cor_hex)
    r = int(r * (1 - fator))
    g = int(g * (1 - fator))
    b = int(b * (1 - fator))
    return f"#{r:02x}{g:02x}{b:02x}"


def gradiente_vertical(largura: int, altura: int, cor_topo: str, cor_base: str) -> Image.Image:
    r1, g1, b1 = hex_para_rgb(cor_topo)
    r2, g2, b2 = hex_para_rgb(cor_base)

    coluna = Image.new("RGB", (1, altura))
    for y in range(altura):
        t = y / max(altura - 1, 1)
        coluna.putpixel(
            (0, y),
            (int(r1 + (r2 - r1) * t), int(g1 + (g2 - g1) * t), int(b1 + (b2 - b1) * t)),
        )
    return coluna.resize((largura, altura))
