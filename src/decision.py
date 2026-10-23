import pandas as pd


def recommend(summary: pd.DataFrame) -> dict[str, str]:
    baseline = summary.loc["Current Model"]
    candidate = summary.loc["Candidate Model"]

    risk_increased = (
        candidate.critical_error_rate > baseline.critical_error_rate
        or candidate.unsafe_response_rate > baseline.unsafe_response_rate
    )
    if risk_increased:
        if candidate.quality_score >= baseline.quality_score - 3 and candidate.cost_per_acceptable < baseline.cost_per_acceptable:
            return {
                "recommendation": "USE SELECTIVELY",
                "reason": "The candidate improves cost efficiency, but its higher critical-risk rate prevents full promotion. Restrict it to lower-risk scenarios until the failing category improves.",
            }
        return {
            "recommendation": "REJECT",
            "reason": "The candidate increases critical risk without enough quality or cost benefit.",
        }

    if (
        candidate.quality_score >= baseline.quality_score
        and candidate.cost_per_acceptable <= baseline.cost_per_acceptable
        and candidate.reliability_score >= 95
    ):
        return {
            "recommendation": "PROMOTE",
            "reason": "The candidate meets risk gates and improves the quality-cost tradeoff without reducing reliability.",
        }

    return {
        "recommendation": "HOLD",
        "reason": "The candidate passes critical risk gates, but the overall quality, cost, latency, and reliability tradeoff remains inconclusive.",
    }

