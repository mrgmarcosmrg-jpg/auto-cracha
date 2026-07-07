"use client";

import { useEffect, useState, type FormEvent } from "react";
import { authFetch } from "@/lib/api";
import type { ConfigOut } from "@/lib/types";

const TEMPLATES = [
  { id: "vertical_padrao", label: "Vertical Padrão", proporcao: "aspect-[5/8]" },
  { id: "horizontal_padrao", label: "Horizontal Padrão", proporcao: "aspect-[8/5]" },
] as const;

const SETORES = [
  { id: "", label: "Não definido" },
  { id: "saude", label: "Saúde" },
  { id: "educacao", label: "Educação" },
  { id: "varejo", label: "Varejo" },
  { id: "industria", label: "Indústria" },
];

export default function CrachaTab() {
  const [templateId, setTemplateId] = useState("vertical_padrao");
  const [setor, setSetor] = useState("");
  const [usarFaixaTreinamento, setUsarFaixaTreinamento] = useState(false);
  const [usarFaixaPcd, setUsarFaixaPcd] = useState(false);
  const [carregado, setCarregado] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    authFetch<ConfigOut>("/config").then((data) => {
      setTemplateId(data.template_id);
      setSetor(data.setor_sugerido || "");
      setUsarFaixaTreinamento(data.usar_faixa_treinamento);
      setUsarFaixaPcd(data.usar_faixa_pcd);
      setCarregado(true);
    });
  }, []);

  async function handleSalvarTemplate(id: string) {
    setTemplateId(id);
    setErro("");
    try {
      await authFetch<ConfigOut>("/config/template", {
        method: "PUT",
        body: JSON.stringify({ template_id: id }),
      });
      setMensagem("Template atualizado.");
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao salvar template");
    }
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setMensagem("");
    setSalvando(true);
    try {
      await authFetch<ConfigOut>("/config/setor", {
        method: "PUT",
        body: JSON.stringify({
          setor_sugerido: setor || null,
          usar_faixa_treinamento: usarFaixaTreinamento,
          usar_faixa_pcd: usarFaixaPcd,
        }),
      });
      setMensagem("Configurações de crachá salvas.");
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
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="mb-3 text-sm font-medium text-slate-700">Modelo de crachá</h2>
        <div className="flex gap-4">
          {TEMPLATES.map((template) => (
            <button
              key={template.id}
              onClick={() => handleSalvarTemplate(template.id)}
              className={`flex w-32 flex-col items-center gap-2 rounded-lg border-2 p-2 ${
                templateId === template.id ? "border-slate-900" : "border-slate-200"
              }`}
            >
              <div className={`w-full rounded bg-slate-100 ${template.proporcao}`} />
              <span className="text-sm">{template.label}</span>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-slate-700">Setor da empresa</span>
          <select value={setor} onChange={(e) => setSetor(e.target.value)} className="h-11 rounded-lg border border-slate-300 px-4 text-base">
            {SETORES.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </select>
        </label>

        <label className="flex h-11 items-center gap-3">
          <input
            type="checkbox"
            checked={usarFaixaTreinamento}
            onChange={(e) => setUsarFaixaTreinamento(e.target.checked)}
            className="h-5 w-5"
          />
          <span className="text-base">Usar faixa "Em treinamento"</span>
        </label>

        <label className="flex h-11 items-center gap-3">
          <input type="checkbox" checked={usarFaixaPcd} onChange={(e) => setUsarFaixaPcd(e.target.checked)} className="h-5 w-5" />
          <span className="text-base">Usar faixa "PCD"</span>
        </label>

        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {mensagem && <p className="text-sm text-green-700">{mensagem}</p>}

        <button
          type="submit"
          disabled={salvando}
          className="h-11 w-full rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60 sm:w-auto sm:px-6"
        >
          {salvando ? "Salvando..." : "Salvar"}
        </button>
      </form>
    </div>
  );
}
