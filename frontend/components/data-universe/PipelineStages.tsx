import { Line } from "@react-three/drei";
import { PipelineStage, PipelineStageId } from "./types";
import { StageNode } from "./StageNode";

interface PipelineStagesProps {
  stages: PipelineStage[];
  selectedStage: PipelineStageId | null;
  onSelect: (stage: PipelineStage) => void;
  reduced: boolean;
}

const STAGE_POSITIONS: Array<[number, number, number]> = [
  [-4.4, 1.35, 0],
  [-3.45, 0.65, 0.15],
  [-2.55, 1.35, 0.05],
  [-1.6, 0.65, 0.2],
  [-0.65, 1.35, 0.05],
  [0.3, 0.65, 0.2],
  [1.25, 1.35, 0],
  [2.2, 0.65, 0.15],
  [3.15, 1.35, 0.05],
  [4.15, 0.65, 0.2],
];

export function PipelineStages({ stages, selectedStage, onSelect, reduced }: PipelineStagesProps) {
  const positions = reduced ? STAGE_POSITIONS.filter((_, index) => index % 2 === 0) : STAGE_POSITIONS;
  const visibleStages = reduced ? stages.filter((_, index) => index % 2 === 0) : stages;

  return (
    <group>
      <Line
        points={positions}
        color="#4d6970"
        lineWidth={reduced ? 1 : 1.4}
        transparent
        opacity={0.7}
      />
      {visibleStages.map((stage, index) => (
        <StageNode
          key={stage.id}
          stage={stage}
          position={positions[index]}
          selected={selectedStage === stage.id}
          onSelect={onSelect}
        />
      ))}
    </group>
  );
}
