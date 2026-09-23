"use client";

import { AlertTriangle, Binary, Database, Target } from "lucide-react";
import { DatasetSession, MlBenchmarkResults } from "@/types";

interface DatasetStorySectionProps {
  session: DatasetSession;
  mlResults: MlBenchmarkResults | null;
}

export function DatasetStorySection({ session, mlResults }: DatasetStorySectionProps) {
  const overview = session.profile.overview;
  const metrics = [
    { label: "Rows", value: overview.rows.toLocaleString(), detail: "observations", icon: Database },
    { label: "Columns", value: overview.columns.toString(), detail: "fields mapped", icon: Binary },
    { label: "Missing", value: `${overview.missing_pct}%`, detail: "of matrix cells", icon: AlertTriangle },
    { label: "Target", value: session.target_col ?? "Open", detail: session.problem_type ?? "not assigned", icon: Target },
  ];

  return (
    <section className="experience-story" aria-labelledby="dataset-story-title">
      <div className="experience-story-heading">
        <span className="experience-kicker">Active dataset / {session.filename}</span>
        <h2 id="dataset-story-title">The data is now in motion.</h2>
        <p>Structure first. Evidence next. The system keeps the original dataset visible while each analytical layer becomes available.</p>
      </div>
      <div className="experience-story-metrics">
        {metrics.map(({ label, value, detail, icon: Icon }) => (
          <div className="experience-story-metric" key={label}>
            <Icon aria-hidden="true" />
            <span className="experience-story-label">{label}</span>
            <strong>{value}</strong>
            <span className="experience-story-detail">{detail}</span>
          </div>
        ))}
      </div>
      <div className="experience-story-footer">
        <span><b>{overview.numerical_columns_count}</b> numeric</span>
        <span><b>{overview.categorical_columns_count}</b> categorical</span>
        <span><b>{session.quality.total_issues}</b> quality signals</span>
        <span><b>{mlResults ? mlResults.best_model_name : "No model yet"}</b></span>
      </div>
    </section>
  );
}
