"use client";

import { useState } from "react";
import { apiFetch } from "@/lib/api";

interface Props {
  qrToken: string;
  exibirContatoPessoal: boolean;
  onAtualizado: () => void;
}

export default function ContatoVisivelSection({ qrToken, exibirContatoPessoal, onAtualizado }: Props) {
  const [salvando, setSalvando] = useState(false);

  async function handleToggle() {
    setSalvando(true);
    try {
      await apiFetch(`/meu-cracha/${qrToken}/contato-visivel`, {
        method: "PATCH",
        body: JSON.stringify({ exibir_contato_pessoal: !exibirContatoPessoal }),
      });
      onAtualizado();
    } finally {
      setSalvando(false);
    }
  }

  return (
    <section className="rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-2 text-sm font-medium text-slate-700">Meu cartão virtual</h2>
      <label className="flex h-11 items-center gap-3">
        <input type="checkbox" checked={exibirContatoPessoal} disabled={salvando} onChange={handleToggle} className="h-5 w-5" />
        <span className="text-base">Exibir meu WhatsApp e e-mail quando alguém escanear meu QR</span>
      </label>
    </section>
  );
}
