# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# AML Graph Detection

- Goal: detect money laundering in transaction graphs, comparing three approaches: rules vs XGBoost vs GNN
- Python 3.11; code in `src/`, tests in `tests/`, notebooks only for exploration
- Use pytest for tests; run them before every commit
- Never commit data files (`data/` is gitignored)
- The user is learning: explain non-obvious choices in code comments and in your replies
- Key metrics: precision, recall, PR-AUC, false positives at fixed recall
