"use client";

import { useState, type FormEvent } from "react";
import { authFetch } from "@/lib/api";
import type { ColaboradorCriadoOut, FilialOut } from "@/lib/types";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

interface Props {
  filiais: FilialOut[];
  onClose: () => void;
  onCriado: () => void;
}

export default function NovoColaboradorModal({ filiais, onClose, onCriado }: Props) {
  const [form, setForm] = useState({
    nome: "",
    cargo: "",
    celular: "",
    email_colaborador: "",
    filial_id: filiais[0]?.id || "",
    cpf: "",
    em_treinamento: false,
    pcd: false,
    pcd_descricao: "",
  });
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [criado, setCriado] = useState<ColaboradorCriadoOut | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setSalvando(true);
    try {
      const resultado = await authFetch<ColaboradorCriadoOut>("/colaboradores", {
        method: "POST",
        body: JSON.stringify({
          nome: form.nome,
          cargo: form.cargo,
          celular: form.celular,
          email_colaborador: form.email_colaborador || null,
          filial_id: form.filial_id || null,
          cpf: form.cpf || null,
          em_treinamento: form.em_treinamento,
          pcd: form.pcd,
          pcd_descricao: form.pcd_descricao || null,
        }),
      });
      setCriado(resultado);
      onCriado();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao cadastrar colaborador");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex w-full max-w-sm flex-col gap-3 rounded-xl bg-white p-5 max-h-[90vh] overflow-y-auto">
        {criado ? (
          <>
            <h2 className="text-lg font-bold text-slate-900">Colaborador cadastrado!</h2>
            <p className="text-sm text-slate-600">
              Envie o link de autorização LGPD para {criado.nome} confirmar os dados pessoais.
            </p>
            <a
              href={criado.link_lgpd.whatsapp_url}
              target="_blank"
              rel="noreferrer"
              className="flex h-11 items-center justify-center rounded-lg bg-green-600 text-base font-semibold text-white"
            >
              Enviar link por WhatsApp
            </a>
            <button onClick={onClose} className="h-11 rounded-lg border border-slate-300 text-base">
              Fechar
            </button>
          </>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <h2 className="text-lg font-bold text-slate-900">Novo colaborador</h2>
            <input
              required
              placeholder="Nome completo"
              value={form.nome}
              onChange={(e) => setForm({ ...form, nome: e.target.value })}
              className={inputClass}
            />
            <input
              required
              placeholder="Cargo"
              value={form.cargo}
              onChange={(e) => setForm({ ...form, cargo: e.target.value })}
              className={inputClass}
            />
            <input
              required
              placeholder="Celular (com DDD)"
              value={form.celular}
              onChange={(e) => setForm({ ...form, celular: e.target.value })}
              className={inputClass}
            />
            <input
              type="email"
              placeholder="E-mail (opcional)"
              value={form.email_colaborador}
              onChange={(e) => setForm({ ...form, email_colaborador: e.target.value })}
              className={inputClass}
            />
            <input
              placeholder="CPF (opcional)"
              value={form.cpf}
              onChange={(e) => setForm({ ...form, cpf: e.target.value })}
              className={inputClass}
            />
            <select
              required
              value={form.filial_id}
              onChange={(e) => setForm({ ...form, filial_id: e.target.value })}
              className={inputClass}
            >
              <option value="">Selecione a filial</option>
              {filiais.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.nome}
                </option>
              ))}
            </select>
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
                placeholder="Descrição PCD (opcional)"
                value={form.pcd_descricao}
                onChange={(e) => setForm({ ...form, pcd_descricao: e.target.value })}
                className={inputClass}
              />
            )}

            {erro && <p className="text-sm text-red-600">{erro}</p>}

            <div className="flex gap-2">
              <button type="button" onClick={onClose} className="h-11 flex-1 rounded-lg border border-slate-300 text-base">
                Cancelar
              </button>
              <button
                type="submit"
                disabled={salvando}
                className="h-11 flex-1 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
              >
                {salvando ? "Salvando..." : "Cadastrar"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
