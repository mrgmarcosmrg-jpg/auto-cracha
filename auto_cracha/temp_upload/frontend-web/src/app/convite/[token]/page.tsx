"use client";

import { useState, type FormEvent } from "react";
import { useParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { salvarToken } from "@/lib/auth";

export default function AceitarConvitePage() {
  const params = useParams<{ token: string }>();
  const router = useRouter();
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      const data = await apiFetch<{ access_token: string }>(`/auth/aceitar-convite/${params.token}`, {
        method: "POST",
        body: JSON.stringify({ senha }),
      });
      salvarToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao aceitar convite");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow-sm">
        <h1 className="mb-2 text-xl font-bold text-slate-900">Criar sua senha</h1>
        <p className="mb-6 text-sm text-slate-600">Defina uma senha para acessar o CrachApp.</p>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            required
            type="password"
            placeholder="Escolha uma senha"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-base"
          />
          {erro && <p className="text-sm text-red-600">{erro}</p>}
          <button
            type="submit"
            disabled={carregando}
            className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
          >
            {carregando ? "Ativando..." : "Ativar minha conta"}
          </button>
        </form>
      </div>
    </main>
  );
}
