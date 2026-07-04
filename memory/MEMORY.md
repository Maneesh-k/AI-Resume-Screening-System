# AI Hiring Copilot — Project Memory

## Project
- Path: `/Users/maneeshk/Projects/Personal/ai native/AI_Resume_Screening_System`
- Type: Full-stack monorepo (pnpm workspaces + turborepo)
- Status: Foundation implemented (July 2026)

## Structure
```
apps/api/   → FastAPI backend (Python 3.12, Clean Architecture + DDD)
apps/web/   → Next.js 14 frontend (TypeScript, Tailwind, shadcn/ui)
```

## Key Docs
- `CLAUDE.md` — project-wide rules and conventions
- `TRD_AI_Hiring_Copilot.md` — full technical requirements document
- `.env.example` — all required environment variables
- `Makefile` — dev commands (`make up`, `make migrate`, `make dev-api`, etc.)

## Backend
- FastAPI + Clean Architecture layers: domain → application → infrastructure → presentation
- All routes at `/api/v1/` prefix
- Auth: JWT (HS256), 15min access / 7d refresh
- DB: PostgreSQL via SQLAlchemy async + asyncpg
- Vector DB: Pinecone (text-embedding-3-large, 3072 dims)
- AI: OpenAI GPT-4o (scoring, parsing, questions, summaries)
- Queue: AWS SQS → ECS worker processes resumes async
- Cache: Redis for AI response caching (24h TTL)
- Migrations: Alembic (`alembic upgrade head`)
- Key env vars: OPENAI_API_KEY, PINECONE_API_KEY, DATABASE_URL, REDIS_URL

## Frontend
- Next.js 14 App Router, TypeScript strict mode
- Dark theme (CSS variables in `src/styles/globals.css`)
- State: Zustand (auth, candidates), TanStack Query v5 (server state)
- Forms: react-hook-form + zod
- Animations: Framer Motion
- API client: `src/lib/api.ts` (typed fetch wrapper, auto-attaches JWT)
- Query keys: `src/lib/query-keys.ts`

## Route Map (Frontend)
- `/login` → auth
- `/dashboard` → stats overview
- `/jobs` → job list
- `/jobs/create` → create job form
- `/jobs/[jobId]` → job detail + ranked candidates
- `/jobs/[jobId]/candidates/[candidateId]` → candidate detail + AI scores
- `/chat` → streaming RAG copilot

## Resume Processing Flow
1. Upload → S3 → SQS message
2. Worker: text extract (PyMuPDF/docx/OCR) → LLM parse → embed → score → Pinecone upsert → save DB
3. For local dev (no SQS): inline async processing triggered automatically

## User Preferences
- Prefers comprehensive, production-quality implementations
- Wants industry-standard patterns throughout (Clean Arch, DDD, etc.)
- Dark UI theme with glass morphism aesthetic
- No shortcuts or stubs — real working code
