const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch(endpoint: string, options: FetchOptions = {}) {
  const { token, headers, ...rest } = options;

  const authHeaders: Record<string, string> = {
    ...(headers as Record<string, string>),
  };

  if (token) {
    authHeaders['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (let browser set boundary)
  if (!(rest.body instanceof FormData)) {
    authHeaders['Content-Type'] = 'application/json';
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: authHeaders,
    ...rest,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// ─── Auth API ───

export async function registerUser(username: string, email: string, password: string, fullName?: string) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ username, email, password, full_name: fullName }),
  });
}

export async function loginUser(username: string, password: string) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

// ─── Document API ───

export async function uploadDocument(file: File, token: string) {
  const formData = new FormData();
  formData.append('file', file);

  return apiFetch('/documents/upload', {
    method: 'POST',
    body: formData,
    token,
  });
}

export async function getResults(documentId: number, token: string) {
  return apiFetch(`/documents/results/${documentId}`, { token });
}

export async function getDocumentHistory(token: string) {
  return apiFetch('/documents/history', { token });
}

export async function getAuditTrail(documentId: number, token: string) {
  return apiFetch(`/documents/audit/${documentId}`, { token });
}

export async function getStandards() {
  return apiFetch('/standards');
}

export async function healthCheck() {
  return apiFetch('/health');
}
