"use client";

import React from "react";
import { CheckCircle2, Clock, PlayCircle, AlertCircle, ArrowRight } from "lucide-react";
import { DatasetSession, MlBenchmarkResults } from "@/types";
import { NavTab } from "../layout/Sidebar";

interface PipelineProgressProps {
  session: DatasetSession | null;
  mlResults: MlBenchmarkResults | null;
  onNavigate: (tab: NavTab) => void;
}

export type StepStatus = "not_started" | "ready" | "running" | "complete" | "needs_attention";

interface StepConfig {
  id: NavTab;
  title: string;
  desc: string;
  status: StepStatus;
  statusLabel: string;
}

export const PipelineProgress: React.FC<PipelineProgressProps> = ({
  session,
  mlResults,
  onNavigate,
}) => {
  const steps: StepConfig[] = [
    {
      id: "upload",
      title: "1. Dataset Upload",
      desc: session ? `${session.filename}` : "Upload CSV or XLSX",
      status: session ? "complete" : "ready",
      statusLabel: session ? "Complete" : "Ready",
    },
    {
      id: "profile",
      title: "2. Data Profiling",
      desc: session ? `${session.columns} features profiled` : "Schema & distributions",
      status: session ? "complete" : "not_started",
      statusLabel: session ? "Complete" : "Not started",
    },
    {
      id: "quality",
      title: "3. Quality Audit",
      desc: session
        ? session.quality.total_issues > 0
          ? `${session.quality.total_issues} issues identified`
          : "Zero critical flaws"
        : "Missingness & outliers",
      status: session
        ? session.quality.total_issues > 0
          ? "needs_attention"
          : "complete"
        : "not_started",
      statusLabel: session
        ? session.quality.total_issues > 0
          ? "Needs attention"
          : "Complete"
        : "Not started",
    },
    {
      id: "eda",
      title: "4. Exploratory EDA",
      desc: session ? "Histograms, boxes & correlations" : "Interactive plots",
      status: session ? "ready" : "not_started",
      statusLabel: session ? "Ready" : "Not started",
    },
    {
      id: "statistics",
      title: "5. Statistics",
      desc: session ? "Hypothesis testing & p-values" : "Parametric tests",
      status: session ? "ready" : "not_started",
      statusLabel: session ? "Ready" : "Not started",
    },
    {
      id: "ml",
      title: "6. ML Benchmark",
      desc: mlResults
        ? `Best: ${mlResults.best_model_name}`
        : session
        ? "Train candidate algorithms"
        : "AutoML benchmarking",
      status: mlResults ? "complete" : session ? "ready" : "not_started",
      statusLabel: mlResults ? "Complete" : session ? "Ready" : "Not started",
    },
    {
      id: "predict",
      title: "7. Predictions",
      desc: mlResults ? "Single & batch inference" : "Requires trained model",
      status: mlResults ? "ready" : "not_started",
      statusLabel: mlResults ? "Ready" : "Not started",
    },
    {
      id: "insights",
      title: "8. AI Insights",
      desc: session ? "Executive & technical briefs" : "Dataset intelligence",
      status: session ? "ready" : "not_started",
      statusLabel: session ? "Ready" : "Not started",
    },
    {
      id: "reports",
      title: "9. Executive Report",
      desc: session ? "Downloadable PDF summary" : "Publication summary",
      status: session ? "ready" : "not_started",
      statusLabel: session ? "Ready" : "Not started",
    },
  ];

  const getStatusBadge = (status: StepStatus, label: string) => {
    switch (status) {
      case "complete":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>{label}</span>
          </span>
        );
      case "ready":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-bold text-sky-400 bg-sky-500/10 px-2 py-0.5 rounded-full border border-sky-500/20">
            <PlayCircle className="w-3 h-3" />
            <span>{label}</span>
          </span>
        );
      case "needs_attention":
        return (
          <span className="flex items-center space-x-1 text-[10px] font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
            <AlertCircle className="w-3 h-3" />
            <span>{label}</span>
          </span>
        );
      default:
        return (
          <span className="flex items-center space-x-1 text-[10px] font-medium text-slate-500 bg-slate-800/40 px-2 py-0.5 rounded-full border border-slate-700/50">
            <Clock className="w-3 h-3" />
            <span>{label}</span>
          </span>
        );
    }
  };

  return (
    <div className="w-full glass-panel rounded-2xl p-5 border border-surface-border">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 pb-3 border-b border-surface-border gap-2">
        <div>
          <h2 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
            Autonomous Pipeline Lifecycle
          </h2>
          <p className="text-xs text-slate-400">
            Automated progression from raw tabular input to verified machine learning models and reports.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3 gap-3">
        {steps.map((step) => {
          const isClickable = step.status !== "not_started";
          return (
            <div
              key={step.id}
              onClick={() => isClickable && onNavigate(step.id)}
              className={`p-3.5 rounded-xl border transition flex flex-col justify-between ${
                isClickable
                  ? "bg-surface-card hover:bg-surface-hover/80 hover:border-brand-cyan/40 cursor-pointer shadow-sm group"
                  : "bg-surface-card/40 border-slate-800/60 opacity-60 cursor-not-allowed"
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <span className="font-semibold text-xs text-slate-200 group-hover:text-brand-sky transition">
                  {step.title}
                </span>
                {getStatusBadge(step.status, step.statusLabel)}
              </div>
              <div className="flex items-center justify-between mt-1">
                <span className="text-[11px] text-slate-400 truncate max-w-[170px]">
                  {step.desc}
                </span>
                {isClickable && (
                  <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-brand-cyan group-hover:translate-x-0.5 transition" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
