export const queryKeys = {
  jobs: {
    all: ["jobs"] as const,
    list: (params?: Record<string, unknown>) => ["jobs", "list", params] as const,
    detail: (id: string) => ["jobs", id] as const,
    candidates: (jobId: string) => ["jobs", jobId, "candidates"] as const,
  },
  candidates: {
    all: ["candidates"] as const,
    detail: (id: string) => ["candidates", id] as const,
    status: (id: string) => ["candidates", id, "status"] as const,
    score: (candidateId: string, jobId: string) =>
      ["candidates", candidateId, "score", jobId] as const,
    questions: (candidateId: string, jobId: string) =>
      ["candidates", candidateId, "questions", jobId] as const,
    skillGap: (candidateId: string, jobId: string) =>
      ["candidates", candidateId, "skill-gap", jobId] as const,
  },
  search: {
    candidates: (query: string, jobId?: string) =>
      ["search", "candidates", query, jobId] as const,
  },
};
