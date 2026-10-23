from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / "src"))

from decision import recommend
from metrics import build_model_summary, category_quality, failure_rows


st.set_page_config(page_title="Prism Model Evaluation", page_icon="◆", layout="wide")
st.markdown(
    """
    <style>
    .block-container {max-width: 1220px; padding-top: 2rem;}
    h1, h2, h3 {letter-spacing: -0.02em;}
    [data-testid="stMetric"] {background: #f4f7fb; border: 1px solid #dce5f1; padding: 14px; border-radius: 10px;}
    .decision {padding: 18px 22px; border-left: 6px solid #2563eb; background: #eff6ff; border-radius: 8px; margin: 12px 0 24px;}
    .caption {color: #53657d; font-size: 0.92rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    results = pd.read_csv(ROOT / "data" / "evaluation_results.csv")
    gold = pd.read_csv(ROOT / "data" / "golden_dataset.csv")
    return results, gold


results, gold = load_data()
summary = build_model_summary(results)
decision = recommend(summary)
baseline = summary.loc["Current Model"]
candidate = summary.loc["Candidate Model"]

st.title("Prism Model Evaluation Dashboard")
st.caption("Synthetic POC · Current Model vs Candidate Model · No live APIs")
st.markdown(
    f"""<div class="decision"><strong>Recommendation: {decision['recommendation']}</strong><br>{decision['reason']}</div>""",
    unsafe_allow_html=True,
)

st.subheader("Executive comparison")
cols = st.columns(5)
cols[0].metric("Quality", f"{candidate.quality_score:.1f}%", f"{candidate.quality_score - baseline.quality_score:+.1f} pp")
cols[1].metric("Critical error rate", f"{candidate.critical_error_rate:.1f}%", f"{candidate.critical_error_rate - baseline.critical_error_rate:+.1f} pp", delta_color="inverse")
cols[2].metric("Cost / acceptable answer", f"${candidate.cost_per_acceptable:.4f}", f"${candidate.cost_per_acceptable - baseline.cost_per_acceptable:+.4f}", delta_color="inverse")
cols[3].metric("p95 latency", f"{candidate.p95_latency_ms:.0f} ms", f"{candidate.p95_latency_ms - baseline.p95_latency_ms:+.0f} ms", delta_color="inverse")
cols[4].metric("Reliability", f"{candidate.reliability_score:.1f}%", f"{candidate.reliability_score - baseline.reliability_score:+.1f} pp")
st.markdown("<p class='caption'>Risk gates remain separate from averaged performance metrics.</p>", unsafe_allow_html=True)

left, right = st.columns([1.2, 1])
with left:
    st.subheader("Quality by category")
    fig = px.bar(
        category_quality(results), x="category", y="quality_score", color="model",
        barmode="group", labels={"category": "", "quality_score": "Average quality score", "model": ""},
        color_discrete_map={"Current Model": "#163b65", "Candidate Model": "#4aa8d8"},
    )
    fig.update_layout(yaxis_range=[0, 100], legend_orientation="h", legend_y=1.12)
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Cost and quality tradeoff")
    tradeoff = summary.reset_index().rename(columns={"index": "model"})
    fig = px.scatter(
        tradeoff, x="cost_per_acceptable", y="quality_score", color="model",
        size="reliability_score", text="model",
        labels={"cost_per_acceptable": "Cost per acceptable answer ($)", "quality_score": "Quality score", "model": ""},
        color_discrete_map={"Current Model": "#163b65", "Candidate Model": "#4aa8d8"},
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Five evaluation requirements")
requirements = pd.DataFrame([
    ["Quality", "Groundedness, citation validity, insight quality, retail clarity"],
    ["Risk", "Critical errors, unsupported claims, unsafe guidance"],
    ["Cost", "Request cost and cost per acceptable answer"],
    ["Latency", "Average and p95 response time"],
    ["Reliability", "Request success, structured output, repeatability"],
], columns=["Requirement", "What Prism measures"])
st.dataframe(requirements, hide_index=True, use_container_width=True)

st.subheader("Failure explorer")
model_filter = st.selectbox("Model", ["Candidate Model", "Current Model"])
failures = failure_rows(results, gold, model_filter)
if failures.empty:
    st.success("No failed cases for this model.")
else:
    selected_id = st.selectbox("Evaluation case", failures["question_id"].tolist())
    selected = failures.loc[failures["question_id"] == selected_id].iloc[0]
    detail_left, detail_right = st.columns(2)
    with detail_left:
        st.markdown("**Question**")
        st.write(selected.question)
        st.markdown("**Expected behavior**")
        st.write(selected.expected_behavior)
        st.markdown("**Required evidence**")
        st.write(selected.required_evidence)
    with detail_right:
        st.markdown("**Observed result**")
        st.write(selected.observed_summary)
        st.markdown("**Failure reason**")
        st.error(selected.failure_reason)
        st.markdown("**Severity**")
        st.write(selected.risk_level)

with st.expander("Methodology and release policy"):
    st.markdown("""
    - Golden cases define expected behavior, evidence, required claims, and forbidden claims.
    - Quality summarizes groundedness, citation validity, insight quality, and retail clarity.
    - Risk gates block unconditional promotion when critical errors or unsafe responses increase.
    - Cost is evaluated per acceptable answer, not only per request.
    - Latency reports average and p95 behavior.
    - Reliability combines request success, structured output, and consistency.
    - All values are synthetic and do not represent real models.
    """)

