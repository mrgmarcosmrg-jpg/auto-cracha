"use client";

import { useEffect, useState, type ChangeEvent, type FormEvent } from "react";
import { authFetch, authUpload } from "@/lib/api";
import type { FilialOut } from "@/lib/types";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

export default function FiliaisTab() {
  const [filiais, setFiliais] = useState<FilialOut[]>([]);
  const [carregado, setCarregado] = useState(false);
  const [erro, setErro] = useState("");
  const [novaFilial, setNovaFilial] = useState({ nome: "", cnpj: "", endereco: "" });
  const [criando, setCriando] = useState(false);
  const [filialEditando, setFilialEditando] = useState<FilialOut | null>(null);

  async function carregarFiliais() {
    const data = await authFetch<FilialOut[]>("/filiais");
    setFiliais(data);
    setCarregado(true);
  }

  useEffect(() => {
    carregarFiliais();
  }, []);

  async function handleCriar(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setCriando(true);
    try {
      await authFetch<FilialOut>("/filiais", {
        method: "POST",
        body: JSON.stringify(novaFilial),
      });
      setNovaFilial({ nome: "", cnpj: "", endereco: "" });
      await carregarFiliais();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao criar filial");
    } finally {
      setCriando(false);
    }
  }

  async function handleDesativar(id: string) {
    await authFetch(`/filiais/${id}`, { method: "DELETE" });
    await carregarFiliais();
  }

  async function handleSalvarEdicao(e: FormEvent) {
    e.preventDefault();
    if (!filialEditando) return;
    await authFetch<FilialOut>(`/filiais/${filialEditando.id}`, {
      method: "PUT",
      body: JSON.stringify({
        nome: filialEditando.nome,
        cnpj: filialEditando.cnpj,
        endereco: filialEditando.endereco,
      }),
    });
    setFilialEditando(null);
    await carregarFiliais();
  }

  async function handleUploadLogoFilial(e: ChangeEvent<HTMLInputElement>) {
    const arquivo = e.target.files?.[0];
    if (!arquivo || !filialEditando) return;
    const formData = new FormData();
    formData.append("arquivo", arquivo);
    const atualizada = await authUpload<FilialOut>(`/filiais/${filialEditando.id}/logo`, formData);
    setFilialEditando(atualizada);
  }

  if (!carregado) {
    return <p className="text-slate-600">Carregando...</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={handleCriar} className="flex flex-col gap-3 rounded-lg border border-slate-200 p-4">
        <h2 className="text-sm font-medium text-slate-700">Nova filial</h2>
        <input
          required
          placeholder="Nome da filial"
          value={novaFilial.nome}
          onChange={(e) => setNovaFilial({ ...novaFilial, nome: e.target.value })}
          className={inputClass}
        />
        <input
          placeholder="CNPJ (opcional)"
          value={novaFilial.cnpj}
          onChange={(e) => setNovaFilial({ ...novaFilial, cnpj: e.target.value })}
          className={inputClass}
        />
        <input
          placeholder="Endereço (opcional)"
          value={novaFilial.endereco}
          onChange={(e) => setNovaFilial({ ...novaFilial, endereco: e.target.value })}
          className={inputClass}
        />
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        <button
          type="submit"
          disabled={criando}
          className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
        >
          {criando ? "Criando..." : "Criar filial"}
        </button>
      </form>

      <ul className="flex flex-col gap-2">
        {filiais.map((filial) => (
          <li
            key={filial.id}
            className="flex items-center justify-between gap-2 rounded-lg border border-slate-200 p-3"
          >
            <div>
              <p className="text-base font-medium text-slate-900">{filial.nome}</p>
              <p className="text-sm text-slate-500">{filial.ativo ? "Ativa" : "Desativada"}</p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setFilialEditando(filial)}
                className="h-11 rounded-lg border border-slate-300 px-3 text-sm"
              >
                Editar
              </button>
              {filial.ativo && (
                <button
                  onClick={() => handleDesativar(filial.id)}
                  className="h-11 rounded-lg border border-red-300 px-3 text-sm text-red-600"
                >
                  Desativar
                </button>
              )}
            </div>
          </li>
        ))}
        {filiais.length === 0 && <p className="text-sm text-slate-500">Nenhuma filial cadastrada.</p>}
      </ul>

      {filialEditando && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <form
            onSubmit={handleSalvarEdicao}
            className="flex w-full max-w-sm flex-col gap-3 rounded-xl bg-white p-5"
          >
            <h2 className="text-lg font-bold text-slate-900">Editar filial</h2>
            <input
              value={filialEditando.nome}
              onChange={(e) => setFilialEditando({ ...filialEditando, nome: e.target.value })}
              className={inputClass}
            />
            <input
              placeholder="CNPJ"
              value={filialEditando.cnpj || ""}
              onChange={(e) => setFilialEditando({ ...filialEditando, cnpj: e.target.value })}
              className={inputClass}
            />
            <input
              placeholder="Endereço"
              value={filialEditando.endereco || ""}
              onChange={(e) => setFilialEditando({ ...filialEditando, endereco: e.target.value })}
              className={inputClass}
            />
            <label className="h-11 flex items-center justify-center rounded-lg border border-slate-300 px-4 text-sm cursor-pointer">
              {filialEditando.logo_filial_url ? "Trocar logo da filial" : "Enviar logo da filial"}
              <input type="file" accept="image/*" className="hidden" onChange={handleUploadLogoFilial} />
            </label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setFilialEditando(null)}
                className="h-11 flex-1 rounded-lg border border-slate-300 text-base"
              >
                Cancelar
              </button>
              <button type="submit" className="h-11 flex-1 rounded-lg bg-slate-900 text-base font-semibold text-white">
                Salvar
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
