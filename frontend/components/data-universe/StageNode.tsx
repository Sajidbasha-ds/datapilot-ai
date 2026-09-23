import { Html } from "@react-three/drei";
import { ThreeEvent } from "@react-three/fiber";
import { useRef } from "react";
import { Mesh } from "three";
import { PipelineStage } from "./types";

interface StageNodeProps {
  stage: PipelineStage;
  position: [number, number, number];
  selected: boolean;
  onSelect: (stage: PipelineStage) => void;
}

export function StageNode({ stage, position, selected, onSelect }: StageNodeProps) {
  const meshRef = useRef<Mesh>(null);
  const isComplete = stage.status === "complete";

  const handleSelect = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    onSelect(stage);
  };

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={handleSelect}
        onPointerOver={(event) => event.stopPropagation()}
      >
        <boxGeometry args={[0.42, 0.42, 0.42]} />
        <meshStandardMaterial
          color={selected ? "#f0b86e" : isComplete ? "#78b9ad" : "#718096"}
          emissive={selected ? "#8a5a2b" : "#1c3739"}
          emissiveIntensity={selected ? 0.35 : 0.12}
          roughness={0.64}
          metalness={0.12}
        />
      </mesh>
      <Html center distanceFactor={8} position={[0, -0.5, 0]}>
        <span className={`pointer-events-none whitespace-nowrap text-[9px] font-bold tracking-[0.16em] ${selected ? "text-amber-200" : isComplete ? "text-emerald-200" : "text-slate-400"}`}>
          {stage.label}
        </span>
      </Html>
    </group>
  );
}
