'use client';

import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface LoginResponse {
  access_token: string;
}

interface LoginError {
  detail?: string;
}

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  async function handleSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Chamar API real do FastAPI
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      const response = await fetch(`${apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password,
        }),
      });

      if (!response.ok) {
        const errorData: LoginError = await response.json().catch(() => ({ detail: 'Erro ao conectar com servidor' }));
        throw new Error(errorData.detail || 'Erro ao fazer login');
      }

      const data: LoginResponse = await response.json();

      // Salvar JWT no localStorage
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        console.log('✅ Token salvo com sucesso');
        console.log('Token:', data.access_token);

        setSuccess('Login realizado com sucesso! Redirecionando...');

        // Redirecionar para dashboard após 500ms
        setTimeout(() => {
          router.push('/dashboard');
        }, 500);
      } else {
        throw new Error('Token não recebido do servidor');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro desconhecido ao fazer login';
      setError(errorMessage);
      console.error('❌ Erro de login:', errorMessage);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-500 to-purple-600 flex flex-col items-center justify-center px-4 py-8">
      {/* Container principal - Mobile First */}
      <div className="w-full max-w-sm bg-white rounded-2xl shadow-2xl overflow-hidden">

        {/* Header com Logo */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-8 text-center">
          <div className="text-5xl mb-3">🆔</div>
          <h1 className="text-3xl font-bold text-white">CrachApp</h1>
          <p className="text-blue-100 text-sm mt-2">Geração de Crachás Inteligentes</p>
        </div>

        {/* Conteúdo do formulário */}
        <div className="px-6 py-8">

          {/* Mensagem de Erro */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Mensagem de Sucesso */}
          {success && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-700 text-sm font-medium">{success}</p>
            </div>
          )}

          {/* Formulário */}
          <form onSubmit={handleSubmit} className="space-y-5">

            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                E-mail
              </label>
              <input
                id="email"
                type="email"
                placeholder="seu@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:bg-gray-100 disabled:cursor-not-allowed text-base"
              />
            </div>

            {/* Senha Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Senha
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition disabled:bg-gray-100 disabled:cursor-not-allowed text-base"
              />
            </div>

            {/* Botão de Entrar - Altura mínima 44px para mobile */}
            <button
              type="submit"
              disabled={loading}
              className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 transition disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center text-base font-medium"
            >
              {loading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>
          </form>

          {/* Links adicionais */}
          <div className="mt-8 pt-6 border-t border-gray-200 space-y-3 text-center">
            <Link
              href="/forgot-password"
              className="block text-sm text-blue-600 hover:text-blue-700 font-medium transition"
            >
              Esqueci minha senha
            </Link>

            <p className="text-gray-600 text-sm">
              Não tem conta?{' '}
              <Link href="/register" className="text-blue-600 hover:text-blue-700 font-medium transition">
                Criar conta
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Footer com aviso de segurança */}
      <p className="mt-8 text-center text-white text-xs max-w-sm">
        Este é um ambiente seguro. Nunca compartilhe sua senha com ninguém.
      </p>
    </div>
  );
}
