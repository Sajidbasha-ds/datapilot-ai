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
- **Tree Ensembles (Random Forest, Gradient Boosting)**: Evaluated via mean decrease in impurity (Gini importance for classification, variance reduction for regression).
- **Generalized Linear Models (Logistic, Ridge)**: Normalized absolute magnitude of coefficient weights $|w_j|$ after feature standardization.
