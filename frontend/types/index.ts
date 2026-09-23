export interface ApiResponse<T = any> {
  success: boolean;
  data: T | null;
  error?: {
    code: string;
    message: string;
    details?: string;
  } | null;
}

export interface SampleDataset {
  id: string;
  name: string;
  description: string;
  target: string;
  task: string;
  filename: string;
}

export interface ColumnProfile {
  name: string;
  dtype: string;
  missing_count: number;
  missing_pct: number;
  unique_count: number;
  cardinality_ratio: number;
  mean?: number;
  std?: number;
  median?: number;
  min?: number;
  max?: number;
  q25?: number;
  q75?: number;
  skewness?: number;
  kurtosis?: number;
  top_categories?: Record<string, number>;
}

export interface DatasetOverview {
  rows: number;
  columns: number;
  duplicate_rows: number;
  duplicate_pct: number;
  total_cells: number;
  total_missing: number;
  missing_pct: number;
  numerical_columns_count: number;
  categorical_columns_count: number;
  datetime_columns_count: number;
  constant_columns: string[];
  constant_columns_count: number;
  suspicious_columns: Array<{
    column: string;
    reason: string;
    detail: string;
    severity: "low" | "medium" | "high";
  }>;
  suspicious_columns_count: number;
}

export interface ProfileData {
  overview: DatasetOverview;
  columns: ColumnProfile[];
  numerical_cols?: string[];
  categorical_cols?: string[];
  datetime_cols?: string[];
}

export interface QualityIssue {
  type: string;
  title: string;
  description: string;
  severity: "low" | "medium" | "high";
  action?: string;
  column?: string;
}

export interface QualityData {
  total_issues: number;
  issues: QualityIssue[];
  duplicate_count: number;
  missing_recommendations: Record<string, {
    missing_count: number;
    missing_pct: number;
    recommended_strategy: string;
    reason: string;
    is_numerical: boolean;
  }>;
  outlier_summary: Record<string, {
    iqr_outliers: number;
    iqr_pct: number;
    lower_bound: number;
    upper_bound: number;
    z_score_outliers: number;
  }>;
  high_corr_pairs: Array<{
    col1: string;
    col2: string;
    correlation: number;
  }>;
  leakage_candidates: Array<{
    feature: string;
    target: string;
    correlation: number;
  }>;
}

export interface TargetInfo {
  suggested_target: string | null;
  confidence: number;
  reason: string;
  task_candidate?: string;
  candidates?: Array<{
    column: string;
    score: number;
    reason: string;
  }>;
}

export interface DatasetSession {
  session_id: string;
  filename: string;
  rows: number;
  columns: number;
  column_names: string[];
  profile: ProfileData;
  quality: QualityData;
  target_info: TargetInfo;
  target_col: string | null;
  problem_type: string | null;
  problem_type_info?: any;
  is_cleaned?: boolean;
  preview: Record<string, any>[];
}

export interface ModelBenchmarkRow {
  Model: string;
  Accuracy?: number;
  "Precision (Macro)"?: number;
  "Recall (Macro)"?: number;
  "F1-Score (Macro)"?: number;
  "Weighted F1"?: number;
  "ROC-AUC"?: number | null;
  "CV F1 (Train)"?: number;
  "CV Std"?: number;
  MAE?: number;
  MSE?: number;
  RMSE?: number;
  "R²"?: number;
  "Adjusted R²"?: number;
  "CV R² (Train)"?: number;
}

export interface MlBenchmarkResults {
  target_col: string;
  problem_type: string;
  best_model_name: string;
  leaderboard: ModelBenchmarkRow[];
  feature_importance: Array<{
    feature: string;
    importance: number;
  }>;
  n_train: number;
  n_test: number;
  test_size: number;
  cv_folds: number;
  reliability_warning: string | null;
  metric_definitions?: Record<string, string>;
  model_descriptions?: Record<string, string>;
  best_k?: number;
  elbow_table?: Array<{ k: number; Inertia: number; "Silhouette Score": number }>;
  pca_variance?: number[];
  pca_points?: Array<{ pca_1: number; pca_2: number; cluster: string }>;
}

export interface PredictionSchema {
  model_name: string;
  target_col: string;
  problem_type: string;
  fields: Array<{
    name: string;
    type: "number" | "select";
    default: any;
    min?: number;
    max?: number;
    options?: string[];
  }>;
}

export interface SinglePredictionResult {
  prediction: any;
  confidence: number | null;
  probabilities: Record<string, number>;
  log_id: number;
}

export interface BatchPredictionResult {
  total_rows: number;
  summary: Record<string, any>;
  preview: Record<string, any>[];
  csv_data: string;
}

export interface AiInsightsData {
  executive_insights: string[];
  technical_insights: string[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}
