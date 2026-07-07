"use client";

import { useState, type ChangeEvent } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Props {
  qrToken: string;
  fotoUrl: string | null;
  onAtualizado: () => void;
}

export default function FotoSection({ qrToken, fotoUrl, onAtualizado }: Props) {
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  async function handleArquivo(e: ChangeEvent<HTMLInputElement>) {
    const arquivo = e.target.files?.[0];
    if (!arquivo) return;
    setErro("");
    setEnviando(true);
    try {
      const formData = new FormData();
      formData.append("arquivo", arquivo);
      const res = await fetch(`${API_URL}/meu-cracha/${qrToken}/foto`, { method: "PATCH", body: formData });
      if (!res.ok) throw new Error("Erro ao enviar a foto");
      onAtualizado();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao enviar a foto");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section className="rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-3 text-sm font-medium text-slate-700">Minha foto</h2>
      <div className="flex items-center gap-4">
        {fotoUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={fotoUrl} alt="Minha foto" className="h-20 w-20 rounded-full object-cover" />
        ) : (
          <div className="h-20 w-20 rounded-full bg-slate-200" />
        )}
        <label className="flex h-11 cursor-pointer items-center rounded-lg border border-slate-300 px-4 text-sm">
          {enviando ? "Enviando..." : "Trocar foto"}
          <input
            type="file"
            accept="image/*"
            capture="user"
            className="hidden"
            onChange={handleArquivo}
            disabled={enviando}
          />
        </label>
      </div>
      {erro && <p className="mt-2 text-sm text-red-600">{erro}</p>}
    </section>
  );
}
