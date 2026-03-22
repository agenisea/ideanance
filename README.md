# Ideanance

**Governance is a design primitive.**

Ideanance is an open-source design workspace where AI governance policies are wired into agent design from day one — not bolted on after.

## Why This Exists

Most AI governance today happens in spreadsheets, PDFs, and compliance reviews — disconnected from the engineers actually building agents. Policies get written, filed, and forgotten. When something goes wrong, the audit trail is a best-effort reconstruction.

Ideanance closes that gap. Governance frameworks become structured data. Evaluation criteria are generated from policy rules, not invented by hand. Every agent design is checked against active policies before it leaves the workspace. The handoff package carries its governance provenance with it.

The bet: if governance is easy to wire in from the start, teams will actually do it.

## How It Works

1. **Activate** a governance framework (NIST AI RMF, EU AI Act, or your own)
2. **Design** agents — 5 governance lenses evaluate every design deterministically in <100ms
3. **Evaluate** — criteria generated directly from the policy rules you activated
4. **Export** — structured handoff packages with full governance provenance

Five lenses run independently, each with its own pattern detection:

| Lens | What It Catches |
|------|----------------|
| **Boundary** | PII leakage, credential exposure, out-of-scope advice |
| **Transparency** | Uncited claims, hidden assumptions, missing contestability |
| **Accountability** | Missing oversight, no escalation path, no answerable human |
| **Privacy** | Data minimization violations, scope creep, excess data collection |
| **Dignity** | Dismissive language, pressure tactics, exclusionary patterns |

Strict state dominance: **BLOCKED > ESCALATE > PROCEED**. Low confidence auto-escalates — the system admits uncertainty rather than guessing.

For the full technical reference — modules, agents, API, SDK, configuration — see **[IDEANANCE.md](IDEANANCE.md)**.

## Documentation

| Document | Audience | What's Inside |
|----------|----------|---------------|
| **[IDEANANCE.md](IDEANANCE.md)** | Architects | Full technical reference — modules, agents, API, SDK |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contributors | Clone-to-PR workflow, testing, conventions |
| **[SECURITY.md](SECURITY.md)** | Security | Vulnerability reporting, threat scope |

## License

[MIT](LICENSE)

---

Built by Patrick Pena, Agenisea 🪼
