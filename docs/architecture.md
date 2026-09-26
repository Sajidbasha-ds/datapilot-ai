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
[ Training-Split Preprocessing & Feature Screening (feature_engineering.py) ]
              │   ├── Outer split before feature screening
              │   ├── Preprocessing fitted on training partition / CV training folds
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

### A. Training-Split Controls and Leakage Limits
- `train_test_split` occurs before supervised feature screening.
- Constant and heuristic high-cardinality ID-like fields are filtered using the outer training features. For regression only, numeric feature/target correlations with absolute Pearson r >= 0.98 are screened using the outer training partition.
- The separate data-quality report can flag numeric feature/target correlations with absolute Pearson r >= 0.95 on the full dataset; it is diagnostic only and does not remove those features.
- Imputers, scalers, and encoders are fitted on the training partition and refitted inside each CV training fold; the holdout is used for evaluation, while candidate ranking uses CV metrics.
- The regression target-correlation screen runs once before internal CV, so CV folds are not fully isolated from that target-based screen. The pipeline does not automatically detect temporal leakage, categorical or semantic post-outcome fields, or related records crossing a random split. These controls reduce specific risks; they do not prove all leakage is absent.

### B. Zero-Hallucination AI Insight Engine
Unlike naive wrappers that forward raw data to external LLMs (which hallucinate numbers or breach privacy), DataPilot AI uses a deterministic statistical rule engine that derives exact numerical conclusions from computed metrics.

### C. State Management
Streamlit `session_state` preserves all loaded data frames, fitted estimators, comparison leaderboards, and user selections across tab navigations without triggering redundant calculations.

### D. Audit Logging
Inference requests are tracked via an embedded SQLite database (`data/datapilot.db`), ensuring an immutable audit trail for compliance and reproducibility.
