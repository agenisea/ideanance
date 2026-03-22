# Contributing to Ideanance

## Getting Started

```bash
git clone https://github.com/agenisea/ideanance.git
cd ideanance
cp .env.example .env  # Add your API keys
```

## Backend Development

```bash
cd backend
uv sync                                          # Install deps
uv run uvicorn main:app --reload                  # Dev server (port 8000)
uv run pytest tests/ -v                          # Run tests 
uv run ruff check src/ tests/                    # Lint
```

## Frontend Development

```bash
cd frontend
pnpm install                                     # Install deps
pnpm dev                                         # Dev server (port 3000)
pnpm build                                       # Type check + build
```

## SDK Development

```bash
cd sdk
uv sync
uv run pytest tests/ -v                          # Run tests 
```

## Running Evals

```bash
cd backend
uv run python evals/eval_governance.py           # Governance engine accuracy
uv run python evals/eval_lenses.py               # Lens correctness
uv run python evals/eval_citations.py            # Citation fidelity
```

## Code Conventions

- **Line length**: 88 (ruff)
- **Python**: 3.12+, absolute imports, `from __future__ import annotations`
- **Async**: `AsyncSession`, `expire_on_commit=False`, eager loading
- **YAML**: `yaml.safe_load()` exclusively
- **Frontend**: oklch colors only, Geist Sans headings, `@agenisea/sse-kit` for SSE
- **Tests**: pydantic-ai `TestModel`, `ALLOW_MODEL_REQUESTS = False`

## Pull Request Process

1. Create a branch from `main`
2. Make changes
3. Run tests: `uv run pytest tests/ -v`
4. Run lint: `uv run ruff check src/ tests/`
5. Verify frontend builds: `cd frontend && pnpm build`
6. Submit PR with description of what changed and why

## Architecture References

- **[IDEANANCE.md](IDEANANCE.md)** — Full technical reference
- **[SECURITY.md](SECURITY.md)** — Security model + vulnerability reporting
