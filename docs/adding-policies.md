# Adding Policies to Lodestar

Lodestar's analytical quality is directly proportional to the quality and diversity of its policy knowledge base. This document explains how to add new policy cases to `seed_policies.json`.

---

## Why Policy Quality Matters

The `seed_policies.json` file is the foundation of Lodestar's semantic matching. When a user queries "housing in Lagos," the engine generates an embedding of that query and compares it against embeddings of all policies in the knowledge base. The quality of the match — and therefore the quality of the analysis — depends entirely on how well the policies in the database are described.

A poorly-described policy (vague outcomes, missing prerequisites, no cultural context) will either fail to surface when it should, or surface inappropriately when it shouldn't. Either failure degrades the analysis.

**Standards before submitting a new policy:**
- All `key_outcomes` must be measurable and cited — no vague claims like "improved quality of life"
- All `prerequisites` must be specific conditions, not generic assertions
- All `data_sources` must be real, accessible citations
- The `description` must be dense with domain-specific vocabulary that helps the embedding model identify relevant queries

---

## JSON Schema

Each policy in `seed_policies.json` follows this schema:

```json
{
  "id": "string",
  "name": "string",
  "country": "string",
  "city": "string",
  "domain": "string",
  "year_start": "integer",
  "description": "string",
  "key_outcomes": ["string"],
  "prerequisites": ["string"],
  "cultural_context": {
    "power_distance": "integer",
    "individualism": "integer",
    "uncertainty_avoidance": "integer",
    "collectivism_notes": "string"
  },
  "success_factors": ["string"],
  "failure_risks": ["string"],
  "data_sources": ["string"]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique snake_case identifier. Example: `curitiba_brt`, `amsterdam_cycling` |
| `name` | string | Yes | Human-readable policy name. Include city and program name. |
| `country` | string | Yes | Country name (full, in English). |
| `city` | string | Yes | Primary city of implementation. Use the originating city, not a secondary rollout. |
| `domain` | string | Yes | One of: `housing`, `governance`, `urban_mobility`, `education`, `infrastructure`, `urban_planning`, `healthcare` |
| `year_start` | integer | Yes | Year the program reached operational scale (not conception/planning year). |
| `description` | string | Yes | 2–4 sentences. Must explain what the program does, how it works, and why it succeeded. Dense with domain vocabulary — this text is embedded and used for semantic matching. |
| `key_outcomes` | string[] | Yes | 3–6 outcomes. Each must be quantified with a specific value, percentage, or measurable indicator. Include the year or timeframe. |
| `prerequisites` | string[] | Yes | 3–5 conditions that must exist for this program to work. Be specific. "Strong governance" is not a prerequisite. "State authority to compulsorily acquire land at below-market rates" is. |
| `cultural_context.power_distance` | integer | Yes | Hofstede PDI score for the source country (0–100). See hofstede-insights.com. |
| `cultural_context.individualism` | integer | Yes | Hofstede IDV score for the source country (0–100). |
| `cultural_context.uncertainty_avoidance` | integer | Yes | Hofstede UAI score for the source country (0–100). |
| `cultural_context.collectivism_notes` | string | Yes | 2–3 sentences explaining how the source country's cultural context shaped implementation. How did cultural values enable or constrain this program? |
| `success_factors` | string[] | Yes | 3–5 specific, non-obvious factors. "Good leadership" is not a success factor. "CPF linkage turned housing into a savings vehicle, generating broad public buy-in" is. |
| `failure_risks` | string[] | Yes | 3–5 known failure modes — ideally drawn from documented cases where similar programs stalled or collapsed. |
| `data_sources` | string[] | Yes | 2–4 citations. Mix of primary sources (government reports, official statistics) and peer-reviewed academic research. Include URLs where available. |

---

## Supported Domains

| Domain | Examples |
|--------|---------|
| `housing` | Public housing programs, rent control, land trust models |
| `governance` | Digital government, participatory budgeting, anti-corruption systems |
| `urban_mobility` | BRT, light rail, cycling infrastructure, cable cars |
| `education` | Curriculum reform, teacher training, early childhood programs |
| `infrastructure` | Water systems, flood defense, energy transition |
| `urban_planning` | Zoning reform, mixed-use development, greening |
| `healthcare` | Universal coverage models, community health systems |

If you're adding a policy in a domain not listed above, open an issue to discuss whether to extend the domain list before submitting.

---

## Example: Adding the Amsterdam Cycling Infrastructure Policy

```json
{
  "id": "amsterdam_cycling",
  "name": "Amsterdam Integrated Cycling Infrastructure",
  "country": "Netherlands",
  "city": "Amsterdam",
  "domain": "urban_mobility",
  "year_start": 1978,
  "description": "Following the 1973 oil crisis and a wave of citizen activism against car-centric urban planning, Amsterdam began a multi-decade program of protected cycling infrastructure: dedicated bike lanes physically separated from motor traffic, priority signaling at intersections, secure parking at transit hubs, and traffic calming in residential areas. By 2020, cycling accounted for 32% of all Amsterdam trips, the highest modal share of any major city globally, achieved at a fraction of the cost of equivalent automotive or transit infrastructure.",
  "key_outcomes": [
    "Cycling modal share reached 32% of all trips by 2020, up from under 10% in the 1970s",
    "Over 500 km of physically protected cycling lanes by 2023, with 99% of Amsterdammers living within 300m of a protected route",
    "Annual cyclist fatalities fell from 40+ per year in the 1970s to under 10 by 2015 despite 3x the cycling volume",
    "Average cycling trip in Amsterdam takes 22% less time than the equivalent car trip during peak hours due to lane prioritization",
    "Health system savings estimated at €200M annually from cycling-related physical activity reductions in cardiovascular disease"
  ],
  "prerequisites": [
    "Flat topography across the metropolitan area (elevation change under 5m across most of Amsterdam) making cycling physically accessible to all age groups",
    "Existing dense urban fabric with short inter-district distances (most destinations reachable within 20 minutes by bike)",
    "Strong municipal governance with authority over street space allocation, able to reduce car lane capacity over sustained business opposition",
    "Cultural openness to cycling as a norm (pre-existing cycling culture from earlier eras provided a baseline)"
  ],
  "cultural_context": {
    "power_distance": 38,
    "individualism": 80,
    "uncertainty_avoidance": 53,
    "collectivism_notes": "Dutch polder model — consensus-seeking governance combined with willingness to subordinate individual convenience to collective urban outcomes — was essential to the sustained political will needed to reallocate road space. Low power distance meant that citizen-led Stop de Kindermoord (Stop the Child Murder) movement directly influenced municipal policy, bypassing technical bureaucracy. High individualism paradoxically supported cycling adoption: the Dutch framed cycling as freedom and autonomy (individual choice), not collective obligation."
  },
  "success_factors": [
    "Physical separation, not paint: Dutch cycling infrastructure uses raised curbs, planters, and grade separation — not painted bike lanes that cars routinely block",
    "Continuous network: investment in closing network gaps so that a cyclist can travel across the city without encountering unprotected sections",
    "Transit integration: secure bike parking at all metro and train stations, free bike repair facilities, and bike-on-train policies created a multimodal commuter system",
    "Traffic calming in residential areas reduced through-traffic speeds to 15–30 km/h, making low-protection routes safe in residential contexts"
  ],
  "failure_risks": [
    "Topography barrier: Amsterdam's flat terrain is the reason cycling is Amsterdam's answer; hilly cities will achieve lower modal share regardless of infrastructure quality",
    "Urban sprawl incompatibility: as cities expand, distances exceed practical cycling range; infrastructure investment must be paired with dense land use planning",
    "E-bike transition is generating new speed conflicts between traditional cyclists and e-bike commuters that existing lane design does not accommodate",
    "Political reversibility: lane reductions faced fierce business opposition in the 1980s; renewed car-centric pressure could undo network investments"
  ],
  "data_sources": [
    "Gemeente Amsterdam, Cycling Facts and Figures (2023): https://www.amsterdam.nl/en/traffic-transport/cycling/",
    "Pucher, J. & Buehler, R. (2008). Making Cycling Irresistible: Lessons from the Netherlands, Denmark and Germany. Transport Reviews, 28(4).",
    "CROW (Dutch cycling expertise center): Design Manual for Bicycle Traffic (2016)",
    "European Cyclists Federation, Cycling Barometer Netherlands (2022)"
  ]
}
```

---

## Submission Process

1. **Fork** the repository on GitHub
2. **Add** your policy entry to `lodestar/data/seed_policies.json` (append to the array)
3. **Run** `make ingest && make test` to verify the policy ingests correctly and all tests pass
4. **Verify** semantic matching: `lodestar analyze --city [analogous city] --domain [domain]` and confirm your policy surfaces in the results
5. **Open a Pull Request** with:
   - A brief explanation of why this policy belongs in the seed set
   - Confirmation that all outcome data is cited to a primary source
   - Any notes about known gaps in the data or limitations of the evidence base

Policy submissions without citations will not be merged. The value of this knowledge base is its reliability, not its volume.

---

## Prioritized Gaps in the Current Knowledge Base

The following domains and regions are underrepresented. Contributions here have the highest marginal impact:

**Underrepresented domains:**
- Healthcare (universal coverage models: Taiwan NHI, Thailand 30-Baht scheme, Rwanda Community-Based Health Insurance)
- Water and sanitation (Singapore NEWater, Singapore ABC Waters, Bogotá water access reform)
- Education at scale (South Korea education reform, Brazil SENAI vocational system, Finland's comprehensive school reform)

**Underrepresented regions:**
- South and Southeast Asia (India, Indonesia, Vietnam, Philippines)
- Middle East and North Africa (Jordan, Morocco, Tunisia)
- East Africa (Kenya, Tanzania, Ethiopia)
- Central America

**Underrepresented failure cases:**
- Chicago public housing (Cabrini-Green) as a counter-case to Vienna Gemeindebau
- UK Right-to-Buy as a cautionary tale for housing privatization
- Bolivia water privatization as a cultural mismatch case study
