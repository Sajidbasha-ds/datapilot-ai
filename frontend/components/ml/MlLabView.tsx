"use client";

import React, { useState } from "react";
import {
  Cpu,
  Play,
  Trophy,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  Layers,
  BarChart,
  HelpCircle,
  Loader2,
  Info,
} from "lucide-react";
import { DatasetSession, MlBenchmarkResults, ModelBenchmarkRow } from "@/types";
import { trainModels } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";
import { FeatureImportanceView } from "./FeatureImportanceView";

interface MlLabViewProps {
  session: DatasetSession;
  mlResults: MlBenchmarkResults | null;
  onResultsUpdated: (results: MlBenchmarkResults) => void;
}

export const MlLabView: React.FC<MlLabViewProps> = ({ session, mlResults, onResultsUpdated }) => {
  const [targetCol, setTargetCol] = useState(session.target_col || "");
  const [problemType, setProblemType] = useState(session.problem_type || "Binary Classification");
  const [testSize, setTestSize] = useState<number>(0.2);
  const [cvFolds, setCvFolds] = useState<number>(3);
  const [training, setTraining] = useState(false);
  const [trainStep, setTrainStep] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);

  const isClassification = problemType.includes("Classification");
  const isUnsupervised = problemType.includes("Unsupervised");

  const handleTrain = async () => {
    setError(null);
    setTraining(true);
    setTrainStep("Engineering datetime & categorical pipelines...");

    try {
      setTimeout(() => setTrainStep("Fitting preprocessors strictly on training fold..."), 1200);
      setTimeout(() => setTrainStep("Cross-validating & evaluating candidate algorithms..."), 2500);

      const res = await trainModels(session.session_id, {
        target_col: targetCol || undefined,
        problem_type: problemType,
        test_size: testSize,
        cv_folds: cvFolds,
      });

      onResultsUpdated(res);
      setSelectedModel(res.best_model_name);
    } catch (err: any) {
      setError(err.message || "Model training failed");
    } finally {
      setTraining(false);
      setTrainStep("");
    }
  };

  const winningModel = mlResults?.best_model_name;
  const activeModel = selectedModel || winningModel;

  return (
    <div className="space-y-6">
      {/* 1. Experimentation Setup Panel */}
      <div className="glass-panel-glow rounded-2xl p-6 border border-brand-cyan/30">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-surface-border">
          <div>
            <div className="flex items-center space-x-2">
              <Cpu className="w-5 h-5 text-brand-cyan" />
              <h2 className="text-lg font-bold text-slate-100">
                Machine Learning Experimentation Lab
              </h2>
              <span className="px-2 py-0.5 rounded text-[10px] uppercase font-bold bg-brand-cyan/20 text-brand-sky border border-brand-cyan/30">
                Automated ML Benchmarking
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Training-split preprocessing, feature screening, stratified splits, multi-model evaluation, and cross-validation analysis.
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleTrain}
              disabled={training}
              className="py-2.5 px-6 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-blue to-brand-cyan hover:from-blue-500 hover:to-cyan-400 transition flex items-center space-x-2 shadow-glow disabled:opacity-50"
            >
              {training ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-white" />
                  <span>{trainStep || "Training..."}</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 text-white fill-white" />
                  <span>Run Automated Model Benchmark</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Configuration Sliders & Selectors */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-5 text-xs">
          <div>
            <label className="text-slate-400 font-semibold block mb-1">Target Feature:</label>
            <select
              value={targetCol}
              onChange={(e) => setTargetCol(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
            >
              <option value="">None (Unsupervised Analysis)</option>
              {session.column_names.map((c) => (
                <option key={c} value={c}>
                  {c} {session.target_info?.suggested_target === c ? "★ (Target)" : ""}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-slate-400 font-semibold block mb-1">Problem Type:</label>
            <select
              value={problemType}
              onChange={(e) => setProblemType(e.target.value)}
              className="w-full px-3 py-2 rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
            >
              <option value="Binary Classification">Binary Classification</option>
              <option value="Multiclass Classification">Multiclass Classification</option>
              <option value="Regression">Regression</option>
              <option value="Unsupervised Analysis">Unsupervised (Clustering)</option>
            </select>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <label className="text-slate-400 font-semibold">Test Hold-Out Ratio:</label>
              <span className="text-brand-cyan font-mono font-bold">{(testSize * 100).toFixed(0)}%</span>
            </div>
            <input
              type="range"
              min="0.1"
              max="0.4"
              step="0.05"
              value={testSize}
              onChange={(e) => setTestSize(parseFloat(e.target.value))}
              className="w-full accent-brand-cyan"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>10% (Fast)</span>
              <span>20% (Standard)</span>
              <span>40% (Small sets)</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-1">
              <label className="text-slate-400 font-semibold">CV Folds (Train Fold):</label>
              <span className="text-brand-cyan font-mono font-bold">{cvFolds} Folds</span>
            </div>
            <input
              type="range"
              min="2"
              max="5"
              step="1"
              value={cvFolds}
              onChange={(e) => setCvFolds(parseInt(e.target.value))}
              className="w-full accent-brand-cyan"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-0.5">
              <span>2 Folds</span>
              <span>3 Folds</span>
              <span>5 Folds</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-3 rounded-xl bg-red-950/40 border border-status-error/40 flex items-center space-x-2 text-red-200 text-xs">
            <AlertTriangle className="w-4 h-4 text-status-error shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* 2. Benchmark Results Area */}
      {mlResults ? (
        <div className="space-y-6">
          {/* Data Split & Sample Size Reliability Disclaimer */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl glass-panel border border-surface-border">
              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                Data Partitioning
              </span>
              <div className="text-sm font-semibold text-slate-200">
                <span className="text-brand-sky font-mono">{mlResults.n_train} training rows</span>
                {" / "}
                <span className="text-brand-cyan font-mono">{mlResults.n_test} test rows</span>
              </div>
              <span className="text-[11px] text-slate-500 block mt-1">
                Strict {(mlResults.test_size * 100).toFixed(0)}% held-out test evaluation split
              </span>
            </div>

            <div className="p-4 rounded-xl glass-panel border border-surface-border">
              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                Candidate Selection Rule
              </span>
              <div className="text-sm font-semibold text-slate-200">
                {isClassification ? "Macro F1 first, then Accuracy" : "R² (Coeff of Det) first, then RMSE"}
              </div>
              <span className="text-[11px] text-slate-500 block mt-1">
                Best Model: <strong className="text-emerald-400">{winningModel}</strong>
              </span>
            </div>

            <div className="p-4 rounded-xl glass-panel border border-surface-border">
              <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                Validation Technique
              </span>
              <div className="text-sm font-semibold text-slate-200">
                {mlResults.cv_folds}-Fold Stratified Cross-Validation
              </div>
              <span className="text-[11px] text-slate-500 block mt-1">
                Preprocessing is fitted within each training fold. Regression target-correlation screening runs on the outer training split before CV.
              </span>
            </div>
          </div>

          {/* Small Sample Warning */}
          {mlResults.reliability_warning && (
            <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 flex items-start space-x-2.5 text-xs text-amber-200">
              <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
              <div>
                <strong className="text-amber-300 block font-semibold">Evaluation Sample Size Notice:</strong>
                <span>{mlResults.reliability_warning}</span>
              </div>
            </div>
          )}

          {/* Leaderboard Table with Clear Separation of Hold-out vs CV */}
          <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-surface-border">
              <div>
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
                  <Trophy className="w-4 h-4 text-yellow-400" />
                  <span>Model Benchmark Leaderboard</span>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Comparison between Hold-out Test performance and Cross-Validation generalization.
                </p>
              </div>

              <div className="flex items-center space-x-4 text-[11px]">
                <div className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-blue-500/30 border border-blue-500" />
                  <span className="text-slate-400 font-medium">Hold-out Test Metrics</span>
                </div>
                <div className="flex items-center space-x-1.5">
                  <span className="w-2.5 h-2.5 rounded bg-emerald-500/30 border border-emerald-500" />
                  <span className="text-slate-400 font-medium">Cross-Validation Metrics</span>
                </div>
              </div>
            </div>

            <div className="overflow-x-auto rounded-xl border border-surface-border">
              <table className="w-full text-xs text-left">
                <thead className="bg-surface-hover/80 text-slate-300 font-semibold border-b border-surface-border">
                  <tr>
                    <th className="py-3 px-4">Model Name</th>
                    {isClassification ? (
                      <>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">Macro F1</th>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">Accuracy</th>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">Precision</th>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">Recall</th>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">ROC-AUC</th>
                        <th className="py-3 px-3 bg-emerald-950/20 text-emerald-300">CV F1 (Train)</th>
                        <th className="py-3 px-3 bg-emerald-950/20 text-emerald-300">CV Std Dev</th>
                      </>
                    ) : (
                      <>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">R²</th>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">RMSE</th>
                        <th className="py-3 px-3 bg-blue-950/20 text-blue-300">MAE</th>
                        <th className="py-3 px-3 bg-emerald-950/20 text-emerald-300">CV R² (Train)</th>
                        <th className="py-3 px-3 bg-emerald-950/20 text-emerald-300">CV Std Dev</th>
                      </>
                    )}
                    <th className="py-3 px-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-border font-mono text-slate-300">
                  {mlResults.leaderboard.map((row, idx) => {
                    const isWinner = row.Model === winningModel;
                    return (
                      <tr
                        key={row.Model}
                        onClick={() => setSelectedModel(row.Model)}
                        className={`hover:bg-surface-hover/60 transition cursor-pointer ${
                          isWinner ? "bg-brand-cyan/5 font-semibold" : ""
                        }`}
                      >
                        <td className="py-3 px-4 font-sans font-bold text-slate-100 flex items-center space-x-2">
                          <span>{row.Model}</span>
                          {isWinner && (
                            <span className="text-[9px] uppercase px-1.5 py-0.5 rounded font-extrabold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center space-x-1">
                              <Trophy className="w-2.5 h-2.5" />
                              <span>Top Model</span>
                            </span>
                          )}
                        </td>

                        {isClassification ? (
                          <>
                            <td className="py-3 px-3 text-brand-sky font-bold">
                              {formatPercent((row["F1-Score (Macro)"] ?? 0) * 100)}
                            </td>
                            <td className="py-3 px-3">{formatPercent((row.Accuracy ?? 0) * 100)}</td>
                            <td className="py-3 px-3 text-slate-400">{formatNumber(row["Precision (Macro)"])}</td>
                            <td className="py-3 px-3 text-slate-400">{formatNumber(row["Recall (Macro)"])}</td>
                            <td className="py-3 px-3 text-slate-400">
                              {row["ROC-AUC"] !== null && row["ROC-AUC"] !== undefined
                                ? formatNumber(row["ROC-AUC"])
                                : "N/A"}
                            </td>
                            <td className="py-3 px-3 text-emerald-400 font-bold">
                              {formatPercent((row["CV F1 (Train)"] ?? 0) * 100)}
                            </td>
                            <td className="py-3 px-3 text-slate-400">
                              ±{formatNumber(row["CV Std"])}
                            </td>
                          </>
                        ) : (
                          <>
                            <td className="py-3 px-3 text-brand-sky font-bold">
                              {formatNumber(row["R²"])}
                            </td>
                            <td className="py-3 px-3 text-slate-200">{formatNumber(row.RMSE)}</td>
                            <td className="py-3 px-3 text-slate-400">{formatNumber(row.MAE)}</td>
                            <td className="py-3 px-3 text-emerald-400 font-bold">
                              {formatNumber(row["CV R² (Train)"])}
                            </td>
                            <td className="py-3 px-3 text-slate-400">
                              ±{formatNumber(row["CV Std"])}
                            </td>
                          </>
                        )}

                        <td className="py-3 px-4 text-right font-sans">
                          {isWinner ? (
                            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                              Selected
                            </span>
                          ) : (
                            <span className="text-[10px] text-slate-500">Evaluated</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* 3. Feature Importance View */}
          <FeatureImportanceView
            features={mlResults.feature_importance}
            modelName={mlResults.best_model_name}
          />
        </div>
      ) : (
        <div className="glass-panel rounded-2xl p-12 text-center space-y-3 border border-surface-border">
          <Cpu className="w-10 h-10 text-brand-cyan/60 mx-auto" />
          <h3 className="text-base font-bold text-slate-200">Ready to Benchmark Candidate Models</h3>
          <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
            Click &apos;Run Automated Model Benchmark&apos; above. DataPilot will evaluate Random Forest, Gradient Boosting, Logistic/Ridge Regression, and Extra Trees using strict cross-validation.
          </p>
        </div>
      )}
    </div>
  );
};
