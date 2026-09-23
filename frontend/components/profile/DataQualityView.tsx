"use client";

import React, { useState } from "react";
import {
  ShieldCheck,
  AlertTriangle,
  AlertCircle,
  CheckCircle2,
  Wand2,
  Target,
  RefreshCw,
  Sparkles,
  ArrowRight,
  Info,
} from "lucide-react";
import { DatasetSession } from "@/types";
import { cleanDataset, updateTarget } from "@/lib/api";

interface DataQualityViewProps {
  session: DatasetSession;
  onSessionUpdated: (updated: DatasetSession) => void;
}

export const DataQualityView: React.FC<DataQualityViewProps> = ({ session, onSessionUpdated }) => {
  const [cleaning, setCleaning] = useState(false);
  const [cleanLogs, setCleanLogs] = useState<string[] | null>(null);
  const [selectedTarget, setSelectedTarget] = useState(session.target_col || "");
  const [updatingTarget, setUpdatingTarget] = useState(false);

  const quality = session.quality;
  const overview = session.profile.overview;

  // Calculate Data Quality Score
  const penalty = Math.min(
    70,
    overview.missing_pct * 0.9 + overview.duplicate_pct * 1.5 + quality.total_issues * 3
  );
  const qualityScore = Math.max(20, Math.round(100 - penalty));

  const handleClean = async () => {
    setCleaning(true);
    try {
      const res = await cleanDataset(session.session_id, {
        drop_duplicates: true,
        impute_missing: true,
        remove_constant: true,
      });
      setCleanLogs(res.logs || ["Dataset cleaned successfully."]);
      onSessionUpdated({
        ...session,
        rows: res.rows,
        columns: res.columns,
        profile: res.profile,
        quality: res.quality,
        is_cleaned: true,
      });
    } catch (err: any) {
      alert(err.message || "Failed to clean dataset");
    } finally {
      setCleaning(false);
    }
  };

  const handleTargetChange = async (newCol: string) => {
    setSelectedTarget(newCol);
    setUpdatingTarget(true);
    try {
      const res = await updateTarget(session.session_id, newCol || null);
      onSessionUpdated({
        ...session,
        target_col: res.target_col,
        problem_type: res.problem_type,
        quality: res.quality,
      });
    } catch (err: any) {
      alert(err.message || "Failed to update target");
    } finally {
      setUpdatingTarget(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Target Detection & Override Bar */}
      <div className="glass-panel-glow rounded-2xl p-6 border border-brand-cyan/30">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center space-x-2">
              <Target className="w-5 h-5 text-brand-cyan" />
              <h3 className="text-base font-bold text-slate-100">
                Automatic Target & Problem Detection
              </h3>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-brand-cyan/20 text-brand-sky border border-brand-cyan/30">
                Real-Time Inference
              </span>
            </div>
            <p className="text-xs text-slate-300">
              Suggested Target: <strong className="text-brand-cyan font-mono">{session.target_info?.suggested_target || "None"}</strong>
              {session.target_info?.confidence ? ` (${(session.target_info.confidence * 100).toFixed(0)}% confidence)` : ""}
              {" — "}
              <span className="text-slate-400 italic">{session.target_info?.reason}</span>
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <div className="text-xs text-slate-400">Override Target:</div>
            <select
              value={selectedTarget}
              onChange={(e) => handleTargetChange(e.target.value)}
              disabled={updatingTarget}
              className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan cursor-pointer"
            >
              <option value="">None (Unsupervised / Clustering)</option>
              {session.column_names.map((col) => (
                <option key={col} value={col}>
                  {col} {session.target_info?.suggested_target === col ? "★ (Suggested)" : ""}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-800 flex flex-wrap items-center gap-4 text-xs text-slate-400">
          <div>
            Active Formulation: <strong className="text-slate-200">{session.problem_type || "Unsupervised Analysis"}</strong>
          </div>
          <div>
            Target Variable: <strong className="text-brand-cyan font-mono">{session.target_col || "None"}</strong>
          </div>
        </div>
      </div>

      {/* Health Score & Cleaning Trigger */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Card */}
        <div className="glass-panel rounded-2xl p-6 border border-surface-border flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Dataset Health Score
              </span>
              <ShieldCheck className={`w-5 h-5 ${qualityScore >= 80 ? "text-emerald-400" : "text-amber-400"}`} />
            </div>

            <div className="flex items-baseline space-x-3">
              <span className="text-4xl font-extrabold text-slate-100">{qualityScore}</span>
              <span className="text-sm font-semibold text-slate-400">/ 100</span>
            </div>

            <div className="w-full bg-slate-800 h-2 rounded-full mt-3 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  qualityScore >= 80
                    ? "bg-gradient-to-r from-emerald-500 to-teal-400"
                    : qualityScore >= 60
                    ? "bg-gradient-to-r from-amber-500 to-yellow-400"
                    : "bg-gradient-to-r from-rose-500 to-red-400"
                }`}
                style={{ width: `${qualityScore}%` }}
              />
            </div>

            <p className="text-xs text-slate-400 mt-3 leading-relaxed">
              {qualityScore >= 85
                ? "Excellent data hygiene. Missingness is negligible and observation vectors exhibit high entropy."
                : qualityScore >= 65
                ? "Moderate quality. Noticeable missing values or duplicate observations may introduce slight bias."
                : "Significant data anomalies detected. Cleaning and imputation are strongly advised."}
            </p>
          </div>

          {/* Clean Trigger Button */}
          <div className="mt-6 pt-4 border-t border-surface-border">
            <button
              onClick={handleClean}
              disabled={cleaning}
              className="w-full py-2.5 px-4 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-blue to-brand-cyan hover:from-blue-500 hover:to-cyan-400 transition flex items-center justify-center space-x-2 shadow-sm disabled:opacity-50"
            >
              <Wand2 className="w-4 h-4" />
              <span>{cleaning ? "Applying Cleaning Transformations..." : "Execute Automated Data Cleaning"}</span>
            </button>
            <span className="block text-center text-[10px] text-slate-500 mt-1.5">
              Non-destructive: Imputes missing values, removes duplicates & constant columns.
            </span>
          </div>
        </div>

        {/* Cleaning Logs or Issues Overview */}
        <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-surface-border">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
                Quality Flaws & Recommendations ({quality.total_issues} detected)
              </h3>
            </div>
            {session.is_cleaned && (
              <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center space-x-1">
                <CheckCircle2 className="w-3 h-3" />
                <span>Cleaned Copy Active</span>
              </span>
            )}
          </div>

          {cleanLogs && (
            <div className="p-3.5 rounded-xl bg-emerald-950/30 border border-emerald-500/30 text-xs space-y-1">
              <strong className="text-emerald-300 font-semibold block">Cleaning Transformations Applied:</strong>
              {cleanLogs.map((log, i) => (
                <p key={i} className="text-emerald-200 font-mono text-[11px]">• {log}</p>
              ))}
            </div>
          )}

          {/* Quality Issues List */}
          <div className="space-y-2.5 max-h-[350px] overflow-y-auto pr-1">
            {quality.issues.length === 0 ? (
              <div className="py-8 text-center text-slate-400 text-xs">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                <span>No severe quality defects found in this dataset!</span>
              </div>
            ) : (
              quality.issues.map((issue, idx) => (
                <div
                  key={idx}
                  className="p-3 rounded-xl bg-surface-card border border-surface-border flex items-start justify-between gap-3 text-xs"
                >
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-bold text-slate-200">{issue.title}</span>
                      <span
                        className={`text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded ${
                          issue.severity === "high"
                            ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                            : issue.severity === "medium"
                            ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                            : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
                        }`}
                      >
                        {issue.severity}
                      </span>
                    </div>
                    <p className="text-slate-400 text-[11px] leading-relaxed">{issue.description}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Outlier & Imputation Strategies */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Missing Recommendations */}
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Recommended Missing-Value Imputation
          </h4>
          <div className="space-y-2 text-xs">
            {Object.keys(quality.missing_recommendations).length === 0 ? (
              <p className="text-slate-500 py-3">No missing values in this dataset.</p>
            ) : (
              Object.entries(quality.missing_recommendations).map(([col, rec]) => (
                <div key={col} className="p-2.5 rounded-lg bg-surface-card border border-surface-border flex justify-between items-center">
                  <div>
                    <span className="font-mono font-bold text-slate-200">{col}</span>
                    <span className="text-slate-500 text-[11px] block">{rec.missing_pct}% nulls — {rec.reason}</span>
                  </div>
                  <span className="px-2 py-1 rounded bg-slate-800 text-brand-sky font-mono font-bold text-[11px]">
                    {rec.recommended_strategy}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Outlier Summary */}
        <div className="glass-panel rounded-2xl p-5 border border-surface-border space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300">
            Numerical Outlier Analysis (Tukey 1.5× IQR)
          </h4>
          <div className="space-y-2 text-xs">
            {Object.keys(quality.outlier_summary).length === 0 ? (
              <p className="text-slate-500 py-3">No numerical columns or outliers detected.</p>
            ) : (
              Object.entries(quality.outlier_summary).slice(0, 5).map(([col, info]) => (
                <div key={col} className="p-2.5 rounded-lg bg-surface-card border border-surface-border flex justify-between items-center">
                  <div>
                    <span className="font-mono font-bold text-slate-200">{col}</span>
                    <span className="text-slate-500 text-[11px] block">
                      Range: [{info.lower_bound.toFixed(1)}, {info.upper_bound.toFixed(1)}]
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-amber-400 font-mono">{info.iqr_outliers} outliers</span>
                    <span className="text-[10px] text-slate-500 block">({info.iqr_pct}%)</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
