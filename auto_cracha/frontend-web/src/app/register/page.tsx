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
    <main className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-2xl">
        <div className="mb-8 text-center">
          <div className="mb-4 inline-flex rounded-full bg-blue-100 p-4">
            <span className="text-3xl">🏢</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">CrachApp</h1>
          <p className="mt-2 text-sm text-slate-600">Crie sua conta empresarial</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Empresa</label>
            <input
              required
              placeholder="Nome da sua empresa"
              value={form.nome_empresa}
              onChange={(e) => atualizarCampo("nome_empresa", e.target.value)}
              className="rounded-lg border border-slate-300 px-4 py-3 transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">CNPJ</label>
            <input
              required
              placeholder="00.000.000/0000-00"
              value={form.cnpj}
              onChange={(e) => atualizarCampo("cnpj", e.target.value)}
              className="rounded-lg border border-slate-300 px-4 py-3 transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Responsável</label>
            <input
              required
              placeholder="Seu nome completo"
              value={form.nome_responsavel}
              onChange={(e) => atualizarCampo("nome_responsavel", e.target.value)}
              className="rounded-lg border border-slate-300 px-4 py-3 transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">E-mail</label>
            <input
              required
              type="email"
              placeholder="seu@email.com"
              value={form.email}
              onChange={(e) => atualizarCampo("email", e.target.value)}
              className="rounded-lg border border-slate-300 px-4 py-3 transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="text-sm font-medium text-slate-700">Senha</label>
            <input
              required
              type="password"
              placeholder="••••••••"
              value={form.senha}
              onChange={(e) => atualizarCampo("senha", e.target.value)}
              className="rounded-lg border border-slate-300 px-4 py-3 transition-all focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
          </div>

          {erro && (
            <div className="rounded-lg bg-red-50 p-3 text-sm font-medium text-red-700 border border-red-200">
              {erro}
            </div>
          )}

          <button
            type="submit"
            disabled={carregando}
            className="mt-2 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-3 text-base font-semibold text-white transition-all hover:shadow-lg hover:from-blue-700 hover:to-blue-800 disabled:opacity-60"
          >
            {carregando ? "Cadastrando..." : "Cadastrar e começar trial 7 dias"}
          </button>
        </form>

        <div className="mt-6 border-t border-slate-200 pt-6">
          <div className="text-center text-sm text-slate-600">
            Já tem conta?{" "}
            <Link href="/login" className="font-medium text-blue-600 hover:text-blue-700 transition-colors">
              Entrar
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
