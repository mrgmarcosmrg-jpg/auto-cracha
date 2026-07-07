import type { StatusLote } from "@/lib/types";

const ESTILOS: Record<StatusLote, string> = {
  PENDENTE: "bg-slate-100 text-slate-700",
  GERADO: "bg-blue-100 text-blue-800",
  IMPRIMINDO: "bg-amber-100 text-amber-800",
  IMPRESSO: "bg-green-100 text-green-800",
  PARCIALMENTE_IMPRESSO: "bg-orange-100 text-orange-800",
  ARQUIVADO: "bg-slate-200 text-slate-600",
};

const LABELS: Record<StatusLote, string> = {
  PENDENTE: "Pendente",
  GERADO: "PDF gerado",
  IMPRIMINDO: "Imprimindo",
  IMPRESSO: "Impresso",
  PARCIALMENTE_IMPRESSO: "Parcialmente impresso",
  ARQUIVADO: "Arquivado",
};

export default function LoteStatusBadge({ status }: { status: StatusLote }) {
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${ESTILOS[status]}`}>
      {LABELS[status]}
    </span>
  );
}
