"use client";

import React, { useState, useRef } from "react";
import { UploadCloud, FileSpreadsheet, CheckCircle2, AlertCircle, ArrowRight, Loader2, Sparkles } from "lucide-react";
import { DatasetSession, SampleDataset } from "@/types";
import { loadSample, uploadDataset } from "@/lib/api";

interface DatasetUploadProps {
  onDatasetLoaded: (session: DatasetSession) => void;
  samples: SampleDataset[];
}

export const DatasetUpload: React.FC<DatasetUploadProps> = ({ onDatasetLoaded, samples }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setLoading(true);
    setLoadingMsg(`Analyzing ${file.name}... profiling distributions & detecting schema`);
    try {
      const session = await uploadDataset(file);
      onDatasetLoaded(session);
    } catch (err: any) {
      setError(err.message || "Failed to process dataset");
    } finally {
      setLoading(false);
      setLoadingMsg("");
    }
  };

  const handleSample = async (sampleId: string, sampleName: string) => {
    setError(null);
    setLoading(true);
    setLoadingMsg(`Loading sample '${sampleName}'... calculating statistics`);
    try {
      const session = await loadSample(sampleId);
      onDatasetLoaded(session);
    } catch (err: any) {
      setError(err.message || "Failed to load sample dataset");
    } finally {
      setLoading(false);
      setLoadingMsg("");
    }
  };

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = () => {
    setIsDragging(false);
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-4">
      {/* Hero Welcome */}
      <div className="text-center space-y-3">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-brand-cyan/15 text-brand-sky border border-brand-cyan/25 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Zero Configuration Required</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-slate-100">
          Turn Raw Data into <span className="bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-400 bg-clip-text text-transparent">Decisions</span>
        </h2>
        <p className="text-sm text-slate-400 max-w-xl mx-auto leading-relaxed">
          Upload any CSV or XLSX file. DataPilot profiles features, repairs missingness, benchmarks candidate models, detects top predictors, and produces production audit reports.
        </p>
      </div>

      {/* Drag and Drop Box */}
      <div
        onDragOver={onDragOver}
        onDragLeave={onDragLeave}
        onDrop={onDrop}
        onClick={() => !loading && fileInputRef.current?.click()}
        className={`glass-panel rounded-2xl p-8 sm:p-12 text-center cursor-pointer transition border-2 border-dashed relative overflow-hidden group ${
          isDragging
            ? "border-brand-cyan bg-brand-cyan/5 shadow-glow"
            : "border-slate-700/80 hover:border-brand-sky/50 hover:bg-surface-card/60"
        }`}
      >
        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          accept=".csv,.xlsx,.xls"
          onChange={(e) => {
            if (e.target.files && e.target.files.length > 0) {
              handleFile(e.target.files[0]);
            }
          }}
        />

        {loading ? (
          <div className="space-y-4 py-6">
            <Loader2 className="w-12 h-12 text-brand-cyan animate-spin mx-auto" />
            <div className="space-y-1">
              <p className="text-base font-bold text-slate-200">{loadingMsg}</p>
              <p className="text-xs text-slate-400">Fitting statistical estimators & building profiles...</p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-blue/30 to-brand-cyan/20 border border-brand-cyan/30 flex items-center justify-center text-brand-sky mx-auto group-hover:scale-105 transition">
              <UploadCloud className="w-8 h-8" />
            </div>

            <div>
              <p className="text-base font-bold text-slate-200">
                Click to browse or drag & drop your dataset here
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports <strong className="text-slate-300">CSV, XLSX, XLS</strong> (up to 100 MB). Evaluated locally & serverless.
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Error Callout */}
      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-status-error/40 flex items-start space-x-3 text-red-200 text-xs">
          <AlertCircle className="w-4 h-4 text-status-error shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong className="block text-status-error font-semibold">Upload Failed</strong>
            <p>{error}</p>
          </div>
        </div>
      )}

      {/* Try Sample Datasets */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Or Explore Instant Sample Datasets
          </h3>
          <span className="text-[11px] text-slate-500">Real tabular data ready for ML benchmark</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
          {samples.map((s) => (
            <div
              key={s.id}
              onClick={() => !loading && handleSample(s.id, s.name)}
              className="p-4 rounded-xl border border-surface-border bg-surface-card hover:border-brand-cyan/40 hover:bg-surface-hover/80 transition cursor-pointer flex flex-col justify-between group shadow-sm"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <FileSpreadsheet className="w-4 h-4 text-brand-cyan" />
                    <span className="text-xs font-bold text-slate-200 group-hover:text-brand-sky transition">
                      {s.name}
                    </span>
                  </div>
                  <span className="text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                    {s.task.split(" ")[0]}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed mb-3">
                  {s.description}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px]">
                <span className="text-slate-400">
                  Target: <strong className="text-slate-200">{s.target}</strong>
                </span>
                <span className="text-brand-cyan flex items-center space-x-1 group-hover:translate-x-0.5 transition font-semibold">
                  <span>Load</span>
                  <ArrowRight className="w-3 h-3" />
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
