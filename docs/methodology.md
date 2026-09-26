# Machine Learning & Statistical Methodology — DataPilot AI

## 1. Data Ingestion & Sanitization

DataPilot AI supports comma-separated values (`.csv`) and Microsoft Excel workbooks (`.xlsx`, `.xls`). The loader executes:
- **Encoding Fallback**: Tries UTF-8 decoding; if bytes contain Windows cp1252 or Latin-1 characters, it falls back seamlessly without crashing.
- **Column Sanitization**: Removes leading/trailing spaces and normalizes column headers into clean strings.
- **Date Ingestion**: Automatically detects standard ISO dates (`YYYY-MM-DD`) and converts them to datetime dtypes.

## 2. Statistical Metrics & Formulations

### Skewness (Fisher-Pearson 3rd Moment)
$$g_1 = \frac{\frac{1}{n} \sum_{i=1}^n (x_i - \bar{x})^3}{\left(\frac{1}{n} \sum_{i=1}^n (x_i - \bar{x})^2\right)^{3/2}}$$
Used to determine whether median or mean imputation is appropriate. If $|g_1| > 1.0$, distribution is asymmetric and median is chosen.

### Outlier Detection (Tukey's Fences)
$$\text{IQR} = Q_3 - Q_1$$
$$\text{Lower Fence} = Q_1 - 1.5 \times \text{IQR}, \quad \text{Upper Fence} = Q_3 + 1.5 \times \text{IQR}$$
Points outside these bounds are flagged. Optional Winsorization caps extreme values to fence boundaries.

### Correlation Analysis
- **Pearson's Product-Moment ($r$)**: Measures linear dependency:
  $$r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$$
- **Spearman's Rank Correlation ($\rho$)**: Non-parametric measure of monotonic relationships using rank variables $d_i = R(x_i) - R(y_i)$:
  $$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$

## 3. Supervised Model Evaluation

### Classification Metrics
- **Accuracy**: $\frac{TP + TN}{TP + TN + FP + FN}$
- **Precision (Macro)**: $\frac{1}{K} \sum_{k=1}^K \frac{TP_k}{TP_k + FP_k}$
- **Recall (Macro)**: $\frac{1}{K} \sum_{k=1}^K \frac{TP_k}{TP_k + FN_k}$
- **F1-Score (Macro)**: $2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$

### Regression Metrics
- **Mean Absolute Error (MAE)**: $\frac{1}{n} \sum |y_i - \hat{y}_i|$
- **Root Mean Squared Error (RMSE)**: $\sqrt{\frac{1}{n} \sum (y_i - \hat{y}_i)^2}$
- **Coefficient of Determination ($R^2$)**: $1 - \frac{\sum (y_i - \hat{y}_i)^2}{\sum (y_i - \bar{y})^2}$
- **Adjusted $R^2$**: $1 - \left[\frac{(1 - R^2)(n - 1)}{n - k - 1}\right]$

## 4. Feature Importance Attribution
- **Tree Models (Decision Tree, Random Forest, Gradient Boosting)**: Report the fitted estimator's tree-based feature importance, derived from impurity reduction. This is model-specific and does not establish causation.
- **Logistic Regression**: Report signed coefficients and coefficient strength for the actual transformed features produced by preprocessing. In binary classification, a positive or negative coefficient raises or lowers the model decision score/log-odds for the positive class; coefficient sign is not a real-world causal effect. Multiclass attribution is shown per class, with maximum absolute coefficient used only to rank strength.
- **Other Linear Models**: Report absolute coefficient magnitude in transformed feature space as a model coefficient strength, not as a causal effect.
- **Models without direct attribution (such as K-Nearest Neighbors)**: No feature attribution is fabricated.

## 5. Training Split and Leakage-Risk Checks
- Supervised training separates the outer train/test partitions before feature screening. Constant columns and some high-cardinality ID-like columns are screened using the outer training features.
- Numeric feature/target correlation screening (absolute Pearson $r \geq 0.98$) is applied only for regression, using the full outer training partition. It runs before internal cross-validation, so validation folds can influence this screen and CV scores may be optimistic. Classification does not use this training target-correlation filter.
- Data-quality analysis separately flags numeric feature/target correlations with absolute Pearson $r \geq 0.95$ on the full dataset for review; this is a diagnostic, not an automatic feature-removal step.
- Imputers, scalers, and encoders are fitted within the training partition; the sklearn pipeline refits preprocessing within each CV training fold. Candidate ranking uses CV metrics, and the outer holdout is used for evaluation.
- These controls reduce specific risks but do not establish that all leakage is absent. They do not automatically detect temporal leakage, categorical or semantic post-outcome features, or related records crossing a random train/test split.
