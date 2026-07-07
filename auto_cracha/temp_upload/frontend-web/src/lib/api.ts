import { obterToken } from "./auth";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function tratarResposta<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const erro = await res.json().catch(() => ({ detail: "Erro inesperado" }));
    throw new Error(erro.detail || "Erro inesperado");
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json();
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  return tratarResposta<T>(res);
}

export async function authFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = obterToken();
  return apiFetch<T>(path, {
    ...options,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  });
}

export async function authUpload<T>(path: string, formData: FormData): Promise<T> {
  const token = obterToken();
  const res = await fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });
  return tratarResposta<T>(res);
}

export async function authDownload(path: string): Promise<Blob> {
  const token = obterToken();
  const res = await fetch(`${API_URL}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) {
    throw new Error("Erro ao baixar arquivo");
  }
  return res.blob();
}
