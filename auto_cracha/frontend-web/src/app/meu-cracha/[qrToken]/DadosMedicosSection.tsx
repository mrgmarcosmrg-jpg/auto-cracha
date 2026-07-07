"use client";

import { useState, type FormEvent } from "react";
import { apiFetch } from "@/lib/api";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

interface Props {
  qrToken: string;
  temDadosMedicos: boolean;
  dataNascimentoAtual: string | null;
  contatoEmergenciaNomeAtual: string | null;
  contatoEmergenciaTelAtual: string | null;
  onAtualizado: () => void;
}

export default function DadosMedicosSection({
  qrToken,
  temDadosMedicos,
  dataNascimentoAtual,
  contatoEmergenciaNomeAtual,
  contatoEmergenciaTelAtual,
  onAtualizado,
}: Props) {
  const [aceiteTermos, setAceiteTermos] = useState(temDadosMedicos);
  const [form, setForm] = useState({
    data_nascimento: dataNascimentoAtual || "",
    tipo_sanguineo: "",
    comorbidades: "",
    remedios_eventuais: "",
    remedios_continuos: "",
    plano_saude: "",
    alergenicos: "",
    contato_emergencia_nome: contatoEmergenciaNomeAtual || "",
    contato_emergencia_tel: contatoEmergenciaTelAtual || "",
  });
  const [pin, setPin] = useState("");
  const [pinConfirmacao, setPinConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [salvando, setSalvando] = useState(false);

  const [mostrarAlterarPin, setMostrarAlterarPin] = useState(false);
  const [pinAtualParaTroca, setPinAtualParaTroca] = useState("");
  const [pinNovo, setPinNovo] = useState("");
  const [erroPin, setErroPin] = useState("");
  const [mensagemPin, setMensagemPin] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setMensagem("");

    if (!temDadosMedicos && pin !== pinConfirmacao) {
      setErro("Os PINs não coincidem.");
      return;
    }
    if (!temDadosMedicos && pin.length !== 4) {
      setErro("O PIN deve ter exatamente 4 dígitos.");
      return;
    }

    setSalvando(true);
    try {
      if (temDadosMedicos) {
        await apiFetch(`/meu-cracha/${qrToken}/dados-medicos`, {
          method: "PATCH",
          body: JSON.stringify({ ...form, pin_atual: pin }),
        });
      } else {
        await apiFetch(`/meu-cracha/${qrToken}/dados-medicos`, {
          method: "POST",
          body: JSON.stringify({ ...form, pin }),
        });
      }
      setMensagem("Dados de emergência salvos.");
      onAtualizado();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao salvar. Verifique o PIN.");
    } finally {
      setSalvando(false);
    }
  }

  async function handleAlterarPin(e: FormEvent) {
    e.preventDefault();
    setErroPin("");
    setMensagemPin("");
    try {
      await apiFetch(`/meu-cracha/${qrToken}/pin`, {
        method: "PATCH",
        body: JSON.stringify({ pin_atual: pinAtualParaTroca, pin_novo: pinNovo }),
      });
      setMensagemPin("PIN atualizado.");
      setPinAtualParaTroca("");
      setPinNovo("");
    } catch (err) {
      setErroPin(err instanceof Error ? err.message : "Erro ao trocar o PIN");
    }
  }

  return (
    <section className="rounded-xl bg-white p-4 shadow-sm">
      <h2 className="mb-2 text-sm font-medium text-slate-700">Dados de emergência (Ficha SOS)</h2>

      {!aceiteTermos ? (
        <label className="flex items-start gap-3">
          <input type="checkbox" onChange={(e) => setAceiteTermos(e.target.checked)} className="mt-1 h-5 w-5" />
          <span className="text-sm text-slate-600">
            Autorizo o armazenamento criptografado dos meus dados médicos, acessíveis apenas com o PIN que eu
            escolher.
          </span>
        </label>
      ) : (
        <form onSubmit={handleSubmit} className="flex flex-col gap-3">
          <input
            type="date"
            value={form.data_nascimento}
            onChange={(e) => setForm({ ...form, data_nascimento: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Tipo sanguíneo"
            value={form.tipo_sanguineo}
            onChange={(e) => setForm({ ...form, tipo_sanguineo: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Comorbidades"
            value={form.comorbidades}
            onChange={(e) => setForm({ ...form, comorbidades: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Remédios eventuais"
            value={form.remedios_eventuais}
            onChange={(e) => setForm({ ...form, remedios_eventuais: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Remédios de uso contínuo"
            value={form.remedios_continuos}
            onChange={(e) => setForm({ ...form, remedios_continuos: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Plano de saúde"
            value={form.plano_saude}
            onChange={(e) => setForm({ ...form, plano_saude: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Alergênicos"
            value={form.alergenicos}
            onChange={(e) => setForm({ ...form, alergenicos: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Nome do contato de emergência"
            value={form.contato_emergencia_nome}
            onChange={(e) => setForm({ ...form, contato_emergencia_nome: e.target.value })}
            className={inputClass}
          />
          <input
            placeholder="Telefone do contato de emergência"
            value={form.contato_emergencia_tel}
            onChange={(e) => setForm({ ...form, contato_emergencia_tel: e.target.value })}
            className={inputClass}
          />

          <input
            inputMode="numeric"
            maxLength={4}
            placeholder={temDadosMedicos ? "PIN atual" : "Escolha um PIN de 4 dígitos"}
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/g, ""))}
            className={`${inputClass} text-center tracking-widest`}
          />
          {!temDadosMedicos && (
            <input
              inputMode="numeric"
              maxLength={4}
              placeholder="Confirme o PIN"
              value={pinConfirmacao}
              onChange={(e) => setPinConfirmacao(e.target.value.replace(/\D/g, ""))}
              className={`${inputClass} text-center tracking-widest`}
            />
          )}

          {erro && <p className="text-sm text-red-600">{erro}</p>}
          {mensagem && <p className="text-sm text-green-700">{mensagem}</p>}

          <button
            type="submit"
            disabled={salvando}
            className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
          >
            {salvando ? "Salvando..." : temDadosMedicos ? "Atualizar dados" : "Cadastrar dados de emergência"}
          </button>
        </form>
      )}

      {temDadosMedicos && (
        <div className="mt-4 border-t border-slate-100 pt-3">
          <button onClick={() => setMostrarAlterarPin((v) => !v)} className="text-sm text-slate-600 underline">
            Trocar meu PIN
          </button>
          {mostrarAlterarPin && (
            <form onSubmit={handleAlterarPin} className="mt-3 flex flex-col gap-3">
              <input
                inputMode="numeric"
                maxLength={4}
                placeholder="PIN atual"
                value={pinAtualParaTroca}
                onChange={(e) => setPinAtualParaTroca(e.target.value.replace(/\D/g, ""))}
                className={`${inputClass} text-center tracking-widest`}
              />
              <input
                inputMode="numeric"
                maxLength={4}
                placeholder="Novo PIN"
                value={pinNovo}
                onChange={(e) => setPinNovo(e.target.value.replace(/\D/g, ""))}
                className={`${inputClass} text-center tracking-widest`}
              />
              {erroPin && <p className="text-sm text-red-600">{erroPin}</p>}
              {mensagemPin && <p className="text-sm text-green-700">{mensagemPin}</p>}
              <button type="submit" className="h-11 rounded-lg border border-slate-300 text-base">
                Salvar novo PIN
              </button>
            </form>
          )}
        </div>
      )}
    </section>
  );
}
