#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Configuração do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://crachapp:crachapp_senha_123456@postgres:5432/crachapp"
)

engine = create_engine(DATABASE_URL)

# Hash da senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    """Inicializa o banco e cria dados padrão"""

    with engine.connect() as conn:
        # Criar extensão UUID
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))

        # Criar tabela usuarios
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                nome VARCHAR(255) NOT NULL,
                senha_hash VARCHAR(255) NOT NULL,
                tenant_id UUID,
                papel VARCHAR(50) DEFAULT 'VISUALIZADOR',
                ativo BOOLEAN DEFAULT true,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        # Inserir usuário admin padrão
        admin_password = "Admin0123456"
        admin_hash = pwd_context.hash(admin_password)

        conn.execute(text("""
            INSERT INTO usuarios (email, nome, senha_hash, papel, ativo)
            VALUES (:email, :nome, :hash, :papel, :ativo)
            ON CONFLICT (email) DO NOTHING
        """), {
            "email": "admin@crachapp.com.br",
            "nome": "Administrador",
            "hash": admin_hash,
            "papel": "SUPER_ADMIN",
            "ativo": True
        })

        conn.commit()
        print("✅ Banco de dados inicializado!")
        print(f"✅ Usuário admin criado: admin@crachapp.com.br / {admin_password}")

if __name__ == "__main__":
    try:
        init_database()
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        sys.exit(1)
