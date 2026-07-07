from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    nome_empresa: str
    cnpj: str
    email: EmailStr
    senha: str = Field(min_length=8)
    nome_responsavel: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(alias="senha")

    model_config = ConfigDict(populate_by_name=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    nova_senha: str = Field(min_length=8)


class AceitarConviteRequest(BaseModel):
    senha: str = Field(min_length=8)
