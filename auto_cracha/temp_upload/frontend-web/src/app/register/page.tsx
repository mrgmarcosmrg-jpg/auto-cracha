"use client";

import { useState, type FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { salvarToken } from "@/lib/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({
    nome_empresa: "",
    cnpj: "",
    email: "",
    senha: "",
    nome_responsavel: "",
  });
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);

  function atualizarCampo(campo: keyof typeof form, valor: string) {
    setForm((prev) => ({ ...prev, [campo]: valor }));
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      const data = await apiFetch<{ access_token: string }>("/auth/register", {
        method: "POST",
        body: JSON.stringify(form),
      });
      salvarToken(data.access_token);
      router.push("/dashboard");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao cadastrar empresa");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow-sm">
        <h1 className="mb-6 text-xl font-bold text-slate-900">Cadastrar empresa</h1>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <input
            required
            placeholder="Nome da empresa"
            value={form.nome_empresa}
            onChange={(e) => atualizarCampo("nome_empresa", e.target.value)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-base"
          />
          <input
            required
            placeholder="CNPJ"
            value={form.cnpj}
            onChange={(e) => atualizarCampo("cnpj", e.target.value)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-base"
          />
          <input
            required
            placeholder="Seu nome"
            value={form.nome_responsavel}
            onChange={(e) => atualizarCampo("nome_responsavel", e.target.value)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-base"
          />
          <input
            required
            type="email"
            placeholder="E-mail"
            value={form.email}
            onChange={(e) => atualizarCampo("email", e.target.value)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-base"
          />
          <input
            required
            type="password"
            placeholder="Senha"
            value={form.senha}
            onChange={(e) => atualizarCampo("senha", e.target.value)}
            className="h-11 rounded-lg border border-slate-300 px-4 text-base"
          />
          {erro && <p className="text-sm text-red-600">{erro}</p>}
          <button
            type="submit"
            disabled={carregando}
            className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
          >
            {carregando ? "Cadastrando..." : "Cadastrar e começar trial de 7 dias"}
          </button>
        </form>
        <p className="mt-4 text-center text-sm">
          <Link href="/login" className="text-slate-600 underline">
            Já tenho conta
          </Link>
        </p>
      </div>
    </main>
  );
}
