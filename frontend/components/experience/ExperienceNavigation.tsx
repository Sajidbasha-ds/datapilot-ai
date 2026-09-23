"use client";

import { ArrowUpRight } from "lucide-react";
import { DatasetSession, MlBenchmarkResults } from "@/types";
import { ExperienceStage, ExperienceStageId } from "./types";
import { NavTab } from "@/components/layout/Sidebar";

interface ExperienceNavigationProps {
  session: DatasetSession | null;
  mlResults: MlBenchmarkResults | null;
  activeTab: NavTab;
  onNavigate: (tab: NavTab) => void;
  insightsReady?: boolean;
  reportReady?: boolean;
}

const STAGES: ExperienceStage[] = [
  { id: "data", label: "DATA", detail: "Load", tab: "upload" },
  { id: "profile", label: "PROFILE", detail: "Map", tab: "profile" },
  { id: "clean", label: "CLEAN", detail: "Repair", tab: "quality" },
  { id: "explore", label: "EXPLORE", detail: "See", tab: "eda" },
  { id: "statistics", label: "STATISTICS", detail: "Measure", tab: "statistics" },
  { id: "target", label: "TARGET", detail: "Frame", tab: "quality" },
  { id: "ml", label: "ML", detail: "Evaluate", tab: "ml" },
  { id: "predict", label: "PREDICT", detail: "Apply", tab: "predict" },
  { id: "insights", label: "INSIGHTS", detail: "Explain", tab: "insights" },
  { id: "report", label: "REPORT", detail: "Deliver", tab: "reports" },
];

function isStageAvailable(stage: ExperienceStage, session: DatasetSession | null) {
  return stage.id === "data" || Boolean(session);
}

function stageIsComplete(
  stage: ExperienceStageId,
  session: DatasetSession | null,
  mlResults: MlBenchmarkResults | null,
  insightsReady: boolean,
  reportReady: boolean,
) {
  if (!session) return false;
  return (
    stage === "data" ||
    stage === "profile" ||
    (stage === "clean" && Boolean(session.is_cleaned)) ||
    (stage === "target" && Boolean(session.target_col)) ||
    (stage === "ml" && Boolean(mlResults)) ||
    (stage === "predict" && Boolean(mlResults)) ||
    (stage === "insights" && insightsReady) ||
    (stage === "report" && reportReady)
  );
}

export function ExperienceNavigation({
  session,
  mlResults,
  activeTab,
  onNavigate,
  insightsReady = false,
  reportReady = false,
}: ExperienceNavigationProps) {
  return (
    <nav className="experience-journey" aria-label="Dataset analysis journey">
      <div className="experience-journey-heading">
        <span className="experience-kicker">The analysis journey</span>
        <span className="experience-journey-line" aria-hidden="true" />
        <span className="experience-journey-note">Every stage opens the working view</span>
      </div>
      <ol className="experience-stage-list">
        {STAGES.map((stage, index) => {
          const available = isStageAvailable(stage, session);
          const selected = activeTab === stage.tab;
          const complete = stageIsComplete(stage.id, session, mlResults, insightsReady, reportReady);
          return (
            <li key={stage.id} className="experience-stage-item">
              <button
                type="button"
                disabled={!available}
                onClick={() => onNavigate(stage.tab)}
                className={`experience-stage-button ${selected ? "experience-stage-selected" : ""} ${complete ? "experience-stage-complete" : ""}`}
                aria-label={`${stage.label}: ${stage.detail}`}
                aria-current={selected ? "page" : undefined}
              >
                <span className="experience-stage-index">{String(index + 1).padStart(2, "0")}</span>
                <span>
                  <span className="experience-stage-label">{stage.label}</span>
                  <span className="experience-stage-detail">{complete ? "Complete" : stage.detail}</span>
                </span>
                <ArrowUpRight className="experience-stage-arrow" aria-hidden="true" />
              </button>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
