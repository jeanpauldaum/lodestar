# Lodestar 🌟

> The world's hardest problems have already been solved somewhere.
> Lodestar finds those solutions — and tells you exactly how to adapt them for where you are.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/jeanpauldaum/lodestar?style=social)](https://github.com/jeanpauldaum/lodestar)

---

## Why This Exists

Capitalism is the most powerful resource allocation system ever built — but traditional financial metrics consistently miss the opportunities that emerge from network effects and cross-cultural implementation.

The solutions to most of the world's hardest problems already exist somewhere. Singapore solved urban density. Estonia solved digital governance. Medellín solved urban mobility in a city written off as ungovernable.

None of those solutions traveled. Not because they couldn't work elsewhere — but because nobody built the intelligence layer to adapt them across cultural, regulatory, and institutional contexts.

Lagos doesn't need to rediscover public housing from scratch. São Paulo doesn't need to reinvent digital identity infrastructure. Detroit doesn't need to commission new studies on post-industrial mobility. The blueprints exist. What's been missing is a system that knows which blueprint matches which city, and how to adapt it for where you actually are.

That's Lodestar.

---

## What It Does

**Input:** A city, country, or region + a problem domain (housing / governance / infrastructure / healthcare)

**Output:** A structured implementation blueprint with:
- The 3 most analogous successful models globally
- Cultural Fit Score (0–100) with adaptation notes
- Predicted impact range with confidence intervals
- Risk analysis and failure mode mapping
- Bear case and counterarguments

---

## The Cultural Layer

This is what makes Lodestar different from every other policy AI tool.

An Italian adopts technology differently from a Swede. Lagos has different institutional trust than Singapore. Brazil's mobile penetration changes everything about how Estonia's digital governance model should land there.

Every Lodestar recommendation is filtered through a **Cultural Fit Score** — a composite of institutional trust, technology adoption curves, regulatory environment, and Hofstede cultural dimensions. The score is computed across six weighted dimensions:

| Dimension | Weight | What It Measures |
|-----------|--------|-----------------|
| Institutional Trust | 20% | Faith in government; probability of sustained commitment |
| Power Distance | 20% | Top-down vs. participatory implementation compatibility |
| Long-Term Orientation | 15% | Whether the target culture will sustain a multi-year program |
| Uncertainty Avoidance | 15% | Need for pilots, legal scaffolding, and risk-reduction |
| Individualism | 15% | Community vs. individual benefit framing |
| Tech Adoption Index | 15% | Digital infrastructure and readiness |

Good ideas that ignore culture fail. Lodestar makes blind copy-paste impossible.

---

## Quick Start

### Install

```bash
git clone https://github.com/jeanpauldaum/lodestar.git
cd lodestar
make install
```

### Configure

```bash
cp .env.example .env
# Add your API keys:
# ANTHROPIC_API_KEY=...   (required — powers impact simulation)
# FRED_API_KEY=...        (optional — economic data enrichment)
# GROK_API_KEY=...        (optional — live web research)
```

### Run Your First Analysis

```bash
# Step 1: Ingest the seed policy knowledge base into the vector database
make ingest

# Step 2: Analyze a city and domain
make analyze CITY="Lagos" DOMAIN="housing" COUNTRY="Nigeria"

# Or use the CLI directly
lodestar analyze --city "Detroit" --domain "urban_mobility" --country "US" --output brief.md

# Save as PDF
lodestar analyze --city "São Paulo" --domain "governance" --country "Brazil" --output brief.pdf
```

### Start the API

```bash
make api
# Visit http://localhost:8000/docs for the interactive Swagger UI
```

```bash
# Example API call
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"city": "Lagos", "domain": "housing", "country": "Nigeria"}'
```

### Run Tests

```bash
make test
```

---

## Demo

See `/examples` for pre-generated analysis outputs:

| Analysis | Cultural Fit Score | Key Finding |
|----------|-------------------|-------------|
| [Singapore Public Housing → Lagos](examples/singapore_to_lagos.md) | 34/100 (F) | Land tenure fragmentation and sub-23% institutional trust require fundamental model redesign |
| [Estonia Digital Governance → Brazil](examples/estonia_to_brazil.md) | 41/100 (D) | Mobile-first architecture mandatory; federal structure demands decentralized X-Road variant |
| [Medellín Cable Car → Detroit](examples/medellin_to_detroit.md) | 67/100 (B) | Strong post-industrial resonance; funding model requires public-private restructuring |

---

## Architecture

Lodestar runs a four-layer pipeline from query to implementation blueprint:

```
User Query (City + Domain)
        │
        ▼
┌───────────────────────────────────┐
│         DATA LAYER                │
│  seed_policies.json (10 policies) │
│  World Bank API (indicators)      │
│  FRED API (economic data)         │
│  Grok xAI (live research)         │
└──────────────┬────────────────────┘
               │
               ▼
┌───────────────────────────────────┐
│         ENGINE LAYER              │
│  ChromaDB (vector embeddings)     │  ← Semantic similarity matching
│  PolicyMatcher (top-3 retrieval)  │
│  ImpactSimulator (Claude Sonnet)  │  ← Monte Carlo impact projection
│  RiskAnalyzer (domain scoring)    │
└──────────────┬────────────────────┘
               │
               ▼
┌───────────────────────────────────┐
│        CULTURE LAYER              │
│  20+ country Hofstede profiles    │  ← Cultural dimension database
│  CulturalScorer (0–100 fit score) │  ← Weighted composite scoring
│  CulturalAdaptor (recommendations)│  ← Adaptation recommendations
└──────────────┬────────────────────┘
               │
               ▼
┌───────────────────────────────────┐
│         OUTPUT LAYER              │
│  Pydantic schema validation       │
│  Markdown brief generator         │
│  PDF export (WeasyPrint)          │
│  FastAPI REST endpoints           │
└───────────────────────────────────┘
               │
               ▼
        Implementation Brief
        (Markdown / PDF / JSON)
```

**Key files:**

| Component | Path |
|-----------|------|
| CLI entry point | `lodestar/cli.py` |
| Policy matching | `lodestar/engine/matcher.py` |
| Impact simulation | `lodestar/engine/simulator.py` |
| Cultural scoring | `lodestar/culture/scorer.py` |
| Country profiles | `lodestar/culture/profiles.py` |
| Seed knowledge base | `lodestar/data/seed_policies.json` |
| Output generation | `lodestar/output/brief.py` |
| REST API | `lodestar/api/routes.py` |

Full architecture documentation: [docs/architecture.md](docs/architecture.md)

---

## API

FastAPI endpoints with automatic Swagger documentation at `/docs`:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Status, version, policy count |
| `POST` | `/analyze` | Full analysis pipeline |
| `GET` | `/policies` | List all seeded policies |
| `GET` | `/policies/{id}` | Single policy detail |

Run: `make api` then visit `http://localhost:8000/docs`

**Request schema:**
```json
{
  "city": "Detroit",
  "domain": "urban_mobility",
  "country": "US",
  "context": "Post-industrial city with 25% poverty rate seeking connectivity solutions"
}
```

---

## Contributing

Contributions welcome — especially:

- **New policy cases** — See [docs/adding-policies.md](docs/adding-policies.md) for the schema and submission process
- **Country cultural profiles** — Currently 20+ countries; growing to 80+ in v0.2
- **Domain expansion** — Healthcare, education, climate adaptation not yet in the seed set

```bash
# Fork the repo, then:
git checkout -b feature/add-policy-curitiba-brt
# Edit lodestar/data/seed_policies.json
make test
# Open a PR with your analysis and citations
```

Please include citations for all outcome data. Policy knowledge without sources is useless.

---

## The Bigger Picture

Lodestar is the intelligence layer of a broader thesis: that the world's most valuable untapped resource is successful ideas trapped in the wrong geography.

Every year, cities reinvent solutions that already exist. Every decade, development programs fail because they copy the mechanism without copying the cultural context. Every generation, hard-won institutional knowledge gets lost because there was no system to encode it, match it, and adapt it.

The goal is not a database of policies. It's a system that makes good governance transferable — that turns the scattered institutional knowledge of the 21st century into something that can compound.

---

Built by Jean-Paul Daum · New York, NY · [jeanpauldaum.com](https://jeanpauldaum.com)
