"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { authFetch } from "@/lib/api";
import { obterToken } from "@/lib/auth";
import type { ColaboradorOut, ConfigOut, FilialOut, LoteCriadoOut, LoteOut, ModoImpressao } from "@/lib/types";

const MESES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
];

export default function NovoLotePage() {
  const router = useRouter();
  const [passo, setPasso] = useState<1 | 2>(1);

  const [colaboradores, setColaboradores] = useState<ColaboradorOut[]>([]);
  const [filiais, setFiliais] = useState<FilialOut[]>([]);
  const [config, setConfig] = useState<ConfigOut | null>(null);
  const [carregado, setCarregado] = useState(false);

  const [filtroFilial, setFiltroFilial] = useState("");
  const [filtroCargo, setFiltroCargo] = useState("");
  const [busca, setBusca] = useState("");
  const [selecionados, setSelecionados] = useState<Set<string>>(new Set());

  const [nomeLote, setNomeLote] = useState("");
  const [modoImpressao, setModoImpressao] = useState<ModoImpressao>("A4_3X3");
  const [erro, setErro] = useState("");
  const [gerando, setGerando] = useState(false);

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
      return;
    }
    Promise.all([
      authFetch<ColaboradorOut[]>("/colaboradores?status=ATIVO"),
      authFetch<ColaboradorOut[]>("/colaboradores?status=PENDENTE_LGPD"),
      authFetch<FilialOut[]>("/filiais"),
      authFetch<ConfigOut>("/config"),
    ]).then(([ativos, pendentes, filiaisData, configData]) => {
      setColaboradores([...ativos, ...pendentes]);
      setFiliais(filiaisData);
      setConfig(configData);
      setCarregado(true);
    });
  }, [router]);

  const cargosDisponiveis = useMemo(
    () => Array.from(new Set(colaboradores.map((c) => c.cargo))).sort(),
    [colaboradores]
  );

  const filtrados = useMemo(() => {
    return colaboradores.filter((c) => {
      if (filtroFilial && c.filial_id !== filtroFilial) return false;
      if (filtroCargo && c.cargo !== filtroCargo) return false;
      if (busca && !c.nome.toLowerCase().includes(busca.toLowerCase())) return false;
      return true;
    });
  }, [colaboradores, filtroFilial, filtroCargo, busca]);

  function nomeFilial(filialId: string) {
    return filiais.find((f) => f.id === filialId)?.nome || "—";
  }

  function alternarSelecao(id: string) {
    setSelecionados((prev) => {
      const novo = new Set(prev);
      if (novo.has(id)) {
        novo.delete(id);
      } else {
        novo.add(id);
      }
      return novo;
    });
  }

  function selecionarTodosFiltrados() {
    setSelecionados((prev) => {
      const novo = new Set(prev);
      filtrados.filter((c) => c.status === "ATIVO").forEach((c) => novo.add(c.id));
      return novo;
    });
  }

  function avancarParaPasso2() {
    const filialUnica = new Set(
      colaboradores.filter((c) => selecionados.has(c.id)).map((c) => c.filial_id)
    );
    const nomeFilialSugerido = filialUnica.size === 1 ? nomeFilial([...filialUnica][0]) : "Geral";
    const agora = new Date();
    setNomeLote(`Crachás ${nomeFilialSugerido} - ${MESES[agora.getMonth()]} ${agora.getFullYear()}`);
    setPasso(2);
  }

  const totalPaginasEstimado = useMemo(() => {
    if (selecionados.size === 0) return 0;
    if (modoImpressao === "A4_UNITARIO") return selecionados.size;
    const porPagina = config?.template_id === "horizontal_padrao" ? 8 : 9;
    return Math.ceil(selecionados.size / porPagina);
  }, [selecionados.size, modoImpressao, config]);

  async function handleGerar() {
    setErro("");
    setGerando(true);
    try {
      const colaboradoresSelecionados = colaboradores.filter((c) => selecionados.has(c.id));
      const filialId = colaboradoresSelecionados[0]?.filial_id;

      const criado = await authFetch<LoteCriadoOut>("/lotes", {
        method: "POST",
        body: JSON.stringify({
          nome_lote: nomeLote,
          colaborador_ids: [...selecionados],
          filial_id: filialId,
          modo_impressao: modoImpressao,
        }),
      });

      await authFetch<LoteOut>(`/lotes/${criado.lote_id}/gerar-pdf`, { method: "POST" });
      router.push(`/dashboard/lotes/${criado.lote_id}`);
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao gerar o lote");
    } finally {
      setGerando(false);
    }
  }

  if (!carregado) {
    return (
      <main className="min-h-screen bg-slate-50 p-6">
        <p className="text-slate-600">Carregando...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <h1 className="mb-4 text-xl font-bold text-slate-900">
        Novo lote — Passo {passo} de 2
      </h1>

      {passo === 1 && (
        <div className="flex flex-col gap-4">
          <div className="flex flex-col gap-2 sm:flex-row">
            <input
              placeholder="Buscar por nome"
              value={busca}
              onChange={(e) => setBusca(e.target.value)}
              className="h-11 flex-1 rounded-lg border border-slate-300 px-4 text-base"
            />
            <select
              value={filtroFilial}
              onChange={(e) => setFiltroFilial(e.target.value)}
              className="h-11 rounded-lg border border-slate-300 px-4 text-base"
            >
              <option value="">Todas as filiais</option>
              {filiais.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.nome}
                </option>
              ))}
            </select>
            <select
              value={filtroCargo}
              onChange={(e) => setFiltroCargo(e.target.value)}
              className="h-11 rounded-lg border border-slate-300 px-4 text-base"
            >
              <option value="">Todos os cargos</option>
              {cargosDisponiveis.map((cargo) => (
                <option key={cargo} value={cargo}>
                  {cargo}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center justify-between">
            <button onClick={selecionarTodosFiltrados} className="h-11 rounded-lg border border-slate-300 px-4 text-sm">
              Selecionar todos os filtrados
            </button>
            <span className="text-sm font-medium text-slate-700">{selecionados.size} selecionado(s)</span>
          </div>

          <ul className="flex flex-col gap-2">
            {filtrados.map((colaborador) => {
              const desabilitado = colaborador.status !== "ATIVO";
              return (
                <li
                  key={colaborador.id}
                  title={desabilitado ? "Colaborador pendente de autorização LGPD" : undefined}
                  className={`flex items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 ${
                    desabilitado ? "opacity-50" : ""
                  }`}
                >
                  <input
                    type="checkbox"
                    disabled={desabilitado}
                    checked={selecionados.has(colaborador.id)}
                    onChange={() => alternarSelecao(colaborador.id)}
                    className="h-5 w-5"
                  />
                  <div className="flex-1">
                    <p className="text-base font-medium text-slate-900">{colaborador.nome}</p>
                    <p className="text-sm text-slate-500">
                      {colaborador.cargo} · {nomeFilial(colaborador.filial_id)}
                      {desabilitado && " · Pendente LGPD"}
                    </p>
                  </div>
                </li>
              );
            })}
            {filtrados.length === 0 && <p className="text-sm text-slate-500">Nenhum colaborador encontrado.</p>}
          </ul>

          <button
            onClick={avancarParaPasso2}
            disabled={selecionados.size === 0}
            className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
          >
            Avançar ({selecionados.size} selecionado(s))
          </button>
        </div>
      )}

      {passo === 2 && (
        <div className="flex max-w-md flex-col gap-4 rounded-xl bg-white p-4 shadow-sm sm:p-6">
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-slate-700">Nome do lote</span>
            <input
              value={nomeLote}
              onChange={(e) => setNomeLote(e.target.value)}
              className="h-11 rounded-lg border border-slate-300 px-4 text-base"
            />
          </label>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium text-slate-700">Modo de impressão</span>
            <label className="flex h-11 items-center gap-3">
              <input
                type="radio"
                checked={modoImpressao === "A4_3X3"}
                onChange={() => setModoImpressao("A4_3X3")}
                className="h-5 w-5"
              />
              <span className="text-base">A4 3×3 (9 crachás por página)</span>
            </label>
            <label className="flex h-11 items-center gap-3">
              <input
                type="radio"
                checked={modoImpressao === "A4_UNITARIO"}
                onChange={() => setModoImpressao("A4_UNITARIO")}
                className="h-5 w-5"
              />
              <span className="text-base">A4 unitário (1 crachá por página)</span>
            </label>
          </div>

          <p className="text-sm text-slate-600">
            {selecionados.size} crachá(s) · aproximadamente {totalPaginasEstimado} página(s) de PDF
          </p>

          {erro && <p className="text-sm text-red-600">{erro}</p>}

          <div className="flex gap-2">
            <button onClick={() => setPasso(1)} className="h-11 flex-1 rounded-lg border border-slate-300 text-base">
              Voltar
            </button>
            <button
              onClick={handleGerar}
              disabled={gerando || !nomeLote}
              className="h-11 flex-1 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
            >
              {gerando ? "Gerando..." : "Gerar PDF"}
            </button>
          </div>
        </div>
      )}
    </main>
  );
}
