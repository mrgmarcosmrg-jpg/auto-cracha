'use client';

import { useEffect, useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

interface Filial {
  id: string;
  nome: string;
  cnpj?: string;
  endereco?: string;
  logo_filial_url?: string;
  ativo: boolean;
}

interface SetorConfig {
  setor_sugerido?: string;
  campos_adicionais_config?: unknown;
}

type SectorType = 'Varejo' | 'Saúde' | 'Indústria' | 'Educação' | '';

export default function FiliaisPage() {
  const router = useRouter();
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [setor, setSetor] = useState<SectorType>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({
    nome: '',
    cnpj: '',
    endereco: '',
  });

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Carregar filiais ao montar o componente
  useEffect(() => {
    carregarFiliais();
    carregarConfigSetor();
  }, []);

  async function carregarFiliais() {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiUrl}/filiais`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Erro ao carregar filiais');

      const data = await response.json();
      setFiliais(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('❌ Erro:', err);
      setError('Erro ao carregar filiais');
    } finally {
      setLoading(false);
    }
  }

  async function carregarConfigSetor() {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiUrl}/config`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Erro ao carregar configuração');

      const data: SetorConfig = await response.json();
      if (data.setor_sugerido) {
        setSetor(data.setor_sugerido as SectorType);
      }
    } catch (err) {
      console.error('❌ Erro ao carregar setor:', err);
    }
  }

  async function handleAdicionarFilial(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiUrl}/filiais`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) throw new Error('Erro ao criar filial');

      setFormData({ nome: '', cnpj: '', endereco: '' });
      setShowModal(false);
      carregarFiliais();
    } catch (err) {
      console.error('❌ Erro:', err);
      setError('Erro ao criar filial');
    }
  }

  async function handleAtualizarSetor() {
    if (!setor) return;
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${apiUrl}/config/setor`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          setor_sugerido: setor,
        }),
      });

      if (!response.ok) throw new Error('Erro ao atualizar setor');
      console.log('✅ Setor atualizado com sucesso');
    } catch (err) {
      console.error('❌ Erro:', err);
      setError('Erro ao atualizar setor');
    }
  }

  // Tela de carregamento
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Carregando...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-6 sticky top-0 z-10">
        <h1 className="text-2xl font-bold text-gray-900">Filiais</h1>
        <p className="text-gray-600 text-sm mt-1">Gerenciar unidades da empresa</p>
      </div>

      {/* Conteúdo */}
      <div className="px-4 py-6 space-y-6">
        {/* Setor da Empresa */}
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Setor da Empresa</h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Selecione o setor
              </label>
              <select
                value={setor}
                onChange={(e) => setSetor(e.target.value as SectorType)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
              >
                <option value="">-- Selecione um setor --</option>
                <option value="Varejo">🛒 Varejo</option>
                <option value="Saúde">🏥 Saúde</option>
                <option value="Indústria">🏭 Indústria</option>
                <option value="Educação">🎓 Educação</option>
              </select>
            </div>

            {setor && (
              <button
                onClick={handleAtualizarSetor}
                className="w-full h-11 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Salvar Setor
              </button>
            )}
          </div>
        </div>

        {/* Erro */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        {/* Listagem de Filiais */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Suas Filiais</h2>

          {filiais.length === 0 ? (
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
              <p className="text-gray-600 mb-4">Nenhuma filial cadastrada</p>
              <button
                onClick={() => setShowModal(true)}
                className="inline-block px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Adicionar Primeira Filial
              </button>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {filiais.map((filial) => (
                <div
                  key={filial.id}
                  className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
                >
                  {filial.logo_filial_url && (
                    <img
                      src={filial.logo_filial_url}
                      alt={filial.nome}
                      className="w-full h-24 object-cover rounded-lg mb-3"
                    />
                  )}

                  <h3 className="font-semibold text-gray-900 mb-1">{filial.nome}</h3>

                  {filial.cnpj && (
                    <p className="text-xs text-gray-500 mb-1">CNPJ: {filial.cnpj}</p>
                  )}

                  {filial.endereco && (
                    <p className="text-xs text-gray-600 mb-3">📍 {filial.endereco}</p>
                  )}

                  <div className="flex gap-2">
                    <button className="flex-1 px-3 py-2 text-xs bg-blue-50 text-blue-600 rounded hover:bg-blue-100 transition font-medium">
                      Editar
                    </button>
                    <button className="flex-1 px-3 py-2 text-xs bg-gray-50 text-gray-600 rounded hover:bg-gray-100 transition font-medium">
                      Desativar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Botão Flutuante */}
      <button
        onClick={() => setShowModal(true)}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 text-white rounded-full shadow-lg hover:bg-blue-700 transition flex items-center justify-center text-2xl"
      >
        +
      </button>

      {/* Modal de Adicionar Filial */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50">
          <div className="w-full bg-white rounded-t-2xl p-6 space-y-4">
            <div>
              <h2 className="text-xl font-bold text-gray-900">Adicionar Filial</h2>
              <button
                onClick={() => setShowModal(false)}
                className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleAdicionarFilial} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nome da Filial
                </label>
                <input
                  type="text"
                  value={formData.nome}
                  onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                  placeholder="Ex: Matriz, São Paulo"
                  required
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  CNPJ (opcional)
                </label>
                <input
                  type="text"
                  value={formData.cnpj}
                  onChange={(e) => setFormData({ ...formData, cnpj: e.target.value })}
                  placeholder="00.000.000/0000-00"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Endereço (opcional)
                </label>
                <input
                  type="text"
                  value={formData.endereco}
                  onChange={(e) => setFormData({ ...formData, endereco: e.target.value })}
                  placeholder="Rua, número, cidade"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-base"
                />
              </div>

              <button
                type="submit"
                className="w-full h-12 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Adicionar Filial
              </button>

              <button
                type="button"
                onClick={() => setShowModal(false)}
                className="w-full h-12 bg-gray-200 text-gray-900 font-semibold rounded-lg hover:bg-gray-300 transition"
              >
                Cancelar
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
