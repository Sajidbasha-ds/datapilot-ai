import { useMemo } from "react";
import { DatasetSession, MlBenchmarkResults } from "@/types";
import { DataUniverseSnapshot, PipelineStage } from "./types";

const stageDefinitions: Array<Pick<PipelineStage, "id" | "label" | "description">> = [
  { id: "data", label: "DATA", description: "Active dataset loaded" },
  { id: "profile", label: "PROFILE", description: "Schema and distributions" },
  { id: "clean", label: "CLEAN", description: "Quality and cleaning state" },
  { id: "explore", label: "EXPLORE", description: "Interactive data exploration" },
  { id: "statistics", label: "STATISTICS", description: "Statistical analysis" },
  { id: "target", label: "TARGET", description: "Target and problem formulation" },
  { id: "ml", label: "ML", description: "Model benchmarking" },
  { id: "predict", label: "PREDICT", description: "Model inference" },
  { id: "insights", label: "INSIGHTS", description: "Grounded dataset insights" },
  { id: "report", label: "REPORT", description: "Executive report generation" },
];

export function useDataUniverse(
  session: DatasetSession,
  mlResults: MlBenchmarkResults | null,
): DataUniverseSnapshot {
  return useMemo(() => {
    const overview = session.profile.overview;
    const hasModel = Boolean(mlResults);
    const stages: PipelineStage[] = stageDefinitions.map((stage) => {
      const complete =
        stage.id === "data" ||
        stage.id === "profile" ||
        (stage.id === "clean" && session.is_cleaned) ||
        stage.id === "target" && Boolean(session.target_col) ||
        stage.id === "ml" && hasModel ||
        stage.id === "predict" && hasModel;

      return {
        ...stage,
        status: complete ? "complete" : stage.id === "data" ? "active" : "ready",
      };
    });

    return {
      datasetSize: overview.rows,
      columnCount: overview.columns,
      numericColumnCount: overview.numerical_columns_count,
      categoricalColumnCount: overview.categorical_columns_count,
      missingPercentage: overview.missing_pct,
      qualityIssueCount: session.quality.total_issues,
      isCleaned: Boolean(session.is_cleaned),
      targetColumn: session.target_col,
      problemType: session.problem_type,
      hasModel,
      bestModel: mlResults?.best_model_name ?? null,
      candidateCount: mlResults?.leaderboard.length ?? 0,
      stages,
    };
  }, [mlResults, session]);
}
