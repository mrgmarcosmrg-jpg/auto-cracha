"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { obterToken } from "@/lib/auth";
import IdentidadeTab from "./IdentidadeTab";
import ContatoTab from "./ContatoTab";
import CrachaTab from "./CrachaTab";
import FiliaisTab from "./FiliaisTab";
import UsuariosTab from "./UsuariosTab";

const ABAS = [
  { id: "identidade", label: "Identidade" },
  { id: "contato", label: "Contato" },
  { id: "cracha", label: "Crachá" },
  { id: "filiais", label: "Filiais" },
  { id: "usuarios", label: "Usuários" },
] as const;

type AbaId = (typeof ABAS)[number]["id"];

export default function ConfiguracoesPage() {
  const router = useRouter();
  const [abaAtiva, setAbaAtiva] = useState<AbaId>("identidade");

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
    }
  }, [router]);

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <h1 className="mb-4 text-xl font-bold text-slate-900">Configurações da empresa</h1>

      <div className="mb-4 flex gap-2 overflow-x-auto pb-2">
        {ABAS.map((aba) => (
          <button
            key={aba.id}
            onClick={() => setAbaAtiva(aba.id)}
            className={`h-11 shrink-0 rounded-lg px-4 text-base font-medium ${
              abaAtiva === aba.id
                ? "bg-slate-900 text-white"
                : "bg-white text-slate-700 border border-slate-300"
            }`}
          >
            {aba.label}
          </button>
        ))}
      </div>

      <div className="rounded-xl bg-white p-4 shadow-sm sm:p-6">
        {abaAtiva === "identidade" && <IdentidadeTab />}
        {abaAtiva === "contato" && <ContatoTab />}
        {abaAtiva === "cracha" && <CrachaTab />}
        {abaAtiva === "filiais" && <FiliaisTab />}
        {abaAtiva === "usuarios" && <UsuariosTab />}
      </div>
    </main>
  );
}
