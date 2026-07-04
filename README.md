<div align="center">

# 🤖 AI Hiring Copilot

### AI-Powered Recruitment & Resume Screening Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Pinecone](https://img.shields.io/badge/Pinecone-VectorDB-00A0A0?style=for-the-badge)](https://pinecone.io)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-Cloud-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com)

**Reduce recruiter screening time by 80% with semantic AI matching, automated resume parsing, and intelligent candidate ranking.**

[Live Demo](#) · [Documentation](#architecture) · [Quick Start](#quick-start) · [API Docs](http://localhost:8000/docs)

</div>

---

## 📸 UI Preview

> **Dark-themed glass morphism design** — professional, data-dense, and beautiful.

```
┌──────────────────────────────────────────────────────────────────────┐
│  🤖 AI Hiring    │  Dashboard                          [🔔] [👤] [→] │
│  Copilot         ├──────────────────────────────────────────────────┤
│                  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  ◉ Dashboard     │  │ Jobs    │ │ Active  │ │Candidat.│ │  Avg   │ │
│  ◯ Jobs          │  │  142    │ │  89     │ │  3,421  │ │  84.2  │ │
│  ◯ AI Copilot ✨ │  │ +3/week │ │         │ │ now     │ │ ↑ 2.1  │ │
│  ◯ Settings      │  └─────────┘ └─────────┘ └─────────┘ └────────┘ │
│                  │                                                    │
│  ─────────────   │  Recent Jobs                          [View all→] │
│  👤 Maneesh K    │  ┌──────────────────────────────────────────────┐ │
│  Recruiter       │  │ #  Score  Name           Title    Skills     │ │
│                  │  │ 1   92   John Doe     Sr. BE Eng  Python AWS │ │
│                  │  │ 2   89   Jane Smith   ML Eng      Python TF  │ │
│                  │  │ 3   83   Bob Chen     Backend     Go Postgres│ │
│                  │  └──────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────────────┐
│  Candidate: John Doe  │  Sr. Backend Engineer · Stripe · 5 yrs      │
│  ─────────────────────┤  ┌────────────────────────────────────────┐  │
│  AI Summary           │  │  AI SCORE              [Highly Recmd.] │  │
│  ─────────────────    │  │                                        │  │
│  John brings 5 years  │  │            92                          │  │
│  of backend expertise │  │         out of 100                     │  │
│  with strong Python,  │  │                                        │  │
│  AWS, and PostgreSQL  │  │  Skills      ████████████░░  88       │  │
│  skills. Payment      │  │  Experience  ███████████░░░  85       │  │
│  domain experience    │  │  Domain      ██████████████  95       │  │
│  aligns well with     │  │  Education   ████████░░░░░░  75       │  │
│  the role.            │  │  Certs       ██████░░░░░░░░  62       │  │
│  ─────────────────    │  └────────────────────────────────────────┘  │
│  ✅ Strengths         │  ┌────────────────────────────────────────┐  │
│  • Payment APIs       │  │  SKILL GAP          Match: 87%        │  │
│  • AWS architecture   │  │  ✅ Python  ✅ AWS  ✅ PostgreSQL     │  │
│  • System design      │  │  ❌ Kubernetes  ❌ Terraform          │  │
│  ─────────────────    │  └────────────────────────────────────────┘  │
│  Interview Questions  │                                               │
│  [Technical] [3] ▼   │                                               │
│  [Behavioral] [3] ▼  │                                               │
│  [Sys Design] [2] ▼  │                                               │
└──────────────────────────────────────────────────────────────────────┘
```

```
┌──────────────────────────────────────────────────────────────────────┐
│  ✨ AI Recruiter Copilot                              🟢 Online      │
│  ──────────────────────────────────────────────────────────────────  │
│                                                                      │
│     🤖  Hello! I'm your AI Hiring Copilot. I can help you           │
│         find, evaluate, and compare candidates using natural          │
│         language. Try: "Find backend engineers with AWS"             │
│                                                                      │
│     👤  Find me senior engineers with payment experience             │
│         and strong AWS skills, scored above 80                       │
│                                                                      │
│     🤖  Found 3 highly matching candidates:                          │
│                                                                      │
│         1. John Doe — Score: 92 | 5yrs | Stripe, AWS, Python        │
│            → Payment gateway expertise, deployed on ECS             │
│                                                                      │
│         2. Sarah Kim — Score: 88 | 7yrs | PayPal, AWS, Go           │
│            → Built high-throughput payment processing APIs          │
│                                                                      │
│         3. Alex Wong — Score: 84 | 4yrs | Square, GCP, Python       │
│            → PCI-DSS compliance, microservices architecture         │
│                                                                      │
│  ┌─────────────────────────────────────────────────┐  [→ Send]     │
│  │ Ask anything about candidates…                  │               │
│  └─────────────────────────────────────────────────┘               │
└──────────────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **🧠 Semantic Resume Matching** | Goes beyond keyword search — understands meaning using vector embeddings |
| **📊 AI Candidate Scoring** | 5-dimension scoring (Skills 35%, Experience 30%, Domain 20%, Education 10%, Certs 5%) |
| **📝 Automated Resume Parsing** | Extracts structured data from PDF/DOCX with LLM + OCR fallback |
| **🏆 Candidate Ranking** | Auto-ranks all applicants by AI match score with explainability |
| **🔍 Skill Gap Analysis** | Identifies exactly which required skills a candidate is missing |
| **💬 Interview Question Gen** | Generates targeted Technical, Behavioral, and System Design questions |
| **🤖 Recruiter Copilot Chat** | RAG-powered chatbot — search candidates with natural language |
| **⚡ Real-time Streaming** | AI summaries and chat stream token-by-token via SSE |
| **🔐 RBAC Auth** | Role-based access: Admin, Recruiter, Hiring Manager |
| **📈 Analytics Dashboard** | Overview of pipeline metrics, top skills, hiring funnel |

---

## 🏗️ Architecture

### High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI HIRING COPILOT                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐     REST/SSE     ┌──────────────────────────────┐ │
│  │   Next.js 14  │ ◄──────────────► │     FastAPI (Python 3.12)    │ │
│  │  TypeScript   │                  │   Clean Architecture + DDD   │ │
│  │  Tailwind CSS │                  └──────────────────────────────┘ │
│  │  Zustand      │                           │         │            │ │
│  │  TanStack Q   │               ┌───────────┤         └────────┐  │ │
│  └──────────────┘                ▼                              ▼  │ │
│                         ┌────────────────┐           ┌──────────────┐│
│                         │  PostgreSQL 16  │           │   Pinecone   ││
│                         │  (RDS / Local) │           │  Vector DB   ││
│                         └────────────────┘           └──────────────┘│
│                                  │                                   │
│                    ┌─────────────┼──────────────┐                   │
│                    ▼             ▼              ▼                   │
│             ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│             │ OpenAI   │  │  AWS S3  │  │  Redis   │              │
│             │  GPT-4o  │  │(Resumes) │  │  Cache   │              │
│             └──────────┘  └──────────┘  └──────────┘              │
│                                  │                                   │
│                         ┌────────────────┐                          │
│                         │  AWS SQS       │                          │
│                         │  Worker (Async)│                          │
│                         └────────────────┘                          │
└─────────────────────────────────────────────────────────────────────┘
```

### Backend Clean Architecture

```
src/
├── domain/              ← Enterprise business rules (no framework deps)
│   ├── entities/        ← User, Job, Candidate (pure Python dataclasses)
│   ├── repositories/    ← Abstract interfaces (ABCs)
│   └── value_objects/   ← Immutable domain types
│
├── application/         ← Application business rules
│   ├── use_cases/       ← One use case per file (Single Responsibility)
│   └── dto/             ← Data Transfer Objects
│
├── infrastructure/      ← Frameworks & drivers (implements domain)
│   ├── database/        ← SQLAlchemy models + repo implementations
│   ├── ai/              ← OpenAI client, prompts, resume parser
│   ├── vector_db/       ← Pinecone client
│   ├── storage/         ← S3 client
│   ├── queue/           ← SQS client
│   └── cache/           ← Redis client
│
├── presentation/        ← FastAPI layer (routers, schemas, middleware)
│   ├── api/v1/          ← Route handlers
│   ├── schemas/         ← Pydantic request/response models
│   └── middleware/      ← Logging, auth
│
└── worker/              ← SQS consumer for async resume processing
```

### Resume Processing Pipeline

```
Upload PDF/DOCX
      │
      ▼
  S3 Storage
      │
      ▼
  SQS Queue ──────────────────────────────────────────────────────────┐
      │                                                                │
      ▼                                                                │
  ECS Worker                                                          │
  ┌──────────────────────────────────────────────────────────────┐   │
  │  1. Extract text  →  PyMuPDF / python-docx / Tesseract OCR   │   │
  │  2. LLM parse     →  GPT-4o → structured JSON                │   │
  │  3. Embed         →  text-embedding-3-large (3072 dims)      │   │
  │  4. Score         →  GPT-4o → 5-dimension scores (0-100)     │   │
  │  5. Summary       →  GPT-4o → 3-5 sentence AI summary        │   │
  │  6. Pinecone      →  upsert vector with metadata              │   │
  │  7. PostgreSQL    →  save all structured data + scores        │   │
  └──────────────────────────────────────────────────────────────┘   │
                                                                      │
  Local Dev: SQS replaced by inline async task ◄───────────────────┘
```

### RAG Copilot Chat Architecture

```
Recruiter query: "Find AWS engineers with payment domain experience"
      │
      ▼
  text-embedding-3-large → 3072-dim query vector
      │
      ▼
  Pinecone similarity search (namespace: resumes, top_k: 8)
      │
      ▼
  Retrieve top candidates → hydrate from PostgreSQL
      │
      ▼
  Build context window:
  [System: You are a recruiter assistant...]
  [Context: Candidate A (score 91), Candidate B (score 88)...]
  [Query: Find AWS engineers with payment domain experience]
      │
      ▼
  GPT-4o streaming response → SSE → Frontend ChatWidget
```

---

## 🛠️ Tech Stack

### Backend
| Technology | Version | Purpose |
|---|---|---|
| **FastAPI** | 0.115 | REST API framework |
| **Python** | 3.12 | Backend language |
| **SQLAlchemy** | 2.x async | ORM (asyncpg driver) |
| **Alembic** | 1.14 | Database migrations |
| **PostgreSQL** | 16 | Primary database |
| **Redis** | 7 | AI response caching, rate limiting |
| **OpenAI** | GPT-4o | LLM (parse, score, summarize, questions) |
| **text-embedding-3-large** | — | Resume + JD embeddings |
| **Pinecone** | v5 | Vector similarity search |
| **AWS S3** | — | Resume file storage |
| **AWS SQS** | — | Async processing queue |
| **PyMuPDF** | 1.25 | PDF text extraction |
| **python-docx** | 1.1 | DOCX text extraction |
| **Tesseract** | — | OCR fallback for scanned PDFs |
| **Pydantic** | v2 | Validation, settings |
| **python-jose** | — | JWT auth (HS256) |
| **tenacity** | 9.0 | Retry with exponential backoff |
| **structlog** | 24 | Structured JSON logging |

### Frontend
| Technology | Version | Purpose |
|---|---|---|
| **Next.js** | 14 (App Router) | React framework |
| **TypeScript** | 5.x strict | Type safety |
| **Tailwind CSS** | 3.x | Utility-first styling |
| **Framer Motion** | 11 | Animations |
| **shadcn/ui** | latest | UI component system |
| **TanStack Query** | v5 | Server state + caching |
| **Zustand** | 5 | Client state (auth, comparison) |
| **react-hook-form** | 7 | Form management |
| **Zod** | 3 | Schema validation |
| **react-dropzone** | 14 | Resume file upload |
| **Recharts** | 2 | Analytics charts |
| **Sonner** | 1.7 | Toast notifications |

---

## 🚀 Quick Start

### Prerequisites
- Node.js 20+ and pnpm
- Python 3.12+
- Docker & Docker Compose
- OpenAI API key
- Pinecone account (free tier works)

### 1. Clone & Setup

```bash
git clone https://github.com/Maneesh-k/AI-Resume-Screening-System.git
cd AI-Resume-Screening-System

# Copy environment variables
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and set the required values:

```env
# Required for core AI features
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...

# Required for file storage (use LocalStack for local dev)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_S3_BUCKET_NAME=ai-hiring-copilot-resumes

# Auto-configured for Docker Compose
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/hiring_copilot
REDIS_URL=redis://localhost:6379/0
```

### 3. Start with Docker Compose (Recommended)

```bash
# Start everything: API + Worker + Web + Postgres + Redis
make up

# Or manually:
docker-compose up --build
```

Access:
- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

### 4. Local Development (Without Docker)

```bash
# Terminal 1 — Start infrastructure
make up-db          # Starts Postgres + Redis only

# Terminal 2 — Backend
cd apps/api
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head      # Run DB migrations
uvicorn src.main:app --reload --port 8000

# Terminal 3 — Frontend
cd apps/web
pnpm install
pnpm dev                  # Starts on :3000
```

### 5. Seed Demo Users

Run the seed script to create demo accounts:

```bash
cd apps/api
source .venv/bin/activate
python scripts/seed.py
```

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@hiringcopilot.ai` | `Admin@1234` |
| **Recruiter** | `recruiter@hiringcopilot.ai` | `Recruit@1234` |
| **Hiring Manager** | `hiring@hiringcopilot.ai` | `Hiring@1234` |

> **Tip:** Use the Admin account for full access — create jobs, manage users, and view all candidates.

---

## 📁 Project Structure

```
AI-Resume-Screening-System/
├── CLAUDE.md                    ← AI coding rules and conventions
├── .env.example                 ← Environment variable template
├── docker-compose.yml           ← Full local stack
├── Makefile                     ← Developer commands
├── turbo.json                   ← Turborepo task config
├── pnpm-workspace.yaml          ← Monorepo workspace
│
├── apps/
│   ├── api/                     ← FastAPI Backend
│   │   ├── src/
│   │   │   ├── main.py          ← App entry point
│   │   │   ├── config.py        ← Settings (pydantic-settings)
│   │   │   ├── domain/          ← Entities, repositories (abstract)
│   │   │   ├── application/     ← Use cases, DTOs
│   │   │   ├── infrastructure/  ← DB, AI, S3, SQS, Redis
│   │   │   ├── presentation/    ← FastAPI routers, schemas
│   │   │   └── worker/          ← SQS consumer + resume processor
│   │   ├── alembic/             ← DB migration files
│   │   ├── pyproject.toml       ← Python dependencies
│   │   └── Dockerfile
│   │
│   └── web/                     ← Next.js 14 Frontend
│       ├── src/
│       │   ├── app/             ← App Router pages
│       │   │   ├── (auth)/      ← Login
│       │   │   └── (dashboard)/ ← Dashboard, Jobs, Chat, Settings
│       │   ├── components/      ← Reusable UI components
│       │   ├── stores/          ← Zustand state stores
│       │   ├── lib/             ← API client, utils, query client
│       │   ├── types/           ← TypeScript type definitions
│       │   └── styles/          ← Global CSS + design tokens
│       ├── package.json
│       └── Dockerfile
│
├── TRD_AI_Hiring_Copilot.md    ← Full Technical Requirements Document
└── memory/MEMORY.md            ← AI coding context (for Claude Code)
```

---

## 🗄️ Database Schema

```sql
users               → Authentication, roles (admin/recruiter/hiring_manager)
jobs                → Job postings with required/preferred skills
candidates          → Uploaded resumes linked to jobs
candidate_skills    → Normalized skill extraction
candidate_experience → Work history per candidate
candidate_education  → Education records
candidate_scores    → AI scoring per candidate×job (5 dimensions)
interview_questions → Generated questions per candidate×job
chat_sessions       → Copilot conversation sessions
chat_messages       → Message history per session
audit_logs          → Action trail for compliance
```

---

## 🔌 API Reference

### Authentication
```http
POST   /api/v1/auth/register    Register new user
POST   /api/v1/auth/login       Login → JWT token
GET    /api/v1/auth/me          Get current user
```

### Jobs
```http
GET    /api/v1/jobs             List jobs (paginated, filterable)
POST   /api/v1/jobs             Create job + generate JD embedding
GET    /api/v1/jobs/{id}        Get job details
PUT    /api/v1/jobs/{id}        Update job
DELETE /api/v1/jobs/{id}        Delete job
GET    /api/v1/jobs/{id}/candidates   Get ranked candidates (by AI score)
```

### Resumes
```http
POST   /api/v1/resumes/upload          Upload resume (PDF/DOCX, ≤10MB)
GET    /api/v1/resumes/{id}/status     Processing status + progress %
GET    /api/v1/resumes/{id}/download-url  Pre-signed S3 URL
```

### AI
```http
POST   /api/v1/ai/score        Compute/retrieve score for candidate×job
POST   /api/v1/ai/summary      Stream AI summary (SSE)
POST   /api/v1/ai/questions    Generate interview questions
POST   /api/v1/ai/skill-gap   Compute skill gap analysis
```

### Search & Chat
```http
GET    /api/v1/search/candidates?q=...   Semantic candidate search
POST   /api/v1/chat/message              RAG copilot chat (SSE stream)
```

---

## 🤖 AI Features Deep Dive

### Scoring Engine (5 Dimensions)
```
Skill Match        35% — Required + preferred skills overlap
Experience Match   30% — Years + role relevance
Domain Match       20% — Industry/domain alignment
Education Match    10% — Degree relevance
Certification Match 5% — Relevant certifications

Overall = Σ (score × weight)  [0–100]
```

### Prompt Engineering
All prompts are in `apps/api/src/infrastructure/ai/prompts/`:
- `resume_parse.txt` — Extracts structured JSON from raw resume text
- `candidate_score.txt` — Evaluates candidate against JD (5 dimensions)
- `summary_generate.txt` — Generates professional 3-5 sentence summary
- `question_generate.txt` — Creates 8 targeted interview questions

### Model Configuration
```python
LLM:       GPT-4o, temperature=0.2, response_format=json_object
Embedding: text-embedding-3-large, dimensions=3072
Fallback:  Claude 3.5 Sonnet → Gemini 1.5 Pro
Retry:     Exponential backoff (1s→2s→4s, max 3 attempts)
Cache:     Redis, TTL=24h per (candidate_id, job_id, model_version)
```

---

## ⚙️ Make Commands

```bash
make help           # Show all commands
make up             # Start full Docker stack
make up-db          # Start only Postgres + Redis
make down           # Stop all containers
make dev-api        # FastAPI with hot reload (:8000)
make dev-web        # Next.js dev server (:3000)
make dev-worker     # SQS resume processing worker
make migrate        # Run Alembic migrations
make migrate-create name=add_table  # Create new migration
make test-api       # Run pytest (with coverage)
make test-web       # Run Vitest
make lint-api       # ruff check + mypy
make format-api     # ruff format
make psql           # Open psql in DB container
```

---

## 🔒 Security

- **Authentication**: JWT (HS256), 15-min access tokens, 7-day refresh via HttpOnly cookie
- **Authorization**: RBAC — Admin, Recruiter, Hiring Manager with permission guards per endpoint
- **Data**: TLS in transit, AES-256 at rest (RDS + S3), all secrets in AWS Secrets Manager
- **PII Protection**: Candidate names/emails/phones never logged — only entity IDs
- **File Validation**: MIME type + magic bytes validation (not just extension)
- **Rate Limiting**: Redis-based per-user limits (AI: 60/min, Upload: 10/min, Chat: 20/min)
- **S3 Access**: Pre-signed URLs only (TTL: 1 hour) — no public bucket access

---

## 📊 Performance Targets

| Operation | P95 Target |
|---|---|
| API response (non-AI) | < 200ms |
| Candidate search (semantic) | < 2s |
| Resume processing (async) | < 10s |
| AI scoring | < 15s |
| Chat first token | < 1s |

---

## 🗺️ Roadmap

### Phase 1 — MVP (Current)
- [x] Job creation with JD embedding
- [x] Resume upload (PDF/DOCX + OCR fallback)
- [x] Semantic parsing with GPT-4o
- [x] 5-dimension AI scoring engine
- [x] Candidate ranking dashboard
- [x] AI summary generation (streaming)
- [x] Interview question generation
- [x] Skill gap analysis
- [x] RAG recruiter copilot chat
- [x] RBAC authentication

### Phase 2 — Planned
- [ ] LinkedIn profile import
- [ ] GitHub activity analysis
- [ ] Candidate self-service portal
- [ ] Email automation (shortlist notifications)
- [ ] Resume fraud detection
- [ ] AI salary prediction

### Phase 3 — Future
- [ ] Voice interview agent
- [ ] AI mock interview simulator
- [ ] Automated interview evaluation
- [ ] Offer recommendation engine

---

## 🤝 Contributing

```bash
# Fork, clone, create branch
git checkout -b feat/your-feature

# Make changes following CLAUDE.md conventions
# Run tests
make test

# Lint and format
make lint-api && make format-api

# Submit PR
git push origin feat/your-feature
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

**Built with FastAPI · Next.js · OpenAI · Pinecone · PostgreSQL · AWS**

*Reducing recruiter effort by 80% with semantic AI matching*

⭐ Star this repo if you find it useful!

</div>
