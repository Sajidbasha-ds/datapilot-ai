# Source Code Modules Reference — DataPilot AI

| Module | Primary Responsibilities | Key Functions / Classes |
| :--- | :--- | :--- |
| `src/data_loader.py` | CSV/Excel file loading, buffer extraction, size validation, encoding fallback. | `load_dataset()`, `get_file_metadata()` |
| `src/profiler.py` | Statistical profiling, dtype categorization, zero-variance and ID column flagging. | `profile_dataset()` |
| `src/cleaner.py` | Imputation strategy recommendations, duplicate detection, Tukey IQR outlier capping. | `analyze_data_quality()`, `clean_dataset()` |
| `src/eda.py` | Plotly interactive chart generators (Histograms, KDE, Correlation Heatmaps, Scatters). | `plot_numerical_distribution()`, `plot_correlation_heatmap()` |
| `src/statistics.py` | Descriptive statistics, Pearson/Spearman p-values, Welch's t-test, Chi-square. | `compute_descriptive_stats()`, `run_hypothesis_test()` |
| `src/target_detector.py` | Heuristic scoring of target candidates via semantic regex and positional biases. | `detect_target_column()` |
| `src/problem_detector.py` | Problem formulation analysis (Binary, Multiclass, Regression, Unsupervised). | `detect_problem_type()` |
| `src/feature_engineering.py` | Training-partition preprocessing, heuristic feature screening, and cyclical calendar features. | `build_preprocessing_pipeline()`, `filter_suspicious_features()` |
| `src/model_selector.py` | Dynamic algorithm registry and parameter selection for laptops. | `get_candidate_models()`, `get_model_descriptions()` |
| `src/model_trainer.py` | Stratified K-fold CV, train/test split, model fitting, and leaderboard ranking. | `train_supervised_models()`, `train_unsupervised_models()` |
| `src/evaluator.py` | Metric calculations (Accuracy, F1, ROC-AUC, RMSE, R2, Silhouette Score). | `evaluate_classification_model()`, `evaluate_regression_model()` |
| `src/predictor.py` | Single dynamic form inference and batch CSV file scoring. | `predict_single()`, `predict_batch()` |
| `src/insights.py` | Deterministic natural-language findings and "Ask DataPilot" chatbot engine. | `generate_automated_insights()`, `answer_datapilot_query()` |
| `src/database.py` | SQLite prediction persistence, query retrieval, and audit trail purge. | `init_db()`, `log_prediction()`, `get_prediction_history()` |
| `src/report_generator.py` | ReportLab executive multi-page PDF generation. | `generate_pdf_report()` |
