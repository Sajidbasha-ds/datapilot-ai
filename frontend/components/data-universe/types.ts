import { DatasetSession, MlBenchmarkResults } from "@/types";

export type PipelineStageId =
  | "data"
  | "profile"
  | "clean"
  | "explore"
  | "statistics"
  | "target"
  | "ml"
  | "predict"
  | "insights"
  | "report";

export type PerformanceMode = "full" | "reduced" | "off";
export type StageStatus = "complete" | "active" | "ready";

export interface PipelineStage {
  id: PipelineStageId;
  label: string;
  description: string;
  status: StageStatus;
}

export interface DataUniverseSnapshot {
  datasetSize: number;
  columnCount: number;
  numericColumnCount: number;
  categoricalColumnCount: number;
  missingPercentage: number;
  qualityIssueCount: number;
  isCleaned: boolean;
  targetColumn: string | null;
  problemType: string | null;
  hasModel: boolean;
  bestModel: string | null;
  candidateCount: number;
  stages: PipelineStage[];
}

export interface DataUniverseProps {
  session: DatasetSession;
  mlResults: MlBenchmarkResults | null;
  performanceMode: PerformanceMode;
  onStageSelect: (stage: PipelineStageId) => void;
}
