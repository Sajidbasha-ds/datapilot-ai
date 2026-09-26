import {
  AiInsightsData,
  ApiResponse,
  BatchPredictionResult,
  ChatMessage,
  DatasetSession,
  MlBenchmarkResults,
  PredictionSchema,
  SampleDataset,
  SinglePredictionResult,
} from "../types";

const API_BASE = "https://datapilot-ai-lnrb.onrender.com";

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errMsg = `Request failed with status ${res.status}`;
    try {
      const json = await res.json();
      if (json.error?.message) errMsg = json.error.message;
    } catch {}
    throw new Error(errMsg);
  }
  const json: ApiResponse<T> = await res.json();
  if (!json.success) {
    throw new Error(json.error?.message || "Operation failed on server");
  }
  return json.data as T;
}

export async function fetchSamples(): Promise<SampleDataset[]> {
  const res = await fetch(`${API_BASE}/api/dataset/samples`);
  return handleResponse<SampleDataset[]>(res);
}

export async function loadSample(sampleId: string): Promise<DatasetSession> {
  const res = await fetch(`${API_BASE}/api/dataset/sample/${sampleId}`);
  return handleResponse<DatasetSession>(res);
}

export async function uploadDataset(file: File): Promise<DatasetSession> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/dataset/upload`, {
    method: "POST",
    body: formData,
  });
  return handleResponse<DatasetSession>(res);
}

export async function fetchSummary(sessionId: string): Promise<DatasetSession> {
  const res = await fetch(`${API_BASE}/api/dataset/summary/${sessionId}`);
  return handleResponse<DatasetSession>(res);
}

export async function updateTarget(
  sessionId: string,
  targetCol: string | null,
  problemType?: string
): Promise<{ target_col: string | null; problem_type: string; quality: any }> {
  const res = await fetch(`${API_BASE}/api/dataset/target`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      target_col: targetCol,
      problem_type: problemType,
    }),
  });
  return handleResponse(res);
}

export async function cleanDataset(
  sessionId: string,
  options: {
    drop_duplicates?: boolean;
    impute_missing?: boolean;
    remove_constant?: boolean;
  }
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/dataset/clean`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      ...options,
    }),
  });
  return handleResponse(res);
}

export async function fetchEdaOptions(sessionId: string): Promise<{
  numerical_columns: string[];
  categorical_columns: string[];
  datetime_columns: string[];
  all_columns: string[];
  target_col: string | null;
  problem_type: string | null;
}> {
  const res = await fetch(`${API_BASE}/api/eda/options/${sessionId}`);
  return handleResponse(res);
}

export async function fetchDistribution(sessionId: string, column: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/eda/distribution`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, column }),
  });
  return handleResponse(res);
}

export async function fetchCorrelation(sessionId: string): Promise<{
  columns: string[];
  matrix: Record<string, any>[];
  plotly: any;
}> {
  const res = await fetch(`${API_BASE}/api/eda/correlation/${sessionId}`);
  return handleResponse(res);
}

export async function fetchScatter(
  sessionId: string,
  xCol: string,
  yCol: string,
  colorCol?: string
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/eda/scatter`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      x_col: xCol,
      y_col: yCol,
      color_col: colorCol,
    }),
  });
  return handleResponse(res);
}

export async function fetchDescriptiveStats(sessionId: string): Promise<Record<string, any>[]> {
  const res = await fetch(`${API_BASE}/api/statistics/descriptive/${sessionId}`);
  return handleResponse(res);
}

export async function fetchPairwiseCorrelation(
  sessionId: string,
  colX: string,
  colY: string
): Promise<any> {
  const res = await fetch(
    `${API_BASE}/api/statistics/pairwise/${sessionId}?col_x=${encodeURIComponent(colX)}&col_y=${encodeURIComponent(colY)}`
  );
  return handleResponse(res);
}

export async function runHypothesisTest(
  sessionId: string,
  col1: string,
  col2: string,
  testType = "auto"
): Promise<any> {
  const res = await fetch(`${API_BASE}/api/statistics/hypothesis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      col1,
      col2,
      test_type: testType,
    }),
  });
  return handleResponse(res);
}

export async function trainModels(
  sessionId: string,
  config: {
    target_col?: string;
    problem_type?: string;
    test_size?: number;
    cv_folds?: number;
  }
): Promise<MlBenchmarkResults> {
  const res = await fetch(`${API_BASE}/api/ml/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      ...config,
    }),
  });
  return handleResponse(res);
}

export async function fetchMlResults(sessionId: string): Promise<MlBenchmarkResults> {
  const res = await fetch(`${API_BASE}/api/ml/results/${sessionId}`);
  return handleResponse(res);
}

export async function fetchPredictionSchema(sessionId: string): Promise<PredictionSchema> {
  const res = await fetch(`${API_BASE}/api/predict/schema/${sessionId}`);
  return handleResponse(res);
}

export async function predictSingle(
  sessionId: string,
  features: Record<string, any>
): Promise<SinglePredictionResult> {
  const res = await fetch(`${API_BASE}/api/predict/single`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      features,
    }),
  });
  return handleResponse(res);
}

export async function predictBatch(
  sessionId: string,
  file: File
): Promise<BatchPredictionResult> {
  const formData = new FormData();
  formData.append("session_id", sessionId);
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/predict/batch`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(res);
}

export async function generateInsights(sessionId: string): Promise<AiInsightsData> {
  const res = await fetch(`${API_BASE}/api/insights/generate/${sessionId}`);
  return handleResponse(res);
}

export async function sendChatMessage(
  sessionId: string,
  message: string
): Promise<{ role: "assistant"; content: string; history: ChatMessage[] }> {
  const res = await fetch(`${API_BASE}/api/insights/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      session_id: sessionId,
      message,
    }),
  });
  return handleResponse(res);
}

export async function generateReport(sessionId: string): Promise<{
  report_filename: string;
  file_size: number;
  generated_at: number;
}> {
  const res = await fetch(`${API_BASE}/api/report/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return handleResponse(res);
}

export function getReportDownloadUrl(sessionId: string): string {
  return `${API_BASE}/api/report/download/${sessionId}`;
}
