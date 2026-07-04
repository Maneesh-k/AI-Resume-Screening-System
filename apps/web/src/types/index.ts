// ── Auth ─────────────────────────────────────────────────────
export interface User {
  id: string;
  email: string;
  name: string;
  role: "admin" | "recruiter" | "hiring_manager";
  is_active: boolean;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// ── Jobs ─────────────────────────────────────────────────────
export type JobStatus = "open" | "closed" | "draft";

export interface Job {
  id: string;
  title: string;
  department: string | null;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_min: number | null;
  experience_max: number | null;
  location: string | null;
  salary_min: number | null;
  salary_max: number | null;
  currency: string;
  status: JobStatus;
  created_by: string;
  created_at: string;
  updated_at: string;
  candidate_count: number;
}

export interface CreateJobPayload {
  title: string;
  description: string;
  department?: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_min?: number;
  experience_max?: number;
  location?: string;
  salary_min?: number;
  salary_max?: number;
  currency?: string;
}

// ── Candidates ───────────────────────────────────────────────
export type ProcessingStatus = "pending" | "processing" | "processed" | "failed";

export interface CandidateSkill {
  name: string;
  proficiency: string | null;
  years: number | null;
}

export interface CandidateExperience {
  company: string | null;
  title: string | null;
  start_date: string | null;
  end_date: string | null;
  is_current: boolean;
  description: string | null;
}

export interface CandidateEducation {
  institution: string | null;
  degree: string | null;
  field: string | null;
  graduation_year: number | null;
}

export interface ScoreBreakdown {
  overall_score: number;
  skill_score: number | null;
  experience_score: number | null;
  domain_score: number | null;
  education_score: number | null;
  certification_score: number | null;
  ai_confidence: number | null;
  ai_summary: string | null;
  skill_gaps: string[];
  score_justification: string | null;
  recommendation: string | null;
  strengths: string[];
  concerns: string[];
}

export interface Candidate {
  id: string;
  job_id: string;
  name: string | null;
  email: string | null;
  phone: string | null;
  experience_years: number | null;
  current_title: string | null;
  current_company: string | null;
  skills: CandidateSkill[];
  experience: CandidateExperience[];
  education: CandidateEducation[];
  certifications: string[];
  processing_status: ProcessingStatus;
  score: ScoreBreakdown | null;
  resume_url: string | null;
  created_at: string;
}

export interface RankedCandidate {
  rank: number;
  candidate: Candidate;
  overall_score: number;
  recommendation: string | null;
  skill_gaps: string[];
  ai_summary: string | null;
}

export interface ProcessingStatusResponse {
  candidate_id: string;
  status: ProcessingStatus;
  progress_pct: number;
  error: string | null;
}

// ── AI ───────────────────────────────────────────────────────
export interface InterviewQuestion {
  type: "technical" | "behavioral" | "system_design";
  question: string;
  rationale: string | null;
  difficulty: "easy" | "medium" | "hard" | null;
}

export interface SkillGap {
  required_skills: string[];
  candidate_skills: string[];
  missing_skills: string[];
  matching_skills: string[];
  match_percentage: number;
}

// ── Search ───────────────────────────────────────────────────
export interface SearchResult {
  candidate_id: string;
  name: string | null;
  similarity_score: number;
  overall_score: number | null;
  current_title: string | null;
  experience_years: number | null;
  skills: string[];
}

// ── Chat ─────────────────────────────────────────────────────
export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  candidateIds?: string[];
}

// ── Pagination ───────────────────────────────────────────────
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// ── Dashboard ────────────────────────────────────────────────
export interface DashboardStats {
  total_jobs: number;
  active_jobs: number;
  total_candidates: number;
  processed_candidates: number;
  avg_match_score: number;
  top_skills: Array<{ skill: string; count: number }>;
}
