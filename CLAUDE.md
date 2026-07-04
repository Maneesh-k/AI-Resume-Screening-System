# AI Hiring Copilot — Claude Rules

## Project Overview
AI-powered recruitment platform using FastAPI + Next.js in a pnpm monorepo.
Backend: Clean Architecture + DDD. Frontend: Next.js 14 App Router + shadcn/ui.

## Repository Structure
```
apps/
  api/   → FastAPI backend (Python 3.12, Clean Architecture)
  web/   → Next.js 14 frontend (TypeScript, Tailwind, shadcn/ui)
```

---

## General Principles

- Write production-quality code. No stubs, no TODO comments in shipped code.
- Follow SOLID principles. Prefer composition over inheritance.
- All new logic must be covered by tests.
- Never commit secrets, API keys, or passwords.
- Validate at system boundaries (API inputs, file uploads). Trust internal code.
- Prefer explicit over implicit. Name things clearly.

---

## Backend Rules (apps/api/)

### Architecture
- **Clean Architecture layers** (strict dependency rule: presentation → application → domain ← infrastructure):
  - `domain/` — entities, value objects, repository interfaces. No framework deps.
  - `application/` — use cases, DTOs. Depends only on domain.
  - `infrastructure/` — DB, AI, S3, SQS, Redis. Implements domain interfaces.
  - `presentation/` — FastAPI routers, schemas, middleware. Calls use cases only.
- Never import `infrastructure` from `domain` or `application`.
- Never import `presentation` from any other layer.
- Use cases must be single-responsibility (one file, one class, one `execute()` method).

### Python Style
- Python 3.12. Use `uv` for package management.
- Type hints everywhere. Use `from __future__ import annotations` in every file.
- Pydantic v2 for all schemas/DTOs. Use `model_config = ConfigDict(...)`.
- SQLAlchemy 2.x async. Always use `async with session` patterns.
- `asyncpg` driver for PostgreSQL.
- Prefer `dataclasses` or Pydantic models over plain dicts in domain.
- Use `structlog` for structured JSON logging. Never use `print()`.
- All exceptions must be domain-defined; convert to HTTP errors in presentation layer only.
- Format with `ruff format`. Lint with `ruff check`. Type-check with `mypy --strict`.

### FastAPI Patterns
- All routers in `presentation/api/v1/`. Prefix: `/api/v1/`.
- Use `APIRouter` with tags and prefix.
- Dependency injection via `dependency-injector`. Never instantiate services in routes.
- Use `Depends()` for auth, DB sessions, and service injection.
- Return Pydantic response models. Never return raw dicts.
- HTTP status codes must be explicit (`status_code=201`, etc.).
- Use `HTTPException` only in presentation layer. Domain raises `DomainError` subclasses.

### Database
- All migrations via Alembic. Never modify DB schema manually.
- All table names snake_case, plural (e.g., `candidates`, `candidate_skills`).
- All PKs are UUID v4 (`gen_random_uuid()`).
- Always include `created_at`, `updated_at` timestamps (auto-managed).
- Soft deletes: use `deleted_at` where appropriate instead of hard delete.
- Index foreign keys and frequently queried columns.

### AI / LLM
- All LLM calls go through `infrastructure/ai/openai_client.py`.
- All prompts are in `infrastructure/ai/prompts/*.txt`. Never inline prompts in code.
- Always set `temperature=0.2` for structured/deterministic outputs.
- Always use `response_format={"type": "json_object"}` for parse/score endpoints.
- Implement retry with exponential backoff via `tenacity`. Max 3 retries.
- Cache AI responses in Redis (TTL: 24h for scores, 24h for summaries).
- Streaming responses use `async_generator` + SSE.

### Async & Worker
- All I/O must be async (`await`). No blocking calls in async context.
- CPU-bound work (OCR) runs in `asyncio.run_in_executor`.
- SQS consumer in `src/worker/`. Polled by separate ECS task.
- Worker processes: text extraction → LLM parse → embed → score → store.

### Testing
- `pytest` + `pytest-asyncio` for all tests.
- Unit tests mock all external dependencies (DB, AI, S3).
- Integration tests use `TestClient` + in-memory SQLite or Postgres test DB.
- Test file naming: `test_<module>.py`. Mirror `src/` structure in `tests/`.
- 80% coverage minimum. Run: `pytest --cov=src --cov-report=term-missing`.

---

## Frontend Rules (apps/web/)

