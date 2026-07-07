"use client";

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import { authFetch, authUpload } from "@/lib/api";
import type { ConfigOut } from "@/lib/types";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

export default function IdentidadeTab() {
  const [config, setConfig] = useState<ConfigOut | null>(null);
  const [form, setForm] = useState({
    nome_fantasia: "",
    razao_social: "",
    cor_primaria: "#0F172A",
    cor_secundaria: "#FFFFFF",
  });
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    authFetch<ConfigOut>("/config").then((data) => {
      setConfig(data);
      setForm({
        nome_fantasia: data.nome_fantasia || "",
        razao_social: data.razao_social || "",
        cor_primaria: data.cor_primaria,
        cor_secundaria: data.cor_secundaria,
      });
    });
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setMensagem("");
    setSalvando(true);
    try {
      const data = await authFetch<ConfigOut>("/config/identidade", {
        method: "PUT",
        body: JSON.stringify(form),
      });
      setConfig(data);
      setMensagem("Identidade atualizada.");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao salvar");
    } finally {
      setSalvando(false);
    }
  }

  async function handleUploadLogo(e: ChangeEvent<HTMLInputElement>, campo: "logo" | "logo-grupo") {
    const arquivo = e.target.files?.[0];
    if (!arquivo) return;
    const formData = new FormData();
    formData.append("arquivo", arquivo);
    try {
      const data = await authUpload<{ logo_url?: string; logo_grupo_url?: string }>(
        `/config/${campo}`,
        formData
      );
      setConfig((prev) =>
        prev
          ? { ...prev, logo_url: data.logo_url ?? prev.logo_url, logo_grupo_url: data.logo_grupo_url ?? prev.logo_grupo_url }
          : prev
      );
      setMensagem("Logo enviada com sucesso.");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao enviar logo");
    }
  }

  if (!config) {
    return <p className="text-slate-600">Carregando...</p>;
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:gap-6">
        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">Logo da empresa</span>
          {config.logo_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={config.logo_url} alt="Logo da empresa" className="h-20 w-20 rounded-lg border object-contain" />
          )}
          <label className="h-11 flex items-center justify-center rounded-lg border border-slate-300 px-4 text-sm cursor-pointer">
            Trocar logo
            <input type="file" accept="image/*" className="hidden" onChange={(e) => handleUploadLogo(e, "logo")} />
          </label>
        </div>

        <div className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">Logo do grupo</span>
          {config.logo_grupo_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={config.logo_grupo_url} alt="Logo do grupo" className="h-20 w-20 rounded-lg border object-contain" />
          )}
          <label className="h-11 flex items-center justify-center rounded-lg border border-slate-300 px-4 text-sm cursor-pointer">
            Trocar logo do grupo
            <input type="file" accept="image/*" className="hidden" onChange={(e) => handleUploadLogo(e, "logo-grupo")} />
          </label>
        </div>
      </div>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">Nome fantasia</span>
        <input
          value={form.nome_fantasia}
          onChange={(e) => setForm({ ...form, nome_fantasia: e.target.value })}
          className={inputClass}
        />
      </label>

      <label className="flex flex-col gap-1">
        <span className="text-sm font-medium text-slate-700">Razão social</span>
        <input
          value={form.razao_social}
          onChange={(e) => setForm({ ...form, razao_social: e.target.value })}
          className={inputClass}
        />
      </label>

      <div className="flex gap-6">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">Cor primária</span>
          <input
            type="color"
            value={form.cor_primaria}
            onChange={(e) => setForm({ ...form, cor_primaria: e.target.value })}
            className="h-11 w-16 rounded-lg border border-slate-300"
          />
        </label>
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">Cor secundária</span>
          <input
            type="color"
            value={form.cor_secundaria}
            onChange={(e) => setForm({ ...form, cor_secundaria: e.target.value })}
            className="h-11 w-16 rounded-lg border border-slate-300"
          />
        </label>
      </div>

      {erro && <p className="text-sm text-red-600">{erro}</p>}
      {mensagem && <p className="text-sm text-green-700">{mensagem}</p>}

      <button
        type="submit"
        disabled={salvando}
        className="h-11 w-full rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60 sm:w-auto sm:px-6"
      >
        {salvando ? "Salvando..." : "Salvar identidade"}
      </button>
    </form>
  );
}
