interface DadosVCard {
  nome: string;
  telefone?: string | null;
  email?: string | null;
  organizacao?: string | null;
}

export function baixarVCard(dados: DadosVCard, nomeArquivo: string) {
  const linhas = [
    "BEGIN:VCARD",
    "VERSION:3.0",
    `FN:${dados.nome}`,
    dados.organizacao ? `ORG:${dados.organizacao}` : "",
    dados.telefone ? `TEL;TYPE=CELL:${dados.telefone}` : "",
    dados.email ? `EMAIL:${dados.email}` : "",
    "END:VCARD",
  ].filter(Boolean);

  const blob = new Blob([linhas.join("\n")], { type: "text/vcard" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = nomeArquivo;
  link.click();
  URL.revokeObjectURL(url);
}
