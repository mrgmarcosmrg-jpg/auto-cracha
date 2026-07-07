"use client";

import { useEffect, useState, type FormEvent } from "react";
import { authFetch } from "@/lib/api";
import type { ConfigOut } from "@/lib/types";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

export default function ContatoTab() {
  const [form, setForm] = useState({
    telefone: "",
    whatsapp: "",
    email_empresa: "",
    endereco_completo: "",
    instagram: "",
    site: "",
  });
  const [carregado, setCarregado] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    authFetch<ConfigOut>("/config").then((data) => {
      setForm({
        telefone: data.telefone || "",
        whatsapp: data.whatsapp || "",
        email_empresa: data.email_empresa || "",
        endereco_completo: data.endereco_completo || "",
        instagram: data.redes_sociais?.instagram || "",
        site: data.redes_sociais?.site || "",
      });
      setCarregado(true);
    });
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setMensagem("");
    setSalvando(true);
    try {
      await authFetch<ConfigOut>("/config/contato", {
        method: "PUT",
        body: JSON.stringify({
          telefone: form.telefone,
          whatsapp: form.whatsapp,
          email_empresa: form.email_empresa,
          endereco_completo: form.endereco_completo,
          redes_sociais: { instagram: form.instagram, site: form.site },
        }),
      });
      setMensagem("Contato atualizado.");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao salvar");
    } finally {
      setSalvando(false);
    }
  }

  if (!carregado) {
    return <p className="text-slate-600">Carregando...</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">Telefone</span>
        <input value={form.telefone} onChange={(e) => setForm({ ...form, telefone: e.target.value })} className={inputClass} />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">WhatsApp</span>
        <input value={form.whatsapp} onChange={(e) => setForm({ ...form, whatsapp: e.target.value })} className={inputClass} />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">E-mail da empresa</span>
        <input
          type="email"
          value={form.email_empresa}
          onChange={(e) => setForm({ ...form, email_empresa: e.target.value })}
          className={inputClass}
        />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">Endereço completo</span>
        <input
          value={form.endereco_completo}
          onChange={(e) => setForm({ ...form, endereco_completo: e.target.value })}
          className={inputClass}
        />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">Instagram</span>
        <input value={form.instagram} onChange={(e) => setForm({ ...form, instagram: e.target.value })} className={inputClass} />
      </label>
      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">Site</span>
        <input value={form.site} onChange={(e) => setForm({ ...form, site: e.target.value })} className={inputClass} />
      </label>

      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {mensagem && <p className="text-sm text-green-700">{mensagem}</p>}

      <button
        type="submit"
        disabled={salvando}
        className="h-11 w-full rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60 sm:w-auto sm:px-6"
      >
        {salvando ? "Salvando..." : "Salvar contato"}
      </button>
    </form>
  );
}
