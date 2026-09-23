"use client";

import { useState } from "react";
import { DataUniverseCanvas } from "./DataUniverseCanvas";
import { getEffectivePerformanceMode, useReducedMotion } from "./accessibility";
import { useDataUniverse } from "./useDataUniverse";
import { DataUniverseProps, PerformanceMode, PipelineStage, PipelineStageId } from "./types";

export function DataUniverseShell({
  session,
  mlResults,
  performanceMode,
  onStageSelect,
}: DataUniverseProps) {
  const [requestedMode, setRequestedMode] = useState<PerformanceMode>(performanceMode);
  const [selectedStage, setSelectedStage] = useState<PipelineStageId | null>(null);
  const reducedMotion = useReducedMotion();
  const effectiveMode = getEffectivePerformanceMode(requestedMode, reducedMotion);
  const snapshot = useDataUniverse(session, mlResults);
  const reduced = effectiveMode === "reduced";

  const selectStage = (stage: PipelineStage) => {
    setSelectedStage(stage.id);
    onStageSelect(stage.id);
  };

  const fallback = (
    <div className="flex h-full flex-col justify-center px-6 text-center">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#d0a46a]">Data Universe</p>
      <p className="mt-2 text-sm text-slate-300">The 3D layer is disabled. Use the accessible pipeline controls below.</p>
    </div>
  );

  return (
    <section className="mb-8 border-y border-[#304548] bg-[#142126] px-4 py-5 sm:px-6" aria-labelledby="data-universe-title">
      <div className="mx-auto max-w-[1500px]">
        <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-[#8bb7ac]">Contextual data map</p>
            <h2 id="data-universe-title" className="mt-1 text-lg font-bold text-slate-100">Data Universe</h2>
            <p className="mt-1 max-w-2xl text-xs leading-relaxed text-slate-400">
              A bounded view of the active dataset: {snapshot.datasetSize.toLocaleString()} rows, {snapshot.columnCount} columns, {snapshot.numericColumnCount} numeric and {snapshot.categoricalColumnCount} categorical fields.
            </p>
          </div>
          <label className="flex items-center gap-2 text-xs text-slate-400">
            <span>3D detail</span>
            <select
              value={requestedMode}
              onChange={(event) => setRequestedMode(event.target.value as PerformanceMode)}
              className="rounded-lg border border-[#3b5355] bg-[#101b20] px-2.5 py-1.5 text-xs text-slate-200 outline-none focus:border-[#8bb7ac]"
              aria-label="3D performance mode"
            >
              <option value="full">Full</option>
              <option value="reduced">Reduced</option>
              <option value="off">Off</option>
            </select>
          </label>
        </div>

        {effectiveMode === "off" ? fallback : (
          <DataUniverseCanvas
            snapshot={snapshot}
            selectedStage={selectedStage}
            onStageSelect={selectStage}
            reduced={reduced}
            fallback={fallback}
          />
        )}

        <nav className="mt-4" aria-label="Data Universe pipeline stages">
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-5 lg:grid-cols-10">
            {snapshot.stages.map((stage) => (
              <button
                key={stage.id}
                type="button"
                onClick={() => selectStage(stage)}
                aria-pressed={selectedStage === stage.id}
                className={`min-h-[58px] rounded-lg border px-2 py-2 text-left transition-colors focus:outline-none focus:ring-2 focus:ring-[#d0a46a] ${selectedStage === stage.id ? "border-[#d0a46a] bg-[#2a302a]" : "border-[#304548] bg-[#101b20] hover:border-[#8bb7ac]"}`}
              >
                <span className="block text-[10px] font-bold tracking-[0.12em] text-slate-200">{stage.label}</span>
                <span className="mt-1 block text-[10px] text-slate-500">{stage.status === "complete" ? "Complete" : stage.status === "active" ? "Active" : "Ready"}</span>
              </button>
            ))}
          </div>
        </nav>

        <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-[11px] text-slate-400">
          <span>Missing data: <strong className="text-slate-200">{snapshot.missingPercentage.toFixed(1)}%</strong></span>
          <span>Quality issues: <strong className="text-slate-200">{snapshot.qualityIssueCount}</strong></span>
          <span>Target: <strong className="text-slate-200">{snapshot.targetColumn ?? "Unassigned"}</strong></span>
          <span>Model: <strong className="text-slate-200">{snapshot.bestModel ?? "Not trained"}</strong></span>
        </div>
      </div>
    </section>
  );
}
