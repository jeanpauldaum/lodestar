# Lodestar Architecture

A technical walkthrough of Lodestar's four-layer pipeline: from user query to implementation blueprint.

---

## Overview

Lodestar converts a two-parameter input (city + domain) into a structured implementation blueprint through four sequential layers:

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER QUERY                               │
│         city="Lagos"  domain="housing"  country="Nigeria"        │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                                │
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │ seed_policies   │  │  World Bank API  │  │  FRED API     │  │
│  │ .json           │  │  (indicators)    │  │  (economic)   │  │
│  │ 10 curated      │  │  WGI governance  │  │  GDP, housing │  │
│  │ global policies │  │  scores          │  │  indices      │  │
│  └────────┬────────┘  └──────────────────┘  └───────────────┘  │
│           │                                                       │
│  ┌────────▼────────┐  ┌──────────────────────────────────────┐  │
│  │  ChromaDB       │  │  Grok xAI (PolicyScraper)            │  │
│  │  Vector DB      │  │  Live web research via LLM           │  │
│  │  .chroma/       │  │  Recent policy developments          │  │
│  └────────┬────────┘  └──────────────────────────────────────┘  │
└───────────┼─────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                       ENGINE LAYER                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PolicyMatcher (matcher.py)                                │ │
│  │  ─────────────────────────────────────────────────────    │ │
│  │  1. Build rich query string from city + domain + country  │ │
│  │  2. Embed query via ChromaDB default embedding function   │ │
│  │  3. Cosine similarity search across policy knowledge base │ │
│  │  4. Return top-3 matches with similarity scores (0–1)    │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
│                                     │                             │
│  ┌──────────────────────────────────▼─────────────────────────┐ │
│  │  ImpactSimulator (simulator.py)                            │ │
│  │  ─────────────────────────────────────────────────────    │ │
│  │  Input: matched policies + target context + fit score     │ │
│  │  Model: Claude Sonnet 4.6                                 │ │
│  │  Output: 4–6 predicted outcomes with confidence ranges   │ │
│  │          bull case / bear case / recommended pilot        │ │
│  │          resource requirements (budget, staff, partners)  │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
│                                     │                             │
│  ┌──────────────────────────────────▼─────────────────────────┐ │
│  │  RiskAnalyzer (risk.py)                                    │ │
│  │  ─────────────────────────────────────────────────────    │ │
│  │  Base score: 30                                           │ │
│  │  + Cultural gap penalty: (100 - fit_score) × 0.25        │ │
│  │  + Governance penalty: (100 - gov_score) × 0.15          │ │
│  │  + Similarity penalty: (1 - avg_similarity) × 20         │ │
│  │  Domain-specific risk factor overlays                     │ │
│  │  Output: 0–100 score, LOW/MEDIUM/HIGH/CRITICAL level     │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
└──────────────────────────────────────┼──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CULTURE LAYER                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  profiles.py — Country Cultural Dimension Database        │ │
│  │  ─────────────────────────────────────────────────────    │ │
│  │  20+ countries with Hofstede dimensions:                  │ │
│  │  power_distance, individualism, uncertainty_avoidance,    │ │
│  │  long_term_orientation, indulgence, masculinity           │ │
│  │  + institutional_trust, tech_adoption_index,              │ │
│  │    regulatory_quality                                      │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
│                                     │                             │
│  ┌──────────────────────────────────▼─────────────────────────┐ │
│  │  CulturalScorer (scorer.py)                                │ │
│  │  ─────────────────────────────────────────────────────    │ │
│  │  Weights: institutional_trust=0.20, power_distance=0.20  │ │
│  │           long_term_orientation=0.15, individualism=0.15  │ │
│  │           uncertainty_avoidance=0.15, tech_adoption=0.15  │ │
│  │  Formula: sum(|source_dim - target_dim| / 100) × weight   │ │
│  │  Output: score (0–100), grade (A–F), dimension_scores,   │ │
│  │          adaptation_notes, summary                        │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
│                                     │                             │
│  ┌──────────────────────────────────▼─────────────────────────┐ │
│  │  CulturalAdaptor (adaptor.py)                              │ │
│  │  ─────────────────────────────────────────────────────    │ │
│  │  Adaptation level: MINIMAL (75+) / MODERATE (55–75)      │ │
│  │                    SIGNIFICANT (35–55) / FUNDAMENTAL (<35)│ │
│  │  Generates: adapted_elements, implementation_approach,    │ │
│  │             communication_strategy, quick_wins,           │ │
│  │             avoid_list                                     │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
└──────────────────────────────────────┼──────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                       OUTPUT LAYER                               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  schema.py — Pydantic Data Models                         │ │
│  │  LodestarBrief: canonical output type combining all      │ │
│  │  layers. Validated at runtime; serializable to JSON.     │ │
│  └──────────────────────────────────┬─────────────────────────┘ │
│                                     │                             │
│         ┌───────────────────────────┼───────────────────────┐   │
│         │                           │                        │   │
│         ▼                           ▼                        ▼   │
│  ┌─────────────┐           ┌──────────────┐         ┌─────────┐ │
│  │  brief.py   │           │   pdf.py     │         │  API    │ │
│  │  Markdown   │           │  WeasyPrint  │         │ (JSON)  │ │
│  │  generator  │           │  PDF export  │         │ routes  │ │
│  └─────────────┘           └──────────────┘         └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Data Layer (`lodestar/data/`)

