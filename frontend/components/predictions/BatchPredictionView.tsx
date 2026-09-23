"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, Download, FileSpreadsheet, CheckCircle2, AlertCircle, Loader2, History } from "lucide-react";
import { BatchPredictionResult, DatasetSession } from "@/types";
import { predictBatch } from "@/lib/api";

interface BatchPredictionViewProps {
  session: DatasetSession;
}

export const BatchPredictionView: React.FC<BatchPredictionViewProps> = ({ session }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BatchPredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (file: File) => {
    setError(null);
    setLoading(true);
    try {
      const res = await predictBatch(session.session_id, file);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Batch scoring failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadCsv = () => {
    if (!result?.csv_data) return;
    const blob = new Blob([result.csv_data], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `scored_${session.filename}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-surface-border">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
              <FileSpreadsheet className="w-4 h-4 text-brand-cyan" />
              <span>High-Throughput Batch Scoring</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Upload unlabelled CSV datasets to append real-time model predictions and class confidence scores.
            </p>
          </div>

          {result && (
            <button
              onClick={handleDownloadCsv}
              className="py-2 px-4 rounded-xl text-xs font-bold text-white bg-brand-blue hover:bg-blue-500 transition flex items-center space-x-2 shadow-sm"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Scored CSV</span>
            </button>
          )}
        </div>

        {/* Upload Drop Zone */}
        <div
          onClick={() => !loading && fileInputRef.current?.click()}
          className="p-8 rounded-xl border-2 border-dashed border-slate-700 hover:border-brand-cyan/50 hover:bg-surface-card/60 transition text-center cursor-pointer"
        >
          <input
            type="file"
            ref={fileInputRef}
            className="hidden"
            accept=".csv"
            onChange={(e) => {
              if (e.target.files && e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
              }
            }}
          />

          {loading ? (
            <div className="py-4 space-y-2">
              <Loader2 className="w-8 h-8 text-brand-cyan animate-spin mx-auto" />
              <p className="text-xs text-slate-300 font-semibold">Running batch inference pipeline...</p>
            </div>
          ) : (
            <div className="space-y-2">
              <UploadCloud className="w-8 h-8 text-brand-cyan mx-auto" />
              <p className="text-xs font-bold text-slate-200">
                Click to upload batch CSV for inference
              </p>
              <p className="text-[11px] text-slate-400">
                Must contain the features expected by the trained pipeline.
              </p>
            </div>
          )}
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-950/30 border border-status-error/40 flex items-start space-x-2.5 text-xs text-red-200">
            <AlertCircle className="w-4 h-4 text-status-error shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Batch Results Overview & Table Preview */}
      {result && (
        <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-surface-card border border-surface-border">
              <span className="text-slate-400 text-[10px] uppercase font-bold block">Total Rows Scored</span>
              <strong className="text-lg font-bold text-slate-100 font-mono">
                {result.total_rows.toLocaleString()}
              </strong>
            </div>

            <div className="p-3 rounded-lg bg-surface-card border border-surface-border">
              <span className="text-slate-400 text-[10px] uppercase font-bold block">Status</span>
              <strong className="text-lg font-bold text-emerald-400 flex items-center space-x-1">
                <CheckCircle2 className="w-4 h-4" />
                <span>100% Complete</span>
              </strong>
            </div>

            <div className="p-3 rounded-lg bg-surface-card border border-surface-border">
              <span className="text-slate-400 text-[10px] uppercase font-bold block">Output Columns Added</span>
              <strong className="text-lg font-bold text-brand-sky font-mono">
                Prediction, Confidence
              </strong>
            </div>

            <div className="p-3 rounded-lg bg-surface-card border border-surface-border flex items-center justify-end">
              <button
                onClick={handleDownloadCsv}
                className="w-full py-2.5 rounded-lg text-xs font-bold text-white bg-gradient-to-r from-brand-blue to-brand-cyan hover:from-blue-500 hover:to-cyan-400 transition flex items-center justify-center space-x-1.5"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export CSV</span>
              </button>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-surface-border">
            <table className="w-full text-xs text-left">
              <thead className="bg-surface-hover/80 text-slate-400 text-[10px] font-semibold uppercase tracking-wider border-b border-surface-border">
                <tr>
                  {result.preview.length > 0 &&
                    Object.keys(result.preview[0]).map((key) => (
                      <th
                        key={key}
                        className={`py-3 px-3 truncate max-w-[120px] ${
                          key.includes("Prediction") || key.includes("Confidence")
                            ? "bg-brand-cyan/10 text-brand-sky font-bold"
                            : ""
                        }`}
                      >
                        {key}
                      </th>
                    ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border text-slate-300 font-mono">
                {result.preview.slice(0, 15).map((row, idx) => (
                  <tr key={idx} className="hover:bg-surface-hover/50 transition">
                    {Object.entries(row).map(([k, val]: [string, any], cIdx) => (
                      <td
                        key={cIdx}
                        className={`py-2.5 px-3 truncate max-w-[120px] ${
                          k.includes("Prediction")
                            ? "font-bold text-brand-sky bg-brand-blue/5"
                            : k.includes("Confidence")
                            ? "font-bold text-brand-cyan"
                            : ""
                        }`}
                      >
                        {typeof val === "number" ? val.toFixed(2) : String(val ?? "")}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
