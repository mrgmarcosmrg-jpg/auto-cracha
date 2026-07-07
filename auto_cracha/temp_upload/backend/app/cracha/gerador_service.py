from PIL import Image

from app.cracha.templates import horizontal_padrao, vertical_padrao

TEMPLATES_FACTORY = {
    "vertical_padrao": vertical_padrao.renderizar,
    "horizontal_padrao": horizontal_padrao.renderizar,
    # novos templates: apenas adicionar aqui + criar o arquivo em app/cracha/templates/
}


def gerar_cracha(dados: dict) -> Image.Image:
    fn = TEMPLATES_FACTORY.get(dados.get("template_id"), vertical_padrao.renderizar)
    return fn(dados)
