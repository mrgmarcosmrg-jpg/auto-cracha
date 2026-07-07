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
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">Lotes de impressão</h1>
        <Link
          href="/dashboard/lotes/novo"
          className="flex h-11 items-center rounded-lg bg-slate-900 px-4 text-sm font-semibold text-white"
        >
          Novo lote
        </Link>
      </div>

      {!carregado ? (
        <p className="text-slate-600">Carregando...</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {lotes.map((lote) => (
            <li key={lote.id} className="rounded-lg border border-slate-200 bg-white p-3">
              <Link href={`/dashboard/lotes/${lote.id}`} className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="text-base font-medium text-slate-900">{lote.nome_lote}</p>
                  <p className="text-sm text-slate-500">
                    {formatarData(lote.criado_em)} · {lote.quantidade_total} crachá(s) · {lote.modo_impressao}
                  </p>
                </div>
                <LoteStatusBadge status={lote.status_lote} />
              </Link>
            </li>
          ))}
          {lotes.length === 0 && <p className="text-sm text-slate-500">Nenhum lote criado ainda.</p>}
        </ul>
      )}
    </main>
  );
}
