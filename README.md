# AML Graph Detection

Detecting money laundering in transaction graphs, comparing three approaches:

1. **Rules**: hand-written heuristics (e.g. structuring, rapid fan-in/fan-out)
2. **XGBoost**: gradient-boosted trees on tabular and graph-derived features
3. **GNN**: graph neural network trained directly on the transaction graph

## Evaluation

Laundering is rare, so accuracy doesn't tell you much. Models are compared on:

- Precision and recall
- PR-AUC
- False positives at a fixed recall (roughly the number of alerts an analyst would have to review)

## Layout

```
src/aml/    library code: loading, graph, rules, features, models
tests/      pytest tests
notebooks/  exploration only
app/        dashboard
results/    metrics tables, charts
data/       datasets (gitignored, never committed)
```

## Setup

Requires Python 3.11.

```bash
brew install python@3.11 libomp   # macOS: libomp is required by xgboost
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```
