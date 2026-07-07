export interface ConfigOut {
  nome_empresa: string;
  cnpj: string;
  logo_url: string | null;
  logo_grupo_url: string | null;
  cor_primaria: string;
  cor_secundaria: string;
  usar_faixa_treinamento: boolean;
  usar_faixa_pcd: boolean;
  faixas_customizadas: unknown[] | null;
  status: string;
  trial_expira_em: string;
  template_id: string;
  setor_sugerido: string | null;
  campos_adicionais_config: unknown[] | null;
  redes_sociais: Record<string, string> | null;
  telefone: string | null;
  whatsapp: string | null;
  email_empresa: string | null;
  endereco_completo: string | null;
  nome_fantasia: string | null;
  razao_social: string | null;
}

export interface FilialOut {
  id: string;
  nome: string;
  cnpj: string | null;
  endereco: string | null;
  logo_filial_url: string | null;
  logo_grupo_url: string | null;
  ativo: boolean;
}

export type PerfilUsuario = "SUPER_ADMIN" | "ADMIN_TENANT" | "GESTOR_FILIAL" | "VISUALIZADOR";

export interface UsuarioOut {
  id: string;
  nome: string;
  email: string;
  perfil: PerfilUsuario;
  filial_id: string | null;
  ativo: boolean;
  criado_em: string;
}

export type StatusColaborador = "PENDENTE_LGPD" | "ATIVO" | "DESLIGADO" | "VISITANTE";

export interface ColaboradorOut {
  id: string;
  filial_id: string;
  status: StatusColaborador;
  qr_token: string;
  nome: string;
  cargo: string;
  celular: string | null;
  email_colaborador: string | null;
  em_treinamento: boolean;
  pcd: boolean;
  pcd_descricao: string | null;
  campos_adicionais: Record<string, unknown> | null;
  foto_url: string | null;
  data_desligamento: string | null;
  criado_em: string;
}

export interface LinkLgpdOut {
  link: string;
  whatsapp_url: string;
}

export interface ColaboradorCriadoOut extends ColaboradorOut {
  link_lgpd: LinkLgpdOut;
}

export interface ErroImportacao {
  linha: number;
  motivo: string;
}

export interface ImportarResultado {
  importados: number;
  erros: ErroImportacao[];
}

export type StatusLote = "PENDENTE" | "GERADO" | "IMPRIMINDO" | "IMPRESSO" | "PARCIALMENTE_IMPRESSO" | "ARQUIVADO";
export type ModoImpressao = "A4_3X3" | "A4_UNITARIO";
export type StatusCracha = "PENDENTE" | "IMPRESSO" | "FALHOU";

export interface LoteCriadoOut {
  lote_id: string;
  quantidade_total: number;
  total_paginas: number;
}

export interface LoteOut {
  id: string;
  filial_id: string;
  nome_lote: string;
  status_lote: StatusLote;
  quantidade_total: number;
  quantidade_impressos: number;
  quantidade_falhados: number;
  template_id: string;
  modo_impressao: ModoImpressao;
  pdf_url: string | null;
  pdf_total_paginas: number | null;
  pdf_tamanho_kb: number | null;
  pago_via: "ASSINATURA" | "PIX_AVULSO" | null;
  criado_em: string;
  pdf_gerado_em: string | null;
  concluido_em: string | null;
  arquivado_em: string | null;
}

export interface LoteCrachaOut {
  id: string;
  colaborador_id: string;
  status_cracha: StatusCracha;
  motivo_falha: string | null;
  posicao_na_pagina: number | null;
  numero_pagina: number | null;
  nome_snapshot: string | null;
  cargo_snapshot: string | null;
  foto_url_snapshot: string | null;
  status_lgpd_snapshot: string | null;
  filial_nome_snapshot: string | null;
}

export interface LoteDetalheOut extends LoteOut {
  crachas: LoteCrachaOut[];
}

export interface HistoricoLoteOut {
  id: string;
  tipo_evento: string;
  quantidade_afetada: number | null;
  descricao: string | null;
  ocorrido_em: string;
}

export interface FalhaRegistradaOut {
  minilote_id: string;
}

export interface PdfUrlOut {
  pdf_url: string;
}

export interface EmpresaPublicaOut {
  nome_fantasia: string | null;
  razao_social: string | null;
  logo_url: string | null;
  endereco_completo: string | null;
  telefone: string | null;
  whatsapp: string | null;
  email_empresa: string | null;
  redes_sociais: Record<string, string> | null;
}

export interface ColaboradorPublicoOut {
  status: StatusColaborador;
  nome: string | null;
  cargo: string | null;
  foto_url: string | null;
  data_desligamento: string | null;
  exibir_contato_pessoal: boolean;
  celular: string | null;
  email_colaborador: string | null;
  contato_emergencia_nome: string | null;
  contato_emergencia_tel: string | null;
  tem_sos: boolean;
  acesso_expirado: boolean;
}

export interface PaginaPublicaOut {
  empresa: EmpresaPublicaOut;
  colaborador: ColaboradorPublicoOut;
}

export interface MeuCrachaOut {
  nome: string;
  cargo: string;
  foto_url: string | null;
  exibir_contato_pessoal: boolean;
  status: string;
  tem_dados_medicos: boolean;
  data_nascimento: string | null;
  contato_emergencia_nome: string | null;
  contato_emergencia_tel: string | null;
}

export interface PlanoOut {
  id: string;
  nome: string;
  descricao: string;
  preco_reais: number;
  max_colaboradores: number;
  recursos: string[];
  destaque: boolean;
}

export interface AssinaturaOut {
  status: string;
  plano: string;
  max_colaboradores: number;
  creditos_pix: number;
  trial_expira_em: string | null;
  mp_payment_id: string | null;
}

export interface PreferenciaCheckoutOut {
  init_point: string;
  sandbox_init_point: string;
}

export interface CreditosPixResponse {
  quantidade: number;
  valor_total_reais: number;
  status: string;
  mensagem: string;
}
