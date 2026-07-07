"use client";

import { useState, type FormEvent } from "react";

interface Props {
  onCancelar: () => void;
  onConfirmar: (motivo: string) => void;
}

export default function MarcarFalhaModal({ onCancelar, onConfirmar }: Props) {
  const [motivo, setMotivo] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    onConfirmar(motivo || "Falha na impressão");
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <form onSubmit={handleSubmit} className="flex w-full max-w-sm flex-col gap-3 rounded-xl bg-white p-5">
        <h2 className="text-lg font-bold text-slate-900">Motivo da falha</h2>
        <input
          autoFocus
          placeholder="Ex: papel atolou, tinta acabou..."
          value={motivo}
          onChange={(e) => setMotivo(e.target.value)}
          className="h-11 rounded-lg border border-slate-300 px-4 text-base"
        />
        <div className="flex gap-2">
          <button type="button" onClick={onCancelar} className="h-11 flex-1 rounded-lg border border-slate-300 text-base">
            Cancelar
          </button>
          <button type="submit" className="h-11 flex-1 rounded-lg bg-red-600 text-base font-semibold text-white">
            Confirmar falha
          </button>
        </div>
      </form>
    </div>
  );
}
