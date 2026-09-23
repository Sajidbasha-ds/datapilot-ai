"use client";

import React, { useState, useEffect } from "react";
import { Zap, Play, CheckCircle2, AlertCircle, Loader2, Sparkles, Sliders } from "lucide-react";
import { DatasetSession, PredictionSchema, SinglePredictionResult } from "@/types";
import { fetchPredictionSchema, predictSingle } from "@/lib/api";
import { formatNumber, formatPercent } from "@/lib/utils";

interface SinglePredictionViewProps {
  session: DatasetSession;
}

export const SinglePredictionView: React.FC<SinglePredictionViewProps> = ({ session }) => {
  const [schema, setSchema] = useState<PredictionSchema | null>(null);
  const [formValues, setFormValues] = useState<Record<string, any>>({});
  const [loadingSchema, setLoadingSchema] = useState(false);
  const [predicting, setPredicting] = useState(false);
  const [result, setResult] = useState<SinglePredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoadingSchema(true);
    fetchPredictionSchema(session.session_id)
      .then((sch) => {
        setSchema(sch);
        const defaults: Record<string, any> = {};
        sch.fields.forEach((f) => {
          defaults[f.name] = f.default ?? (f.type === "number" ? 0 : "");
        });
        setFormValues(defaults);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoadingSchema(false));
  }, [session.session_id]);

  const handleInputChange = (name: string, val: any) => {
    setFormValues((prev) => ({ ...prev, [name]: val }));
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredicting(true);
    setError(null);
    try {
      const res = await predictSingle(session.session_id, formValues);
      setResult(res);
    } catch (err: any) {
      setError(err.message || "Prediction failed");
    } finally {
      setPredicting(false);
    }
  };

  if (loadingSchema) {
    return (
      <div className="py-24 text-center glass-panel rounded-2xl border border-surface-border">
        <Loader2 className="w-8 h-8 text-brand-cyan animate-spin mx-auto mb-2" />
        <span className="text-xs text-slate-400">Inspecting model signature and compiling dynamic form...</span>
      </div>
    );
  }

  if (error && !schema) {
    return (
      <div className="p-8 text-center glass-panel rounded-2xl border border-surface-border space-y-3">
        <AlertCircle className="w-8 h-8 text-amber-400 mx-auto" />
        <h3 className="text-sm font-bold text-slate-200">No Trained Model Found</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto">
          Please run candidate model training in the <strong>ML Lab</strong> tab before performing live inference.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Form Area */}
      <div className="lg:col-span-2 glass-panel rounded-2xl p-6 border border-surface-border space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-surface-border">
          <div>
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
              <Zap className="w-4 h-4 text-brand-cyan" />
              <span>Single Record Real-Time Inference</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Powered by <strong className="text-brand-sky">{schema?.model_name}</strong> for {schema?.problem_type}
            </p>
          </div>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-400">
            Target: {schema?.target_col}
          </span>
        </div>

        <form onSubmit={handlePredict} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[420px] overflow-y-auto pr-2">
            {schema?.fields.map((field) => (
              <div key={field.name} className="space-y-1 text-xs">
                <label className="text-slate-300 font-semibold block truncate" title={field.name}>
                  {field.name}
                </label>
                {field.type === "number" ? (
                  <input
                    type="number"
                    step="any"
                    value={formValues[field.name] ?? ""}
                    onChange={(e) => handleInputChange(field.name, parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-card border border-surface-border text-slate-100 font-mono text-xs focus:outline-none focus:border-brand-cyan"
                    required
                  />
                ) : (
                  <select
                    value={formValues[field.name] ?? ""}
                    onChange={(e) => handleInputChange(field.name, e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-surface-card border border-surface-border text-slate-100 text-xs focus:outline-none focus:border-brand-cyan"
                    required
                  >
                    {field.options?.map((opt) => (
                      <option key={opt} value={opt}>{opt}</option>
                    ))}
                  </select>
                )}
              </div>
            ))}
          </div>

          <div className="pt-3 border-t border-surface-border flex justify-end">
            <button
              type="submit"
              disabled={predicting}
              className="py-2.5 px-6 rounded-xl text-xs font-bold text-white bg-gradient-to-r from-brand-blue to-brand-cyan hover:from-blue-500 hover:to-cyan-400 transition flex items-center space-x-2 shadow-sm disabled:opacity-50"
            >
              {predicting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Play className="w-3.5 h-3.5 fill-white" />}
              <span>Execute Real-Time Prediction</span>
            </button>
          </div>
        </form>
      </div>

      {/* Prediction Output Badge */}
      <div className="glass-panel-glow rounded-2xl p-6 border border-brand-cyan/30 flex flex-col justify-between">
        <div className="space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Inference Outcome
            </span>
            <span className="w-2 h-2 rounded-full bg-status-success animate-pulse" />
          </div>

          {result ? (
            <div className="space-y-4">
              <div>
                <span className="text-[11px] text-slate-400 block mb-1">
                  Predicted {schema?.target_col}:
                </span>
                <div className="text-3xl font-extrabold text-brand-sky font-mono bg-surface-card p-3 rounded-xl border border-surface-border truncate">
                  {result.prediction}
                </div>
              </div>

              {result.confidence !== null && (
                <div className="p-3.5 rounded-xl bg-surface-card border border-surface-border space-y-2 text-xs">
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400 font-semibold">Prediction Confidence:</span>
                    <span className="font-bold text-brand-cyan font-mono">
                      {(result.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-brand-cyan h-full rounded-full transition-all duration-500"
                      style={{ width: `${result.confidence * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {result.probabilities && Object.keys(result.probabilities).length > 0 && (
                <div className="space-y-1.5 text-xs">
                  <span className="text-slate-400 block text-[11px] font-semibold">
                    Class Probability Distribution:
                  </span>
                  <div className="space-y-1.5">
                    {Object.entries(result.probabilities).map(([cls, prob]) => (
                      <div key={cls} className="p-2 rounded-lg bg-surface/80 border border-surface-border flex justify-between items-center text-[11px] font-mono">
                        <span className="text-slate-300 truncate max-w-[120px]">{cls}</span>
                        <span className="text-slate-200 font-bold">{(prob * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="text-[10px] text-slate-500 pt-2 border-t border-slate-800">
                Audit Trail ID: #{result.log_id} (persisted in SQLite log)
              </div>
            </div>
          ) : (
            <div className="py-16 text-center space-y-2 text-xs text-slate-500">
              <Sparkles className="w-8 h-8 text-slate-600 mx-auto" />
              <p>Fill feature inputs and click predict to calculate outcomes.</p>
            </div>
          )}
        </div>

        <div className="pt-4 border-t border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Active Pipeline:</span>
          <span className="font-semibold text-slate-200 truncate max-w-[140px]">{schema?.model_name}</span>
        </div>
      </div>
    </div>
  );
};
