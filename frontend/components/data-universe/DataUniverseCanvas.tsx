"use client";

import { Canvas } from "@react-three/fiber";
import { ReactNode } from "react";
import { DataUniverseScene } from "./DataUniverseScene";
import { DataUniverseSnapshot, PipelineStage, PipelineStageId } from "./types";

interface DataUniverseCanvasProps {
  snapshot: DataUniverseSnapshot;
  selectedStage: PipelineStageId | null;
  onStageSelect: (stage: PipelineStage) => void;
  reduced: boolean;
  fallback: ReactNode;
}

export function DataUniverseCanvas({
  snapshot,
  selectedStage,
  onStageSelect,
  reduced,
  fallback,
}: DataUniverseCanvasProps) {
  return (
    <div className="h-[360px] w-full overflow-hidden rounded-xl border border-[#3b5355] bg-[#101b20]" aria-label="Interactive Data Universe visualization">
      <Canvas
        dpr={reduced ? [1, 1] : [1, 1.5]}
        frameloop={reduced ? "demand" : "always"}
        gl={{ antialias: !reduced, powerPreference: "high-performance", alpha: false }}
        fallback={fallback}
      >
        <color attach="background" args={["#101b20"]} />
        <DataUniverseScene
          snapshot={snapshot}
          selectedStage={selectedStage}
          onStageSelect={onStageSelect}
          reduced={reduced}
        />
      </Canvas>
    </div>
  );
}
