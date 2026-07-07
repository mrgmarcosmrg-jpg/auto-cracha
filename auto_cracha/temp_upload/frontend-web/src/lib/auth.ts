const TOKEN_KEY = "crachapp_token";

export function salvarToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function obterToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function limparToken() {
  localStorage.removeItem(TOKEN_KEY);
}
