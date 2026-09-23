"use client";

import React, { useState, useEffect } from "react";
import { Calculator, Play, AlertCircle, CheckCircle2, Info, Loader2, Sparkles } from "lucide-react";
import { DatasetSession } from "@/types";
import { fetchDescriptiveStats, fetchPairwiseCorrelation, runHypothesisTest } from "@/lib/api";
import { formatNumber } from "@/lib/utils";

interface StatisticsViewProps {
  session: DatasetSession;
}

export const StatisticsView: React.FC<StatisticsViewProps> = ({ session }) => {
  const [statsData, setStatsData] = useState<Record<string, any>[]>([]);
  const [loadingStats, setLoadingStats] = useState(false);

  // Pairwise test state
  const [colX, setColX] = useState<string>("");
  const [colY, setColY] = useState<string>("");
  const [pairwiseRes, setPairwiseRes] = useState<any>(null);
  const [loadingPairwise, setLoadingPairwise] = useState(false);

  // Hypothesis test state
  const [hCol1, setHCol1] = useState<string>("");
  const [hCol2, setHCol2] = useState<string>("");
  const [hTestType, setHTestType] = useState<string>("auto");
  const [hypothesisRes, setHypothesisRes] = useState<any>(null);
  const [loadingHTest, setLoadingHTest] = useState(false);

  const numCols = session.profile.columns
    .filter((c) => c.mean !== undefined)
    .map((c) => c.name);

  useEffect(() => {
    setLoadingStats(true);
    fetchDescriptiveStats(session.session_id)
      .then(setStatsData)
      .catch(console.error)
      .finally(() => setLoadingStats(false));

    if (numCols.length >= 2) {
      setColX(numCols[0]);
      setColY(numCols[1]);
      setHCol1(numCols[0]);
      setHCol2(numCols[1]);
    }
  }, [session.session_id]);

  const handleRunPairwise = async () => {
    if (!colX || !colY) return;
    setLoadingPairwise(true);
    try {
      const res = await fetchPairwiseCorrelation(session.session_id, colX, colY);
      setPairwiseRes(res);
    } catch (err: any) {
      alert(err.message || "Failed to calculate correlation");
    } finally {
      setLoadingPairwise(false);
    }
  };

  const handleRunHypothesis = async () => {
    if (!hCol1 || !hCol2) return;
    setLoadingHTest(true);
    try {
      const res = await runHypothesisTest(session.session_id, hCol1, hCol2, hTestType);
      setHypothesisRes(res);
    } catch (err: any) {
      alert(err.message || "Failed to execute hypothesis test");
    } finally {
      setLoadingHTest(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Descriptive Statistics Table */}
      <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div>
            <h2 className="text-base font-bold text-slate-100 flex items-center space-x-2">
              <Calculator className="w-5 h-5 text-brand-cyan" />
              <span>Parametric & Non-Parametric Descriptive Statistics</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Measures of central tendency, dispersion, interquartile range (IQR), skewness, and excess kurtosis.
            </p>
          </div>
        </div>

        {loadingStats ? (
          <div className="py-16 text-center">
            <Loader2 className="w-8 h-8 text-brand-cyan animate-spin mx-auto mb-2" />
            <span className="text-xs text-slate-400">Computing higher statistical moments...</span>
          </div>
        ) : statsData.length > 0 ? (
          <div className="overflow-x-auto rounded-xl border border-surface-border">
            <table className="w-full text-xs text-left">
              <thead className="bg-surface-hover/80 text-slate-400 uppercase text-[10px] tracking-wider font-semibold border-b border-surface-border">
                <tr>
                  <th className="py-3 px-4">Feature</th>
                  <th className="py-3 px-3">Count</th>
                  <th className="py-3 px-3">Mean</th>
                  <th className="py-3 px-3">Std Dev</th>
                  <th className="py-3 px-3">Median</th>
                  <th className="py-3 px-3">Min</th>
                  <th className="py-3 px-3">25% (Q1)</th>
                  <th className="py-3 px-3">75% (Q3)</th>
                  <th className="py-3 px-3">Max</th>
                  <th className="py-3 px-3">IQR</th>
                  <th className="py-3 px-3">Skewness</th>
                  <th className="py-3 px-4">Kurtosis</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border text-slate-300 font-mono">
                {statsData.map((row) => (
                  <tr key={row.Feature} className="hover:bg-surface-hover/50 transition">
                    <td className="py-2.5 px-4 font-semibold text-slate-100 font-sans">{row.Feature}</td>
                    <td className="py-2.5 px-3 text-slate-400">{row.Count}</td>
                    <td className="py-2.5 px-3">{formatNumber(row.Mean)}</td>
                    <td className="py-2.5 px-3 text-slate-400">{formatNumber(row["Std Dev"])}</td>
                    <td className="py-2.5 px-3 text-brand-cyan font-bold">{formatNumber(row.Median)}</td>
                    <td className="py-2.5 px-3 text-slate-400">{formatNumber(row.Min)}</td>
                    <td className="py-2.5 px-3 text-slate-400">{formatNumber(row["25%"])}</td>
                    <td className="py-2.5 px-3 text-slate-400">{formatNumber(row["75%"])}</td>
                    <td className="py-2.5 px-3 text-slate-400">{formatNumber(row.Max)}</td>
                    <td className="py-2.5 px-3">{formatNumber(row.IQR)}</td>
                    <td className="py-2.5 px-3 text-slate-300">{formatNumber(row.Skewness)}</td>
                    <td className="py-2.5 px-4 text-slate-300">{formatNumber(row.Kurtosis)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-8 text-center text-xs text-slate-500">
            No continuous numerical features found in this dataset.
          </div>
        )}
      </div>

      {/* 2. Pairwise Correlation with p-values */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Pairwise Correlation & Significance Testing
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Calculates Pearson (linear) and Spearman rank correlations with exact two-tailed p-values.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Feature X:</label>
              <select
                value={colX}
                onChange={(e) => setColX(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
              >
                {numCols.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Feature Y:</label>
              <select
                value={colY}
                onChange={(e) => setColY(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
              >
                {numCols.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleRunPairwise}
            disabled={loadingPairwise || !colX || !colY}
            className="w-full py-2 px-4 rounded-xl text-xs font-bold text-white bg-brand-blue hover:bg-blue-500 transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loadingPairwise ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            <span>Compute Correlation & P-Values</span>
          </button>

          {pairwiseRes && (
            <div className="p-4 rounded-xl bg-surface-card border border-surface-border space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg bg-surface/80 border border-surface-border">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Pearson r</span>
                  <span className="text-lg font-bold text-brand-sky font-mono">
                    {pairwiseRes.pearson?.coefficient}
                  </span>
                  <div className="text-[11px] text-slate-400 mt-1">
                    p-value: <span className="font-mono text-slate-200">{pairwiseRes.pearson?.p_value?.toExponential(3)}</span>
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-surface/80 border border-surface-border">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Spearman ρ</span>
                  <span className="text-lg font-bold text-brand-cyan font-mono">
                    {pairwiseRes.spearman?.rho}
                  </span>
                  <div className="text-[11px] text-slate-400 mt-1">
                    p-value: <span className="font-mono text-slate-200">{pairwiseRes.spearman?.p_value?.toExponential(3)}</span>
                  </div>
                </div>
              </div>

              <div className="p-3 rounded-lg bg-brand-cyan/10 border border-brand-cyan/20 text-slate-300 text-[11px] leading-relaxed">
                <strong>Natural Language Finding:</strong> {colX} and {colY} show a measurable association in this dataset ({pairwiseRes.pearson?.interpretation}).
              </div>

              <div className="p-2.5 rounded-lg bg-amber-950/20 border border-amber-500/20 text-amber-300 text-[10px] flex items-start space-x-2">
                <Info className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                <span>{pairwiseRes.scientific_disclaimer}</span>
              </div>
            </div>
          )}
        </div>

        {/* 3. Formal Hypothesis Testing */}
        <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Automated Hypothesis Testing
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Select variables to automatically infer and run Two-Sample T-Tests, ANOVA, or Chi-Square tests.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <label className="text-slate-400 block mb-1">Variable 1:</label>
              <select
                value={hCol1}
                onChange={(e) => setHCol1(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
              >
                {session.column_names.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-slate-400 block mb-1">Variable 2:</label>
              <select
                value={hCol2}
                onChange={(e) => setHCol2(e.target.value)}
                className="w-full px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
              >
                {session.column_names.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            onClick={handleRunHypothesis}
            disabled={loadingHTest || !hCol1 || !hCol2}
            className="w-full py-2 px-4 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-blue to-brand-cyan hover:from-blue-500 hover:to-cyan-400 transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loadingHTest ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-3.5 h-3.5" />}
            <span>Execute Hypothesis Test</span>
          </button>

          {hypothesisRes && (
            <div className="p-4 rounded-xl bg-surface-card border border-surface-border space-y-3 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <span className="font-bold text-slate-200">{hypothesisRes.test_name || "Hypothesis Test"}</span>
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                    hypothesisRes.statistically_significant
                      ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      : "bg-slate-800 text-slate-400 border border-slate-700"
                  }`}
                >
                  {hypothesisRes.statistically_significant ? "Statistically Significant (p < 0.05)" : "Fail to Reject Null (p ≥ 0.05)"}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                <div className="p-2 rounded bg-surface/80 border border-surface-border">
                  <span className="text-[10px] text-slate-400 block font-sans">Test Statistic</span>
                  <span className="font-bold text-slate-200">{formatNumber(hypothesisRes.test_statistic)}</span>
                </div>
                <div className="p-2 rounded bg-surface/80 border border-surface-border">
                  <span className="text-[10px] text-slate-400 block font-sans">p-value</span>
                  <span className="font-bold text-slate-200">{hypothesisRes.p_value?.toExponential(4)}</span>
                </div>
              </div>

              {hypothesisRes.interpretation && (
                <p className="text-slate-300 text-[11px] leading-relaxed">
                  {hypothesisRes.interpretation}
                </p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
