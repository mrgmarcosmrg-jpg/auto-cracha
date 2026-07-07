import uuid

from pydantic import BaseModel


class PreviewRequest(BaseModel):
    colaborador_id: uuid.UUID
    template_id: str = "vertical_padrao"
