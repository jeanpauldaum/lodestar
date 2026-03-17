"""
Markdown brief generator for Lodestar analysis outputs.

Converts structured LodestarBrief data into beautifully formatted
Markdown documents suitable for publication and sharing.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def generate_markdown_brief(brief_data: dict[str, Any]) -> str:
    """
    Generate a rich Markdown brief from a LodestarBrief dict.

    Args:
        brief_data: Dict matching the LodestarBrief Pydantic schema.

    Returns:
        Formatted Markdown string ready for file output or display.
    """
    city = brief_data.get("query_city", "Unknown City")
    country = brief_data.get("query_country", "Unknown Country")
    domain = brief_data.get("query_domain", "Unknown Domain")
    generated_at = brief_data.get("generated_at", "")
    domain_display = domain.replace("_", " ").title()

    lines: list[str] = []

    # Header
    lines.extend(
        [
            f"# Lodestar Analysis: {domain_display} in {city}, {country}",
            "",
            f"> **Generated:** {generated_at}  ",
            f"> **Domain:** {domain_display}  ",
            f"> **Target:** {city}, {country}",
            "",
            "---",
            "",
        ]
    )

    # Executive Summary
    exec_summary = brief_data.get("executive_summary", "")
    if exec_summary:
        lines.extend(
            [
                "## Executive Summary",
                "",
                exec_summary,
                "",
                "---",
                "",
            ]
        )

    # Matched Policies
    matched = brief_data.get("matched_policies", [])
    if matched:
        lines.extend(
            [
                "## Top Matched Global Models",
                "",
                "| Rank | Policy | Country | Domain | Year | Match Score |",
                "|------|--------|---------|--------|------|-------------|",
            ]
        )
        for i, policy in enumerate(matched, 1):
            sim_pct = round(policy.get("similarity_score", 0) * 100, 1)
            lines.append(
                f"| {i} | **{policy.get('name', 'Unknown')}** | "
                f"{policy.get('country', '')} | "
                f"{policy.get('domain', '').replace('_', ' ').title()} | "
                f"{policy.get('year_start', '')} | "
                f"{sim_pct}% |"
            )
        lines.extend(["", "---", ""])

    # Cultural Fit Scores
    cultural_scores = brief_data.get("cultural_fit_scores", [])
    if cultural_scores:
        lines.extend(
            [
                "## Cultural Fit Analysis",
                "",
                "| Policy Source | Fit Score | Grade | Key Challenge |",
                "|---------------|-----------|-------|---------------|",
            ]
        )
        for cs in cultural_scores:
            first_note = (cs.get("adaptation_notes") or ["No major gaps identified"])[0]
            short_note = first_note[:80] + "..." if len(first_note) > 80 else first_note
            lines.append(
                f"| {cs.get('source_country', '')} | "
                f"**{cs.get('score', 0):.0f}/100** | "
                f"{cs.get('grade', 'N/A')} | "
                f"{short_note} |"
            )
        lines.extend(["", ""])

        # Detailed adaptation notes for top match
        if cultural_scores and cultural_scores[0].get("adaptation_notes"):
            top = cultural_scores[0]
            lines.extend(
                [
                    f"### Adaptation Notes: {top.get('source_country', '')} → {top.get('target_country', '')}",
                    "",
                    f"**Score:** {top.get('score', 0):.0f}/100 ({top.get('grade', '')})",
                    "",
                    f"_{top.get('summary', '')}_",
                    "",
                ]
            )
            for note in top.get("adaptation_notes", []):
                lines.append(f"- {note}")
            lines.extend(["", "---", ""])

    # Impact Simulation
    simulation = brief_data.get("simulation", {})
    if simulation:
        lines.extend(
            [
                "## Impact Simulation",
                "",
                f"**Overall Confidence:** {round(simulation.get('confidence_score', 0) * 100)}%  ",
                f"**Timeline:** {simulation.get('timeline', 'N/A')}",
                "",
                "### Predicted Outcomes",
                "",
                "| Outcome | Predicted Range | Confidence | Timeline |",
                "|---------|----------------|------------|----------|",
            ]
        )
        for outcome in simulation.get("predicted_outcomes", []):
            conf_pct = round(outcome.get("confidence", 0) * 100)
            lines.append(
                f"| {outcome.get('outcome', '')} | "
                f"{outcome.get('value_range', '')} | "
                f"{conf_pct}% | "
                f"{outcome.get('timeline', '')} |"
            )

        req = simulation.get("resource_requirements", {})
        if req:
            lines.extend(
                [
                    "",
                    "### Resource Requirements",
                    "",
                    f"- **Budget:** {req.get('estimated_budget_usd', 'TBD')}",
                    f"- **Staffing:** {req.get('key_staffing', 'TBD')}",
                    f"- **Key Partners:** {', '.join(req.get('critical_partners', []))}",
                ]
            )

        lines.extend(
            [
                "",
                "### Scenario Analysis",
                "",
                f"**Bull Case (Best):** {simulation.get('bull_case', '')}",
                "",
                f"**Bear Case (Worst):** {simulation.get('bear_case', '')}",
                "",
                f"**Recommended Pilot:** {simulation.get('recommended_pilot', '')}",
                "",
                "---",
                "",
            ]
        )

    # Risk Assessment
    risk = brief_data.get("risk_assessment", {})
    if risk:
        risk_level = risk.get("risk_level", "UNKNOWN")
        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(
            risk_level, "⚪"
        )
        lines.extend(
            [
                "## Risk Assessment",
                "",
                f"**Overall Risk:** {risk_emoji} {risk_level} ({risk.get('overall_risk_score', 0):.0f}/100)",
                "",
            ]
        )

        warnings = risk.get("key_warnings", [])
        if warnings:
            lines.extend(["### Critical Warnings", ""])
            for w in warnings:
                lines.append(f"> ⚠️ {w}")
            lines.append("")

        lines.extend(["### Risk Factors", ""])
        for rf in risk.get("risk_factors", []):
            lines.append(f"- {rf}")

        lines.extend(["", "### Mitigation Strategies", ""])
        for ms in risk.get("mitigation_strategies", []):
            lines.append(f"- {ms}")
        lines.extend(["", "---", ""])

    # Adapted Recommendations
    adapted = brief_data.get("adapted_recommendations", [])
    if adapted:
        lines.extend(["## Culturally-Adapted Recommendations", ""])
        for rec in adapted[:1]:  # Show top recommendation in detail
            lines.extend(
                [
                    f"### {rec.get('original_policy', 'Policy')} → {rec.get('target_country', '')}",
                    "",
                    f"**Adaptation Level:** {rec.get('adaptation_level', '')}  ",
                    f"**Fit Score:** {rec.get('cultural_fit_score', 0):.0f}/100",
                    "",
                    f"**Implementation Approach:** {rec.get('implementation_approach', '')}",
                    "",
                    f"**Communication Strategy:** {rec.get('communication_strategy', '')}",
                    "",
                    f"**Governance Structure:** {rec.get('governance_structure', '')}",
                    "",
                ]
            )
            if rec.get("adapted_elements"):
                lines.extend(["**Specific Adaptations:**", ""])
                for elem in rec["adapted_elements"]:
                    lines.append(f"- {elem}")
                lines.append("")

            if rec.get("quick_wins"):
                lines.extend(["**Quick Wins (0-6 months):**", ""])
                for qw in rec["quick_wins"]:
                    lines.append(f"- {qw}")
                lines.append("")

            if rec.get("avoid_list"):
                lines.extend(["**Do NOT replicate from source model:**", ""])
                for av in rec["avoid_list"]:
                    lines.append(f"- ❌ {av}")
                lines.append("")

    # Footer
    lines.extend(
        [
            "---",
            "",
            "*Generated by [Lodestar](https://github.com/jeanpauldaum/lodestar) — "
            "AI platform for culturally-adapted global policy intelligence.*",
            "",
            "*Built by [Jean-Paul Daum](https://jeanpauldaum.com) · New York, NY*",
        ]
    )

    return "\n".join(lines)
