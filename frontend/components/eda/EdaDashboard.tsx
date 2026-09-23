"use client";

import React, { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  Cell,
} from "recharts";
import { BarChart3, ScatterChart as ScatterIcon, Grid, Filter, Loader2, Info } from "lucide-react";
import { DatasetSession } from "@/types";
import { fetchCorrelation, fetchDistribution, fetchEdaOptions, fetchScatter } from "@/lib/api";

interface EdaDashboardProps {
  session: DatasetSession;
}

interface DistributionChartDatum {
  label: string;
  count: number;
}

export const EdaDashboard: React.FC<EdaDashboardProps> = ({ session }) => {
  const [activeSubTab, setActiveSubTab] = useState<"distribution" | "correlation" | "scatter">("distribution");
  const [options, setOptions] = useState<{
    numerical_columns: string[];
    categorical_columns: string[];
    all_columns: string[];
  } | null>(null);

  // Distribution tab state
  const [selectedColumn, setSelectedColumn] = useState<string>("");
  const [distData, setDistData] = useState<any>(null);
  const [loadingDist, setLoadingDist] = useState(false);

  // Correlation tab state
  const [corrData, setCorrData] = useState<{ columns: string[]; matrix: any[] } | null>(null);
  const [loadingCorr, setLoadingCorr] = useState(false);

  // Scatter tab state
  const [xCol, setXCol] = useState<string>("");
  const [yCol, setYCol] = useState<string>("");
  const [scatterPoints, setScatterPoints] = useState<any[]>([]);
  const [loadingScatter, setLoadingScatter] = useState(false);

  useEffect(() => {
    fetchEdaOptions(session.session_id)
      .then((opts) => {
        setOptions(opts);
        if (opts.all_columns.length > 0) {
          const firstCol = opts.all_columns[0];
          setSelectedColumn(firstCol);
          loadDistribution(firstCol);
        }
        if (opts.numerical_columns.length >= 2) {
          setXCol(opts.numerical_columns[0]);
          setYCol(opts.numerical_columns[1]);
        }
      })
      .catch(console.error);
  }, [session.session_id]);

  const loadDistribution = async (col: string) => {
    setLoadingDist(true);
    try {
      const res = await fetchDistribution(session.session_id, col);
      setDistData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingDist(false);
    }
  };

  const loadCorrelation = async () => {
    if (corrData) return;
    setLoadingCorr(true);
    try {
      const res = await fetchCorrelation(session.session_id);
      setCorrData(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingCorr(false);
    }
  };

  const loadScatter = async (x: string, y: string) => {
    if (!x || !y) return;
    setLoadingScatter(true);
    try {
      const res = await fetchScatter(session.session_id, x, y);
      // Format scatter points from plotly data or sample df
      const traces = res.plotly?.data?.[0];
      if (traces && traces.x && traces.y) {
        const pts = traces.x.map((xVal: any, i: number) => ({
          x: xVal,
          y: traces.y[i],
        }));
        setScatterPoints(pts);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingScatter(false);
    }
  };

  // Convert distribution plotly histogram into Recharts bar format
  const getRechartsDistData = (): DistributionChartDatum[] => {
    if (!distData?.plotly?.data?.[0]) return [];
    const trace = distData.plotly.data[0];

    // If categorical bar chart
    if (trace.type === "bar" && trace.x && trace.y) {
      return trace.x.map((category: string, i: number) => ({
        label: category,
        count: trace.y[i],
      }));
    }

    // If numerical histogram, compute bins from data values
    if (trace.x && Array.isArray(trace.x)) {
      const vals = trace.x.filter((v: any) => typeof v === "number" && !isNaN(v)).sort((a: number, b: number) => a - b);
      if (vals.length === 0) return [];
      const min = vals[0];
      const max = vals[vals.length - 1];
      const numBins = 15;
      const binWidth = (max - min) / numBins || 1;

      const bins = Array.from({ length: numBins }, (_, i) => ({
        label: `${(min + i * binWidth).toFixed(1)}`,
        count: 0,
      }));

      vals.forEach((v: number) => {
        const idx = Math.min(numBins - 1, Math.floor((v - min) / binWidth));
        if (bins[idx]) bins[idx].count++;
      });
      return bins;
    }

    return [];
  };

  const chartData = getRechartsDistData();

  return (
    <div className="space-y-6">
      {/* Top Controls & Sub-tabs */}
      <div className="glass-panel rounded-2xl p-6 border border-surface-border">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-border">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center space-x-2">
              <BarChart3 className="w-5 h-5 text-brand-cyan" />
              <span>Exploratory Data Analysis Workspace</span>
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Interactive univariate distributions, bivariate scatter relationships, and multivariate correlations.
            </p>
          </div>

          <div className="flex items-center space-x-1.5 p-1 rounded-xl bg-surface-card border border-surface-border text-xs">
            <button
              onClick={() => setActiveSubTab("distribution")}
              className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                activeSubTab === "distribution"
                  ? "bg-brand-blue text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Distributions
            </button>
            <button
              onClick={() => {
                setActiveSubTab("correlation");
                loadCorrelation();
              }}
              className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                activeSubTab === "correlation"
                  ? "bg-brand-blue text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              Correlation Matrix
            </button>
            <button
              onClick={() => {
                setActiveSubTab("scatter");
                if (xCol && yCol) loadScatter(xCol, yCol);
              }}
              className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                activeSubTab === "scatter"
                  ? "bg-brand-blue text-white shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              2D Scatter Plot
            </button>
          </div>
        </div>

        {/* 1. DISTRIBUTION SUBTAB */}
        {activeSubTab === "distribution" && (
          <div className="mt-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-400 font-semibold">Select Feature:</span>
                <select
                  value={selectedColumn}
                  onChange={(e) => {
                    setSelectedColumn(e.target.value);
                    loadDistribution(e.target.value);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
                >
                  {options?.all_columns.map((c) => (
                    <option key={c} value={c}>
                      {c} {options.numerical_columns.includes(c) ? "(Numeric)" : "(Categorical)"}
                    </option>
                  ))}
                </select>
              </div>

              {distData?.summary && (
                <div className="flex items-center space-x-3 text-xs">
                  {distData.is_numeric ? (
                    <>
                      <div className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        Mean: <strong className="text-brand-sky font-mono">{distData.summary.mean}</strong>
                      </div>
                      <div className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        Median: <strong className="text-brand-cyan font-mono">{distData.summary.median}</strong>
                      </div>
                      <div className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300">
                        Std: <strong className="text-slate-200 font-mono">{distData.summary.std}</strong>
                      </div>
                    </>
                  ) : (
                    <div className="px-2.5 py-1 rounded bg-slate-800 border border-slate-700 text-slate-300">
                      Unique Classes: <strong className="text-brand-sky font-mono">{distData.summary.unique_count}</strong>
                    </div>
                  )}
                </div>
              )}
            </div>

            {loadingDist ? (
              <div className="py-24 text-center">
                <Loader2 className="w-8 h-8 text-brand-cyan animate-spin mx-auto mb-2" />
                <span className="text-xs text-slate-400">Rendering interactive distribution...</span>
              </div>
            ) : chartData.length > 0 ? (
              <div className="h-80 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 25 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                    <XAxis
                      dataKey="label"
                      stroke="#64748B"
                      fontSize={11}
                      tickLine={false}
                      angle={-20}
                      textAnchor="end"
                    />
                    <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#0F172A",
                        borderColor: "rgba(148, 163, 184, 0.2)",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Bar dataKey="count" fill="#0ea5e9" radius={[4, 4, 0, 0]}>
                      {chartData.map((_datum: DistributionChartDatum, index: number) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={index % 2 === 0 ? "#0284c7" : "#0ea5e9"}
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-500">
                Select a column to generate frequency or spread analysis.
              </div>
            )}
          </div>
        )}

        {/* 2. CORRELATION MATRIX SUBTAB */}
        {activeSubTab === "correlation" && (
          <div className="mt-5 space-y-4">
            {loadingCorr ? (
              <div className="py-24 text-center">
                <Loader2 className="w-8 h-8 text-brand-cyan animate-spin mx-auto mb-2" />
                <span className="text-xs text-slate-400">Calculating pairwise Pearson correlation coefficients...</span>
              </div>
            ) : corrData ? (
              <div className="overflow-x-auto rounded-xl border border-surface-border">
                <table className="w-full text-xs text-center border-collapse">
                  <thead>
                    <tr className="bg-surface-hover/80 text-slate-300 font-semibold text-[11px]">
                      <th className="p-3 text-left">Feature</th>
                      {corrData.columns.map((c) => (
                        <th key={c} className="p-3 truncate max-w-[100px]" title={c}>
                          {c}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-surface-border">
                    {corrData.matrix.map((row) => (
                      <tr key={row.feature} className="hover:bg-surface-hover/50 transition">
                        <td className="p-3 font-semibold text-left text-slate-200 font-mono">
                          {row.feature}
                        </td>
                        {corrData.columns.map((c) => {
                          const val = row[c] ?? 0;
                          const isHigh = Math.abs(val) >= 0.7;
                          const isPositive = val > 0;
                          return (
                            <td
                              key={c}
                              className={`p-3 font-mono font-medium ${
                                val === 1
                                  ? "text-slate-500 bg-slate-900/40"
                                  : isHigh
                                  ? isPositive
                                    ? "bg-blue-600/30 text-blue-200 font-bold"
                                    : "bg-rose-600/30 text-rose-200 font-bold"
                                  : "text-slate-400"
                              }`}
                            >
                              {val.toFixed(2)}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-500">
                At least 2 numerical features required to render correlation matrix.
              </div>
            )}
          </div>
        )}

        {/* 3. 2D SCATTER PLOT SUBTAB */}
        {activeSubTab === "scatter" && (
          <div className="mt-5 space-y-4">
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-400 font-semibold">X Axis:</span>
                <select
                  value={xCol}
                  onChange={(e) => {
                    setXCol(e.target.value);
                    loadScatter(e.target.value, yCol);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
                >
                  {options?.numerical_columns.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center space-x-2 text-xs">
                <span className="text-slate-400 font-semibold">Y Axis:</span>
                <select
                  value={yCol}
                  onChange={(e) => {
                    setYCol(e.target.value);
                    loadScatter(xCol, e.target.value);
                  }}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
                >
                  {options?.numerical_columns.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {loadingScatter ? (
              <div className="py-24 text-center">
                <Loader2 className="w-8 h-8 text-brand-cyan animate-spin mx-auto mb-2" />
                <span className="text-xs text-slate-400">Plotting bivariate scatter relationships...</span>
              </div>
            ) : scatterPoints.length > 0 ? (
              <div className="h-80 w-full pt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 20, right: 30, bottom: 20, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
                    <XAxis
                      type="number"
                      dataKey="x"
                      name={xCol}
                      stroke="#64748B"
                      fontSize={11}
                      tickLine={false}
                    />
                    <YAxis
                      type="number"
                      dataKey="y"
                      name={yCol}
                      stroke="#64748B"
                      fontSize={11}
                      tickLine={false}
                    />
                    <Tooltip
                      cursor={{ strokeDasharray: "3 3" }}
                      contentStyle={{
                        backgroundColor: "#0F172A",
                        borderColor: "rgba(148, 163, 184, 0.2)",
                        borderRadius: "8px",
                        fontSize: "12px",
                      }}
                    />
                    <Scatter name="Observations" data={scatterPoints} fill="#38bdf8" fillOpacity={0.7} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-slate-500">
                Select continuous X and Y variables to inspect bivariate relationships.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
