import { Edges, Line } from "@react-three/drei";
import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import { Group } from "three";
import { DataUniverseSnapshot } from "./types";

interface DataCoreProps {
  snapshot: DataUniverseSnapshot;
  reduced: boolean;
}

interface CoreNode {
  position: [number, number, number];
  size: number;
  kind: "numeric" | "categorical" | "quality";
}

function buildNodes(snapshot: DataUniverseSnapshot, reduced: boolean): CoreNode[] {
  const nodeCount = Math.min(reduced ? 12 : 24, Math.max(6, snapshot.columnCount));
  const numericCount = Math.min(nodeCount, snapshot.numericColumnCount);
  const categoricalCount = Math.min(nodeCount - numericCount, snapshot.categoricalColumnCount);
  const qualityCount = Math.max(0, nodeCount - numericCount - categoricalCount);

  return Array.from({ length: nodeCount }, (_, index) => {
    const angle = (index / nodeCount) * Math.PI * 2;
    const ring = 1.15 + (index % 3) * 0.28;
    const kind = index < numericCount ? "numeric" : index < numericCount + categoricalCount ? "categorical" : "quality";
    return {
      position: [Math.cos(angle) * ring, Math.sin(angle) * ring * 0.7, ((index % 4) - 1.5) * 0.32] as [number, number, number],
      size: kind === "quality" ? 0.07 + Math.min(snapshot.missingPercentage / 100, 0.12) : 0.055 + Math.min(snapshot.datasetSize / 10000, 0.08),
      kind,
    };
  });
}

function nodeColor(kind: CoreNode["kind"], snapshot: DataUniverseSnapshot): string {
  if (kind === "numeric") return "#72a9a1";
  if (kind === "categorical") return "#d0a46a";
  return snapshot.qualityIssueCount > 0 ? "#c98267" : "#9bb6a5";
}

export function DataCore({ snapshot, reduced }: DataCoreProps) {
  const groupRef = useRef<Group>(null);
  const nodes = useMemo(() => buildNodes(snapshot, reduced), [reduced, snapshot]);
  const anchor: [number, number, number] = [0, 0, 0];

  useFrame((state, delta) => {
    if (!groupRef.current) return;
    const targetX = state.pointer.y * 0.08;
    const targetY = state.pointer.x * 0.12;
    groupRef.current.rotation.x += (targetX - groupRef.current.rotation.x) * delta * 2;
    groupRef.current.rotation.y += (targetY - groupRef.current.rotation.y) * delta * 2;
  });

  return (
    <group ref={groupRef} position={[0, -0.15, 0]}>
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[1.28, 0.92, 0.72]} />
        <meshStandardMaterial color="#27454a" roughness={0.72} metalness={0.18} />
      </mesh>
      <Edges scale={[1.28, 0.92, 0.72]} color="#8bb7ac" linewidth={0.8} />
      {nodes.map((node, index) => (
        <group key={`${node.kind}-${index}`}>
          <mesh position={node.position}>
            <sphereGeometry args={[node.size, reduced ? 6 : 8, reduced ? 4 : 6]} />
            <meshStandardMaterial color={nodeColor(node.kind, snapshot)} roughness={0.58} />
          </mesh>
          <Line
            points={[anchor, node.position]}
            color={nodeColor(node.kind, snapshot)}
            lineWidth={reduced ? 0.5 : 0.8}
            transparent
            opacity={reduced ? 0.16 : 0.3}
          />
        </group>
      ))}
    </group>
  );
}
