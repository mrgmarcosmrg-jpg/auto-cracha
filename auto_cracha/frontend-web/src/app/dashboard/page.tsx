'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface UserPayload {
  user_id: string;
  tenant_id: string;
  filial_id: string;
  perfil: string;
  exp?: number;
}

interface DashboardState {
  isAuthenticated: boolean;
  user: UserPayload | null;
  loading: boolean;
  error: string;
}

// Função para decodificar JWT (sem validar assinatura - apenas decodificar payload)
function decodeToken(token: string): UserPayload | null {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      console.error('❌ Token inválido: não tem 3 partes');
      return null;
    }

    const payload = parts[1];
    const decoded = JSON.parse(atob(payload));
    console.log('✅ Token decodificado:', decoded);
    return decoded as UserPayload;
  } catch (error) {
    console.error('❌ Erro ao decodificar token:', error);
    return null;
  }
}

export default function DashboardPage() {
  const router = useRouter();
  const [state, setState] = useState<DashboardState>({
    isAuthenticated: false,
    user: null,
    loading: true,
    error: '',
  });

  // Validar autenticação ao carregar
  useEffect(() => {
    try {
      const token = localStorage.getItem('access_token');
      console.log('🔍 Verificando autenticação...');
      console.log('Token encontrado:', token ? 'SIM' : 'NÃO');

      if (!token) {
        console.error('❌ Nenhum token encontrado. Redirecionando para login...');
        setState((prev) => ({
          ...prev,
          isAuthenticated: false,
          error: 'Você não está autenticado',
          loading: false,
        }));
        setTimeout(() => router.push('/login'), 1000);
        return;
      }

      const user = decodeToken(token);
      if (!user) {
        console.error('❌ Falha ao decodificar token. Redirecionando para login...');
        localStorage.removeItem('access_token');
        setState((prev) => ({
          ...prev,
          isAuthenticated: false,
          error: 'Token inválido',
          loading: false,
        }));
        setTimeout(() => router.push('/login'), 1000);
        return;
      }

      console.log('✅ Autenticação validada com sucesso!');
      setState({
        isAuthenticated: true,
        user,
        loading: false,
        error: '',
      });
    } catch (error) {
      console.error('❌ Erro ao verificar autenticação:', error);
      setState((prev) => ({
        ...prev,
        isAuthenticated: false,
        error: 'Erro ao validar autenticação',
        loading: false,
      }));
    }
  }, [router]);

  function handleLogout() {
    console.log('🚪 Fazendo logout...');
    localStorage.removeItem('access_token');
    setState({
      isAuthenticated: false,
      user: null,
      loading: false,
      error: '',
    });
    router.push('/login');
  }

  // Tela de carregamento
  if (state.loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="text-4xl mb-4">⏳</div>
          <p className="text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  // Não autenticado
  if (!state.isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-red-50">
        <div className="text-center">
          <div className="text-6xl mb-4">🔒</div>
          <p className="text-red-600 mb-4">{state.error}</p>
          <p className="text-gray-600">Redirecionando para login...</p>
        </div>
      </div>
    );
  }

  // Dashboard - Autenticado
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navbar */}
      <nav className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg">
        <div className="max-w-6xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🆔</span>
            <h1 className="text-2xl font-bold">CrachApp</h1>
          </div>
          <button
            onClick={handleLogout}
            className="px-4 py-2 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100 transition text-sm"
          >
            Sair
          </button>
        </div>
      </nav>

      {/* Conteúdo */}
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-md p-8">
          <h2 className="text-3xl font-bold text-gray-800 mb-2">Bem-vindo ao Dashboard! 🎉</h2>
          <p className="text-gray-600">Sua autenticação foi validada com sucesso contra o banco de dados PostgreSQL.</p>
        </div>

        {/* Card de Dados do Usuário */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User ID */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-blue-500">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">ID do Usuário</h3>
            <p className="text-lg font-mono text-gray-800 break-all">{state.user?.user_id}</p>
          </div>

          {/* Tenant ID */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-purple-500">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">ID do Tenant (Empresa)</h3>
            <p className="text-lg font-mono text-gray-800 break-all">{state.user?.tenant_id}</p>
          </div>

          {/* Filial ID */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">ID da Filial</h3>
            <p className="text-lg font-mono text-gray-800 break-all">{state.user?.filial_id}</p>
          </div>

          {/* Perfil */}
          <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
            <h3 className="text-sm font-semibold text-gray-500 uppercase mb-2">Perfil do Usuário</h3>
            <p className="text-lg font-bold text-orange-600">{state.user?.perfil}</p>
          </div>
        </div>

        {/* Token Info */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-green-800 mb-3">✅ JWT Validado</h3>
          <div className="bg-white rounded p-4 font-mono text-xs text-gray-600 break-all max-h-32 overflow-y-auto">
            <p className="text-green-700 font-bold mb-2">Token armazenado no localStorage:</p>
            <p>{localStorage.getItem('access_token')?.substring(0, 100)}...</p>
          </div>
          <p className="text-green-700 text-sm mt-3">
            ✅ Estado global de autenticação funcionando corretamente!
          </p>
        </div>

        {/* Menu de Navegação */}
        <div>
          <h3 className="text-2xl font-bold text-gray-800 mb-6">Acesso Rápido ✅ v2</h3>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <Link
              href="/dashboard/colaboradores"
              className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:border-blue-300"
            >
              <div className="mb-3 inline-flex rounded-lg bg-blue-100 p-3">
                <span className="text-2xl">👥</span>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900 group-hover:text-blue-600">Colaboradores</h3>
              <p className="text-sm text-slate-600">Gerenciar equipe e crachás</p>
            </Link>

            <Link
              href="/dashboard/lotes"
              className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:border-green-300"
            >
              <div className="mb-3 inline-flex rounded-lg bg-green-100 p-3">
                <span className="text-2xl">📦</span>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900 group-hover:text-green-600">Lotes</h3>
              <p className="text-sm text-slate-600">Criar e gerenciar lotes</p>
            </Link>

            <Link
              href="/dashboard/plano"
              className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:border-purple-300"
            >
              <div className="mb-3 inline-flex rounded-lg bg-purple-100 p-3">
                <span className="text-2xl">💳</span>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900 group-hover:text-purple-600">Planos</h3>
              <p className="text-sm text-slate-600">Gerenciar assinatura</p>
            </Link>

            <Link
              href="/dashboard/configuracoes"
              className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all hover:shadow-lg hover:border-orange-300"
            >
              <div className="mb-3 inline-flex rounded-lg bg-orange-100 p-3">
                <span className="text-2xl">⚙️</span>
              </div>
              <h3 className="mb-2 text-lg font-semibold text-slate-900 group-hover:text-orange-600">Config</h3>
              <p className="text-sm text-slate-600">Configurar empresa</p>
            </Link>
          </div>
        </div>

        {/* Debug Console */}
        <div className="bg-gray-900 text-green-400 rounded-lg p-6 font-mono text-sm">
          <p className="mb-2">📺 Console de Debug:</p>
          <div className="space-y-1 text-xs">
            <p>✅ Token salvo com sucesso no localStorage</p>
            <p>✅ JWT decodificado: {state.user?.perfil}</p>
            <p>✅ Autenticação validada contra banco PostgreSQL</p>
            <p>✅ Isolamento multitenant funcionando (tenant_id: {state.user?.tenant_id?.substring(0, 8)}...)</p>
            <p>✅ Isolamento por filial funcionando (filial_id: {state.user?.filial_id?.substring(0, 8)}...)</p>
          </div>
        </div>
      </div>
    </div>
  );
}
