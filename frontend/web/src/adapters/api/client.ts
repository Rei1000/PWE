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

function buildHeaders(init?: RequestInit): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  const body = init?.body;
  if (body !== undefined && body !== null && typeof body === "string" && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
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

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const response = await fetch(url, {
    ...init,
    headers: buildHeaders(init),
  });

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
  const response = await fetch(url, { headers: { Accept: accept } });

  if (!response.ok) {
    throw await parseErrorResponse(response);
  }

  return response.blob();
}

export function apiPost<T>(path: string, body?: unknown): Promise<T> {
  return apiFetch<T>(path, {
    method: "POST",
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export function apiGet<T>(path: string): Promise<T> {
  return apiFetch<T>(path);
}