### Architecture
- **Next.js 14 App Router** exclusively. Never use `pages/` directory.
- Route groups: `(auth)` for public, `(dashboard)` for protected routes.
- Server Components by default. Use `"use client"` only when needed (interactivity, hooks, browser APIs).
- Co-locate components with routes when used only there. Shared components in `src/components/`.
- API calls from Server Components use fetch with `cache: 'no-store'` or revalidation tags.
- Client-side mutations via TanStack Query mutations + Zustand state updates.

### TypeScript
- `strict: true` in tsconfig. No `any`. Use `unknown` + type guards when needed.
- All API response types defined in `src/types/index.ts`.
- Zod schemas for all form validation. Infer TypeScript types from Zod schemas.
- Path aliases: `@/` maps to `src/`. Use `@/components/...` not `../../components/...`.

### Styling
- Tailwind CSS only. No inline styles. No CSS modules (except `globals.css`).
- Design system: dark theme primary. Use CSS variables defined in `globals.css`.
- Use `cn()` utility (from `@/lib/utils`) for conditional class merging.
- shadcn/ui for all base UI components. Customize via `className` prop.
- Animations via Framer Motion (`motion.*` components, `AnimatePresence`).
- Responsive: mobile-first. All layouts must work on 768px+.
- Color tokens: `--background`, `--foreground`, `--primary`, `--muted`, etc.

### State Management
- **Server state**: TanStack Query v5 (`useQuery`, `useMutation`, `useInfiniteQuery`).
  - Query keys in `src/lib/query-keys.ts`.
  - Centralized query client config in `src/lib/query-client.ts`.
- **Client state**: Zustand stores in `src/stores/`.
  - One store per domain (auth, jobs, candidates, ui).
  - Use `immer` middleware for complex state updates.
- No prop drilling beyond 2 levels. Use context or Zustand.

### Forms
- `react-hook-form` + `@hookform/resolvers/zod` for all forms.
- Never use uncontrolled inputs without react-hook-form.
- Show validation errors inline below fields.
- Disable submit button during submission.

### API Integration
- All API calls through `src/lib/api.ts` (typed fetch wrapper).
- Always handle loading, error, and empty states.
- Streaming (SSE) via `EventSource` or `fetch` with `ReadableStream`.
- Auth token attached to all requests via fetch interceptor.
- On 401: auto-refresh token or redirect to login.

### UX Principles
- Every action must have a loading state (skeleton or spinner).
- Every error must have a user-friendly message (toast or inline).
- Confirm destructive actions with a dialog.
- File uploads: validate type and size client-side before sending.
- Optimistic updates for like/shortlist actions.
- Keyboard navigable. `aria-*` attributes on all interactive elements.

### File Naming
- Components: `PascalCase.tsx` (e.g., `CandidateCard.tsx`).
- Utilities/hooks: `kebab-case.ts` (e.g., `use-candidates.ts`).
- Stores: `<name>.store.ts` (e.g., `auth.store.ts`).
- Types: defined in `src/types/index.ts` or co-located `types.ts`.

---

## Monorepo Rules

- **Package manager**: pnpm workspaces.
- **Task runner**: Turborepo (`turbo.json`).
- Run frontend: `pnpm dev --filter web`.
- Run backend: `make dev` (uvicorn with reload).
- Run all: `docker-compose up`.
- Shared env: `.env` at root, copied to apps as needed.
- Never commit `.env`. Use `.env.example` with all keys (no values).

---

## Git & CI

- Branch naming: `feat/`, `fix/`, `chore/`, `docs/`.
- Commit style: Conventional Commits (`feat: add candidate ranking API`).
- PR must pass: lint + type-check + tests before merge.
- Never force-push to `main`.
- Never skip pre-commit hooks.

---

## Security

- Never log PII (name, email, phone). Log entity IDs only.
- S3 resume access via pre-signed URLs only (TTL: 1 hour).
- All secrets from environment variables. No hardcoded credentials.
- Validate file type via MIME + magic bytes (not just extension).
- Rate limit AI endpoints: 60 req/min per user (Redis-based).
- CORS: allow only the configured frontend origin.
- JWT: RS256, access TTL 15min, refresh TTL 7 days (HttpOnly cookie).

---

## Running the Project

```bash
# Local development (full stack)
docker-compose up

# Backend only
cd apps/api && uvicorn src.main:app --reload --port 8000

# Frontend only
cd apps/web && pnpm dev

# DB migrations
cd apps/api && alembic upgrade head

# Run tests
cd apps/api && pytest
cd apps/web && pnpm test

# Lint & format
cd apps/api && ruff check . && ruff format .
cd apps/web && pnpm lint && pnpm type-check
```
