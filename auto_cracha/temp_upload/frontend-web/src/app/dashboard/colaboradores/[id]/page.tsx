"use client";

import { useEffect, useState, type FormEvent } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { authFetch } from "@/lib/api";
import { obterToken } from "@/lib/auth";
import type { ColaboradorOut } from "@/lib/types";
import StatusBadge from "../StatusBadge";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

export default function ColaboradorDetalhePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [colaborador, setColaborador] = useState<ColaboradorOut | null>(null);
  const [form, setForm] = useState({
    nome: "",
    cargo: "",
    celular: "",
    email_colaborador: "",
    cpf: "",
    em_treinamento: false,
    pcd: false,
    pcd_descricao: "",
  });
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  async function carregar() {
    const data = await authFetch<ColaboradorOut>(`/colaboradores/${params.id}`);
    setColaborador(data);
    setForm({
      nome: data.nome,
      cargo: data.cargo,
      celular: data.celular || "",
      email_colaborador: data.email_colaborador || "",
      cpf: "",
      em_treinamento: data.em_treinamento,
      pcd: data.pcd,
      pcd_descricao: data.pcd_descricao || "",
    });
  }

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
      return;
    }
    carregar();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [router, params.id]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setMensagem("");
    setSalvando(true);
    try {
      const atualizado = await authFetch<ColaboradorOut>(`/colaboradores/${params.id}`, {
        method: "PUT",
        body: JSON.stringify({
          nome: form.nome,
          cargo: form.cargo,
          celular: form.celular,
          email_colaborador: form.email_colaborador || null,
          cpf: form.cpf || undefined,
          em_treinamento: form.em_treinamento,
          pcd: form.pcd,
          pcd_descricao: form.pcd_descricao || null,
        }),
      });
      setColaborador(atualizado);
      setMensagem("Dados atualizados.");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao salvar");
    } finally {
      setSalvando(false);
    }
  }

  async function handleEnviarWhatsapp() {
    const data = await authFetch<{ link: string; whatsapp_url: string }>(`/colaboradores/${params.id}/link-lgpd`);
    window.open(data.whatsapp_url, "_blank");
  }

  async function handleDesligar() {
    if (!confirm("Confirma o desligamento deste colaborador? O QR Code passará a exibir 'Vínculo Encerrado'.")) {
      return;
    }
    const atualizado = await authFetch<ColaboradorOut>(`/colaboradores/${params.id}/desligar`, { method: "POST" });
    setColaborador(atualizado);
  }

  async function handleReativar() {
    const atualizado = await authFetch<ColaboradorOut>(`/colaboradores/${params.id}/reativar`, { method: "POST" });
    setColaborador(atualizado);
  }

  if (!colaborador) {
    return (
      <main className="min-h-screen bg-slate-50 p-6">
        <p className="text-slate-600">Carregando...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <Link href="/dashboard/colaboradores" className="text-sm text-slate-600 underline">
        ← Voltar para colaboradores
      </Link>

      <div className="mt-3 flex items-center justify-between gap-2">
        <h1 className="text-xl font-bold text-slate-900">{colaborador.nome}</h1>
        <StatusBadge status={colaborador.status} />
      </div>

      <div className="mt-4 flex flex-col gap-2 sm:flex-row">
        <button
          onClick={handleEnviarWhatsapp}
          className="h-11 rounded-lg bg-green-600 px-4 text-base font-semibold text-white"
        >
          Enviar link WhatsApp
        </button>
        {colaborador.status === "DESLIGADO" ? (
          <button onClick={handleReativar} className="h-11 rounded-lg border border-slate-300 px-4 text-base">
            Reativar colaborador
          </button>
        ) : (
          <button onClick={handleDesligar} className="h-11 rounded-lg border border-red-300 px-4 text-base text-red-600">
            Desligar colaborador
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="mt-6 flex max-w-md flex-col gap-4 rounded-xl bg-white p-4 shadow-sm sm:p-6">
        <h2 className="text-sm font-medium text-slate-700">Dados profissionais</h2>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">Nome</span>
          <input value={form.nome} onChange={(e) => setForm({ ...form, nome: e.target.value })} className={inputClass} />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">Cargo</span>
          <input value={form.cargo} onChange={(e) => setForm({ ...form, cargo: e.target.value })} className={inputClass} />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">Celular</span>
          <input value={form.celular} onChange={(e) => setForm({ ...form, celular: e.target.value })} className={inputClass} />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">E-mail</span>
          <input
            type="email"
            value={form.email_colaborador}
            onChange={(e) => setForm({ ...form, email_colaborador: e.target.value })}
            className={inputClass}
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">CPF (deixe vazio para não alterar)</span>
          <input value={form.cpf} onChange={(e) => setForm({ ...form, cpf: e.target.value })} className={inputClass} />
        </label>

        <label className="flex h-11 items-center gap-3">
          <input
            type="checkbox"
            checked={form.em_treinamento}
            onChange={(e) => setForm({ ...form, em_treinamento: e.target.checked })}
            className="h-5 w-5"
          />
          <span className="text-base">Em treinamento</span>
        </label>
        <label className="flex h-11 items-center gap-3">
          <input
            type="checkbox"
            checked={form.pcd}
            onChange={(e) => setForm({ ...form, pcd: e.target.checked })}
            className="h-5 w-5"
          />
          <span className="text-base">PCD</span>
        </label>
        {form.pcd && (
          <input
            placeholder="Descrição PCD"
            value={form.pcd_descricao}
            onChange={(e) => setForm({ ...form, pcd_descricao: e.target.value })}
            className={inputClass}
          />
        )}

        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {mensagem && <p className="text-sm text-green-700">{mensagem}</p>}

        <button
          type="submit"
          disabled={salvando}
          className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
        >
          {salvando ? "Salvando..." : "Salvar alterações"}
        </button>
      </form>
    </main>
  );
}
