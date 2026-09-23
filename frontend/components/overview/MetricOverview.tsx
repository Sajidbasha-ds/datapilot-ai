"use client";

import React from "react";
import { Table, Columns, AlertTriangle, ShieldCheck, Target, Cpu, Trophy, Activity } from "lucide-react";
import { DatasetSession, MlBenchmarkResults } from "@/types";

interface MetricOverviewProps {
  session: DatasetSession;
  mlResults: MlBenchmarkResults | null;
}

export const MetricOverview: React.FC<MetricOverviewProps> = ({ session, mlResults }) => {
  const overview = session.profile.overview;
  const quality = session.quality;

  // Compute a clean quality health index (100 - penalties for missing/duplicates/outliers)
  const qualityPenalty = Math.min(
    60,
    overview.missing_pct * 0.8 + overview.duplicate_pct * 1.5 + quality.total_issues * 3
  );
  const healthScore = Math.max(25, Math.round(100 - qualityPenalty));

  const bestModel = mlResults?.best_model_name || "Benchmark Pending";
  const winningRow = mlResults?.leaderboard?.[0];
  let scoreLabel = "Score: N/A";

  if (winningRow) {
    if (winningRow["F1-Score (Macro)"] !== undefined) {
      scoreLabel = `F1: ${(winningRow["F1-Score (Macro)"] * 100).toFixed(1)}% | Acc: ${(
        (winningRow.Accuracy ?? 0) * 100
      ).toFixed(1)}%`;
    } else if (winningRow["R²"] !== undefined) {
      scoreLabel = `R²: ${winningRow["R²"].toFixed(3)} | RMSE: ${winningRow.RMSE?.toFixed(2)}`;
    }
  }

  const cards = [
    {
      label: "Total Rows",
      value: overview.rows.toLocaleString(),
      sub: `${overview.duplicate_rows} duplicates (${overview.duplicate_pct}%)`,
      icon: Table,
      color: "from-blue-500/20 to-indigo-500/10",
      accent: "text-blue-400",
    },
    {
      label: "Features",
      value: overview.columns.toString(),
      sub: `${overview.numerical_columns_count} numeric, ${overview.categorical_columns_count} categorical`,
      icon: Columns,
      color: "from-sky-500/20 to-blue-500/10",
      accent: "text-sky-400",
    },
    {
      label: "Missing Values",
      value: `${overview.total_missing.toLocaleString()}`,
      sub: `${overview.missing_pct}% of matrix cells`,
      icon: AlertTriangle,
      color: overview.total_missing > 0 ? "from-amber-500/20 to-orange-500/10" : "from-emerald-500/20 to-teal-500/10",
      accent: overview.total_missing > 0 ? "text-amber-400" : "text-emerald-400",
    },
    {
      label: "Data Health Score",
      value: `${healthScore}/100`,
      sub: `${quality.total_issues} quality checks flagged`,
      icon: ShieldCheck,
      color: healthScore >= 80 ? "from-emerald-500/20 to-teal-500/10" : "from-amber-500/20 to-orange-500/10",
      accent: healthScore >= 80 ? "text-emerald-400" : "text-amber-400",
    },
    {
      label: "Target Feature",
      value: session.target_col || "Unassigned",
      sub: session.target_info?.confidence ? `Confidence: ${(session.target_info.confidence * 100).toFixed(0)}%` : "Manual or auto",
      icon: Target,
      color: "from-cyan-500/20 to-blue-500/10",
      accent: "text-cyan-400",
    },
    {
      label: "Problem Type",
      value: session.problem_type || "Unsupervised",
      sub: "Auto-detected by target cardinality",
      icon: Activity,
      color: "from-indigo-500/20 to-violet-500/10",
      accent: "text-indigo-400",
    },
    {
      label: "Winning Model",
      value: bestModel,
      sub: mlResults ? `${mlResults.leaderboard.length} candidates evaluated` : "Run ML Lab to train",
      icon: Trophy,
      color: "from-amber-500/20 to-yellow-500/10",
      accent: "text-yellow-400",
    },
    {
      label: "Validation Metric",
      value: mlResults ? scoreLabel : "Awaiting Benchmark",
      sub: mlResults ? `${mlResults.n_test} held-out test rows (${(mlResults.test_size * 100).toFixed(0)}%)` : "Stratified train/test split",
      icon: Cpu,
      color: "from-emerald-500/20 to-green-500/10",
      accent: "text-emerald-400",
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5 my-6">
      {cards.map((c, i) => {
        const Icon = c.icon;
        return (
          <div
            key={i}
            className="p-4 rounded-xl border border-surface-border bg-surface-card hover:border-slate-700/80 transition shadow-sm relative overflow-hidden"
          >
            <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-bl ${c.color} rounded-bl-full pointer-events-none opacity-40`} />
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
                {c.label}
              </span>
              <Icon className={`w-4 h-4 ${c.accent}`} />
            </div>
            <div className="text-xl font-extrabold text-slate-100 truncate" title={c.value}>
              {c.value}
            </div>
            <div className="text-[11px] text-slate-400 mt-1 truncate" title={c.sub}>
              {c.sub}
            </div>
          </div>
        );
      })}
    </div>
  );
};
