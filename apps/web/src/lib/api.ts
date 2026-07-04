import { useAuthStore } from "@/stores/auth.store";
import type {
  AuthResponse,
  Candidate,
  CreateJobPayload,
  InterviewQuestion,
  Job,
  PaginatedResponse,
  ProcessingStatusResponse,
  RankedCandidate,
  SearchResult,
  SkillGap,
} from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = useAuthStore.getState().token;

  const headers: Record<string, string> = {
    ...(options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string>),
  };

  const res = await fetch(`${API_BASE}/api/v1${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    useAuthStore.getState().logout();
    window.location.href = "/login";
    throw new ApiError(401, "UNAUTHORIZED", "Session expired");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const error = body?.error ?? {};
    throw new ApiError(
      res.status,
      error.code ?? "UNKNOWN_ERROR",
      error.message ?? `Request failed with ${res.status}`,
    );
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ─────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  register: (payload: { email: string; password: string; name: string; role?: string }) =>
    request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  me: () => request<AuthResponse["user"]>("/auth/me"),
};

// ── Jobs ─────────────────────────────────────────────────────
export const jobsApi = {
  list: (params?: { status?: string; page?: number; limit?: number }) => {
    const qs = new URLSearchParams();
    if (params?.status) qs.set("status", params.status);
    if (params?.page) qs.set("page", String(params.page));
    if (params?.limit) qs.set("limit", String(params.limit));
    return request<PaginatedResponse<Job>>(`/jobs?${qs}`);
  },

  get: (id: string) => request<Job>(`/jobs/${id}`),

  create: (payload: CreateJobPayload) =>
    request<Job>("/jobs", { method: "POST", body: JSON.stringify(payload) }),

  update: (id: string, payload: Partial<CreateJobPayload> & { status?: string }) =>
    request<Job>(`/jobs/${id}`, { method: "PUT", body: JSON.stringify(payload) }),

  delete: (id: string) => request<void>(`/jobs/${id}`, { method: "DELETE" }),

  getRankedCandidates: (jobId: string, params?: { limit?: number; offset?: number }) => {
    const qs = new URLSearchParams();
    if (params?.limit) qs.set("limit", String(params.limit));
    if (params?.offset) qs.set("offset", String(params.offset));
    return request<RankedCandidate[]>(`/jobs/${jobId}/candidates?${qs}`);
  },
};

// ── Resumes ──────────────────────────────────────────────────
export const resumesApi = {
  upload: (file: File, jobId: string) => {
    const form = new FormData();
    form.append("file", file);
    form.append("job_id", jobId);
    return request<{ candidate_id: string; status: string; message: string }>("/resumes/upload", {
      method: "POST",
      body: form,
    });
  },

  getStatus: (candidateId: string) =>
    request<ProcessingStatusResponse>(`/resumes/${candidateId}/status`),

  getDownloadUrl: (candidateId: string) =>
    request<{ url: string; expires_in: number }>(`/resumes/${candidateId}/download-url`),
};

// ── Candidates ───────────────────────────────────────────────
export const candidatesApi = {
  get: (id: string) => request<Candidate>(`/candidates/${id}`),

  delete: (id: string) => request<void>(`/candidates/${id}`, { method: "DELETE" }),
};

// ── AI ───────────────────────────────────────────────────────
export const aiApi = {
  getSkillGap: (candidateId: string, jobId: string) =>
    request<SkillGap>(`/ai/skill-gap?candidate_id=${candidateId}&job_id=${jobId}`, {
      method: "POST",
    }),

  getQuestions: (candidateId: string, jobId: string) =>
    request<InterviewQuestion[]>(`/ai/questions?candidate_id=${candidateId}&job_id=${jobId}`, {
      method: "POST",
    }),

  getSummaryStream: (candidateId: string, jobId: string): EventSource => {
    const token = useAuthStore.getState().token ?? "";
    // Use fetch + ReadableStream for auth support
    return new EventSource(
      `${API_BASE}/api/v1/ai/summary?candidate_id=${candidateId}&job_id=${jobId}&token=${token}`,
    );
  },
};

// ── Search ───────────────────────────────────────────────────
export const searchApi = {
  candidates: (query: string, jobId?: string, limit = 10) => {
    const qs = new URLSearchParams({ q: query, limit: String(limit) });
    if (jobId) qs.set("job_id", jobId);
    return request<{ query: string; results: SearchResult[] }>(`/search/candidates?${qs}`);
  },
};

// ── Streaming fetch helper ────────────────────────────────────
export async function* streamChat(
  message: string,
  sessionId: string | null,
  jobId?: string,
): AsyncGenerator<{ type: string; content?: string; data?: string[]; session_id?: string }> {
  const token = useAuthStore.getState().token;

  const res = await fetch(`${API_BASE}/api/v1/chat/message`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ message, session_id: sessionId, job_id: jobId }),
  });

  if (!res.ok || !res.body) throw new Error("Chat stream failed");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          const data = JSON.parse(line.slice(6));
          yield data;
        } catch {
          // skip malformed
        }
      }
    }
  }
}

export { ApiError };
