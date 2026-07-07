"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { authFetch } from "@/lib/api";
import { obterToken } from "@/lib/auth";
import type { AssinaturaOut, CreditosPixResponse, PlanoOut, PreferenciaCheckoutOut } from "@/lib/types";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

function PlanoContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [planos, setPlanos] = useState<PlanoOut[]>([]);
  const [assinatura, setAssinatura] = useState<AssinaturaOut | null>(null);
  const [carregado, setCarregado] = useState(false);
  const [processando, setProcessando] = useState(false);
  const [creditosQtd, setCreditosQtd] = useState(10);

  useEffect(() => {
    if (!obterToken()) {
      router.replace("/login");
      return;
    }

    Promise.all([
      authFetch<PlanoOut[]>("/pagamento/planos"),
      authFetch<AssinaturaOut>("/pagamento/assinatura"),
    ])
      .then(([planosData, assinaturaData]) => {
        setPlanos(planosData);
        setAssinatura(assinaturaData);
        setCarregado(true);
      })
      .catch(() => setCarregado(true));

    const status = searchParams.get("status");
    if (status === "success") {
      const timer = setTimeout(() => window.location.reload(), 3000);
      return () => clearTimeout(timer);
    }
  }, [router, searchParams]);

  async function handleComprarPlano(planoId: string) {
    setProcessando(true);
    try {
      const dados = await authFetch<PreferenciaCheckoutOut>("/pagamento/criar-preferencia", {
        method: "POST",
        body: JSON.stringify({ plano_id: planoId }),
      });
      window.location.href = dados.init_point || dados.sandbox_init_point;
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao processar pagamento");
    } finally {
      setProcessando(false);
    }
  }

  async function handleComprarCreditos() {
    setProcessando(true);
    try {
      const resultado = await authFetch<CreditosPixResponse>("/pagamento/creditos-pix", {
        method: "POST",
        body: JSON.stringify({ quantidade: creditosQtd }),
      });
      alert(`${resultado.mensagem}\nValor: R$ ${resultado.valor_total_reais.toFixed(2)}`);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao solicitar créditos");
    } finally {
      setProcessando(false);
    }
  }

  if (!carregado) {
    return (
      <main className="min-h-screen bg-slate-50 p-6">
        <p className="text-slate-600">Carregando...</p>
      </main>
    );
  }

  const statusLabel: Record<string, string> = {
    TRIAL: "Período de teste",
    ATIVO: "Assinatura ativa",
    INADIMPLENTE: "Pagamento pendente",
    CANCELADO: "Cancelado",
  };

  const planoPago = assinatura?.plano.toUpperCase() || "TRIAL";
  const trialExpirado = assinatura?.trial_expira_em && new Date(assinatura.trial_expira_em) < new Date();

  return (
    <main className="min-h-screen bg-slate-50 p-4 sm:p-6">
      <h1 className="mb-2 text-2xl font-bold text-slate-900">Planos e Pagamentos</h1>

      {/* Status atual */}
      <div className="mb-6 rounded-xl bg-white p-6 shadow-sm">
        <h2 className="mb-2 text-base font-medium text-slate-700">Status Atual</h2>
        <p className="text-lg font-bold text-slate-900">
          {statusLabel[assinatura?.status || "TRIAL"]}
          {trialExpirado && " (expirado)"}
        </p>
        <p className="text-sm text-slate-600">
          Plano: {planoPago} · Até {assinatura?.max_colaboradores || 10} colaboradores
        </p>
        {assinatura?.trial_expira_em && !trialExpirado && (
          <p className="text-sm text-amber-600">
            Teste expira em {new Date(assinatura.trial_expira_em).toLocaleDateString("pt-BR")}
          </p>
        )}
        <p className="mt-2 text-sm text-slate-600">
          Créditos Pix disponíveis: <span className="font-semibold">{assinatura?.creditos_pix || 0}</span>
        </p>
      </div>

      {/* Planos */}
      <div className="mb-6">
        <h2 className="mb-4 text-lg font-bold text-slate-900">Escolha seu plano</h2>
        <div className="grid gap-4 sm:grid-cols-3">
          {planos.map((plano) => (
            <div
              key={plano.id}
              className={`flex flex-col gap-3 rounded-xl p-5 shadow-sm ${
                plano.destaque ? "border-2 border-slate-900 bg-slate-900 text-white" : "border border-slate-200 bg-white"
              }`}
            >
              {plano.destaque && <span className="inline-block w-fit rounded-full bg-white px-3 py-1 text-xs font-bold text-slate-900">Mais popular</span>}
              <h3 className="text-lg font-bold">{plano.nome}</h3>
              <p className={`text-sm ${plano.destaque ? "text-slate-100" : "text-slate-600"}`}>{plano.descricao}</p>
              <p className="text-2xl font-bold">
                R$ {plano.preco_reais.toFixed(2)}
                <span className={`text-sm font-normal ${plano.destaque ? "text-slate-100" : "text-slate-600"}`}>/mês</span>
              </p>
              <ul className="flex flex-col gap-2 text-sm">
                {plano.recursos.map((recurso, i) => (
                  <li key={i} className="flex gap-2">
                    <span>✓</span>
                    <span>{recurso}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleComprarPlano(plano.id)}
                disabled={processando || planoPago === plano.id.toUpperCase()}
                className={`mt-4 h-11 rounded-lg font-semibold transition ${
                  planoPago === plano.id.toUpperCase()
                    ? "bg-slate-200 text-slate-400"
                    : plano.destaque
                      ? "bg-white text-slate-900 hover:bg-slate-50"
                      : "bg-slate-900 text-white hover:bg-slate-800"
                }`}
              >
                {planoPago === plano.id.toUpperCase() ? "Plano atual" : `Escolher ${plano.nome}`}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Créditos Pix */}
      <div className="max-w-md rounded-xl bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-lg font-bold text-slate-900">Comprar créditos Pix</h2>
        <p className="mb-4 text-sm text-slate-600">
          Cada crédito permite gerar 1 lote de crachás. R$ 0,50 por crédito.
        </p>
        <label className="flex flex-col gap-2">
          <span className="text-sm font-medium text-slate-700">Quantidade de créditos</span>
          <input
            type="number"
            min="1"
            max="1000"
            value={creditosQtd}
            onChange={(e) => setCreditosQtd(Math.max(1, Number(e.target.value)))}
            className={inputClass}
          />
        </label>
        <p className="mt-2 text-sm text-slate-600">
          Total: <span className="font-semibold">R$ {(creditosQtd * 0.5).toFixed(2)}</span>
        </p>
        <button
          onClick={handleComprarCreditos}
          disabled={processando}
          className="mt-4 w-full rounded-lg bg-slate-900 py-2.5 font-semibold text-white hover:bg-slate-800 disabled:opacity-60"
        >
          {processando ? "Processando..." : "Comprar via Pix"}
        </button>
      </div>
    </main>
  );
}

export default function PlanoPage() {
  return (
    <Suspense fallback={<main className="min-h-screen bg-slate-50 p-6"><p className="text-slate-600">Carregando...</p></main>}>
      <PlanoContent />
    </Suspense>
  );
}
