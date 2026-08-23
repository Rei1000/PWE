/** API-Fehler — Transport, keine Domain-Logik. */

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(message: string, status: number, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

export function getApiBaseUrl(): string {
  return import.meta.env.VITE_API_BASE_URL ?? "/api";
}

const CSRF_COOKIE = "pwe_csrf";
const CSRF_HEADER = "X-CSRF-Token";

function readCookie(name: string): string | undefined {
  if (typeof document === "undefined") {
    return undefined;
  }
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : undefined;
}

function buildHeaders(init?: RequestInit): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  const body = init?.body;
  if (body !== undefined && body !== null && typeof body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const method = (init?.method ?? "GET").toUpperCase();
  if (method !== "GET" && method !== "HEAD" && method !== "OPTIONS") {
    const csrf = readCookie(CSRF_COOKIE);
    if (csrf && !headers[CSRF_HEADER]) {
      headers[CSRF_HEADER] = csrf;
    }
  }
  return headers;
}

async function parseErrorResponse(response: Response): Promise<ApiError> {
  let detail = response.statusText;
  let code: string | undefined;
  try {
    const body = (await response.json()) as { detail?: string; code?: string };
    detail = body.detail ?? detail;
    code = body.code;
  } catch {
    /* leerer Body */
  }
  return new ApiError(detail, response.status, code);
}

async function rawFetch(path: string, init?: RequestInit): Promise<Response> {
  const url = `${getApiBaseUrl()}${path}`;
  return fetch(url, {
    ...init,
    credentials: "include",
    headers: buildHeaders(init),
  });
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await rawFetch(path, init);

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export async function apiFetchBlob(path: string, accept = "application/pdf"): Promise<Blob> {
  const url = `${getApiBaseUrl()}${path}`;
  const response = await fetch(url, {
    credentials: "include",
    headers: buildHeaders({ headers: { Accept: accept } }),
  });

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }

  return response.blob();
}

/** Multipart-Upload — kein Content-Type setzen (Boundary durch Browser). */
export async function apiPostMultipart<T>(path: string, formData: FormData): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const csrf = readCookie(CSRF_COOKIE);
  const headers: Record<string, string> = { Accept: "application/json" };
  if (csrf) {
    headers[CSRF_HEADER] = csrf;
  }
  const response = await fetch(url, {
    method: "POST",
    body: formData,
    credentials: "include",
    headers,
  });

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }

  return (await response.json()) as T;
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export function apiPut<T>(path: string, body: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export function apiDelete(path: string): Promise<void> {
  return apiFetch<void>(path, { method: "DELETE" });
}

export function apiGet<T>(path: string): Promise<T> {
  return apiFetch<T>(path);
}