The data layer provides the raw material for analysis. It has two modes:

**Static (default):** `seed_policies.json` contains 10 hand-curated global policy successes with structured metadata: key outcomes, prerequisites, cultural context, success factors, failure risks, and data sources. This is the knowledge base from which the engine retrieves analogues.

**Live (optional):** When `GROK_API_KEY` is set, `PolicyScraper` queries Grok xAI with live web search to retrieve recent developments for matched policies. When `WORLD_BANK_API_KEY` is set (not required; World Bank API is open), `WorldBankClient` enriches target country profiles with governance indicators. When `FRED_API_KEY` is set, `FREDClient` provides economic time series data.

**Ingestion:** Before the engine can run, policies must be ingested into ChromaDB:

```bash
lodestar ingest  # or: make ingest
```

This reads `seed_policies.json`, generates embeddings for each policy (using ChromaDB's default embedding function), and stores them in `.chroma/` for subsequent retrieval. Ingestion is idempotent — re-running does not duplicate entries.

---

### Engine Layer (`lodestar/engine/`)

**PolicyMatcher** constructs a rich query string from the user's inputs and performs cosine similarity search against the ChromaDB vector store. The query format:

```
City seeking policy solutions: {city}. Problem domain: {domain}.
Country context: {country}. {context}. Looking for successful {domain}
policies, governance models, and implementation frameworks...
```

This verbose query format is deliberate: it generates embeddings that capture domain-specific semantics rather than just keyword overlap.

**ImpactSimulator** passes the top-3 matched policies, target context, and Cultural Fit Score to Claude Sonnet 4.6 with a structured prompt. The system prompt frames Claude as a senior policy analyst with access to global development data. The output is parsed as structured JSON:

```json
{
  "predicted_outcomes": [
    {
      "outcome": "Housing affordability improvement",
      "value_range": "20-35%",
      "confidence": 0.55,
      "timeline": "5-8 years"
    }
  ],
  "confidence_score": 0.55,
  "resource_requirements": { ... },
  "key_risks": [...],
  "bear_case": "...",
  "bull_case": "...",
  "recommended_pilot": "..."
}
```

**RiskAnalyzer** computes a composite risk score from cultural gap, governance capacity (derived from World Bank WGI scores when available), semantic similarity of the match, and domain-specific risk overlays. Domain risk factors are hardcoded based on known failure modes:
- `housing`: land_tenure, construction_capacity, financing
- `governance`: institutional_capacity, political_continuity, technical_skills
- `urban_mobility`: maintenance_capacity, ridership_assumptions, construction_risk
- etc.

---

### Culture Layer (`lodestar/culture/`)

**Country Profiles** are stored as a dictionary in `profiles.py`, keyed by ISO 3166-1 alpha-2 country codes. Each profile contains Hofstede dimensions (0–100), institutional trust, technology adoption index, and regulatory quality — plus interpretive notes.

Adding a new country profile:

```python
"XX": {
    "name": "Country Name",
    "power_distance": 0,        # 0-100, Hofstede PDI
    "individualism": 0,         # 0-100, Hofstede IDV
    "uncertainty_avoidance": 0, # 0-100, Hofstede UAI
    "long_term_orientation": 0, # 0-100, Hofstede LTO
    "indulgence": 0,            # 0-100, Hofstede IND
    "masculinity": 0,           # 0-100, Hofstede MAS
    "institutional_trust": 0,   # 0-100, composite (WGI + survey data)
    "tech_adoption_index": 0,   # 0-100, ITU Digital Development Index
    "regulatory_quality": 0,    # 0-100, World Bank WGI regulatory quality
    "notes": "..."              # interpretive context
}
```

**Dimension Weights** in `scorer.py`:

```python
DIMENSION_WEIGHTS = {
    "power_distance": 0.20,
    "individualism": 0.15,
    "uncertainty_avoidance": 0.15,
    "long_term_orientation": 0.15,
    "institutional_trust": 0.20,
    "tech_adoption_index": 0.15,
}
```

The `institutional_trust` and `power_distance` dimensions receive the highest weights (0.20 each) because empirical evidence from policy transfer failures shows these two dimensions are most predictive of implementation success or failure.

**Adaptation Notes** are generated automatically when any dimension gap exceeds 20 points. See `scorer.py:_generate_adaptation_note()` for the full note logic.

**CulturalAdaptor** translates the Cultural Fit Score into actionable recommendations. The four adaptation levels map to different design approaches:

| Score Range | Adaptation Level | Implementation Approach |
|-------------|-----------------|------------------------|
| 75–100 | MINIMAL | Direct transfer with minor localization |
| 55–74 | MODERATE | Targeted redesign of specific mechanisms |
| 35–54 | SIGNIFICANT | Core mechanism preserved; governance/finance redesigned |
| 0–34 | FUNDAMENTAL | Principles preserved; full contextual redesign required |

---

### Output Layer (`lodestar/output/`)

**Schema** (`schema.py`) defines the canonical `LodestarBrief` Pydantic model that combines all layer outputs. All fields are validated at runtime. The brief is serializable to JSON for the API and rendered to Markdown or PDF for the CLI.

**Markdown Brief** (`brief.py`) generates publication-ready analysis documents with tables, scenario narratives, and structured recommendations. The format is designed to be readable by both policy audiences (executive summary, adaptation notes) and technical audiences (scores, confidence intervals, data sources).

**PDF Export** (`pdf.py`) uses WeasyPrint to convert the Markdown output to a formatted PDF report with professional typography, page numbers, and print-optimized styling.

---

## API Architecture (`lodestar/api/`)

The REST API wraps the same pipeline used by the CLI:

```
POST /analyze
  → PolicyMatcher.match()
  → CulturalScorer.score()
  → RiskAnalyzer.analyze()
  → ImpactSimulator.simulate()
  → CulturalAdaptor.adapt()
  → LodestarBrief (JSON response)
```

Instances of each service are initialized once at module load and shared across requests (thread-safe for the current single-process deployment):

```python
# lodestar/api/routes.py
embeddings_db = EmbeddingsDB()
matcher = PolicyMatcher(embeddings_db)
scorer = CulturalScorer()
adaptor = CulturalAdaptor()
analyzer = RiskAnalyzer()
```

CORS is set to allow all origins in the current development configuration. Production deployment should restrict this to the frontend origin.

---

## CLI Architecture (`lodestar/cli.py`)

The CLI uses Typer with Rich terminal UI. The `analyze` command runs the full five-stage pipeline with progress spinners and a summary table:

```
Stage 1: Policy Matching        [spinner] → top-3 matches
Stage 2: Cultural Fit Scoring   [spinner] → score + notes
Stage 3: Risk Analysis          [spinner] → risk level
Stage 4: Impact Simulation      [spinner] → outcomes (Claude)
Stage 5: Cultural Adaptation    [spinner] → recommendations
```

The `ingest` command populates the ChromaDB vector database from `seed_policies.json`. This must be run once before `analyze` will work.

---

## Development Setup

```bash
git clone https://github.com/jeanpauldaum/lodestar.git
cd lodestar
make install        # pip install -e ".[dev]"
cp .env.example .env && vim .env  # add API keys
make ingest         # populate ChromaDB
make test           # run 24 unit tests
make api            # start FastAPI on :8000
```

The `.chroma/` directory is created on first ingest and persists across runs. Delete it with `make clean` to reset the vector database.

---

## Testing

Tests are in `tests/` and cover the three core layers:

| File | Tests | Coverage |
|------|-------|---------|
| `test_matcher.py` | 7 | PolicyMatcher, EmbeddingsDB |
| `test_culture.py` | 10 | CulturalScorer, CulturalAdaptor, profiles |
| `test_output.py` | 7 | Schema validation, brief generation |

Run: `make test` or `pytest tests/ -v`

Key test patterns:
- Same-country scoring returns 100 (identity check)
- Known high-fit pairs (DK → SE) score above 80
- Known low-fit pairs (SG → NG on housing) score below 45
- Adaptation level correctly maps to score ranges
- Generated Markdown briefs are non-empty and contain expected fields

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `anthropic` | Claude Sonnet 4.6 for impact simulation |
| `chromadb` | Vector embedding database for policy retrieval |
| `fastapi` + `uvicorn` | REST API server |
| `pydantic` | Data validation and serialization |
| `typer` + `rich` | CLI framework and terminal UI |
| `weasyprint` | PDF report generation |
| `openai` | Grok xAI client (OpenAI-compatible API) |
| `fredapi` + `requests` | Economic data clients |
| `python-dotenv` | Environment variable management |

Full version specifications: `pyproject.toml`
