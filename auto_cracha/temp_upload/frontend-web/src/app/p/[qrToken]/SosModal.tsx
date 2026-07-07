"use client";

import { useState, type FormEvent } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface DadosMedicos {
  tipo_sanguineo: string | null;
  comorbidades: string | null;
  remedios_eventuais: string | null;
  remedios_continuos: string | null;
  plano_saude: string | null;
  alergenicos: string | null;
}

const CAMPOS: { chave: keyof DadosMedicos; label: string }[] = [
  { chave: "tipo_sanguineo", label: "Tipo sanguíneo" },
  { chave: "comorbidades", label: "Comorbidades" },
  { chave: "remedios_eventuais", label: "Remédios eventuais" },
  { chave: "remedios_continuos", label: "Remédios de uso contínuo" },
  { chave: "plano_saude", label: "Plano de saúde" },
  { chave: "alergenicos", label: "Alergênicos" },
];

export default function SosModal({ qrToken, onClose }: { qrToken: string; onClose: () => void }) {
  const [pin, setPin] = useState("");
  const [erro, setErro] = useState("");
  const [carregando, setCarregando] = useState(false);
  const [dados, setDados] = useState<DadosMedicos | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setCarregando(true);
    try {
      const res = await fetch(`${API_URL}/p/${qrToken}/sos`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pin }),
      });
      const corpo = await res.json().catch(() => ({}));

      if (!res.ok) {
        const detalhe = corpo.detail;
        if (detalhe && typeof detalhe === "object" && "bloqueado_por_segundos" in detalhe) {
          const minutos = Math.ceil(Number(detalhe.bloqueado_por_segundos) / 60);
          setErro(`Muitas tentativas. Tente de novo em ${minutos} minuto(s).`);
        } else if (detalhe && typeof detalhe === "object" && "tentativas_restantes" in detalhe) {
          setErro(`PIN incorreto. ${detalhe.tentativas_restantes} tentativa(s) restante(s).`);
        } else {
          setErro(typeof detalhe === "string" ? detalhe : "PIN incorreto.");
        }
        return;
      }

      setDados(corpo as DadosMedicos);
    } catch {
      setErro("Erro ao verificar o PIN. Tente novamente.");
    } finally {
      setCarregando(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex w-full max-w-sm flex-col gap-3 rounded-xl bg-white p-5">
        <h2 className="text-lg font-bold text-slate-900">🚑 Dados de emergência</h2>

        {dados ? (
          <div className="flex flex-col gap-2">
            {CAMPOS.map((campo) => (
              <p key={campo.chave} className="text-sm">
                <span className="font-medium text-slate-700">{campo.label}: </span>
                <span className="text-slate-600">{dados[campo.chave] || "—"}</span>
              </p>
            ))}
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex flex-col gap-3">
            <p className="text-sm text-slate-600">Digite o PIN de 4 dígitos para liberar os dados médicos.</p>
            <input
              autoFocus
              inputMode="numeric"
              maxLength={4}
              placeholder="0000"
              value={pin}
              onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
              className="h-11 rounded-lg border border-slate-300 px-4 text-center text-2xl tracking-widest"
            />
            {erro && <p className="text-sm text-red-600">{erro}</p>}
            <button
              type="submit"
              disabled={carregando || pin.length !== 4}
              className="h-11 rounded-lg bg-red-600 text-base font-semibold text-white disabled:opacity-60"
            >
              {carregando ? "Verificando..." : "Liberar dados"}
            </button>
          </form>
        )}

        <button onClick={onClose} className="h-11 rounded-lg border border-slate-300 text-base">
          Fechar
        </button>
      </div>
    </div>
  );
}
