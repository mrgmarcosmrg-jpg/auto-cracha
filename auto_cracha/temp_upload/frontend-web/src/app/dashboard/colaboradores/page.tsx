"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authFetch } from "@/lib/api";
import { obterToken } from "@/lib/auth";
import type { ColaboradorOut, FilialOut, StatusColaborador } from "@/lib/types";
import StatusBadge from "./StatusBadge";
import NovoColaboradorModal from "./NovoColaboradorModal";
import ImportarCsvModal from "./ImportarCsvModal";

const STATUS_OPCOES: { id: StatusColaborador | ""; label: string }[] = [
  { id: "", label: "Todos os status" },
  { id: "PENDENTE_LGPD", label: "Pendente LGPD" },
  { id: "ATIVO", label: "Ativo" },
  { id: "DESLIGADO", label: "Desligado" },
  { id: "VISITANTE", label: "Visitante" },
];

export default function ColaboradoresPage() {
  const router = useRouter();
  const [colaboradores, setColaboradores] = useState<ColaboradorOut[]>([]);
  const [filiais, setFiliais] = useState<FilialOut[]>([]);
  const [carregado, setCarregado] = useState(false);
  const [filtroFilial, setFiltroFilial] = useState("");
  const [filtroStatus, setFiltroStatus] = useState<StatusColaborador | "">("");
  const [busca, setBusca] = useState("");
  const [mostrarNovo, setMostrarNovo] = useState(false);
  const [mostrarImportar, setMostrarImportar] = useState(false);

  async function carregar() {
    const params = new URLSearchParams();
    if (filtroFilial) params.set("filial_id", filtroFilial);
    if (filtroStatus) params.set("status", filtroStatus);
    if (busca) params.set("busca", busca);

    const [colaboradoresData, filiaisData] = await Promise.all([
      authFetch<ColaboradorOut[]>(`/colaboradores?${params.toString()}`),
      authFetch<FilialOut[]>("/filiais"),
    ]);
    setColaboradores(colaboradoresData);
    setFiliais(filiaisData);
    setCarregado(true);
  }

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
      return;
    }
    carregar();
  }, [router]);

  useEffect(() => {
    if (carregado) carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtroFilial, filtroStatus]);

  function handleBuscaSubmit() {
    carregar();
  }

  function nomeFilial(filialId: string) {
    return filiais.find((f) => f.id === filialId)?.nome || "—";
  }

  function abrirWhatsapp(colaborador: ColaboradorOut) {
    authFetch<{ link: string; whatsapp_url: string }>(`/colaboradores/${colaborador.id}/link-lgpd`).then((data) => {
      window.open(data.whatsapp_url, "_blank");
    });
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-xl font-bold text-slate-900">Colaboradores</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setMostrarImportar(true)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-sm"
          >
            Importar CSV
          </button>
          <button
            onClick={() => setMostrarNovo(true)}
            className="h-11 rounded-lg bg-slate-900 px-4 text-sm font-semibold text-white"
          >
            Adicionar colaborador
          </button>
        </div>
      </div>

      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center">
        <input
          placeholder="Buscar por nome ou CPF"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleBuscaSubmit()}
          className="h-11 flex-1 rounded-lg border border-slate-300 px-4 text-base"
        />
        <div className="flex gap-2">
          <select
            value={filtroFilial}
            onChange={(e) => setFiltroFilial(e.target.value)}
            className="h-11 flex-1 rounded-lg border border-slate-300 px-4 text-base sm:flex-none sm:min-w-[160px]"
          >
            <option value="">Todas as filiais</option>
            {filiais.map((f) => (
              <option key={f.id} value={f.id}>
                {f.nome}
              </option>
            ))}
          </select>
          <select
            value={filtroStatus}
            onChange={(e) => setFiltroStatus(e.target.value as StatusColaborador | "")}
            className="h-11 flex-1 rounded-lg border border-slate-300 px-4 text-base sm:flex-none sm:min-w-[160px]"
          >
            {STATUS_OPCOES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
        <button onClick={handleBuscaSubmit} className="h-11 rounded-lg border border-slate-300 px-4 text-base font-medium sm:min-w-fit">
          Buscar
        </button>
      </div>

      {!carregado ? (
        <p className="text-slate-600">Carregando...</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {colaboradores.map((colaborador) => (
            <li
              key={colaborador.id}
              className="flex flex-wrap items-center justify-between gap-3 rounded-lg border border-slate-200 bg-white p-3"
            >
              <Link href={`/dashboard/colaboradores/${colaborador.id}`} className="flex-1 min-w-[180px]">
                <p className="text-base font-medium text-slate-900">{colaborador.nome}</p>
                <p className="text-sm text-slate-500">
                  {colaborador.cargo} · {nomeFilial(colaborador.filial_id)}
                </p>
              </Link>
              <StatusBadge status={colaborador.status} />
              {colaborador.status === "PENDENTE_LGPD" && (
                <button
                  onClick={() => abrirWhatsapp(colaborador)}
                  className="h-11 rounded-lg bg-green-600 px-3 text-sm font-semibold text-white"
                >
                  Enviar link WhatsApp
                </button>
              )}
            </li>
          ))}
          {colaboradores.length === 0 && <p className="text-sm text-slate-500">Nenhum colaborador encontrado.</p>}
        </ul>
      )}

      {mostrarNovo && (
        <NovoColaboradorModal
          filiais={filiais}
          onClose={() => setMostrarNovo(false)}
          onCriado={carregar}
        />
      )}

      {mostrarImportar && (
        <ImportarCsvModal onClose={() => setMostrarImportar(false)} onImportado={carregar} />
      )}
    </main>
  );
}
