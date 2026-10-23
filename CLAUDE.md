# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# AML Graph Detection

- Goal: detect money laundering in transaction graphs, comparing three approaches: rules vs XGBoost vs GNN
- Python 3.11; code in `src/`, tests in `tests/`, notebooks only for exploration
- Use pytest for tests; run them before every commit
- Never commit data files (`data/` is gitignored)
- The user is learning: explain non-obvious choices in code comments and in your replies
- Key metrics: precision, recall, PR-AUC, false positives at fixed recall
  - Laundering is rare, so never judge a model by accuracy
  - False positives at fixed recall stands in for analyst workload (alerts to review); it is the main operational comparison between approaches
- Model artifacts (`models/`, `*.pt`, `*.pkl`, `mlruns/`) are gitignored: regenerate them from code, don't commit them

## Commands

```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # macOS also needs `brew install libomp` for xgboost
pytest                                   # all tests
pytest tests/test_file.py::test_name     # single test
```
