"use client";

import { useEffect, useState, type FormEvent } from "react";
import { authFetch } from "@/lib/api";
import type { FilialOut, PerfilUsuario, UsuarioOut } from "@/lib/types";

const inputClass = "h-11 rounded-lg border border-slate-300 px-4 text-base";

const PERFIS: { id: PerfilUsuario; label: string }[] = [
  { id: "ADMIN_TENANT", label: "Administrador" },
  { id: "GESTOR_FILIAL", label: "Gestor de filial" },
  { id: "VISUALIZADOR", label: "Visualizador" },
];

export default function UsuariosTab() {
  const [usuarios, setUsuarios] = useState<UsuarioOut[]>([]);
  const [filiais, setFiliais] = useState<FilialOut[]>([]);
  const [carregado, setCarregado] = useState(false);
  const [convite, setConvite] = useState({ nome: "", email: "", perfil: "VISUALIZADOR" as PerfilUsuario, filial_id: "" });
  const [convidando, setConvidando] = useState(false);
  const [erro, setErro] = useState("");
  const [mensagem, setMensagem] = useState("");

  async function carregar() {
    const [usuariosData, filiaisData] = await Promise.all([
      authFetch<UsuarioOut[]>("/usuarios"),
      authFetch<FilialOut[]>("/filiais"),
    ]);
    setUsuarios(usuariosData);
    setFiliais(filiaisData);
    setCarregado(true);
  }

  useEffect(() => {
    carregar();
  }, []);

  async function handleConvidar(e: FormEvent) {
    e.preventDefault();
    setErro("");
    setMensagem("");
    setConvidando(true);
    try {
      await authFetch<UsuarioOut>("/usuarios/convidar", {
        method: "POST",
        body: JSON.stringify({
          nome: convite.nome,
          email: convite.email,
          perfil: convite.perfil,
          filial_id: convite.perfil === "GESTOR_FILIAL" ? convite.filial_id || null : null,
        }),
      });
      setConvite({ nome: "", email: "", perfil: "VISUALIZADOR", filial_id: "" });
      setMensagem("Convite enviado. O link foi impresso no console do backend (modo dev).");
      await carregar();
    } catch (err) {
      setErro(err instanceof Error ? err.message : "Erro ao convidar usuário");
    } finally {
      setConvidando(false);
    }
  }

  async function handleRevogar(id: string) {
    await authFetch(`/usuarios/${id}/revogar`, { method: "POST" });
    await carregar();
  }

  function nomeFilial(filialId: string | null) {
    if (!filialId) return "Todas as filiais";
    return filiais.find((f) => f.id === filialId)?.nome || "—";
  }

  if (!carregado) {
    return <p className="text-slate-600">Carregando...</p>;
  }

  return (
    <div className="flex flex-col gap-6">
      <form onSubmit={handleConvidar} className="flex flex-col gap-3 rounded-lg border border-slate-200 p-4">
        <h2 className="text-sm font-medium text-slate-700">Convidar usuário</h2>
        <input
          required
          placeholder="Nome"
          value={convite.nome}
          onChange={(e) => setConvite({ ...convite, nome: e.target.value })}
          className={inputClass}
        />
        <input
          required
          type="email"
          placeholder="E-mail"
          value={convite.email}
          onChange={(e) => setConvite({ ...convite, email: e.target.value })}
          className={inputClass}
        />
        <select
          value={convite.perfil}
          onChange={(e) => setConvite({ ...convite, perfil: e.target.value as PerfilUsuario })}
          className={inputClass}
        >
          {PERFIS.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </select>
        {convite.perfil === "GESTOR_FILIAL" && (
          <select
            value={convite.filial_id}
            onChange={(e) => setConvite({ ...convite, filial_id: e.target.value })}
            className={inputClass}
          >
            <option value="">Selecione a filial</option>
            {filiais.map((f) => (
              <option key={f.id} value={f.id}>
                {f.nome}
              </option>
            ))}
          </select>
        )}
        {erro && <p className="text-sm text-red-600">{erro}</p>}
        {mensagem && <p className="text-sm text-green-700">{mensagem}</p>}
        <button
          type="submit"
          disabled={convidando}
          className="h-11 rounded-lg bg-slate-900 text-base font-semibold text-white disabled:opacity-60"
        >
          {convidando ? "Convidando..." : "Enviar convite"}
        </button>
      </form>

      <ul className="flex flex-col gap-2">
        {usuarios.map((usuario) => (
          <li key={usuario.id} className="flex items-center justify-between gap-2 rounded-lg border border-slate-200 p-3">
            <div>
              <p className="text-base font-medium text-slate-900">{usuario.nome}</p>
              <p className="text-sm text-slate-500">
                {usuario.email} · {PERFIS.find((p) => p.id === usuario.perfil)?.label || usuario.perfil}
                {usuario.perfil === "GESTOR_FILIAL" && ` · ${nomeFilial(usuario.filial_id)}`}
              </p>
              <p className="text-sm text-slate-500">{usuario.ativo ? "Ativo" : "Acesso revogado"}</p>
            </div>
            {usuario.ativo && (
              <button
                onClick={() => handleRevogar(usuario.id)}
                className="h-11 rounded-lg border border-red-300 px-3 text-sm text-red-600"
              >
                Revogar
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
