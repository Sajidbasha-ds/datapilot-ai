"use client";

import React, { useState } from "react";
import { Sparkles, Database, FileText, Activity, HelpCircle, RefreshCw, Layers } from "lucide-react";
import { DatasetSession } from "@/types";

interface HeaderProps {
  session: DatasetSession | null;
  onReset: () => void;
}

export const Header: React.FC<HeaderProps> = ({ session, onReset }) => {
  const [showHelp, setShowHelp] = useState(false);

  return (
    <header className="sticky top-0 z-40 w-full border-b border-surface-border bg-surface/80 backdrop-blur-xl px-6 py-3.5 flex items-center justify-between">
      {/* Brand & Subtitle */}
      <div className="flex items-center space-x-3.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-blue to-brand-cyan flex items-center justify-center shadow-glow text-white">
          <Sparkles className="w-5 h-5 animate-pulse" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-blue-400 via-sky-300 to-cyan-400 bg-clip-text text-transparent">
              DATAPILOT AI
            </h1>
            <span className="px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded-full bg-brand-cyan/15 text-brand-sky border border-brand-cyan/30">
              v2.0 Autonomous
            </span>
          </div>
          <p className="text-xs text-slate-400 font-medium">
            Autonomous AI Data Scientist & ML Intelligence Platform
          </p>
        </div>
      </div>

      {/* Center / Status Indicator */}
      <div className="hidden md:flex items-center space-x-3 text-xs">
        {session ? (
          <div className="flex items-center space-x-2.5 px-3 py-1.5 rounded-lg bg-surface-card border border-surface-border">
            <span className="w-2 h-2 rounded-full bg-status-success animate-ping" />
            <span className="text-slate-400">Active Dataset:</span>
            <span className="font-semibold text-slate-200 truncate max-w-[180px]">
              {session.filename}
            </span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-300 font-mono">
              {session.rows.toLocaleString()} × {session.columns}
            </span>
          </div>
        ) : (
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-surface-card/60 border border-surface-border text-slate-400">
            <span className="w-2 h-2 rounded-full bg-slate-500" />
            <span>No dataset loaded</span>
          </div>
        )}
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2.5">
        {session && (
          <button
            onClick={onReset}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 bg-slate-800/80 hover:bg-slate-700 border border-slate-700 transition"
            title="Load another dataset"
          >
            <RefreshCw className="w-3.5 h-3.5 text-slate-400" />
            <span className="hidden sm:inline">New Analysis</span>
          </button>
        )}

        <button
          onClick={() => setShowHelp(!showHelp)}
          className="p-2 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-surface-hover transition border border-transparent hover:border-surface-border"
          aria-label="Help & About"
        >
          <HelpCircle className="w-4 h-4" />
        </button>
      </div>

      {/* Help Modal */}
      {showHelp && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="glass-panel-glow max-w-lg w-full rounded-2xl p-6 relative">
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-2.5">
                <div className="w-8 h-8 rounded-lg bg-brand-cyan/20 flex items-center justify-center text-brand-cyan">
                  <Activity className="w-4 h-4" />
                </div>
                <h3 className="text-lg font-bold text-slate-100">About DataPilot AI</h3>
              </div>
              <button
                onClick={() => setShowHelp(false)}
                className="text-slate-400 hover:text-slate-200 text-lg font-bold p-1"
              >
                ✕
              </button>
            </div>

            <p className="text-sm text-slate-300 mb-4 leading-relaxed">
              DataPilot AI is an autonomous, full-stack machine learning workbench. It executes genuine statistical and ML pipelines without mock metrics or hallucinated insights.
            </p>

            <div className="space-y-2.5 text-xs text-slate-400 mb-6">
              <div className="flex items-start space-x-2">
                <span className="text-brand-cyan font-bold">•</span>
                <span><strong className="text-slate-200">Training-Split Controls:</strong> Preprocessing scalers and encoders are fitted on training data; checks reduce specific risks but cannot identify every leakage source.</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-brand-cyan font-bold">•</span>
                <span><strong className="text-slate-200">Real Benchmark:</strong> Compares candidates using cross-validation alongside held-out test evaluation.</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-brand-cyan font-bold">•</span>
                <span><strong className="text-slate-200">Production Reports:</strong> Generates downloadable, publication-quality executive PDF reports.</span>
              </div>
            </div>

            <div className="flex justify-end">
              <button
                onClick={() => setShowHelp(false)}
                className="px-4 py-2 text-xs font-semibold rounded-lg bg-brand-blue hover:bg-blue-500 text-white transition shadow-sm"
              >
                Got it
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};
