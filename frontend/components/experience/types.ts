import { DatasetSession, MlBenchmarkResults } from "@/types";
import { NavTab } from "@/components/layout/Sidebar";

export type ExperienceStageId =
  | "data"
  | "profile"
  | "clean"
  | "explore"
  | "statistics"
  | "target"
  | "ml"
  | "predict"
  | "insights"
  | "report";

export interface ExperienceStage {
  id: ExperienceStageId;
  label: string;
  detail: string;
  tab: NavTab;
}

export interface ExperienceShellProps {
  session: DatasetSession | null;
  mlResults: MlBenchmarkResults | null;
  activeTab: NavTab;
  onNavigate: (tab: NavTab) => void;
  insightsReady?: boolean;
  reportReady?: boolean;
  showHero?: boolean;
  children: React.ReactNode;
}
