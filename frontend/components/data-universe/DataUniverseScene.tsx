import { Float, PerspectiveCamera } from "@react-three/drei";
import { DataCore } from "./DataCore";
import { PipelineStages } from "./PipelineStages";
import { DataUniverseSnapshot, PipelineStage, PipelineStageId } from "./types";

interface DataUniverseSceneProps {
  snapshot: DataUniverseSnapshot;
  selectedStage: PipelineStageId | null;
  onStageSelect: (stage: PipelineStage) => void;
  reduced: boolean;
}

export function DataUniverseScene({
  snapshot,
  selectedStage,
  onStageSelect,
  reduced,
}: DataUniverseSceneProps) {
  return (
    <>
      <PerspectiveCamera makeDefault position={[0, 1.2, 9.5]} fov={34} />
      <ambientLight intensity={1.5} color="#d7e1d5" />
      <directionalLight position={[2, 4, 5]} intensity={2.2} color="#f0d8b1" />
      <directionalLight position={[-4, -1, 2]} intensity={0.8} color="#8db0a9" />
      <Float
        speed={reduced ? 0 : 0.35}
        rotationIntensity={reduced ? 0 : 0.08}
        floatIntensity={reduced ? 0 : 0.12}
      >
        <DataCore snapshot={snapshot} reduced={reduced} />
      </Float>
      <PipelineStages
        stages={snapshot.stages}
        selectedStage={selectedStage}
        onSelect={onStageSelect}
        reduced={reduced}
      />
    </>
  );
}
