"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { authFetch } from "@/lib/api";
import { obterToken } from "@/lib/auth";
import type { HistoricoLoteOut, LoteCrachaOut, LoteDetalheOut, PdfUrlOut } from "@/lib/types";
import LoteStatusBadge from "../LoteStatusBadge";
import MarcarFalhaModal from "./MarcarFalhaModal";

export default function LoteDetalhePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [lote, setLote] = useState<LoteDetalheOut | null>(null);
  const [aba, setAba] = useState<"crachas" | "historico">("crachas");
  const [historico, setHistorico] = useState<HistoricoLoteOut[]>([]);
  const [crachaFalhando, setCrachaFalhando] = useState<LoteCrachaOut | null>(null);
  const [erro, setErro] = useState("");

  async function carregar() {
    const data = await authFetch<LoteDetalheOut>(`/lotes/${params.id}`);
    setLote(data);
  }

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
      return;
    }
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, params.id]);

  async function carregarHistorico() {
    const data = await authFetch<HistoricoLoteOut[]>(`/lotes/${params.id}/historico`);
    setHistorico(data);
  }

  function abrirAba(novaAba: "crachas" | "historico") {
    setAba(novaAba);
    if (novaAba === "historico") carregarHistorico();
  }

  async function marcarImpresso(crachaId: string) {
    setErro("");
    try {
      await authFetch(`/lotes/${params.id}/crachas/${crachaId}/impresso`, { method: "PATCH" });
      await carregar();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao marcar como impresso");
    }
  }

  async function confirmarFalha(motivo: string) {
    if (!crachaFalhando) return;
    setErro("");
    try {
      await authFetch(`/lotes/${params.id}/crachas/${crachaFalhando.id}/falhou`, {
        method: "PATCH",
        body: JSON.stringify({ motivo_falha: motivo }),
      });
      setCrachaFalhando(null);
      await carregar();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao marcar falha");
    }
  }

  async function handleBaixarPdf() {
    const data = await authFetch<PdfUrlOut>(`/lotes/${params.id}/pdf`);
    window.open(data.pdf_url, "_blank");
  }

  async function handleArquivar() {
    if (!confirm("Confirma o arquivamento deste lote?")) return;
    await authFetch(`/lotes/${params.id}/arquivar`, { method: "POST" });
    await carregar();
  }

  if (!lote) {
    return (
      <main className="min-h-screen bg-slate-50 p-6">
        <p className="text-slate-600">Carregando...</p>
      </main>
    );
  }

  const processados = lote.quantidade_impressos + lote.quantidade_falhados;
  const progresso = lote.quantidade_total > 0 ? Math.round((processados / lote.quantidade_total) * 100) : 0;
  const podeArquivar = lote.status_lote === "IMPRESSO" || lote.status_lote === "PARCIALMENTE_IMPRESSO";

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-bold text-slate-900">{lote.nome_lote}</h1>
        <LoteStatusBadge status={lote.status_lote} />
      </div>

      <div className="mt-3 h-3 w-full rounded-full bg-slate-200">
        <div className="h-3 rounded-full bg-green-600" style={{ width: `${progresso}%` }} />
      </div>
      <p className="mt-1 text-sm text-slate-600">
        {processados} de {lote.quantidade_total} processados ({lote.quantidade_impressos} impressos,{" "}
        {lote.quantidade_falhados} falharam)
      </p>

      <div className="mt-4 flex flex-wrap gap-2">
        {lote.pdf_url && (
          <button onClick={handleBaixarPdf} className="h-11 rounded-lg bg-slate-900 px-4 text-sm font-semibold text-white">
            Baixar PDF
          </button>
        )}
        {podeArquivar && (
          <button onClick={handleArquivar} className="h-11 rounded-lg border border-slate-300 px-4 text-sm">
            Arquivar lote
          </button>
        )}
      </div>

      {erro && <p className="mt-2 text-sm text-red-600">{erro}</p>}

      <div className="mt-4 flex gap-2">
        <button
          onClick={() => abrirAba("crachas")}
          className={`h-11 rounded-lg px-4 text-sm font-medium ${aba === "crachas" ? "bg-slate-900 text-white" : "border border-slate-300"}`}
        >
          Crachás
        </button>
        <button
          onClick={() => abrirAba("historico")}
          className={`h-11 rounded-lg px-4 text-sm font-medium ${aba === "historico" ? "bg-slate-900 text-white" : "border border-slate-300"}`}
        >
          Histórico
        </button>
      </div>

      {aba === "crachas" && (
        <ul className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {lote.crachas.map((cracha) => (
            <li key={cracha.id} className="flex flex-col gap-2 rounded-lg border border-slate-200 bg-white p-3">
              <p className="text-base font-medium text-slate-900">{cracha.nome_snapshot}</p>
              <p className="text-sm text-slate-500">{cracha.cargo_snapshot}</p>
              <p className="text-xs text-slate-400">
                Pág. {cracha.numero_pagina} · Pos. {cracha.posicao_na_pagina}
              </p>
              {cracha.status_cracha === "PENDENTE" && (
                <div className="flex gap-2">
                  <button
                    onClick={() => marcarImpresso(cracha.id)}
                    className="h-11 flex-1 rounded-lg bg-green-600 text-sm font-semibold text-white"
                  >
                    ✓ Impresso
                  </button>
                  <button
                    onClick={() => setCrachaFalhando(cracha)}
                    className="h-11 flex-1 rounded-lg bg-red-600 text-sm font-semibold text-white"
                  >
                    ✗ Falhou
                  </button>
                </div>
              )}
              {cracha.status_cracha === "IMPRESSO" && <p className="text-sm font-medium text-green-700">✓ Impresso</p>}
              {cracha.status_cracha === "FALHOU" && (
                <p className="text-sm font-medium text-red-600">✗ Falhou: {cracha.motivo_falha}</p>
              )}
            </li>
          ))}
        </ul>
      )}

      {aba === "historico" && (
        <ul className="mt-4 flex flex-col gap-2">
          {historico.map((evento) => (
            <li key={evento.id} className="rounded-lg border border-slate-200 bg-white p-3 text-sm">
              <p className="font-medium text-slate-900">{evento.tipo_evento}</p>
              <p className="text-slate-500">
                {new Date(evento.ocorrido_em).toLocaleString("pt-BR")}
                {evento.quantidade_afetada != null && ` · ${evento.quantidade_afetada} item(ns)`}
              </p>
              {evento.descricao && <p className="text-slate-600">{evento.descricao}</p>}
            </li>
          ))}
          {historico.length === 0 && <p className="text-sm text-slate-500">Sem eventos registrados.</p>}
        </ul>
      )}

      {crachaFalhando && (
        <MarcarFalhaModal onCancelar={() => setCrachaFalhando(null)} onConfirmar={confirmarFalha} />
      )}
    </main>
  );
}
