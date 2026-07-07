#!/usr/bin/env python
"""
Script de seed para popular banco de dados com dados iniciais.
Cria: 1 super admin, 1 tenant de teste, 1 filial de teste, e 5 colaboradores de teste.

Executar: python seed.py
"""

import os
import uuid
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.core.security import hash_password
from app.models.assinatura import Assinatura, PlanoAssinatura, StatusAssinatura
from app.models.colaborador import Colaborador
from app.models.config_empresa import ConfigEmpresa
from app.models.filial import Filial
from app.models.tenant import Tenant
from app.models.usuario import Usuario


def seed_database():
    """Cria dados iniciais no banco de dados."""
    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        print("Erro: DATABASE_URL não configurado")
        return

    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Verificar se já existe super admin
        super_admin = session.query(Usuario).filter(
            Usuario.email == "admin@crachapp.com.br"
        ).first()

        if super_admin:
            print("✓ Super admin já existe")
        else:
            super_admin = Usuario(
                id=uuid.uuid4(),
                nome="Super Admin",
                email="admin@crachapp.com.br",
                senha_hash=hash_password("Admin@123456"),
                perfil="SUPER_ADMIN",
                ativo=True,
                tenant_id=None,
                filial_id=None,
            )
            session.add(super_admin)
            print("✓ Super admin criado (admin@crachapp.com.br / Admin@123456)")

        # Criar tenant de teste
        tenant_teste = session.query(Tenant).filter(
            Tenant.nome == "Empresa Teste"
        ).first()

        if not tenant_teste:
            tenant_teste = Tenant(
                id=uuid.uuid4(),
                nome="Empresa Teste",
                cnpj="12.345.678/0001-99",
                email_admin="teste@empresa.com.br",
                ativo=True,
                criado_em=datetime.utcnow(),
            )
            session.add(tenant_teste)
            session.flush()
            print("✓ Tenant de teste criado")

            # Criar admin do tenant
            admin_tenant = Usuario(
                id=uuid.uuid4(),
                nome="Admin Teste",
                email="teste@empresa.com.br",
                senha_hash=hash_password("Teste@123456"),
                perfil="ADMIN_TENANT",
                ativo=True,
                tenant_id=tenant_teste.id,
                filial_id=None,
            )
            session.add(admin_tenant)
            print("✓ Admin do tenant criado (teste@empresa.com.br / Teste@123456)")

            # Criar config da empresa
            config = ConfigEmpresa(
                id=uuid.uuid4(),
                tenant_id=tenant_teste.id,
                nome_empresa="Empresa Teste",
                cnpj="12.345.678/0001-99",
                logo_url=None,
                cor_primaria="#1e293b",
                cor_secundaria="#64748b",
                usar_faixa_treinamento=True,
                usar_faixa_pcd=True,
                status="ATIVO",
                trial_expira_em=datetime.utcnow() + timedelta(days=30),
                template_id="vertical_padrao",
            )
            session.add(config)
            print("✓ Configuração da empresa criada")

            # Criar filial de teste
            filial = Filial(
                id=uuid.uuid4(),
                tenant_id=tenant_teste.id,
                nome="Filial Principal",
                cnpj=None,
                endereco="Rua Teste, 123 - São Paulo, SP",
                logo_filial_url=None,
                logo_grupo_url=None,
                ativo=True,
            )
            session.add(filial)
            session.flush()
            print("✓ Filial de teste criada")

            # Criar gestor de filial
            gestor_filial = Usuario(
                id=uuid.uuid4(),
                nome="Gestor Filial",
                email="gestor@empresa.com.br",
                senha_hash=hash_password("Gestor@123456"),
                perfil="GESTOR_FILIAL",
                ativo=True,
                tenant_id=tenant_teste.id,
                filial_id=filial.id,
            )
            session.add(gestor_filial)
            print("✓ Gestor de filial criado (gestor@empresa.com.br / Gestor@123456)")

            # Criar colaboradores de teste
            for i in range(1, 6):
                colaborador = Colaborador(
                    id=uuid.uuid4(),
                    tenant_id=tenant_teste.id,
                    filial_id=filial.id,
                    qr_token=uuid.uuid4(),
                    nome=f"Colaborador Teste {i}",
                    cargo="Desenvolvedor" if i % 2 == 0 else "Designer",
                    cpf_criptografado=None,
                    cpf_hash=None,
                    celular="11999999999",
                    email_colaborador=f"colab{i}@empresa.com.br",
                    em_treinamento=i == 1,
                    pcd=i == 2,
                    status="PENDENTE_LGPD" if i <= 2 else "ATIVO",
                    foto_url=None,
                )
                session.add(colaborador)
            print("✓ 5 colaboradores de teste criados")

            # Criar assinatura de teste
            assinatura = Assinatura(
                id=uuid.uuid4(),
                tenant_id=tenant_teste.id,
                plano=PlanoAssinatura.PRATA,
                status=StatusAssinatura.ATIVO,
                max_colaboradores=200,
                creditos_pix=10,
                trial_expira_em=datetime.utcnow() + timedelta(days=30),
            )
            session.add(assinatura)
            print("✓ Assinatura de teste criada (Plano Prata)")

        else:
            print("✓ Tenant de teste já existe")

        session.commit()
        print("\n✅ Seed concluído com sucesso!")
        print("\nCredenciais de teste:")
        print("  Super Admin: admin@crachapp.com.br / Admin@123456")
        print("  Admin Tenant: teste@empresa.com.br / Teste@123456")
        print("  Gestor Filial: gestor@empresa.com.br / Gestor@123456")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Erro ao fazer seed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
