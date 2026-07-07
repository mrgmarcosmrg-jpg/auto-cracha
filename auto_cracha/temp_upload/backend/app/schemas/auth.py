from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    nome_empresa: str
    cnpj: str
    email: EmailStr
    senha: str = Field(min_length=8)
    nome_responsavel: str


class LoginRequest(BaseModel):
    email: EmailStr
    senha: str


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
