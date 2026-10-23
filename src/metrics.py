import pandas as pd


QUALITY_COLUMNS = ["groundedness", "citation_score", "insight_quality", "retail_clarity"]
RELIABILITY_COLUMNS = ["request_success", "structured_output", "consistent_output"]


def build_model_summary(results: pd.DataFrame) -> pd.DataFrame:
    frame = results.copy()
    frame["quality_row"] = frame[QUALITY_COLUMNS].mean(axis=1)
    frame["acceptable"] = (
        (frame["quality_row"] >= 0.75)
        & (frame["critical_error"] == 0)
        & (frame["unsafe_response"] == 0)
        & (frame["request_success"] == 1)
    )

    rows = []
    for model, group in frame.groupby("model"):
        accepted = int(group["acceptable"].sum())
        total_cost = float(group["cost_usd"].sum())
        rows.append({
            "model": model,
            "quality_score": group["quality_row"].mean() * 100,
            "acceptable_answer_rate": group["acceptable"].mean() * 100,
            "critical_error_rate": group["critical_error"].mean() * 100,
            "unsupported_claim_rate": group["unsupported_claim"].mean() * 100,
            "unsafe_response_rate": group["unsafe_response"].mean() * 100,
            "average_cost_usd": group["cost_usd"].mean(),
            "cost_per_acceptable": total_cost / accepted if accepted else float("inf"),
            "average_latency_ms": group["latency_ms"].mean(),
            "p95_latency_ms": group["latency_ms"].quantile(0.95),
            "reliability_score": group[RELIABILITY_COLUMNS].mean(axis=1).mean() * 100,
        })
    return pd.DataFrame(rows).set_index("model")


def category_quality(results: pd.DataFrame) -> pd.DataFrame:
    frame = results.copy()
    frame["quality_score"] = frame[QUALITY_COLUMNS].mean(axis=1) * 100
    return frame.groupby(["model", "category"], as_index=False)["quality_score"].mean()


def failure_rows(results: pd.DataFrame, gold: pd.DataFrame, model: str) -> pd.DataFrame:
    selected = results.loc[(results["model"] == model) & (results["status"] == "fail")]
    return selected.merge(gold, on=["question_id", "category"], how="left")

