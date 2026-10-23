# Prism Model Evaluation Dashboard

An offline proof of concept for deciding whether a candidate AI model should replace
Prism's current model.

The dashboard evaluates five requirements:

1. **Quality** - groundedness, citation validity, insight quality, and retail clarity.
2. **Risk** - critical errors, unsupported claims, and unsafe financial guidance.
3. **Cost** - average request cost and cost per acceptable answer.
4. **Latency** - average and p95 response time.
5. **Reliability** - request success, structured output, and repeatability.

All data and model names are synthetic. No API key or live model access is required.

## Problem

Model selection can become subjective. A candidate may look better in a demo while
introducing critical financial errors, invalid citations, higher cost, or unstable
platform behavior. Prism needs a repeatable way to compare a current model against a
candidate and reach a defensible **Promote, Hold, Use selectively, or Reject** decision.

## What the POC demonstrates

- A versioned golden-dataset structure for Prism-like retail research scenarios.
- Synthetic evaluation results for `Current Model` and `Candidate Model`.
- Hard risk gates separated from averaged performance metrics.
- Quality, risk, cost, latency, and reliability comparisons.
- A failure explorer for reviewing individual evaluation cases.
- A path from synthetic POC to an SME-approved production benchmark.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\generate_synthetic_data.py
streamlit run app.py
```

Run tests:

```powershell
python -m pytest tests -q
```

## Repository structure

```text
app.py                              Streamlit dashboard
data/golden_dataset.csv             Synthetic benchmark definition
data/evaluation_results.csv         Synthetic model outcomes
scripts/generate_synthetic_data.py  Reproducible data generator
src/metrics.py                      Model metric calculations
src/decision.py                     Release recommendation policy
tests/                              Deterministic tests
```

## Golden dataset

Each case defines the scenario, expected behavior, required evidence, risk level, and
evaluation category. Insight questions use required and forbidden claims instead of one
exact prose answer.

The POC includes 20 cases covering factual research, evidence-grounded insight, citation
behavior, ambiguity, missing information, safety, and retail communication.

## Decision policy

Critical risk thresholds act as release gates. Better cost or latency cannot compensate
for additional critical financial errors or unsafe responses.

The synthetic candidate intentionally demonstrates a tradeoff: it is cheaper and faster,
but it has a critical weakness in insight grounding. The dashboard therefore recommends
selective use rather than unconditional promotion.

## Production path

1. Prism's finance SMEs replace or approve the synthetic golden cases.
2. Real model outputs populate the same evaluation-results contract.
3. Human reviewers calibrate groundedness, insight-quality, and safety rubrics.
4. Historical production failures become regression cases.
5. The evaluation runs before model, prompt, retrieval, or policy releases.

## Limitations

- Results are synthetic and do not measure any real model.
- The recommendation demonstrates policy behavior, not a production decision.
- Cost and latency values are illustrative.
- Finance SMEs must approve production gold labels and release thresholds.

This project is an evaluation-system POC and does not provide financial advice.

