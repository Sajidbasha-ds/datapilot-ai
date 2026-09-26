# ⚡ DATAPILOT AI — Autonomous AI Data Scientist

[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-red.svg)](https://streamlit.io/)
[![Machine Learning](https://img.shields.io/badge/ML-Scikit--Learn-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-SQLite-lightgrey.svg)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end autonomous Data Science web application built in Python and Streamlit. **DataPilot AI** transforms raw CSV and Excel datasets into statistical profiles, applies training-split preprocessing and targeted leakage-risk checks, trains and compares machine learning algorithms with cross-validation, serves single and batch predictions, generates grounded AI explanations, and compiles executive multi-page PDF reports.

---

## 🌟 Key Capabilities & Highlights

1. **Dataset Ingestion & Validation**: Multi-format ingestion (`.csv`, `.xlsx`, `.xls`) with UTF-8 / Latin-1 encoding fallback, schema validation, and memory footprint analysis.
2. **Automated Profiling Engine**: Instant overview of rows, columns, missing cells, duplicates, cardinality ratios, and suspicious columns (ID columns, zero-variance constant features, high-cardinality nominals).
3. **Data Quality & Cleaning Engine**: Statistical missing value imputation (median for skewed distributions, mode for categoricals), Tukey IQR outlier detection and Winsorization, and collinearity alerts. Original data is never mutated in place.
4. **Exploratory Data Analysis (EDA)**: Interactive 60fps Plotly visualizations — distributions with box-plot margins, category frequencies, annotated Pearson/Spearman heatmaps, and bivariate scatter plots with trendlines.
5. **Statistical Rigor**: Descriptive statistics (Skewness, Kurtosis), hypothesis testing suite (Two-sample Welch's t-test, Mann-Whitney U, Chi-Square test of independence) with strict scientific disclaimers emphasizing that correlation does not imply causation.
6. **Heuristic Target & Problem Formulation**: Semantic regex and positional analysis to suggest target columns; automatically classifies problem type into **Binary Classification**, **Multiclass Classification**, **Regression**, or **Unsupervised Analysis**.
7. **Training-Split Controls**: Supervised training splits before feature screening; preprocessing transformers are fit on training partitions and refit within CV folds. Constant and heuristic ID-like columns are screened, and regression numeric target-correlation screening uses the outer training partition. A separate full-dataset data-quality diagnostic can flag numeric target-correlation candidates for review. These controls reduce specific risks but do not detect every form of leakage; regression screening is not isolated per CV fold.
8. **Automated ML Benchmarking**: Trains multiple candidate algorithms with K-Fold cross-validation:
   - **Classification**: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, K-Nearest Neighbors.
   - **Regression**: Linear Regression (OLS), Ridge Regression (L2), Decision Tree Regressor, Random Forest Regressor, Gradient Boosting Regressor.
   - **Unsupervised**: K-Means Clustering (Elbow Inertia curve) + PCA 2D Dimensionality Reduction.
9. **Inference & Prediction System**: Dynamic schema-generated input forms for real-time single predictions with probability confidence scores, plus batch CSV file scoring with downloadable CSV outputs.
10. **SQLite Audit Trail**: Logs every prediction event with timestamps and model metadata into an embedded SQLite database (`data/datapilot.db`).
11. **Grounded AI Insights & Chatbot**: 100% deterministic, mathematically sound natural-language explanations (Executive & Technical modes), plus an interactive **Ask DataPilot** chatbot answering factual questions about the active dataset with zero hallucination and zero paid API requirement.
12. **Executive PDF Reports**: Generates professional multi-page PDF reports using ReportLab containing dataset metadata, quality findings, model leaderboards, model-appropriate feature attribution, and methodology disclaimers.

---

## 🏛️ System Architecture

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

---

## 📂 Project Structure

```
google workshop/
├── app.py                     # Main Streamlit web application & orchestrator
├── requirements.txt           # Pinned, verified dependencies
├── README.md                  # Complete technical documentation
├── .gitignore                 # Python, venv, cache, db ignore rules
│
├── data/
│   ├── uploads/               # Directory for user-uploaded files
│   ├── sample/                # Verified benchmark datasets
│   │   ├── customer_churn.csv # Binary classification benchmark
│   │   ├── house_prices.csv   # Continuous regression benchmark
│   │   └── student_performance.csv # Grade classification benchmark
│   └── datapilot.db           # SQLite database for prediction audit logs
│
├── docs/                      # Comprehensive College Viva & Technical Documentation
│   ├── architecture.md        # Detailed lifecycle & component architecture
│   ├── methodology.md         # Mathematical basis of all preprocessing and ML metrics
│   ├── modules.md             # API reference of all Python modules
│   └── viva_questions.md      # 21 in-depth viva questions & answers for external defense
│
├── reports/                   # Output folder for generated ReportLab PDF documents
│
├── src/                       # Modular source code
│   ├── __init__.py
│   ├── data_loader.py         # File ingestion, buffer handling, schema validation
│   ├── profiler.py            # Summary statistics, dtypes, suspicious column detection
│   ├── cleaner.py             # Imputation recommendations, deduplication, IQR outlier capping
│   ├── eda.py                 # Interactive Plotly charts (distributions, heatmaps, scatters)
│   ├── statistics.py          # Parametric/non-parametric tests, skewness, Pearson/Spearman p-values
│   ├── target_detector.py     # Heuristic scoring of target candidates
│   ├── problem_detector.py    # Problem formulation (Classification, Regression, Unsupervised)
│   ├── feature_engineering.py # Training-split preprocessing and heuristic screening
│   ├── model_selector.py      # Algorithm registry tailored for responsive execution
│   ├── model_trainer.py       # Stratified K-fold CV, model training, feature attribution
│   ├── evaluator.py           # Multi-metric evaluation (Accuracy, F1, ROC-AUC, RMSE, R2)
│   ├── predictor.py           # Single dynamic form inference and batch CSV scoring
│   ├── insights.py            # Deterministic AI insights and 'Ask DataPilot' chatbot
│   ├── database.py            # SQLite audit trail logging and retrieval
│   └── report_generator.py    # ReportLab executive multi-page PDF generation
│
└── tests/                     # Automated Pytest Suite
    ├── test_data_loader.py    # Ingestion and format validation tests
    ├── test_analysis.py       # Profiler, cleaner, EDA, and statistical tests
    ├── test_ml.py             # Preprocessing pipelines, model training, and metrics tests
    ├── test_database.py       # SQLite database logging and retrieval tests
    └── test_reports.py        # PDF generation validation tests
```

---

## 💻 Installation & Setup (Windows)

### 1. Prerequisites
- Python 3.11, 3.12, or 3.13 installed on Windows.
- Make sure Python is in your PATH.

### 2. Create and Activate Virtual Environment
Open PowerShell in the project directory:

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment on Windows
.venv\Scripts\Activate.ps1
```

*(If you are using the system Python directly, you can run commands with your Python path, e.g. `& "C:\Users\...\python.exe"`).*

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🚀 Running the Application

Launch the Streamlit web dashboard:

```powershell
streamlit run app.py
```

Streamlit will launch locally in your default web browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:

```powershell
pytest tests/ -v
```

All 13 test suites validate file validation, statistical profiling, cleaning, hypothesis testing, target detection, problem classification, model training, cross-validation, single/batch prediction, SQLite logging, and PDF report creation.

---

## 📊 Sample Datasets (Included)

The application includes 3 realistic benchmark datasets located in `data/sample/`:
1. `customer_churn.csv` (Binary Classification): 50 customer profiles with contract type, monthly charges, tenure, and churn status.
2. `house_prices.csv` (Regression): 40 residential properties with square footage, bedrooms, bathrooms, neighborhood, and sale price.
3. `student_performance.csv` (Classification): 30 student records with study hours, attendance rate, parental education, and final grades.

You can load these with 1-click directly from the **Home** tab or **Upload Dataset** tab!

---

## 🎓 College Viva & Presentation Guide

For a 5-minute college presentation or external examiner evaluation:
1. **Minute 1 — Problem & Vision**: Show the **Home** tab and explain the difference between a static dashboard and an autonomous Data Science system.
2. **Minute 2 — Profiling & Hygiene**: Load `customer_churn.csv`. Show the **Data Overview** and **Data Quality** tabs, pointing out the automatic identification of suspicious columns and Tukey IQR outliers.
3. **Minute 3 — Rigorous Statistics & EDA**: Open **EDA** to showcase the interactive Plotly correlation heatmap and **Statistics** to demonstrate Welch's t-test and Pearson p-values.
4. **Minute 4 — ML Benchmarking & Training-Split Controls**: Open **ML Lab**. Point out that preprocessing is fitted on training data and the holdout is reserved for evaluation. Mention that screening reduces specific risks but does not detect every leakage source. Click "Run Automated Model Training", review the comparison leaderboard, and inspect the winning Random Forest model and feature importances.
5. **Minute 5 — Inference & Deliverables**: In **Predictions**, show real-time single prediction with dynamic schema widgets and the SQLite audit trail. Then navigate to **Reports** and generate the multi-page ReportLab PDF.

For 21 comprehensive viva questions with full answers, refer to [docs/viva_questions.md](docs/viva_questions.md).

---

## 📜 License
Released under the open-source MIT License.
