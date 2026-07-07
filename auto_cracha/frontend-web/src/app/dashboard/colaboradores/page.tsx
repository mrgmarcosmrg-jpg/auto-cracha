'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

interface Colaborador {
  id: string;
  nome: string;
  cargo: string;
  celular?: string;
  email_colaborador?: string;
  status: 'PENDENTE_LGPD' | 'ATIVO' | 'DESLIGADO' | 'VISITANTE';
  em_treinamento: boolean;
  pcd: boolean;
  filial_id: string;
}

interface Filial {
  id: string;
  nome: string;
}

interface LinkLgpd {
  link: string;
  whatsapp_url: string;
}

const statusColors: Record<string, { bg: string; text: string; label: string }> = {
  PENDENTE_LGPD: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: '⏳ Pendente' },
  ATIVO: { bg: 'bg-green-100', text: 'text-green-800', label: '✅ Ativo' },
  DESLIGADO: { bg: 'bg-red-100', text: 'text-red-800', label: '❌ Desligado' },
  VISITANTE: { bg: 'bg-blue-100', text: 'text-blue-800', label: '👤 Visitante' },
};

export default function ColaboradoresPage() {
  const router = useRouter();
  const [colaboradores, setColaboradores] = useState<Colaborador[]>([]);
  const [filiais, setFiliais] = useState<Filial[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [filtroStatus, setFiltroStatus] = useState<string>('');
  const [formData, setFormData] = useState({
    nome: '',
    cargo: '',
    celular: '',
    email_colaborador: '',
    filial_id: '',
    em_treinamento: false,
    pcd: false,
  });

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const params = filtroStatus ? `?status=${filtroStatus}` : '';

      const [colabResponse, filiaisResponse] = await Promise.all([
        fetch(`http://157.245.217.95:8000/colaboradores${params}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://157.245.217.95:8000/filiais', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (colabResponse.ok && filiaisResponse.ok) {
        const colabData = await colabResponse.json();
        const filiaisData = await filiaisResponse.json();
        setColaboradores(colabData);
        setFiliais(filiaisData);
      }
      setLoading(false);
    } catch (err) {
      console.error('Erro ao buscar dados:', err);
      setLoading(false);
    }
  };

  const getNomeFilial = (filialId: string) => {
    return filiais.find(f => f.id === filialId)?.nome || '—';
  };

  const handleAddColaborador = async () => {
    if (!formData.nome || !formData.cargo || !formData.celular || !formData.filial_id) {
      setError('Nome, cargo, celular e filial são obrigatórios');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://157.245.217.95:8000/colaboradores', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setFormData({ nome: '', cargo: '', celular: '', email_colaborador: '', filial_id: '', em_treinamento: false, pcd: false });
        setShowModal(false);
        setError('');
        fetchData();
      } else {
        const data = await response.json();
        setError(data.detail || 'Erro ao adicionar');
      }
    } catch (err) {
      setError('Erro de conexão');
    }
  };

  const handleEnviarWhatsApp = async (colaboradorId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://157.245.217.95:8000/colaboradores/${colaboradorId}/link-lgpd`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const linkData: LinkLgpd = await response.json();
        window.open(linkData.whatsapp_url, '_blank');
      }
    } catch (err) {
      console.error('Erro:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-600 to-blue-600 p-4 pb-24">
      {/* Header Mobile-First */}
      <div className="flex items-center gap-3 mb-6 mt-4">
        <Link href="/dashboard" className="text-white hover:opacity-80 text-xl">
          ←
        </Link>
        <h1 className="text-2xl font-bold text-white">Colaboradores</h1>
      </div>

      {/* Filtro Status */}
      <div className="mb-6 bg-white rounded-lg shadow p-3">
        <label className="block text-xs font-semibold text-gray-600 mb-2">Status</label>
        <select
          value={filtroStatus}
          onChange={(e) => setFiltroStatus(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
        >
          <option value="">Todos</option>
          <option value="PENDENTE_LGPD">⏳ Pendente LGPD</option>
          <option value="ATIVO">✅ Ativo</option>
          <option value="DESLIGADO">❌ Desligado</option>
          <option value="VISITANTE">👤 Visitante</option>
        </select>
      </div>

      {/* Lista de Colaboradores */}
      <div className="space-y-4 mb-8">
        {colaboradores.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-600 text-sm">Nenhum colaborador cadastrado</p>
          </div>
        ) : (
          colaboradores.map((col) => {
            const statusInfo = statusColors[col.status] || statusColors.PENDENTE_LGPD;
            return (
              <div key={col.id} className="bg-white rounded-lg shadow-md p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-sm font-bold text-gray-800">{col.nome}</h3>
                  <span className={`${statusInfo.bg} ${statusInfo.text} text-xs font-bold px-2 py-1 rounded`}>
                    {statusInfo.label}
                  </span>
                </div>

                <p className="text-xs text-gray-600 mb-1">📋 {col.cargo}</p>
                <p className="text-xs text-gray-600 mb-1">🏢 {getNomeFilial(col.filial_id)}</p>

                {col.celular && (
                  <p className="text-xs text-gray-600 mb-2">📱 {col.celular}</p>
                )}

                <div className="flex gap-2 mb-3">
                  {col.em_treinamento && (
                    <span className="text-xs bg-orange-100 text-orange-800 px-2 py-1 rounded">🎓 Treino</span>
                  )}
                  {col.pcd && (
                    <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded">♿ PCD</span>
                  )}
                </div>

                {col.status === 'PENDENTE_LGPD' && (
                  <button
                    onClick={() => handleEnviarWhatsApp(col.id)}
                    className="w-full bg-green-500 text-white py-2 px-3 rounded-lg font-semibold text-sm hover:bg-green-600 transition active:scale-95 touch-none"
                  >
                    📱 WhatsApp
                  </button>
                )}
              </div>
            );
          })
        )}
      </div>

      {/* Floating Add Button */}
      <button
        onClick={() => setShowModal(true)}
        className="fixed bottom-8 right-4 w-14 h-14 bg-purple-600 text-white rounded-full shadow-lg flex items-center justify-center text-2xl hover:bg-purple-700 transition active:scale-95 touch-none"
      >
        +
      </button>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-end z-50">
          <div className="bg-white rounded-t-3xl shadow-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="mb-4 flex justify-between items-center">
              <h2 className="text-xl font-bold text-gray-800">Novo Colaborador</h2>
              <button
                onClick={() => { setShowModal(false); setError(''); }}
                className="text-2xl text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {error && <p className="text-red-600 text-sm mb-4 p-2 bg-red-50 rounded">{error}</p>}

            <div className="space-y-3 mb-6">
              <input
                type="text"
                placeholder="Nome *"
                value={formData.nome}
                onChange={(e) => setFormData({ ...formData, nome: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-purple-500 touch-none"
              />
              <input
                type="text"
                placeholder="Cargo *"
                value={formData.cargo}
                onChange={(e) => setFormData({ ...formData, cargo: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-purple-500 touch-none"
              />
              <input
                type="tel"
                placeholder="Celular (11999999999) *"
                value={formData.celular}
                onChange={(e) => setFormData({ ...formData, celular: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-purple-500 touch-none"
              />
              <input
                type="email"
                placeholder="Email"
                value={formData.email_colaborador}
                onChange={(e) => setFormData({ ...formData, email_colaborador: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-purple-500 touch-none"
              />
              <select
                value={formData.filial_id}
                onChange={(e) => setFormData({ ...formData, filial_id: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-base focus:outline-none focus:ring-2 focus:ring-purple-500 touch-none"
              >
                <option value="">Filial *</option>
                {filiais.map(f => (
                  <option key={f.id} value={f.id}>{f.nome}</option>
                ))}
              </select>

              <div className="space-y-2 border-t pt-3">
                <label className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded">
                  <input
                    type="checkbox"
                    checked={formData.em_treinamento}
                    onChange={(e) => setFormData({ ...formData, em_treinamento: e.target.checked })}
                    className="w-5 h-5 rounded cursor-pointer"
                  />
                  <span className="text-gray-700 text-sm">Em Treinamento</span>
                </label>
                <label className="flex items-center gap-2 p-2 hover:bg-gray-50 rounded">
                  <input
                    type="checkbox"
                    checked={formData.pcd}
                    onChange={(e) => setFormData({ ...formData, pcd: e.target.checked })}
                    className="w-5 h-5 rounded cursor-pointer"
                  />
                  <span className="text-gray-700 text-sm">PCD</span>
                </label>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => { setShowModal(false); setError(''); }}
                className="flex-1 px-4 py-3 text-gray-700 border border-gray-300 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Cancelar
              </button>
              <button
                onClick={handleAddColaborador}
                className="flex-1 px-4 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition active:scale-95"
              >
                Adicionar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
