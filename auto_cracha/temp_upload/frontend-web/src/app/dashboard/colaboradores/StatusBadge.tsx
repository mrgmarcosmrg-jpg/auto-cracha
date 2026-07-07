import type { StatusColaborador } from "@/lib/types";

const ESTILOS: Record<StatusColaborador, string> = {
  PENDENTE_LGPD: "bg-amber-100 text-amber-800",
  ATIVO: "bg-green-100 text-green-800",
  DESLIGADO: "bg-red-100 text-red-800",
  VISITANTE: "bg-blue-100 text-blue-800",
};

const LABELS: Record<StatusColaborador, string> = {
  PENDENTE_LGPD: "Pendente LGPD",
  ATIVO: "Ativo",
  DESLIGADO: "Desligado",
  VISITANTE: "Visitante",
};

export default function StatusBadge({ status }: { status: StatusColaborador }) {
  return (
    <span className={`rounded-full px-2 py-1 text-xs font-medium ${ESTILOS[status]}`}>
      {LABELS[status]}
    </span>
  );
}
