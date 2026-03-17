"""
Lodestar CLI entry point.

Provides two commands:
  lodestar ingest   — loads seed_policies.json into ChromaDB
  lodestar analyze  — runs full analysis and outputs a brief
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

load_dotenv()

app = typer.Typer(
    name="lodestar",
    help="AI platform for culturally-adapted global policy intelligence.",
    add_completion=False,
)
console = Console()
logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging level based on verbosity flag."""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )


@app.command()
def ingest(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    Load seed policies from seed_policies.json into ChromaDB.

    This command must be run before 'lodestar analyze' can find any matches.
    Policies are upserted — running multiple times is safe.
    """
    _setup_logging(verbose)
    from lodestar.engine.embeddings import EmbeddingsDB

    seed_path = Path(__file__).parent / "data" / "seed_policies.json"
    if not seed_path.exists():
        console.print(f"[red]Error: seed_policies.json not found at {seed_path}[/red]")
        raise typer.Exit(1)

    console.print(
        Panel.fit(
            "[bold blue]Lodestar[/bold blue] — Policy Ingestion",
            subtitle=f"Loading from {seed_path.name}",
        )
    )

    with open(seed_path) as f:
        policies = json.load(f)

    console.print(f"Found [cyan]{len(policies)}[/cyan] policies to ingest.\n")

    db = EmbeddingsDB()
    db.initialize_db()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Ingesting policies...", total=len(policies))
        for policy in policies:
            progress.update(
                task, description=f"Ingesting: [cyan]{policy['name']}[/cyan]"
            )
            db.add_policy(policy)
            progress.advance(task)

    count = db.collection.count() if db.collection else 0
    console.print(
        f"\n[green]✓ Ingestion complete.[/green] {count} policies in ChromaDB."
    )


@app.command()
def analyze(
    city: str = typer.Option(
        ..., "--city", "-c", help="Target city for analysis (e.g., 'Lagos')"
    ),
    domain: str = typer.Option(
        ...,
        "--domain",
        "-d",
        help="Policy domain: housing, governance, urban_mobility, etc.",
    ),
    country: str = typer.Option(
        "", "--country", help="Target country (improves cultural scoring)"
    ),
    output: str = typer.Option(
        "", "--output", "-o", help="Output file path for Markdown brief"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    Run full Lodestar analysis for a city and domain.

    Performs semantic policy matching, cultural fit scoring, impact simulation,
    risk analysis, and outputs a structured implementation blueprint.

    Examples:
        lodestar analyze --city Lagos --domain housing --country Nigeria
        lodestar analyze --city Detroit --domain urban_mobility --output brief.md
    """
    _setup_logging(verbose)

    from lodestar.culture.adaptor import CulturalAdaptor
    from lodestar.culture.scorer import CulturalScorer
    from lodestar.engine.matcher import PolicyMatcher
    from lodestar.engine.risk import RiskAnalyzer
    from lodestar.engine.simulator import ImpactSimulator
    from lodestar.output.brief import generate_markdown_brief

    console.print(
        Panel.fit(
            "[bold blue]Lodestar[/bold blue] — Policy Intelligence",
            subtitle=f"Analyzing [cyan]{domain}[/cyan] for [cyan]{city}[/cyan]",
        )
    )

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Step 1: Match policies
        task = progress.add_task("Searching global policy database...", total=None)
        matcher = PolicyMatcher()
        matched = matcher.match(city=city, domain=domain, country=country)
        progress.update(
            task, description=f"[green]✓[/green] Found {len(matched)} matching policies"
        )
        progress.stop_task(task)

        if not matched:
            console.print(
                "\n[red]No matching policies found.[/red] Run [bold]lodestar ingest[/bold] first."
            )
            raise typer.Exit(1)

        # Step 2: Cultural fit scoring
        task2 = progress.add_task("Computing Cultural Fit Scores...", total=None)
        scorer = CulturalScorer()
        country_code_map = {
            "nigeria": "NG",
            "brazil": "BR",
            "colombia": "CO",
            "rwanda": "RW",
            "india": "IN",
            "china": "CN",
            "germany": "DE",
            "france": "FR",
            "united states": "US",
            "us": "US",
            "uk": "UK",
            "singapore": "SG",
            "estonia": "EE",
            "netherlands": "NL",
            "finland": "FI",
            "japan": "JP",
            "denmark": "DK",
            "south korea": "KR",
            "uae": "AE",
            "sweden": "SE",
            "lagos": "NG",
            "detroit": "US",
        }
        target_code = country_code_map.get(
            country.lower(), country_code_map.get(city.lower(), "US")
        )

        source_map = {
            "singapore": "SG",
            "estonia": "EE",
            "colombia": "CO",
            "austria": "AT",
            "rwanda": "RW",
            "brazil": "BR",
            "finland": "FI",
            "netherlands": "NL",
            "japan": "JP",
            "denmark": "DK",
            "south korea": "KR",
        }
        cultural_fits = []
        for policy in matched:
            src = source_map.get(policy.get("country", "").lower(), "US")
            try:
                cs = scorer.score(src, target_code)
                cultural_fits.append(cs)
            except ValueError:
                cultural_fits.append(
                    {
                        "score": 50.0,
                        "grade": "C",
                        "source_country": policy.get("country", ""),
                        "target_country": country,
                        "dimension_scores": {},
                        "adaptation_notes": [],
                        "summary": "",
                    }
                )
        progress.update(
            task2, description="[green]✓[/green] Cultural Fit Scores computed"
        )
        progress.stop_task(task2)

        avg_fit = (
            sum(cs["score"] for cs in cultural_fits) / len(cultural_fits)
            if cultural_fits
            else 50.0
        )

        # Step 3: Risk assessment
        task3 = progress.add_task("Running risk analysis...", total=None)
        risk_analyzer = RiskAnalyzer()
        risk = risk_analyzer.analyze(
            matched_policies=matched,
            target_city=city,
            target_country=country,
            domain=domain,
            cultural_fit_score=avg_fit,
        )
        progress.update(task3, description="[green]✓[/green] Risk analysis complete")
        progress.stop_task(task3)

        # Step 4: Impact simulation
        task4 = progress.add_task("Running impact simulation via Claude...", total=None)
        simulation = {}
        try:
            simulator = ImpactSimulator()
            simulation = simulator.simulate(
                matched_policies=matched,
                target_city=city,
                target_country=country,
                domain=domain,
                cultural_fit_score=avg_fit,
            )
            progress.update(
                task4, description="[green]✓[/green] Impact simulation complete"
            )
        except Exception as exc:
            progress.update(
                task4, description=f"[yellow]⚠[/yellow] Simulation skipped: {exc}"
            )
            simulation = {
                "predicted_outcomes": [],
                "confidence_score": 0.0,
                "timeline": "Simulation unavailable (check ANTHROPIC_API_KEY)",
                "resource_requirements": {
                    "estimated_budget_usd": "TBD",
                    "key_staffing": "TBD",
                    "critical_partners": [],
                },
                "key_risks": [],
                "bear_case": "N/A",
                "bull_case": "N/A",
                "recommended_pilot": "N/A",
            }
        progress.stop_task(task4)

        # Step 5: Cultural adaptation
        task5 = progress.add_task("Generating cultural adaptations...", total=None)
        adaptor = CulturalAdaptor()

        seed_path = Path(__file__).parent / "data" / "seed_policies.json"
        seed_lookup: dict[str, dict] = {}
        if seed_path.exists():
            with open(seed_path) as f:
                for p in json.load(f):
                    seed_lookup[p["id"]] = p

        adapted_recs = []
        for i, policy in enumerate(matched):
            full_policy = seed_lookup.get(policy["id"], policy)
            cs = (
                cultural_fits[i]
                if i < len(cultural_fits)
                else {"score": 50.0, "adaptation_notes": []}
            )
            try:
                rec = adaptor.adapt(full_policy, cs, target_code)
                adapted_recs.append(rec)
            except Exception as exc:
                logger.warning("Adaptation failed: %s", exc)
        progress.update(task5, description="[green]✓[/green] Adaptations generated")
        progress.stop_task(task5)

    # Print summary table
    console.print("\n")
    table = Table(
        title="Top Matched Policies", show_header=True, header_style="bold magenta"
    )
    table.add_column("Rank", style="dim", width=5)
    table.add_column("Policy", min_width=30)
    table.add_column("Country", min_width=15)
    table.add_column("Match", min_width=8)
    table.add_column("Cultural Fit", min_width=12)

    for i, policy in enumerate(matched):
        sim_pct = f"{round(policy.get('similarity_score', 0) * 100, 1)}%"
        fit_score = cultural_fits[i]["score"] if i < len(cultural_fits) else 50.0
        fit_grade = cultural_fits[i]["grade"] if i < len(cultural_fits) else "C"
        fit_color = (
            "green" if fit_score >= 65 else "yellow" if fit_score >= 45 else "red"
        )
        table.add_row(
            str(i + 1),
            policy.get("name", ""),
            policy.get("country", ""),
            sim_pct,
            f"[{fit_color}]{fit_score:.0f}/100 ({fit_grade})[/{fit_color}]",
        )
    console.print(table)

    risk_level = risk.get("risk_level", "UNKNOWN")
    risk_colors = {
        "LOW": "green",
        "MEDIUM": "yellow",
        "HIGH": "orange1",
        "CRITICAL": "red",
    }
    risk_color = risk_colors.get(risk_level, "white")
    console.print(
        f"\n[bold]Risk Level:[/bold] [{risk_color}]{risk_level}[/{risk_color}] "
        f"({risk.get('overall_risk_score', 0):.0f}/100)"
    )

    if simulation.get("confidence_score"):
        console.print(
            f"[bold]Simulation Confidence:[/bold] {round(simulation['confidence_score'] * 100)}%"
        )

    # Generate brief
    brief_data = {
        "query_city": city,
        "query_country": country,
        "query_domain": domain,
        "matched_policies": matched,
        "cultural_fit_scores": cultural_fits,
        "simulation": simulation,
        "risk_assessment": risk,
        "adapted_recommendations": adapted_recs,
        "executive_summary": (
            f"Lodestar analysis for {domain.replace('_', ' ')} in {city}, {country}. "
            f"Identified {len(matched)} highly analogous global success cases with strong semantic similarity. "
            f"Cultural Fit Score: {avg_fit:.0f}/100. Risk Level: {risk_level}."
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    markdown_brief = generate_markdown_brief(brief_data)

    if output:
        out_path = Path(output)
        out_path.write_text(markdown_brief)
        console.print(f"\n[green]✓ Brief saved to:[/green] {out_path.resolve()}")
    else:
        console.print("\n" + "─" * 60)
        console.print(markdown_brief)


if __name__ == "__main__":
    app()
