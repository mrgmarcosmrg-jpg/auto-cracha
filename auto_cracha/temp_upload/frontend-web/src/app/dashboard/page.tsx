"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { limparToken, obterToken } from "@/lib/auth";

export default function DashboardPage() {
  const router = useRouter();

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
    }
  }, [router]);

  function handleLogout() {
    limparToken();
    router.replace("/login");
  }

  return (
    <main className="flex min-h-screen flex-col p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-slate-900">Dashboard</h1>
        <button
          onClick={handleLogout}
          className="h-11 rounded-lg border border-slate-300 px-4 text-sm"
        >
          Sair
        </button>
      </div>
      <p className="mt-4 text-slate-600">
        Login funcionando.
      </p>
      <div className="mt-4 flex flex-wrap gap-3">
        <Link
          href="/dashboard/colaboradores"
          className="flex h-11 w-fit items-center rounded-lg bg-slate-900 px-4 text-base font-semibold text-white"
        >
          Colaboradores
        </Link>
        <Link
          href="/dashboard/lotes"
          className="flex h-11 w-fit items-center rounded-lg bg-slate-900 px-4 text-base font-semibold text-white"
        >
          Lotes de impressão
        </Link>
        <Link
          href="/dashboard/plano"
          className="flex h-11 w-fit items-center rounded-lg border border-slate-300 px-4 text-base font-semibold text-slate-700"
        >
          Planos e Pagamentos
        </Link>
        <Link
          href="/dashboard/configuracoes"
          className="flex h-11 w-fit items-center rounded-lg border border-slate-300 px-4 text-base font-semibold text-slate-700"
        >
          Configurações da empresa
        </Link>
      </div>
    </main>
  );
}
