"use client";

import { HeroSection } from "./HeroSection";
import { ExperienceNavigation } from "./ExperienceNavigation";
import { TransitionLayer } from "./TransitionLayer";
import { DatasetStorySection } from "./DatasetStorySection";
import { ExperienceShellProps } from "./types";

export function ExperienceShell({
  session,
  mlResults,
  activeTab,
  onNavigate,
  insightsReady = false,
  reportReady = false,
  showHero = true,
  children,
}: ExperienceShellProps) {
  const chapterCopy: Record<string, { kicker: string; title: string }> = {
    profile: { kicker: "Chapter 02 / structure", title: "First, understand what exists." },
    quality: { kicker: "Chapter 03 / trust", title: "Before intelligence, there is trust." },
    eda: { kicker: "Chapter 04 / discovery", title: "Patterns begin to emerge." },
    statistics: { kicker: "Chapter 05 / evidence", title: "A pattern is not evidence." },
    ml: { kicker: "Chapter 07 / competition", title: "Now let the models compete." },
    predict: { kicker: "Chapter 08 / action", title: "From understanding to action." },
    insights: { kicker: "Chapter 09 / observatory", title: "What does the data actually tell us?" },
    reports: { kicker: "Chapter 10 / decision", title: "Turn analysis into a decision." },
  };
  const chapter = chapterCopy[activeTab];
  return (
    <div className="experience-shell">
      {showHero ? (
        <HeroSection session={session} onBegin={() => onNavigate("upload")} />
      ) : (
        <div className="experience-view-header">
          <div>
            <span className="experience-kicker">DataPilot analytical workspace</span>
            <h2>{session?.filename ?? "Dataset intake"}</h2>
          </div>
          {session && <span className="experience-view-status">{session.rows.toLocaleString()} rows / {session.columns} columns</span>}
        </div>
      )}
      {showHero && session && <DatasetStorySection session={session} mlResults={mlResults} />}
      {!showHero && chapter && (
        <div className="experience-chapter-intro">
          <span className="experience-kicker">{chapter.kicker}</span>
          <h2>{chapter.title}</h2>
        </div>
      )}
      <ExperienceNavigation
        session={session}
        mlResults={mlResults}
        activeTab={activeTab}
        onNavigate={onNavigate}
        insightsReady={insightsReady}
        reportReady={reportReady}
      />
      <TransitionLayer className="experience-content">
        {children}
      </TransitionLayer>
    </div>
  );
}
