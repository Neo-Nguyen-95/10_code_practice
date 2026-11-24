# Phase 6 — Data science & machine learning

**Dates:** 2028-02-07 → 2028-04-16 (W63–W72) · **Buffer:** W73, 2028-04-17 → 2028-04-23
**Prerequisites:** Phase 5 (warehouse marts), Statistics thread from Phase 3 · [← Phase 5](05-data-engineering.md) · [Learning path](../learning-path.md) · [Next: Phase 7 →](07-ai-engineering.md)

## Goal

Turn my analyst experience into solid data-science foundations: probability and inference, experiment design, the linear algebra behind models, and classical ML done properly (validation, leakage, calibration). I also learn to ship models, not just notebooks.

QuizLab gives me a rare advantage. The Phase 2 seed data was generated from **hidden ground-truth** student ability and question difficulty, so I can check whether my models actually recover the truth.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | Probability, distributions, expectation, CLT | [Think Stats 3e](https://greenteapress.com/wp/think-stats-3e/) ch. 1–5 + StatQuest | Simulate the CLT in a notebook |
| 2 | Inference: estimation, confidence intervals, hypothesis tests, bootstrap | Think Stats inference chapters + StatQuest "p-values" | When to bootstrap vs use a formula |
| 3 | Experiment design & A/B testing: randomization, power, sample size, peeking, guardrail metrics | Kohavi et al., *Trustworthy Online Controlled Experiments* ch. 1–3 | A/B test plan template |
| 4 | Linear algebra for ML; gradient descent; maximum likelihood | [3Blue1Brown: Essence of linear algebra](https://www.3blue1brown.com/topics/linear-algebra) ch. 1–7 + [ISLP](https://www.statlearning.com/) ch. 3 | Derive the gradient of logistic loss |
| 5 | Classification: logistic regression; **Item Response Theory (Rasch/2PL) as logistic regression** | ISLP ch. 4 + a Rasch model tutorial | Explain IRT difficulty vs raw % correct |
| 6 | Model evaluation: cross-validation, grouped CV, metrics (AUC, log loss), calibration, leakage | ISLP ch. 5 + *Hands-On ML* (Géron) ch. 2–3 | Leakage traps in student data |
| 7 | Trees, random forests, gradient boosting; knowledge tracing (BKT) | ISLP ch. 8 + *Hands-On ML* ch. 6–7 + [pyBKT](https://github.com/CAHLR/pyBKT) README | Boosting vs bagging in one paragraph |
| 8 | ML lifecycle: experiment tracking, model registry, reproducibility | Chip Huyen, *Designing Machine Learning Systems* ch. 6 + [MLflow docs](https://mlflow.org/docs/latest/) | My model-versioning rules |
| 9 | Unsupervised: clustering, PCA | ISLP ch. 12 | When clustering results are meaningless |
| 10 | Production ML: serving, training/serving skew, drift, monitoring | *Designing ML Systems* ch. 7–8 | Drift monitoring plan |

## Project track (in `quizlab/ml/`)

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | EDA on warehouse marts: accuracy, time-on-question, sessions; simulate CLT on real metrics | `ml/notebooks/01_eda.ipynb` | Analysis, viz |
| 2 | Bootstrap CIs for topic accuracy; compare classes with correct tests; written findings | `docs/ml-report.md` §1 | Inference |
| 3 | **A/B test:** feature flag for a "hint" button in the API; random assignment logged as an event; power analysis; simulate traffic; pre-registered analysis | `docs/ml-report.md` §2 | Experimentation |
| 4 | **Rasch IRT from scratch** in NumPy (MLE + gradient descent); check it recovers the hidden seed difficulty (correlation plot) | `ml/irt/rasch.py` + tests | Linear algebra, MLE |
| 5 | Compare with `statsmodels` logistic regression and a 2PL library fit; write `difficulty_irt` back to `questions` | Difficulty column populated | Modeling |
| 6 | **Mastery model:** dbt feature mart → predict P(correct on next attempt); logistic baseline; GroupKFold by student | `ml/mastery/train.py` | Features, validation |
| 7 | Gradient boosting (LightGBM); BKT baseline (pyBKT); calibration curves; SHAP explanations | Model comparison table | Ensembles |
| 8 | MLflow tracking + model registry; Airflow DAG retrains weekly from the warehouse | `dags/train_mastery.py` | MLOps basics |
| 9 | Serve the registered model in the API: `GET /students/{id}/mastery`; student clustering into learning profiles | Endpoint + profiles | Serving |
| 10 | **Teacher dashboard** (Streamlit): class mastery heatmap, struggling topics, question difficulty, A/B result; weekly drift job (PSI); tag `v0.6.0` | `dashboard/` + final ML report | Viz, monitoring |

## Done when

- [ ] I can design an A/B test with a power calculation and explain the common pitfalls.
- [ ] I can derive and implement logistic regression / Rasch by hand.
- [ ] I can explain why GroupKFold is needed for student data.
- [ ] IRT difficulty recovers the hidden truth (r ≥ 0.9 on seed data).
- [ ] The mastery model is served by the API, retrained by Airflow and tracked in MLflow.
- [ ] Teacher dashboard is deployed (ECS or Streamlit Community Cloud with demo data).

## Threads this phase

- **SQL / DSA:** 1 each per week.
- **Writing:** ADR 0011 (model choice), ADR 0012 (how models are served and versioned).

## Stretch goals

- Bayesian IRT with PyMC; compare uncertainty estimates.
- Deep knowledge tracing (simple LSTM in PyTorch): a bridge to Phase 7.
- Kaggle: one tabular competition as extra practice.
