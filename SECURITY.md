# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public issue
2. Email the maintainer directly or use GitHub's private vulnerability reporting
3. Include steps to reproduce, impact assessment, and any suggested fixes
4. You will receive a response within 72 hours

## Security Model

### Local-First Architecture

Ideanance is designed to run locally. By default:

- **No telemetry** — no data is collected or transmitted
- **No cloud storage** — all data stored in local SQLite database
- **No code execution** — Ideanance evaluates governance policies and generates eval criteria; it never runs or executes agent code
- **LLM calls are explicit** — only made when agents are invoked via the API; no background LLM calls

### Governance Safety

- **Deterministic engine** — the governance engine is pure computation with no LLM calls (<100ms)
- **YAML safe loading** — `yaml.safe_load()` exclusively; no `!!python/object` deserialization
- **Content fencing** — user prompts wrapped in `<user_content>` delimiters before passing to LLM agents
- **PII detection** — 6 regex patterns (email, phone, SSN, credit card, address, DOB) with governance content allowlist
- **Secret scanning** — 10 patterns (API keys, tokens, private keys) block accidental credential leakage
- **Audit trail** — every governance check persisted with verdict, confidence, findings, and evidence

### Authentication

- The REST API supports optional JWT authentication via `ENABLE_AUTH` and `SECRET_KEY` environment variables
- When `ENABLE_AUTH=false` (default), no authentication is enforced — suitable for local development
- **Set `ENABLE_AUTH=true` and a strong `SECRET_KEY` when exposing the API on a network**
- Production auth warnings logged on startup if auth is disabled

### Data Handling

- **SQLite** stores workspaces, projects, governance policies, eval criteria, and wirings
- Database is a local file — no external database connections by default
- Database file stored in `backend/` directory (gitignored)
- **PostgreSQL + pgvector** available for production (configured via `DATABASE_URL`)

### Agent Resilience

- **Kill switches** — `AGENTS_ENABLED=false` disables all LLM agents instantly
- **Circuit breakers** — per-agent failure tracking prevents cascade failures
- **Rate limiting** — configurable per-workspace request limits
- **Cost tracking** — daily cost aggregation with automatic agent shutdown on budget breach

## Dependencies

- All Python dependencies pinned in `uv.lock`
- Frontend dependencies pinned in `pnpm-lock.yaml`
- CI runs on every PR to verify lint, type checks, and tests pass

## Best Practices for Users

- Keep API keys in `.env` files (gitignored) — never commit them
- Set `ENABLE_AUTH=true` when deploying beyond localhost
- Review `CORS_ORIGINS` configuration before network deployment
- Use Docker Compose for isolated deployments

## Security Architecture

The security architecture covers OWASP Agentic AI Top 10 mapping, trust boundaries, and threat modeling. See **[IDEANANCE.md](IDEANANCE.md)** for the full technical reference including the security pipeline, PII detection, and audit trail.
