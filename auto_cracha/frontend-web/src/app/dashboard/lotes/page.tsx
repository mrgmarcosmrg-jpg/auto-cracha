"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { authFetch } from "@/lib/api";
import { obterToken } from "@/lib/auth";
import type { LoteOut } from "@/lib/types";
import LoteStatusBadge from "./LoteStatusBadge";

export default function LotesPage() {
  const router = useRouter();
  const [lotes, setLotes] = useState<LoteOut[]>([]);
  const [carregado, setCarregado] = useState(false);

  async function carregar() {
    const data = await authFetch<LoteOut[]>("/lotes");
    setLotes(data);
    setCarregado(true);
  }

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
      return;
    }
    carregar();
  }, [router]);

  function formatarData(iso: string) {
    return new Date(iso).toLocaleDateString("pt-BR");
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 to-green-50 p-4 sm:p-6">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">Lotes de impressão</h1>
            <p className="mt-1 text-slate-600">Criar e gerenciar lotes de crachás</p>
          </div>
          <Link
            href="/dashboard/lotes/novo"
            className="inline-flex items-center rounded-lg bg-green-600 px-4 py-2 text-sm font-semibold text-white transition-all hover:bg-green-700 hover:shadow-lg"
          >
            + Novo lote
          </Link>
        </div>

        {!carregado ? (
          <div className="text-center py-12">
            <p className="text-slate-600">Carregando lotes...</p>
          </div>
        ) : (
          <div className="grid gap-4">
            {lotes.map((lote) => (
              <Link
                key={lote.id}
                href={`/dashboard/lotes/${lote.id}`}
                className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:border-green-300"
              >
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <h3 className="text-lg font-semibold text-slate-900 group-hover:text-green-600">{lote.nome_lote}</h3>
                    <p className="mt-2 text-sm text-slate-600">
                      📅 {formatarData(lote.criado_em)} • 🖨️ {lote.modo_impressao} • 📦 {lote.quantidade_total} crachá(s)
                    </p>
                  </div>
                  <LoteStatusBadge status={lote.status_lote} />
                </div>
              </Link>
            ))}
            {lotes.length === 0 && (
              <div className="rounded-xl border border-slate-200 bg-white p-12 text-center">
                <p className="text-lg text-slate-600">Nenhum lote criado ainda</p>
                <p className="mt-2 text-sm text-slate-500">Clique no botão acima para criar seu primeiro lote</p>
              </div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
