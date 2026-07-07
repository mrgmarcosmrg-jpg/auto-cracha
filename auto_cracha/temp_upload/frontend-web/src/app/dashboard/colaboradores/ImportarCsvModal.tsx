"use client";

import { useState, type ChangeEvent } from "react";
import { authDownload, authUpload } from "@/lib/api";
import type { ImportarResultado } from "@/lib/types";

interface Props {
  onClose: () => void;
  onImportado: () => void;
}

export default function ImportarCsvModal({ onClose, onImportado }: Props) {
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState<ImportarResultado | null>(null);
  const [erro, setErro] = useState("");

  async function handleArquivo(e: ChangeEvent<HTMLInputElement>) {
    const arquivo = e.target.files?.[0];
    if (!arquivo) return;
    setErro("");
    setEnviando(true);
    try {
      const formData = new FormData();
      formData.append("arquivo", arquivo);
      const dados = await authUpload<ImportarResultado>("/colaboradores/importar", formData);
      setResultado(dados);
      onImportado();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao importar arquivo");
    } finally {
      setEnviando(false);
    }
  }

  async function handleBaixarTemplate() {
    const blob = await authDownload("/colaboradores/template-csv");
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "colaboradores_template.csv";
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="flex w-full max-w-sm flex-col gap-3 rounded-xl bg-white p-5">
        <h2 className="text-lg font-bold text-slate-900">Importar colaboradores</h2>
        <p className="text-sm text-slate-600">Envie um arquivo .csv ou .xlsx com as colunas: nome, cargo, celular, email, cpf, filial_nome.</p>

        <button
          onClick={handleBaixarTemplate}
          className="h-11 rounded-lg border border-slate-300 text-base"
        >
          Baixar modelo CSV
        </button>

        <label className="flex h-11 items-center justify-center rounded-lg bg-slate-900 text-base font-semibold text-white cursor-pointer">
          {enviando ? "Importando..." : "Selecionar arquivo"}
          <input type="file" accept=".csv,.xlsx" className="hidden" onChange={handleArquivo} disabled={enviando} />
        </label>

        {erro && <p className="text-sm text-red-600">{erro}</p>}

        {resultado && (
          <div className="rounded-lg bg-slate-50 p-3 text-sm">
            <p className="font-medium text-green-700">{resultado.importados} colaborador(es) importado(s).</p>
            {resultado.erros.length > 0 && (
              <div className="mt-2">
                <p className="font-medium text-red-600">{resultado.erros.length} erro(s):</p>
                <ul className="mt-1 list-disc pl-5 text-slate-600">
                  {resultado.erros.map((e, i) => (
                    <li key={i}>
                      Linha {e.linha}: {e.motivo}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        <button onClick={onClose} className="h-11 rounded-lg border border-slate-300 text-base">
          Fechar
        </button>
      </div>
    </div>
  );
}
