# System Architecture — DataPilot AI

## 1. System Overview

**DataPilot AI** is an autonomous machine learning and statistical intelligence engine designed to automate the complete data science lifecycle without black-box opacity or external paid API dependencies.

```
[ Raw CSV / Excel Dataset ]
              │
              ▼
[ Ingestion & Validation (data_loader.py) ]
              │
              ├──► [ Profiling Engine (profiler.py) ]
              ├──► [ Data Quality & Hygiene (cleaner.py) ]
              ├──► [ EDA Visualizer (eda.py) ]
              └──► [ Statistical Engine (statistics.py) ]
              │
              ▼
[ Target & Problem Detector (target_detector.py, problem_detector.py) ]
              │
              ▼
[ Leakage-Free Preprocessing (feature_engineering.py) ]
              │   ├── Fitted exclusively on X_train fold
              │   ├── Imputation (Median / Mode / Unknown)
              │   ├── Categorical OneHotEncoding (handle_unknown='ignore')
              │   └── Standardization (StandardScaler)
              ▼
[ Model Selection & Training (model_selector.py, model_trainer.py) ]
              │   ├── Stratified / K-Fold Cross-Validation
              │   ├── Classification: LogReg, DT, RF, GBDT, KNN
              │   ├── Regression: OLS, Ridge, DT, RF, GBDT
              │   └── Unsupervised: K-Means (Elbow curve) + PCA (2D projection)
              ▼
[ Multi-Metric Evaluation & Comparison (evaluator.py) ]
              │
              ├──► [ Dynamic Inference (predictor.py) ] ──► [ SQLite DB (database.py) ]
              ├──► [ Deterministic Insights & Chatbot (insights.py) ]
              └──► [ Multi-Page PDF Compilation (report_generator.py) ]
```

## 2. Component Design Principles

### A. Strict Data Leakage Isolation
In classical competitive data science and academic projects, data leakage is a fatal design flaw where information from outside the training dataset is used to create the model. In DataPilot AI:
- `train_test_split` occurs **before** any imputers, scalers, or encoders are fit.
- All transformers in `ColumnTransformer` are fitted solely on `X_train` and applied down to `X_test`.

### B. Zero-Hallucination AI Insight Engine
Unlike naive wrappers that forward raw data to external LLMs (which hallucinate numbers or breach privacy), DataPilot AI uses a deterministic statistical rule engine that derives exact numerical conclusions from computed metrics.

### C. State Management
Streamlit `session_state` preserves all loaded data frames, fitted estimators, comparison leaderboards, and user selections across tab navigations without triggering redundant calculations.

### D. Audit Logging
Inference requests are tracked via an embedded SQLite database (`data/datapilot.db`), ensuring an immutable audit trail for compliance and reproducibility.
