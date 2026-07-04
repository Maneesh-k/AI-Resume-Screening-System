# Technical Requirements Document (TRD)
# AI Hiring Copilot

**Version:** 1.0
**Author:** Maneesh K
**Date:** 2026-07-04
**Status:** Draft
**Reference PRD:** AI Hiring Copilot PRD v1.0

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Frontend Technical Specifications](#3-frontend-technical-specifications)
4. [Backend Technical Specifications](#4-backend-technical-specifications)
5. [Database Design](#5-database-design)
6. [AI & ML Architecture](#6-ai--ml-architecture)
7. [RAG Pipeline](#7-rag-pipeline)
8. [API Contracts](#8-api-contracts)
9. [Cloud Infrastructure](#9-cloud-infrastructure)
10. [Security Architecture](#10-security-architecture)
11. [Performance Requirements](#11-performance-requirements)
12. [Data Flow Diagrams](#12-data-flow-diagrams)
13. [Error Handling & Resilience](#13-error-handling--resilience)
14. [Observability & Monitoring](#14-observability--monitoring)
15. [Testing Strategy](#15-testing-strategy)
16. [Deployment Strategy](#16-deployment-strategy)
17. [MVP Implementation Checklist](#17-mvp-implementation-checklist)

---

## 1. Overview

### 1.1 Purpose

This document defines the technical specifications, architecture decisions, implementation details, and engineering constraints for building the AI Hiring Copilot platform as described in the PRD v1.0.

### 1.2 Scope

Covers the full-stack implementation including:
- Next.js frontend
- FastAPI backend (Clean Architecture + DDD)
- PostgreSQL relational data store
- Pinecone vector database
- OpenAI GPT-4o integration
- AWS cloud infrastructure
- RAG-based recruiter copilot chat

### 1.3 Assumptions

- OpenAI API access is available with GPT-4o and text-embedding-3-large models
- AWS account provisioned with appropriate IAM permissions
- Pinecone account provisioned (Starter or Standard tier)
- Target user volume for MVP: up to 100 concurrent recruiters, 10,000 jobs, 100,000 resumes

### 1.4 Tech Stack Summary

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, Zustand, TanStack Query |
| Backend | FastAPI, Python 3.12, Clean Architecture + DDD |
| Relational DB | PostgreSQL 16 (AWS RDS) |
| Vector DB | Pinecone (text-embedding-3-large) |
| File Storage | AWS S3 |
| LLM | OpenAI GPT-4o |
| Auth | AWS Cognito + JWT |
| Queue | AWS SQS |
| Events | AWS EventBridge |
| CDN | AWS CloudFront |
| Container | AWS ECS Fargate |
| Search | AWS OpenSearch |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
[Browser / Client]
        |
        v
[CloudFront CDN]
        |
        v
[Next.js App - Vercel / S3 + CloudFront]
        |
   REST / WebSocket
        |
        v
[API Gateway (AWS)]
        |
        v
[ECS Fargate - FastAPI Services]
   |          |          |
   v          v          v
[RDS       [S3         [Pinecone
PostgreSQL] Resume      Vector DB]
           Storage]
        |
        v
[OpenAI API / Claude / Gemini]
        |
        v
[SQS + EventBridge (Async Jobs)]
```

### 2.2 Service Decomposition

The backend is split into the following logical services (deployed as separate ECS tasks or as modules within a monolith for MVP):

| Service | Responsibility |
|---|---|
| `auth-service` | Login, JWT issuance, user management |
| `job-service` | Job CRUD, JD embedding generation |
| `resume-service` | File upload, parsing, embedding |
| `candidate-service` | Candidate profile management, scoring retrieval |
| `ai-service` | Scoring, ranking, summaries, question generation |
| `search-service` | Semantic search via Pinecone |
| `chat-service` | Recruiter copilot chat (RAG) |

For MVP, all services are implemented as FastAPI routers within a single deployable FastAPI application with clean module boundaries, enabling future extraction into microservices.

### 2.3 Async Processing Architecture

Heavy AI operations are processed asynchronously via SQS:

```
Resume Upload API
      |
      v
S3 Storage (raw file)
      |
      v
SQS: resume-processing-queue
      |
      v
ECS Worker (Consumer)
   - Text extraction
   - LLM structuring
   - Embedding generation
   - Candidate scoring
   - Pinecone upsert
      |
      v
PostgreSQL (structured data stored)
EventBridge → Webhook/Notification
```

---

## 3. Frontend Technical Specifications

### 3.1 Tech Stack

| Concern | Solution |
|---|---|
| Framework | Next.js 14 (App Router) |
| Language | TypeScript 5.x |
| Styling | Tailwind CSS 3.x |
| UI Components | shadcn/ui |
| State Management | Zustand |
| Server State / Data Fetching | TanStack Query v5 |
| Authentication | AWS Cognito via `amazon-cognito-identity-js` + JWT |
| Form Handling | React Hook Form + Zod |
| File Upload | Dropzone.js |
| Charts / Analytics | Recharts |
| WebSocket (Chat) | native WebSocket API |

### 3.2 Page & Route Structure

```
/
├── /login                        → Login Page
├── /dashboard                    → Recruiter Dashboard
├── /jobs
│   ├── /                         → Jobs List
│   ├── /create                   → Create Job Form
│   └── /[jobId]
│       ├── /                     → Job Details + Candidates
│       └── /candidates
│           ├── /[candidateId]    → Candidate Detail
│           └── /compare          → Candidate Comparison
├── /chat                         → AI Recruiter Copilot Chat
└── /settings                     → Settings
```

### 3.3 Component Architecture

#### Shared Components

| Component | Description |
|---|---|
| `CandidateCard` | Score, name, experience summary, quick actions |
| `RankingTable` | Sortable table with match scores |
| `SkillGapWidget` | Required vs. present skills diff visualization |
| `AISummaryWidget` | LLM-generated candidate summary display |
| `InterviewQuestionsPanel` | Categorized question list |
| `ChatWidget` | Streaming chat interface with recruiter copilot |
| `FileUploadZone` | Drag-and-drop resume upload (PDF/DOCX) |
| `ScoreBreakdownChart` | Radar/bar chart of scoring dimensions |
| `DashboardStats` | Total jobs, candidates, active openings, top skills |

#### State Management (Zustand Stores)

```typescript
// auth.store.ts
interface AuthStore {
  user: User | null;
  token: string | null;
  login: (credentials: LoginPayload) => Promise<void>;
  logout: () => void;
}

// job.store.ts
interface JobStore {
  selectedJobId: string | null;
  setSelectedJob: (id: string) => void;
}

// candidate.store.ts
interface CandidateStore {
  comparisonList: string[];   // candidate IDs for comparison
  addToComparison: (id: string) => void;
  removeFromComparison: (id: string) => void;
  clearComparison: () => void;
}
```

### 3.4 Authentication Flow

```
1. User submits login form
2. POST /api/auth/login → Backend validates credentials
3. Backend returns { access_token, refresh_token, user }
4. Frontend stores access_token in memory (Zustand)
5. Refresh token stored in HttpOnly cookie
6. TanStack Query attaches Bearer token to all requests
7. On 401 → auto-refresh via /api/auth/refresh
```

### 3.5 File Upload Flow

```
1. Recruiter drops file on FileUploadZone
2. Client validates: file type (PDF/DOCX), size (≤ 10MB)
3. POST /api/resumes/upload (multipart/form-data)
4. Backend uploads to S3, triggers SQS event
5. Frontend polls GET /api/candidates/{id}/status
6. On status = "processed" → TanStack Query invalidates candidate cache
7. UI updates with parsed candidate data
```

---

## 4. Backend Technical Specifications

### 4.1 Framework & Architecture

- **Framework:** FastAPI (Python 3.12)
- **Architecture Pattern:** Clean Architecture with Domain-Driven Design (DDD)
- **Dependency Injection:** `dependency-injector` library
- **Validation:** Pydantic v2
- **ORM:** SQLAlchemy 2.x (async) with `asyncpg` driver
- **Migrations:** Alembic
- **Task Queue Consumer:** `aiobotocore` for SQS polling

### 4.2 Clean Architecture Layer Structure

```
src/
├── domain/                    # Enterprise business rules
│   ├── entities/
│   │   ├── candidate.py
│   │   ├── job.py
│   │   └── user.py
│   ├── value_objects/
│   │   ├── skill.py
│   │   ├── score.py
│   │   └── experience.py
│   ├── repositories/          # Abstract interfaces
│   │   ├── candidate_repository.py
│   │   ├── job_repository.py
│   │   └── user_repository.py
│   └── services/              # Domain services
│       └── scoring_service.py
│
├── application/               # Application business rules (use cases)
│   ├── use_cases/
│   │   ├── create_job.py
│   │   ├── upload_resume.py
│   │   ├── parse_resume.py
│   │   ├── score_candidate.py
│   │   ├── rank_candidates.py
│   │   ├── generate_summary.py
│   │   ├── generate_questions.py
│   │   ├── search_candidates.py
│   │   └── chat_with_copilot.py
│   └── dto/
│       ├── job_dto.py
│       ├── candidate_dto.py
│       └── score_dto.py
│
├── infrastructure/            # Frameworks, drivers, external integrations
│   ├── database/
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── repositories/      # Concrete repository implementations
│   │   └── session.py
│   ├── ai/
│   │   ├── openai_client.py
│   │   ├── embedding_service.py
│   │   └── prompts/
│   │       ├── resume_parse.txt
│   │       ├── candidate_score.txt
│   │       ├── summary_generate.txt
│   │       └── question_generate.txt
│   ├── vector_db/
│   │   └── pinecone_client.py
│   ├── storage/
│   │   └── s3_client.py
│   ├── queue/
│   │   └── sqs_client.py
│   └── search/
│       └── opensearch_client.py
│
└── presentation/              # API layer (FastAPI routers)
    ├── api/
    │   ├── auth.py
    │   ├── jobs.py
    │   ├── resumes.py
    │   ├── candidates.py
    │   ├── ai.py
    │   ├── search.py
    │   └── chat.py
    ├── middleware/
    │   ├── auth_middleware.py
    │   └── logging_middleware.py
    └── dependencies.py
```

### 4.3 Module Specifications

#### Authentication Service

```
Endpoints:
  POST   /api/auth/login
  POST   /api/auth/refresh
  POST   /api/auth/logout
  GET    /api/auth/me

JWT Strategy:
  - Access token TTL: 15 minutes
  - Refresh token TTL: 7 days
  - Algorithm: RS256
  - Stored: access in memory, refresh in HttpOnly cookie

RBAC Roles: admin | recruiter | hiring_manager
```

#### Job Service

```
Endpoints:
  POST   /api/jobs                    Create job
  GET    /api/jobs                    List jobs (paginated)
  GET    /api/jobs/{id}               Get job details
  PUT    /api/jobs/{id}               Update job
  DELETE /api/jobs/{id}               Delete job
  GET    /api/jobs/{id}/candidates    Get ranked candidates for job

On Job Create:
  1. Save to PostgreSQL
  2. Generate embedding for JD text via text-embedding-3-large
  3. Upsert JD embedding into Pinecone (namespace: jobs)
```

#### Resume Service

```
Endpoints:
  POST   /api/resumes/upload          Upload resume (multipart)
  GET    /api/resumes/{id}            Get parsed resume
  GET    /api/resumes/{id}/status     Get processing status

Processing Pipeline (async via SQS):
  1. Upload to S3 (key: resumes/{job_id}/{candidate_id}/{filename})
  2. Push message to SQS: resume-processing-queue
  3. Worker picks up, extracts text (PyMuPDF / python-docx / OCR)
  4. LLM structures text into JSON schema
  5. Embeddings generated for skills + full text
  6. Candidate score computed vs. JD embedding
  7. Results stored in PostgreSQL + Pinecone
  8. Status updated to "processed"
```

#### AI Service

```
Endpoints:
  POST   /api/ai/score                Score candidate vs. job
  POST   /api/ai/summary              Generate candidate summary
  POST   /api/ai/questions            Generate interview questions
  GET    /api/ai/ranking/{job_id}     Get ranked candidates
  POST   /api/ai/skill-gap            Compute skill gap

All AI endpoints:
  - Rate limited: 60 req/min per user
  - Response cached in Redis (TTL: 1 hour) where deterministic
  - Streamed responses for summary and questions (SSE)
```

#### Search Service

```
Endpoints:
  GET    /api/search/candidates       Semantic search (query param: q, job_id)

Implementation:
  1. Embed query text via text-embedding-3-large
  2. Query Pinecone namespace: resumes
  3. Filter by job_id metadata
  4. Return top-k candidates with scores
  5. Hydrate with PostgreSQL data
  6. Return ranked results
```

#### Chat Service

```
Endpoints:
  POST   /api/chat/message            Send message, receive streamed response
  GET    /api/chat/history            Get chat history

Implementation:
  - RAG-based: query → embed → Pinecone search → context injection → GPT-4o
  - Streamed via Server-Sent Events (SSE)
  - Conversation history stored in PostgreSQL (chat_sessions table)
  - System prompt enforces recruiter context and tool usage
```

---

## 5. Database Design

### 5.1 PostgreSQL Schema

```sql
-- Users
CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email       VARCHAR(255) UNIQUE NOT NULL,
    name        VARCHAR(255) NOT NULL,
    role        VARCHAR(50) NOT NULL CHECK (role IN ('admin', 'recruiter', 'hiring_manager')),
    cognito_sub VARCHAR(255) UNIQUE,
    is_active   BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs
CREATE TABLE jobs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               VARCHAR(255) NOT NULL,
    department          VARCHAR(255),
    description         TEXT NOT NULL,
    required_skills     JSONB DEFAULT '[]',
    preferred_skills    JSONB DEFAULT '[]',
    experience_min      INTEGER,
    experience_max      INTEGER,
    location            VARCHAR(255),
    salary_min          INTEGER,
    salary_max          INTEGER,
    currency            VARCHAR(10) DEFAULT 'USD',
    status              VARCHAR(50) DEFAULT 'open' CHECK (status IN ('open', 'closed', 'draft')),
    pinecone_vector_id  VARCHAR(255),
    created_by          UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Candidates
CREATE TABLE candidates (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id              UUID REFERENCES jobs(id) ON DELETE CASCADE,
    name                VARCHAR(255),
    email               VARCHAR(255),
    phone               VARCHAR(50),
    resume_s3_key       VARCHAR(500) NOT NULL,
    resume_text         TEXT,
    parsed_data         JSONB,
    processing_status   VARCHAR(50) DEFAULT 'pending'
                        CHECK (processing_status IN ('pending', 'processing', 'processed', 'failed')),
    processing_error    TEXT,
    pinecone_vector_id  VARCHAR(255),
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- Candidate Skills
CREATE TABLE candidate_skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID REFERENCES candidates(id) ON DELETE CASCADE,
    skill_name      VARCHAR(255) NOT NULL,
    proficiency     VARCHAR(50),  -- 'beginner' | 'intermediate' | 'expert'
    years           FLOAT,
    is_verified     BOOLEAN DEFAULT FALSE
);

-- Candidate Experience
CREATE TABLE candidate_experience (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID REFERENCES candidates(id) ON DELETE CASCADE,
    company         VARCHAR(255),
    title           VARCHAR(255),
    start_date      DATE,
    end_date        DATE,
    is_current      BOOLEAN DEFAULT FALSE,
    description     TEXT,
    duration_months INTEGER
);

-- Candidate Education
CREATE TABLE candidate_education (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID REFERENCES candidates(id) ON DELETE CASCADE,
    institution     VARCHAR(255),
    degree          VARCHAR(255),
    field           VARCHAR(255),
    graduation_year INTEGER,
    gpa             FLOAT
);

-- Candidate Scores
CREATE TABLE candidate_scores (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id        UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id              UUID REFERENCES jobs(id) ON DELETE CASCADE,
    overall_score       FLOAT NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
    skill_score         FLOAT,
    experience_score    FLOAT,
    domain_score        FLOAT,
    education_score     FLOAT,
    certification_score FLOAT,
    ai_confidence       FLOAT,
    ai_summary          TEXT,
    skill_gaps          JSONB DEFAULT '[]',
    score_justification TEXT,
    model_version       VARCHAR(100),
    scored_at           TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (candidate_id, job_id)
);

-- Interview Questions
CREATE TABLE interview_questions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id    UUID REFERENCES candidates(id) ON DELETE CASCADE,
    job_id          UUID REFERENCES jobs(id) ON DELETE CASCADE,
    question_type   VARCHAR(50) CHECK (question_type IN ('technical', 'behavioral', 'system_design')),
    question_text   TEXT NOT NULL,
    rationale       TEXT,
    difficulty      VARCHAR(20) CHECK (difficulty IN ('easy', 'medium', 'hard')),
    generated_at    TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Sessions
CREATE TABLE chat_sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id),
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Chat Messages
CREATE TABLE chat_messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id  UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role        VARCHAR(20) CHECK (role IN ('user', 'assistant')),
    content     TEXT NOT NULL,
    metadata    JSONB,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Audit Logs
CREATE TABLE audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES users(id),
    action      VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id   UUID,
    metadata    JSONB,
    ip_address  INET,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 5.2 Indexes

```sql
CREATE INDEX idx_candidates_job_id ON candidates(job_id);
CREATE INDEX idx_candidates_status ON candidates(processing_status);
CREATE INDEX idx_candidate_scores_job_id ON candidate_scores(job_id);
CREATE INDEX idx_candidate_scores_overall ON candidate_scores(overall_score DESC);
CREATE INDEX idx_candidate_skills_name ON candidate_skills(skill_name);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id, created_at ASC);
```

### 5.3 Pinecone Vector Database

**Index Configuration:**

```
Index Name:    ai-hiring-copilot
Dimension:     3072               # text-embedding-3-large output
Metric:        cosine
Pods:          2 (p2.x1)          # or Serverless on AWS us-east-1

Namespaces:
  - resumes        # Candidate resume embeddings
  - jobs           # Job description embeddings
  - guidelines     # Hiring guidelines for RAG
```

**Vector Metadata Schema:**

```json
// Resume vector
{
  "type": "resume",
  "candidate_id": "uuid",
  "job_id": "uuid",
  "name": "John Doe",
  "experience_years": 5,
  "skills": ["Python", "AWS"],
  "overall_score": 87.5
}

// JD vector
{
  "type": "job",
  "job_id": "uuid",
  "title": "Backend Engineer",
  "department": "Engineering",
  "status": "open"
}
```

---

## 6. AI & ML Architecture

### 6.1 LLM Configuration

```python
LLM_CONFIG = {
    "model": "gpt-4o",
    "temperature": 0.2,           # Low temp for structured outputs
    "max_tokens": 2048,
    "response_format": {"type": "json_object"},  # For parsing/scoring
}

EMBEDDING_CONFIG = {
    "model": "text-embedding-3-large",
    "dimensions": 3072,
}
```

### 6.2 Resume Parsing Prompt

**System Prompt:**
```
You are a resume parsing expert. Extract structured information from the provided resume text.
Return a valid JSON object matching the exact schema provided. Do not add fields not in the schema.
If a field is not found, return null or an empty array as appropriate.
```

**Output Schema:**
```json
{
  "candidate_name": "string",
  "email": "string",
  "phone": "string",
  "experience_years": "number",
  "current_title": "string",
  "current_company": "string",
  "skills": ["string"],
  "experience": [
    {
      "company": "string",
      "title": "string",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM | null",
      "is_current": "boolean",
      "description": "string"
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string",
      "field": "string",
      "graduation_year": "number | null"
    }
  ],
  "certifications": ["string"],
  "projects": [
    {
      "name": "string",
      "description": "string",
      "technologies": ["string"]
    }
  ]
}
```

### 6.3 Candidate Scoring Prompt

**System Prompt:**
```
You are a technical hiring evaluator. Score the candidate's resume against the job description
across 5 dimensions. Return a JSON object with scores (0-100) and brief justification for each.
Be objective and base scores only on evidence in the resume.
```

**Scoring Dimensions & Weights:**

| Dimension | Weight |
|---|---|
| Skill Match | 35% |
| Experience Match | 30% |
| Domain Match | 20% |
| Education Match | 10% |
| Certification Match | 5% |

**Output Schema:**
```json
{
  "skill_score": 85,
  "experience_score": 90,
  "domain_score": 75,
  "education_score": 80,
  "certification_score": 60,
  "overall_score": 84.75,
  "ai_confidence": 0.92,
  "skill_gaps": ["Kubernetes", "Terraform"],
  "score_justification": "Candidate demonstrates strong Python and AWS skills...",
  "recommendation": "Highly Recommended"
}
```

**Final Score Computation:**
```python
overall_score = (
    skill_score        * 0.35 +
    experience_score   * 0.30 +
    domain_score       * 0.20 +
    education_score    * 0.10 +
    certification_score * 0.05
)
```

### 6.4 Candidate Summary Prompt

**System Prompt:**
```
You are a recruitment assistant. Generate a concise 3-5 sentence professional summary
of the candidate based on their resume, highlighting their key strengths relative to
the job requirements. Use third person. Be factual.
```

### 6.5 Interview Question Generation Prompt

**System Prompt:**
```
You are a senior interviewer. Based on the candidate's resume and job description,
generate targeted interview questions. Return JSON with exactly:
- 3 technical questions (specific to their tech stack)
- 3 behavioral questions (STAR format prompts)
- 2 system design questions (relevant to the role)
Each question should include a rationale and difficulty level.
```

### 6.6 AI Fallback Strategy

```
Primary:   OpenAI GPT-4o
Fallback 1: Anthropic Claude 3.5 Sonnet
Fallback 2: Google Gemini 1.5 Pro

Implementation:
  - Exponential backoff: 1s, 2s, 4s (max 3 retries)
  - On persistent failure → fallback model
  - Circuit breaker: open after 10 failures/minute
  - Alerts via CloudWatch on model fallback
```

---

## 7. RAG Pipeline

### 7.1 Indexing Pipeline

```
Document (Resume / JD / Guideline)
        |
        v
Text Extraction & Cleaning
        |
        v
Chunking Strategy:
  - Resumes: full document (single chunk, <8K tokens)
  - JDs: full document (single chunk)
  - Guidelines: 512-token chunks with 50-token overlap
        |
        v
Embedding: text-embedding-3-large (3072 dims)
        |
        v
Upsert to Pinecone with metadata
```

### 7.2 Retrieval Pipeline (Recruiter Chat)

```
User Query: "Find backend engineers with payment experience"
        |
        v
Embed query → 3072-dim vector
        |
        v
Pinecone similarity search:
  - namespace: resumes
  - top_k: 10
  - filter: { job_id: <current_job_id> }   (optional)
        |
        v
Retrieve top candidates (metadata + scores)
        |
        v
Hydrate from PostgreSQL (full candidate data)
        |
        v
Build context window:
  [System Prompt]
  [Recruiter Query]
  [Retrieved Candidate Summaries with Scores]
        |
        v
GPT-4o generates response with:
  - Matching candidates list
  - Score breakdown
  - Justification per candidate
        |
        v
Stream response via SSE to frontend
```

### 7.3 Context Window Management

```python
MAX_CONTEXT_TOKENS = 12000

Context Budget:
  - System prompt:         ~500 tokens
  - Conversation history:  ~2000 tokens (last 5 turns)
  - Retrieved context:     ~8000 tokens (top 10 candidates @ 800 tokens each)
  - User query:            ~200 tokens
  - Reserved for output:   ~2000 tokens
```

---

## 8. API Contracts

### 8.1 Authentication

```
POST /api/auth/login
Request:
{
  "email": "string",
  "password": "string"
}
Response 200:
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 900,
  "user": {
    "id": "uuid",
    "email": "string",
    "name": "string",
    "role": "recruiter | hiring_manager | admin"
  }
}
```

### 8.2 Jobs

```
POST /api/jobs
Request:
{
  "title": "string",
  "department": "string",
  "description": "string",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "experience_min": 0,
  "experience_max": 10,
  "location": "string",
  "salary_min": 0,
  "salary_max": 0,
  "currency": "USD"
}
Response 201:
{
  "id": "uuid",
  "title": "string",
  "status": "open",
  "created_at": "ISO8601"
}

GET /api/jobs?page=1&limit=20&status=open
Response 200:
{
  "items": [{ ...job }],
  "total": 150,
  "page": 1,
  "limit": 20
}

GET /api/jobs/{job_id}/candidates?sort_by=score&order=desc
Response 200:
{
  "job_id": "uuid",
  "candidates": [
    {
      "candidate_id": "uuid",
      "name": "string",
      "overall_score": 92.5,
      "rank": 1,
      "ai_summary": "string",
      "skill_gaps": ["string"],
      "recommendation": "string"
    }
  ]
}
```

### 8.3 Resumes

```
POST /api/resumes/upload
Content-Type: multipart/form-data
Fields:
  - file: File (PDF | DOCX, ≤ 10MB)
  - job_id: UUID
Response 202:
{
  "candidate_id": "uuid",
  "status": "pending",
  "message": "Resume uploaded. Processing started."
}

GET /api/resumes/{candidate_id}/status
Response 200:
{
  "candidate_id": "uuid",
  "status": "pending | processing | processed | failed",
  "progress_pct": 75,
  "error": null
}
```

### 8.4 AI Endpoints

```
POST /api/ai/questions
Request:
{
  "candidate_id": "uuid",
  "job_id": "uuid"
}
Response 200 (SSE stream):
data: {"type": "technical", "question": "...", "difficulty": "hard"}
data: {"type": "behavioral", "question": "...", "difficulty": "medium"}
...
data: {"type": "done"}

POST /api/ai/skill-gap
Request:
{
  "candidate_id": "uuid",
  "job_id": "uuid"
}
Response 200:
{
  "required_skills": ["Kubernetes", "Terraform", "Python"],
  "candidate_skills": ["Python", "Docker", "AWS"],
  "missing_skills": ["Kubernetes", "Terraform"],
  "partial_match": [{"required": "Kubernetes", "candidate_has": "Docker", "similarity": 0.72}]
}
```

### 8.5 Search

```
GET /api/search/candidates?q=payment+engineer+AWS&job_id=uuid&limit=10
Response 200:
{
  "query": "payment engineer AWS",
  "results": [
    {
      "candidate_id": "uuid",
      "name": "string",
      "similarity_score": 0.94,
      "overall_score": 89,
      "highlights": ["AWS", "Payment Gateway", "5 years experience"]
    }
  ]
}
```

### 8.6 Chat

```
POST /api/chat/message
Content-Type: application/json
Accept: text/event-stream
Request:
{
  "session_id": "uuid | null",
  "message": "Find me backend engineers with Kubernetes experience",
  "job_id": "uuid | null"
}
Response (SSE):
data: {"type": "token", "content": "Based"}
data: {"type": "token", "content": " on"}
...
data: {"type": "candidates", "data": [{candidate_id, name, score}]}
data: {"type": "done", "session_id": "uuid"}
```

### 8.7 Standard Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR | NOT_FOUND | UNAUTHORIZED | AI_SERVICE_ERROR",
    "message": "Human-readable message",
    "details": {}
  }
}
```

---

## 9. Cloud Infrastructure

### 9.1 AWS Services Architecture

```
Region: us-east-1 (primary)

Networking:
  VPC (10.0.0.0/16)
  ├── Public Subnets (10.0.1.x, 10.0.2.x)  → ALB, NAT Gateway
  └── Private Subnets (10.0.3.x, 10.0.4.x) → ECS, RDS, ElastiCache

Compute:
  ECS Fargate Cluster
  ├── api-service (FastAPI)       → 2 vCPU, 4GB RAM, min 2 tasks
  └── worker-service (SQS consumer) → 1 vCPU, 2GB RAM, min 1 task

Load Balancing:
  Application Load Balancer (ALB)
  └── Target Group → ECS api-service tasks

Storage:
  RDS PostgreSQL 16
  ├── Instance: db.t3.medium (MVP), db.r6g.large (prod)
  ├── Multi-AZ: enabled (prod), disabled (MVP)
  └── Automated backups: 7-day retention

  S3 Buckets:
  ├── ai-hiring-copilot-resumes   → Resume storage (SSE-S3, versioned)
  └── ai-hiring-copilot-frontend  → Static Next.js export (if used)

Cache:
  ElastiCache Redis 7.x (cache.t3.micro for MVP)
  └── Used for: AI response caching, rate limiting

Queue:
  SQS Standard Queue: resume-processing-queue
  └── DLQ: resume-processing-dlq (maxReceiveCount: 3)

Events:
  EventBridge
  └── Rules:
      ├── resume.processed → notify-service
      └── scoring.complete → analytics

CDN:
  CloudFront Distribution
  └── Origin: S3 (frontend) + ALB (API with /api/* path)

Auth:
  AWS Cognito User Pool
  └── App Client: ai-hiring-copilot-client

Secrets:
  AWS Secrets Manager:
  ├── /prod/openai/api_key
  ├── /prod/pinecone/api_key
  ├── /prod/db/credentials
  └── /prod/cognito/client_secret

Monitoring:
  CloudWatch Logs (all ECS tasks)
  CloudWatch Metrics + Alarms
  X-Ray Tracing (ECS tasks)
```

### 9.2 Environment Configuration

```
Environments:
  development  → Local Docker Compose
  staging      → AWS (single-AZ, smaller instances)
  production   → AWS (Multi-AZ, autoscaling)

Environment Variables (injected via ECS Task Definitions from Secrets Manager):
  DATABASE_URL
  REDIS_URL
  OPENAI_API_KEY
  PINECONE_API_KEY
  PINECONE_INDEX_NAME
  AWS_S3_BUCKET_NAME
  AWS_SQS_QUEUE_URL
  COGNITO_USER_POOL_ID
  COGNITO_CLIENT_ID
  JWT_SECRET
  ENVIRONMENT
  LOG_LEVEL
```

### 9.3 Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ ./src/
EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

```yaml
# docker-compose.yml (local development)
services:
  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/hiring
      REDIS_URL: redis://redis:6379

  worker:
    build: .
    command: python -m src.worker
    depends_on: [postgres, redis]

  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: hiring
      POSTGRES_PASSWORD: postgres
    ports: ["5432:5432"]
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

volumes:
  pgdata:
```

---

## 10. Security Architecture

### 10.1 Authentication & Authorization

```
Authentication: AWS Cognito + JWT (RS256)
Authorization:  Role-Based Access Control (RBAC)

Role Permissions Matrix:
                          Admin    Recruiter    Hiring Manager
Create Job                  ✓         ✓              ✗
View Jobs                   ✓         ✓              ✓
Upload Resume               ✓         ✓              ✗
View Candidates             ✓         ✓              ✓
View AI Scores              ✓         ✓              ✓
Generate Questions          ✓         ✓              ✗
Compare Candidates          ✓         ✓              ✓
Use Recruiter Chat          ✓         ✓              ✗
Manage Users                ✓         ✗              ✗
View Audit Logs             ✓         ✗              ✗
```

### 10.2 Data Security

```
Transport:
  - TLS 1.2+ enforced on all endpoints
  - HSTS headers
  - CloudFront HTTPS only

At Rest:
  - RDS: AES-256 encryption (AWS-managed KMS key)
  - S3: SSE-S3 (server-side encryption)
  - Pinecone: encrypted at rest (managed)
  - Redis: encryption at rest enabled

Secrets:
  - All secrets in AWS Secrets Manager
  - No secrets in environment variables, code, or logs
  - IAM roles for ECS tasks (no long-lived access keys)

PII Handling:
  - Candidate name, email, phone treated as PII
  - Masked in logs (log.info("Processing candidate {id}"))
  - S3 bucket: private, pre-signed URLs for file access (TTL: 1 hour)
```

### 10.3 API Security

```
Rate Limiting (per user per minute):
  /api/resumes/upload:    10 req/min
  /api/ai/*:              60 req/min
  /api/search/*:          30 req/min
  /api/chat/message:      20 req/min

Input Validation:
  - All inputs validated via Pydantic v2 models
  - File type validation: MIME type + magic bytes check
  - Max file size enforced at API and S3 policy level
  - SQL injection prevented via SQLAlchemy parameterized queries
  - XSS prevented via Pydantic sanitization + CSP headers

CORS:
  Allowed origins: [frontend domain only]
  Allowed methods: GET, POST, PUT, DELETE, OPTIONS
  Allow credentials: true
```

---

## 11. Performance Requirements

### 11.1 SLOs (Service Level Objectives)

| Operation | Target P95 | Target P99 |
|---|---|---|
| API response (non-AI) | < 200ms | < 500ms |
| Resume upload API | < 500ms | < 1s |
| Resume processing (async) | < 10s | < 20s |
| Candidate search | < 2s | < 3s |
| AI analysis (scoring) | < 15s | < 25s |
| AI summary generation | < 8s | < 12s |
| Chat first token | < 1s | < 2s |
| Dashboard load | < 1s | < 2s |

### 11.2 Scale Targets

```
Concurrent users:    100 (MVP), 1,000 (Phase 2)
Total resumes:       100,000
Total jobs:          10,000
Resumes per job:     ~500 average, 2,000 max
Daily resume uploads: 1,000 (MVP), 10,000 (Phase 2)
SQS throughput:      50 messages/min (MVP), 500/min (Phase 2)
```

### 11.3 Caching Strategy

```
Layer 1: Redis (ElastiCache)
  - AI scores: TTL 24 hours (keyed by candidate_id + job_id + model_version)
  - AI summaries: TTL 24 hours
  - Interview questions: TTL 24 hours
  - Ranked candidate list: TTL 5 minutes
  - Search results: TTL 2 minutes

Layer 2: TanStack Query (client-side)
  - Job list: staleTime 60s
  - Candidate list: staleTime 30s
  - Candidate detail: staleTime 120s
  - Dashboard stats: staleTime 300s
```

---

## 12. Data Flow Diagrams

### 12.1 Resume Upload & Processing Flow

```
Recruiter
   |
   | 1. Upload resume (PDF/DOCX)
   v
Next.js Frontend
   |
   | 2. POST /api/resumes/upload (multipart)
   v
FastAPI (resume-service)
   |
   | 3. Validate file (type, size)
   | 4. Upload to S3
   | 5. Create candidate record (status=pending)
   | 6. Publish to SQS
   |
   v
SQS: resume-processing-queue
   |
   v
ECS Worker
   | 7. Extract text (PyMuPDF / python-docx / Tesseract OCR)
   | 8. LLM call: parse resume → structured JSON
   | 9. Generate embedding: text-embedding-3-large
   | 10. Upsert to Pinecone (namespace: resumes)
   | 11. LLM call: score candidate vs. JD embedding
   | 12. LLM call: generate AI summary
   | 13. Save to PostgreSQL (candidate_scores, candidate_skills, etc.)
   | 14. Update status → "processed"
   v
PostgreSQL + Pinecone (updated)
   |
   v
EventBridge → (future: notifications)
```

### 12.2 Candidate Ranking Flow

```
Recruiter opens Job Detail page
   |
   | GET /api/jobs/{job_id}/candidates?sort_by=score
   v
FastAPI (candidate-service)
   |
   | Query PostgreSQL:
   | SELECT c.*, cs.overall_score, cs.ai_summary, cs.skill_gaps
   | FROM candidates c
   | JOIN candidate_scores cs ON cs.candidate_id = c.id
   | WHERE c.job_id = {job_id} AND c.processing_status = 'processed'
   | ORDER BY cs.overall_score DESC
   v
Return ranked list to frontend
```

### 12.3 Recruiter Chat RAG Flow

```
Recruiter: "Find me AWS engineers with 5+ years experience"
   |
   v
POST /api/chat/message
   |
   | 1. Embed query → 3072-dim vector
   v
Pinecone (namespace: resumes)
   |
   | 2. Similarity search (top_k=10)
   v
Top 10 candidate vector IDs + metadata
   |
   | 3. Hydrate from PostgreSQL (full profiles)
   v
Context Builder:
   [System: You are a recruiter assistant...]
   [Retrieved: Candidate A (score 91), Candidate B (score 88)...]
   [User: Find me AWS engineers with 5+ years experience]
   |
   | 4. Send to GPT-4o (streaming)
   v
SSE Stream → Frontend ChatWidget
```

---

## 13. Error Handling & Resilience

### 13.1 Error Categories

```
Category            | HTTP Code | Retry | User Visible
--------------------|-----------|-------|-------------
Validation error    | 400       | No    | Yes (field details)
Auth failure        | 401       | No    | Yes
Permission denied   | 403       | No    | Yes
Not found           | 404       | No    | Yes
AI service timeout  | 503       | Yes   | Partial (retry message)
LLM parse failure   | 500       | Yes   | No (graceful fallback)
Queue full          | 503       | Yes   | No (queue internally)
Rate limited        | 429       | Yes   | Yes (retry-after header)
```

### 13.2 Resilience Patterns

```
Resume Processing:
  - SQS visibility timeout: 300s (5 min for processing)
  - DLQ after 3 receive attempts
  - Failed resumes: status = "failed", error stored in DB
  - DLQ processor: alert + log for manual review

AI API Calls:
  - Retry: exponential backoff (1s, 2s, 4s), max 3 retries
  - Timeout: 30s per LLM call
  - Fallback: Claude 3.5 Sonnet → Gemini 1.5 Pro
  - Circuit breaker: opens after 10 failures/minute

Database:
  - Connection pool: min=5, max=20 (SQLAlchemy async pool)
  - Query timeout: 30s
  - Automatic reconnection via asyncpg

Pinecone:
  - Retry on transient errors (retry-after: 1s, 2s, 4s)
  - Fallback: PostgreSQL full-text search if Pinecone unavailable
```

---

## 14. Observability & Monitoring

### 14.1 Logging

```python
# Structured logging (JSON)
{
  "timestamp": "ISO8601",
  "level": "INFO | WARNING | ERROR",
  "service": "api | worker",
  "request_id": "uuid",
  "user_id": "uuid",         # if authenticated
  "action": "resume.upload",
  "candidate_id": "uuid",    # no PII in logs
  "duration_ms": 234,
  "message": "string"
}
```

### 14.2 Metrics (CloudWatch)

```
Application Metrics:
  - resume_uploads_total (counter)
  - resume_processing_duration_seconds (histogram)
  - ai_scoring_duration_seconds (histogram)
  - ai_api_errors_total (counter, by model)
  - candidate_score_distribution (histogram)
  - active_jobs_total (gauge)
  - pinecone_query_duration_seconds (histogram)

Infrastructure Metrics (auto from ECS/RDS):
  - ECS CPU/Memory utilization
  - RDS CPU, connections, read/write IOPS
  - SQS queue depth (ApproximateNumberOfMessagesVisible)
  - ALB request count, 4xx/5xx rates, latency

Alarms:
  - SQS DLQ message count > 0 → PagerDuty alert
  - AI API error rate > 5% → Slack + PagerDuty
  - Resume processing P95 > 30s → Slack alert
  - RDS CPU > 80% for 5min → Slack alert
  - ECS task crash → immediate PagerDuty
```

### 14.3 Tracing

```
AWS X-Ray distributed tracing:
  - Trace ID propagated across API → Worker → AI calls
  - Segments: HTTP request, DB query, AI API call, Pinecone query
  - Sampling: 100% errors, 10% success (MVP), tunable
```

---

## 15. Testing Strategy

### 15.1 Backend Testing

```
Unit Tests (pytest):
  - Domain entities and value objects
  - Scoring computation logic
  - Prompt building functions
  - Repository implementations (with test DB)
  Coverage target: 80%

Integration Tests:
  - API endpoint tests (TestClient + test database)
  - SQS message processing (LocalStack)
  - S3 upload/download (LocalStack)
  - Pinecone operations (mock)

AI Tests (eval harness):
  - Resume parsing accuracy: test against 20 labeled resumes
  - Scoring consistency: same resume+JD = ±2 score variance
  - Question quality: manual review checklist

Load Tests (Locust):
  - 100 concurrent users, 10 min sustained
  - Ramp: 0→50 users in 2 min
  Targets: p95 < 2s for search, p95 < 200ms for non-AI APIs
```

### 15.2 Frontend Testing

```
Unit Tests (Vitest):
  - Zustand store logic
  - Utility functions
  - Component rendering (React Testing Library)

E2E Tests (Playwright):
  - Login flow
  - Job creation
  - Resume upload + status polling
  - Candidate ranking view
  - Chat interaction
```

---

## 16. Deployment Strategy

### 16.1 CI/CD Pipeline (GitHub Actions)

```yaml
Triggers:
  - PR → run tests, lint, type-check
  - Merge to main → deploy to staging
  - Tag v*.*.* → deploy to production

Pipeline Steps:
  1. lint + type-check (ruff, mypy, eslint, tsc)
  2. unit tests (pytest, vitest)
  3. build Docker image
  4. push to ECR
  5. run Alembic migrations (staging/prod)
  6. update ECS task definition
  7. ECS rolling deployment (min 50% healthy, max 200%)
  8. smoke tests against deployed endpoint
  9. Slack notification on success/failure
```

### 16.2 Database Migrations

```
Tool: Alembic
Strategy:
  - All schema changes via migration files (never manual)
  - Backward-compatible migrations only (no column drops in same deploy)
  - Run in CI before ECS update
  - Rollback: alembic downgrade -1
```

### 16.3 Blue/Green Considerations

For production, ECS rolling deployment with:
- `minimumHealthyPercent: 50`
- `maximumPercent: 200`
- Health check: `GET /api/health` → 200 with `{"status": "ok"}`

---

## 17. MVP Implementation Checklist

### Phase 1 (MVP) — 8 Weeks

**Week 1-2: Foundation**
- [ ] Project scaffold (FastAPI, Next.js, Docker Compose)
- [ ] PostgreSQL schema + Alembic migrations
- [ ] AWS Cognito user pool setup
- [ ] JWT auth endpoints + middleware
- [ ] RBAC implementation

**Week 3: Job & Resume Services**
- [ ] Job CRUD API
- [ ] Resume upload to S3
- [ ] SQS queue + worker consumer scaffold
- [ ] Text extraction (PyMuPDF, python-docx, OCR fallback)

**Week 4: AI Pipeline**
- [ ] OpenAI client with retry + fallback
- [ ] Resume parsing prompt + JSON extraction
- [ ] Candidate scoring engine (5 dimensions + weights)
- [ ] Embedding generation + Pinecone upsert

**Week 5: AI Features**
- [ ] AI summary generation (SSE streaming)
- [ ] Interview question generator (SSE streaming)
- [ ] Skill gap computation
- [ ] Candidate ranking API

**Week 6: Search & Chat**
- [ ] Semantic search via Pinecone
- [ ] Recruiter copilot RAG chat (SSE)
- [ ] Redis caching for AI responses

**Week 7: Frontend**
- [ ] Login, Dashboard, Jobs List, Create Job pages
- [ ] Candidate List + Ranking Table
- [ ] Candidate Detail + AI Summary
- [ ] Skill Gap Widget, Interview Questions Panel
- [ ] Recruiter Chat widget

**Week 8: Hardening**
- [ ] Rate limiting
- [ ] Logging (structured JSON)
- [ ] CloudWatch alarms
- [ ] Load testing
- [ ] AWS ECS + RDS production deployment
- [ ] End-to-end smoke testing

---

## Appendix A: Dependencies

### Backend (requirements.txt)

```
fastapi==0.115.x
uvicorn[standard]==0.30.x
pydantic==2.x
sqlalchemy[asyncio]==2.x
asyncpg==0.29.x
alembic==1.13.x
openai==1.x
pinecone-client==4.x
pymupdf==1.24.x
python-docx==1.1.x
pytesseract==0.3.x
boto3==1.34.x
aiobotocore==2.x
redis[asyncio]==5.x
python-jose[cryptography]==3.x
dependency-injector==4.x
structlog==24.x
httpx==0.27.x
tenacity==8.x          # retry library
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "next": "14.x",
    "react": "18.x",
    "typescript": "5.x",
    "tailwindcss": "3.x",
    "zustand": "4.x",
    "@tanstack/react-query": "5.x",
    "react-hook-form": "7.x",
    "zod": "3.x",
    "react-dropzone": "14.x",
    "recharts": "2.x",
    "shadcn-ui": "latest",
    "@radix-ui/react-*": "latest",
    "amazon-cognito-identity-js": "6.x",
    "eventsource-parser": "2.x"
  }
}
```

---

*TRD v1.0 — AI Hiring Copilot — Maneesh K — 2026-07-04*
