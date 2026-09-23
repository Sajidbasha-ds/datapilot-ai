"use client";

import React, { useState } from "react";
import { Search, AlertOctagon, HelpCircle, FileText, CheckCircle2, ChevronDown, ChevronUp } from "lucide-react";
import { ColumnProfile, DatasetSession } from "@/types";
import { formatNumber, formatPercent } from "@/lib/utils";

interface DataProfileViewProps {
  session: DatasetSession;
}

export const DataProfileView: React.FC<DataProfileViewProps> = ({ session }) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<"all" | "numeric" | "categorical">("all");
  const [expandedCol, setExpandedCol] = useState<string | null>(null);

  const profile = session.profile;
  const overview = profile.overview;

  const filteredCols = profile.columns.filter((col) => {
    const matchesSearch = col.name.toLowerCase().includes(searchTerm.toLowerCase());
    const isNum = col.mean !== undefined || col.dtype.includes("int") || col.dtype.includes("float");
    if (filterType === "numeric") return matchesSearch && isNum;
    if (filterType === "categorical") return matchesSearch && !isNum;
    return matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Top Banner / Dimensions */}
      <div className="glass-panel rounded-2xl p-6 border border-surface-border">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-surface-border">
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="text-lg font-bold text-slate-100">Dataset Profiling & Schema Architecture</h2>
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-brand-cyan/20 text-brand-sky border border-brand-cyan/30">
                Automated Profiler
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              File: <span className="font-semibold text-slate-200">{session.filename}</span> — Comprehensive statistical inventory across all features.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs">
            <div className="px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border">
              <span className="text-slate-400">Rows:</span>{" "}
              <strong className="text-slate-200 font-mono">{overview.rows.toLocaleString()}</strong>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border">
              <span className="text-slate-400">Features:</span>{" "}
              <strong className="text-slate-200 font-mono">{overview.columns}</strong>
            </div>
            <div className="px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border">
              <span className="text-slate-400">Missingness:</span>{" "}
              <strong className={overview.missing_pct > 0 ? "text-amber-400 font-mono" : "text-emerald-400 font-mono"}>
                {overview.missing_pct}%
              </strong>
            </div>
          </div>
        </div>

        {/* Suspicious Columns Alert Box */}
        {overview.suspicious_columns.length > 0 && (
          <div className="mt-4 p-4 rounded-xl bg-amber-950/20 border border-amber-500/30">
            <div className="flex items-center space-x-2 text-amber-300 font-semibold text-xs mb-2">
              <AlertOctagon className="w-4 h-4 text-amber-400" />
              <span>Potential Data Hygiene & Leakage Warnings Detected</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
              {overview.suspicious_columns.map((item, idx) => (
                <div key={idx} className="p-2.5 rounded-lg bg-surface/80 border border-amber-500/20">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-slate-200">{item.column}</span>
                    <span className="text-[10px] uppercase font-bold text-amber-400 px-1.5 py-0.5 rounded bg-amber-500/10">
                      {item.reason}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1 leading-snug">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Feature Inventory Table */}
      <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200">
              Feature Inventory ({filteredCols.length} columns)
            </h3>
            <p className="text-xs text-slate-400">
              Click any column to view statistical distributions, quartiles, and skewness.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                type="text"
                placeholder="Search features..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8 pr-3 py-1.5 text-xs rounded-lg bg-surface-card border border-surface-border text-slate-200 focus:outline-none focus:border-brand-cyan"
              />
            </div>

            <div className="flex rounded-lg border border-surface-border p-0.5 bg-surface-card text-xs">
              <button
                onClick={() => setFilterType("all")}
                className={`px-2.5 py-1 rounded-md transition ${filterType === "all" ? "bg-brand-blue text-white" : "text-slate-400 hover:text-slate-200"}`}
              >
                All
              </button>
              <button
                onClick={() => setFilterType("numeric")}
                className={`px-2.5 py-1 rounded-md transition ${filterType === "numeric" ? "bg-brand-blue text-white" : "text-slate-400 hover:text-slate-200"}`}
              >
                Numeric
              </button>
              <button
                onClick={() => setFilterType("categorical")}
                className={`px-2.5 py-1 rounded-md transition ${filterType === "categorical" ? "bg-brand-blue text-white" : "text-slate-400 hover:text-slate-200"}`}
              >
                Categorical
              </button>
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto rounded-xl border border-surface-border">
          <table className="w-full text-left text-xs">
            <thead className="bg-surface-hover/50 text-slate-400 uppercase text-[10px] tracking-wider font-semibold border-b border-surface-border">
              <tr>
                <th className="py-3 px-4">Column Name</th>
                <th className="py-3 px-3">Data Type</th>
                <th className="py-3 px-3">Missing</th>
                <th className="py-3 px-3">Unique Values</th>
                <th className="py-3 px-3">Mean / Mode</th>
                <th className="py-3 px-3">Min - Max</th>
                <th className="py-3 px-4 text-right">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border text-slate-300">
              {filteredCols.map((col) => {
                const isExpanded = expandedCol === col.name;
                const isNumeric = col.mean !== undefined;
                const isTarget = session.target_col === col.name;

                return (
                  <React.Fragment key={col.name}>
                    <tr
                      onClick={() => setExpandedCol(isExpanded ? null : col.name)}
                      className={`hover:bg-surface-hover/60 transition cursor-pointer ${
                        isTarget ? "bg-brand-cyan/5" : ""
                      }`}
                    >
                      <td className="py-3 px-4 font-mono font-medium text-slate-100 flex items-center space-x-2">
                        <span>{col.name}</span>
                        {isTarget && (
                          <span className="text-[9px] uppercase px-1.5 py-0.5 rounded font-bold bg-brand-cyan/20 text-brand-sky border border-brand-cyan/30">
                            Target
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
                          {col.dtype}
                        </span>
                      </td>
                      <td className="py-3 px-3">
                        {col.missing_count === 0 ? (
                          <span className="text-emerald-400 font-medium">0 (0%)</span>
                        ) : (
                          <span className="text-amber-400 font-medium">
                            {col.missing_count} ({col.missing_pct}%)
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-3 font-mono">
                        {col.unique_count.toLocaleString()} ({(col.cardinality_ratio * 100).toFixed(1)}%)
                      </td>
                      <td className="py-3 px-3 font-mono">
                        {isNumeric ? formatNumber(col.mean) : Object.keys(col.top_categories || {})[0] || "N/A"}
                      </td>
                      <td className="py-3 px-3 font-mono text-slate-400">
                        {isNumeric ? `${formatNumber(col.min)} → ${formatNumber(col.max)}` : "Categorical"}
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button className="p-1 text-slate-400 hover:text-slate-200">
                          {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                        </button>
                      </td>
                    </tr>

                    {/* Expandable Deep Statistical Distribution */}
                    {isExpanded && (
                      <tr className="bg-surface-card/80 border-b border-surface-border">
                        <td colSpan={7} className="p-4">
                          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-3 text-xs bg-surface/80 p-3.5 rounded-xl border border-surface-border">
                            {isNumeric ? (
                              <>
                                <div>
                                  <span className="text-slate-500 block text-[10px] uppercase">Mean</span>
                                  <strong className="text-slate-200 font-mono">{formatNumber(col.mean)}</strong>
                                </div>
                                <div>
                                  <span className="text-slate-500 block text-[10px] uppercase">Std Dev</span>
                                  <strong className="text-slate-200 font-mono">{formatNumber(col.std)}</strong>
                                </div>
                                <div>
                                  <span className="text-slate-500 block text-[10px] uppercase">Median (50%)</span>
                                  <strong className="text-slate-200 font-mono">{formatNumber(col.median)}</strong>
                                </div>
                                <div>
                                  <span className="text-slate-500 block text-[10px] uppercase">25% (Q1)</span>
                                  <strong className="text-slate-200 font-mono">{formatNumber(col.q25)}</strong>
                                </div>
                                <div>
                                  <span className="text-slate-500 block text-[10px] uppercase">75% (Q3)</span>
                                  <strong className="text-slate-200 font-mono">{formatNumber(col.q75)}</strong>
                                </div>
                                <div>
                                  <span className="text-slate-500 block text-[10px] uppercase">Skewness</span>
                                  <strong className="text-slate-200 font-mono">{formatNumber(col.skewness)}</strong>
                                </div>
                              </>
                            ) : (
                              <div className="col-span-6">
                                <span className="text-slate-400 block text-[11px] font-semibold mb-2">
                                  Top Category Frequencies:
                                </span>
                                <div className="flex flex-wrap gap-2">
                                  {Object.entries(col.top_categories || {}).map(([cat, cnt]) => (
                                    <span
                                      key={cat}
                                      className="px-2.5 py-1 rounded-lg bg-surface-card border border-surface-border text-slate-300 font-mono text-[11px]"
                                    >
                                      {cat}: <strong className="text-brand-cyan">{cnt}</strong>
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
