# Ideanance — Technical Reference

---

## Architecture

Modular monolith with 7 feature modules, 5 AI agents, and a deterministic governance engine.

```
Backend:  Python 3.12+ / FastAPI / pydantic-ai / SQLAlchemy 2.0 async
Frontend: Next.js 16 / React 19 / Tailwind CSS v4 / shadcn/ui / antd
LLM:      Claude Sonnet 4.6 (primary) → Haiku 4.5 (routing) → GPT-4o (fallback)
Database: SQLite (dev) / PostgreSQL + pgvector (prod)
SSE:      @agenisea/sse-kit 2.0
```

## What's Built

- **2 governance frameworks** — NIST AI RMF (20 policies) + EU AI Act (21 policies)
- **5 governance lenses** — Boundary, Transparency, Accountability, Privacy, Dignity with strict-dominance synthesizer
- **5 AI agents** — Query Router, Design Advisor, Policy Interpreter, Eval Generator, Export Formatter
- **Governance-as-Code SDK** — `ideanance check design.yml --framework nist-ai-rmf`
- **Multi-framework composition** — conflict detection + cross-framework mapping
- **Custom framework authoring** — create, validate, export/import governance frameworks
- **Template export/import** — share governance frameworks as ZIP packages
- **Security pipeline** — PII detection, secret scanning, composable guard chain, audit trail
- **Governance analytics** — project scores, framework coverage, snapshots
- **Agent resilience** — circuit breakers, 5-level fallback chain, handoff protocol, kill switches

## Modules

| Module | Scope | Key Files |
|--------|-------|-----------|
| **Workspace** | Projects, workspaces | `modules/workspace/` |
| **Governance** | Policies, engine, lenses, composition, conflicts | `modules/governance/` |
| **Design** | Agent/pipeline design artifacts | `modules/design/` |
| **Evaluation** | Eval criteria, wirings, suggestions | `modules/evaluation/` |
| **Agents** | 5 pydantic-ai agents, pipeline, resilience | `modules/agents/` |
| **Export** | Handoff packages, promptfoo, CI workflow | `modules/export/` |
| **Ingestion** | Chunking, embedding, seeding, RAG | `modules/ingestion/` |
| **Analytics** | Snapshots, scores, coverage | `modules/analytics/` |
| **Templates** | ZIP export/import for framework sharing | `modules/templates/` |

## Governance Engine

Deterministic — no LLM calls. Evaluates design artifacts against structured policy rules. Budget: <100ms.

**Rule types**: `field_present`, `field_min_length`, `field_one_of`, `field_not_empty_list`, `field_matches_pattern`

**5 Governance Lenses**:

| Lens | Evaluates |
|------|-----------|
| Boundary | Scope, risk management, accuracy, robustness |
| Transparency | Documentation, disclosure, interpretability |
| Accountability | Human oversight, audit, record-keeping |
| Privacy | Data minimization, PII, consent |
| Dignity | Non-discrimination, fairness, fundamental rights |

**Synthesizer**: Strict state dominance — BLOCKED > ESCALATE > PROCEED. Confidence = minimum across lenses. Low confidence (<0.4) auto-escalates (honesty rule).

## Agent Pipeline

```
User Prompt → Content Fence → Query Router (Haiku)
    → Handoff Manager → Domain Agent (Sonnet)
    → Governance Filter (deterministic)
    → Cost Tracking → Response
```

**Resilience**: `ResilientExecutor` → `CircuitBreaker` → `FallbackChain` (Primary → Simplified → Template → Cache → HonestError)

**Kill Switches**: `AGENTS_ENABLED=false` disables all agents via env var.

## RAG Pipeline

```
Query → Query Rewriter → Hybrid Search (keyword + pgvector) → RRF Fusion → Context Assembly → Agent
```

**Chunking**: Rule-level (each policy rule is its own chunk with parent_chunk_id). **Embedding**: text-embedding-3-small (1536 dims). **SQLite fallback**: keyword-only (LIKE).

## Security

**Composable pipeline**: `ContentSizeGuard` → `SecretScanGuard` → `PIIDetectionGuard` → `RateLimitGuard`

**PII Detection**: 5 patterns (email, phone, SSN, credit card, gov ID) with governance content allowlist to suppress false positives.

**Audit Trail**: `GovernanceAuditEntry` persists every governance check with verdict, confidence, findings, evidence. 90-day retention.

## API (versioned)

All endpoints under `/api/v1/` via `api_v1_router`. Health at `/health` (root).

| Group | Key Endpoints |
|-------|---------------|
| Workspaces | `POST /workspaces/`, `GET /workspaces/{id}/projects` |
| Governance | `POST /governance/check`, `POST /governance/projects/{id}/activate` |
| Agents | `POST /agents/{id}/run` |
| Analytics | `GET /analytics/projects/{id}/score`, `POST /analytics/projects/{id}/snapshot` |
| Integrations | `POST /integrations/promptfoo/config`, `POST /integrations/ci-workflow` |
| Topology | `POST /topology/evaluate` |
| Templates | `POST /templates/export`, `POST /templates/import` |

## SDK

```bash
pip install ideanance-sdk

# Check a design
ideanance check design.yml --framework nist-ai-rmf --format json

# Strict mode (warnings = failures)
ideanance check design.yml --framework nist-ai-rmf --strict

# CI one-liner
ideanance check design.yml --framework nist-ai-rmf --ci
```

## Development

```bash
# Backend
cd backend && uv sync && uv run uvicorn ideanance.main:app --reload

# Frontend
cd frontend && pnpm install && pnpm dev

# Tests
cd backend && uv run pytest tests/ -v          # 425 tests
cd sdk && uv run pytest tests/ -v              # 12 tests

# Evals
cd backend && uv run python evals/eval_governance.py
cd backend && uv run python evals/eval_lenses.py
cd backend && uv run python evals/eval_citations.py
```

## Configuration

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | — | Claude Sonnet/Haiku agents |
| `OPENAI_API_KEY` | — | text-embedding-3-small embeddings |
| `DATABASE_URL` | `sqlite+aiosqlite:///./ideanance.db` | Database connection |
| `AGENTS_ENABLED` | `true` | Kill switch — set `false` to disable all agents |
| `APP_ENV` | `development` | `production` enables auth warnings |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key |

## Core Axioms

1. **Governance > Velocity** — never ship without governance traceability
2. **Evaluation > Documentation** — eval criteria before agent design
3. **Structured Handoff > Vibe Documents** — machine-readable exports
4. **Constraint Clarity > Feature Breadth** — do fewer things better
5. **Open Source > Control** — MIT, transparent, auditable
