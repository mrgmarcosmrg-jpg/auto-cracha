"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch } from "@/lib/api";
import type { MeuCrachaOut } from "@/lib/types";
import FotoSection from "./FotoSection";
import ContatoVisivelSection from "./ContatoVisivelSection";
import DadosMedicosSection from "./DadosMedicosSection";

export default function MeuCrachaPage() {
  const params = useParams<{ qrToken: string }>();
  const [dados, setDados] = useState<MeuCrachaOut | null>(null);
  const [erro, setErro] = useState("");
  const [autorizando, setAutorizando] = useState(false);

  async function carregar() {
    try {
      const data = await apiFetch<MeuCrachaOut>(`/meu-cracha/${params.qrToken}`);
      setDados(data);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Link inválido");
    }
  }

  useEffect(() => {
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params.qrToken]);

  async function handleAutorizar() {
    setAutorizando(true);
    try {
      await apiFetch(`/meu-cracha/${params.qrToken}/autorizar`, { method: "POST" });
      await carregar();
    } finally {
      setAutorizando(false);
    }
  }

  if (erro) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <p className="text-slate-600">{erro}</p>
      </main>
    );
  }

  if (!dados) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-slate-50">
        <p className="text-slate-600">Carregando...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mx-auto flex max-w-md flex-col gap-4">
        <div className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
          ⚠️ Este link é pessoal — não compartilhe.
        </div>

        <h1 className="text-xl font-bold text-slate-900">Olá, {dados.nome}</h1>
        <p className="text-sm text-slate-500">{dados.cargo}</p>

        {dados.status === "PENDENTE_LGPD" && (
          <div className="rounded-xl bg-white p-4 shadow-sm">
            <p className="mb-3 text-sm text-slate-600">
              Confirme seus dados para ativar seu crachá. Você pode revisar e editar tudo abaixo antes de
              autorizar.
            </p>
            <button
              onClick={handleAutorizar}
              disabled={autorizando}
              className="h-11 w-full rounded-lg bg-green-600 text-base font-semibold text-white disabled:opacity-60"
            >
              {autorizando ? "Autorizando..." : "Autorizar meus dados e ativar meu crachá"}
            </button>
          </div>
        )}

        <FotoSection qrToken={params.qrToken} fotoUrl={dados.foto_url} onAtualizado={carregar} />

        <ContatoVisivelSection
          qrToken={params.qrToken}
          exibirContatoPessoal={dados.exibir_contato_pessoal}
          onAtualizado={carregar}
        />

        <DadosMedicosSection
          qrToken={params.qrToken}
          temDadosMedicos={dados.tem_dados_medicos}
          dataNascimentoAtual={dados.data_nascimento}
          contatoEmergenciaNomeAtual={dados.contato_emergencia_nome}
          contatoEmergenciaTelAtual={dados.contato_emergencia_tel}
          onAtualizado={carregar}
        />
      </div>
    </main>
  );
}
