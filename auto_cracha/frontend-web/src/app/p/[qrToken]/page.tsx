"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { baixarVCard } from "@/lib/vcard";
import type { PaginaPublicaOut } from "@/lib/types";
import SosModal from "./SosModal";

export default function PaginaPublicaCracha() {
  const params = useParams<{ qrToken: string }>();
  const [pagina, setPagina] = useState<PaginaPublicaOut | null>(null);
  const [erro, setErro] = useState("");
  const [mostrarSos, setMostrarSos] = useState(false);

  useEffect(() => {
    apiFetch<PaginaPublicaOut>(`/p/${params.qrToken}`)
      .then(setPagina)
      .catch((err) => setErro(err instanceof Error ? err.message : "Crachá não encontrado"));
  }, [params.qrToken]);

  if (erro) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 p-6 text-center">
        <p className="text-slate-600">{erro}</p>
      </main>
    );
  }

  if (!pagina) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-slate-600">Carregando...</p>
      </main>
    );
  }

  const { empresa, colaborador } = pagina;

  function linkMaps() {
    if (!empresa.endereco_completo) return null;
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(empresa.endereco_completo)}`;
  }

  function linkWhatsappEmpresa() {
    if (!empresa.whatsapp) return null;
    const digitos = empresa.whatsapp.replace(/\D/g, "");
    return `https://wa.me/55${digitos}`;
  }

  function linkWhatsappColaborador() {
    if (!colaborador.celular) return null;
    const digitos = colaborador.celular.replace(/\D/g, "");
    return `https://wa.me/55${digitos}`;
  }

  function salvarContatoEmpresa() {
    baixarVCard(
      {
        nome: empresa.nome_fantasia || "Empresa",
        telefone: empresa.whatsapp || empresa.telefone,
        email: empresa.email_empresa,
      },
      "empresa.vcf"
    );
  }

  function salvarContatoColaborador() {
    baixarVCard(
      {
        nome: colaborador.nome || "Colaborador",
        telefone: colaborador.celular,
        email: colaborador.email_colaborador,
        organizacao: empresa.nome_fantasia,
      },
      "colaborador.vcf"
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mx-auto flex max-w-md flex-col gap-4">
        {/* Camada 1: dados da empresa */}
        <div className="flex flex-col items-center gap-2 rounded-xl bg-white p-5 text-center shadow-sm">
          {empresa.logo_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={empresa.logo_url} alt={empresa.nome_fantasia || ""} className="h-16 max-w-[200px] object-contain" />
          )}
          <h1 className="text-lg font-bold text-slate-900">{empresa.nome_fantasia}</h1>
          {empresa.razao_social && <p className="text-sm text-slate-500">{empresa.razao_social}</p>}

          <div className="mt-2 flex flex-col gap-1 text-sm text-slate-600">
            {empresa.endereco_completo && (
              <p>
                {empresa.endereco_completo}
                {linkMaps() && (
                  <>
                    {" · "}
                    <a href={linkMaps()!} target="_blank" rel="noreferrer" className="text-blue-600 underline">
                      Ver no Maps
                    </a>
                  </>
                )}
              </p>
            )}
            {empresa.telefone && <p>{empresa.telefone}</p>}
            {empresa.email_empresa && <p>{empresa.email_empresa}</p>}
          </div>

          <div className="mt-2 flex flex-wrap justify-center gap-2 text-sm">
            {linkWhatsappEmpresa() && (
              <a href={linkWhatsappEmpresa()!} target="_blank" rel="noreferrer" className="text-green-700 underline">
                WhatsApp
              </a>
            )}
            {empresa.redes_sociais?.instagram && (
              <a
                href={`https://instagram.com/${empresa.redes_sociais.instagram.replace("@", "")}`}
                target="_blank"
                rel="noreferrer"
                className="text-pink-600 underline"
              >
                Instagram
              </a>
            )}
            {empresa.redes_sociais?.site && (
              <a href={empresa.redes_sociais.site} target="_blank" rel="noreferrer" className="text-blue-600 underline">
                Site
              </a>
            )}
          </div>

          <button onClick={salvarContatoEmpresa} className="mt-2 h-11 rounded-lg border border-slate-300 px-4 text-sm">
            Salvar contato da empresa
          </button>
        </div>

        {/* Camada 2: dados do colaborador, conforme status */}
        <div className="flex flex-col items-center gap-2 rounded-xl bg-white p-5 text-center shadow-sm">
          {colaborador.status === "PENDENTE_LGPD" && (
            <>
              <p className="text-lg font-medium text-slate-900">{colaborador.nome}</p>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-sm font-medium text-amber-800">
                Aguardando autorização
              </span>
            </>
          )}

          {colaborador.acesso_expirado && (
            <span className="rounded-full bg-slate-200 px-3 py-1 text-sm font-medium text-slate-600">
              Acesso Expirado
            </span>
          )}

          {colaborador.status === "DESLIGADO" && (
            <>
              {colaborador.foto_url && (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={colaborador.foto_url}
                  alt={colaborador.nome || ""}
                  className="h-28 w-28 rounded-full object-cover grayscale"
                />
              )}
              <p className="text-lg font-medium text-slate-900">{colaborador.nome}</p>
              <span className="rounded-full bg-red-100 px-3 py-1 text-sm font-medium text-red-800">
                Vínculo Encerrado
                {colaborador.data_desligamento && ` em ${new Date(colaborador.data_desligamento).toLocaleDateString("pt-BR")}`}
              </span>
            </>
          )}

          {!colaborador.acesso_expirado && (colaborador.status === "ATIVO" || colaborador.status === "VISITANTE") && (
            <>
              {colaborador.foto_url && (
                // eslint-disable-next-line @next/next/no-img-element
                <img src={colaborador.foto_url} alt={colaborador.nome || ""} className="h-28 w-28 rounded-full object-cover" />
              )}
              <p className="text-lg font-medium text-slate-900">{colaborador.nome}</p>
              <p className="text-sm text-slate-500">{colaborador.cargo}</p>
              <span className="rounded-full bg-green-100 px-3 py-1 text-sm font-medium text-green-800">
                ✓ Colaborador Ativo
              </span>

              {colaborador.exibir_contato_pessoal && (
                <div className="mt-2 flex gap-2">
                  {linkWhatsappColaborador() && (
                    <a
                      href={linkWhatsappColaborador()!}
                      target="_blank"
                      rel="noreferrer"
                      className="flex h-11 items-center rounded-lg bg-green-600 px-4 text-sm font-semibold text-white"
                    >
                      WhatsApp
                    </a>
                  )}
                  <button onClick={salvarContatoColaborador} className="h-11 rounded-lg border border-slate-300 px-4 text-sm">
                    Salvar contato
                  </button>
                </div>
              )}
            </>
          )}
        </div>

        {/* Camada 3: contato de emergência (visível sem PIN) */}
        {colaborador.contato_emergencia_nome && (
          <div className="rounded-xl bg-white p-4 shadow-sm">
            <p className="text-sm font-medium text-slate-700">🆘 Contato de emergência</p>
            <p className="text-base text-slate-900">{colaborador.contato_emergencia_nome}</p>
            <p className="text-sm text-slate-600">{colaborador.contato_emergencia_tel}</p>
            <p className="mt-1 text-xs text-slate-400">Informação de emergência — visível para qualquer pessoa.</p>
          </div>
        )}

        {/* Camada 4: botão SOS (só se houver PIN cadastrado) */}
        {colaborador.tem_sos && (
          <button
            onClick={() => setMostrarSos(true)}
            className="h-12 rounded-lg bg-red-600 text-base font-semibold text-white"
          >
            🚑 Dados de Emergência
          </button>
        )}
      </div>

      {mostrarSos && <SosModal qrToken={params.qrToken} onClose={() => setMostrarSos(false)} />}
    </main>
  );
}
