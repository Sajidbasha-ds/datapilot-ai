"use client";

import { ArrowDownRight, Database, ScanLine } from "lucide-react";
import { useState } from "react";
import { DatasetSession } from "@/types";

interface HeroSectionProps {
  session: DatasetSession | null;
  onBegin: () => void;
}

export function HeroSection({ session, onBegin }: HeroSectionProps) {
  const [pointer, setPointer] = useState({ x: 0, y: 0 });

  return (
    <section
      className="experience-hero"
      onPointerMove={(event) => {
        if (event.pointerType === "touch") return;
        const bounds = event.currentTarget.getBoundingClientRect();
        setPointer({
          x: (event.clientX - bounds.left) / bounds.width - 0.5,
          y: (event.clientY - bounds.top) / bounds.height - 0.5,
        });
      }}
      onPointerLeave={() => setPointer({ x: 0, y: 0 })}
      style={{ "--hero-x": `${pointer.x * 12}px`, "--hero-y": `${pointer.y * 8}px` } as React.CSSProperties}
    >
      <div className="experience-hero-grid" aria-hidden="true" />
      <div className="experience-hero-copy">
        <p className="experience-kicker">Autonomous data science system</p>
        <h1 className="experience-display-title">
          <span>Data</span>
          <span className="experience-display-indent">Pilot <em>AI</em></span>
        </h1>
        <h2 className="experience-hero-statement">Your data has a story.</h2>
        <p className="experience-hero-description">
          DataPilot turns raw data into evidence, models, predictions, and decisions through one observable analytical journey.
        </p>
        <button type="button" onClick={onBegin} className="experience-primary-action">
          <span>{session ? "Open data intake" : "Start analysis"}</span>
          <ArrowDownRight aria-hidden="true" />
        </button>
        {session && <button type="button" onClick={onBegin} className="experience-secondary-action">Explore dataset</button>}
      </div>

      <div className="experience-hero-signal" style={{ transform: "translate3d(var(--hero-x), var(--hero-y), 0)" }} aria-label="DataPilot status visualization">
        <div className="experience-signal-frame">
          <div className="experience-signal-topline">
            <span><ScanLine size={14} aria-hidden="true" /> LIVE WORKSPACE</span>
            <span>{session ? "DATA CONNECTED" : "AWAITING DATA"}</span>
          </div>
          <div className="experience-signal-core" aria-hidden="true">
            <span className="experience-signal-axis experience-signal-axis-x" />
            <span className="experience-signal-axis experience-signal-axis-y" />
            <span className="experience-signal-orbit experience-signal-orbit-one" />
            <span className="experience-signal-orbit experience-signal-orbit-two" />
            <span className="experience-signal-point experience-signal-point-one" />
            <span className="experience-signal-point experience-signal-point-two" />
            <span className="experience-signal-point experience-signal-point-three" />
          </div>
          <div className="experience-signal-footer">
            <Database size={15} aria-hidden="true" />
            <span>{session ? session.filename : "Your next dataset"}</span>
            {session && <strong>{session.rows.toLocaleString()} rows / {session.columns} cols</strong>}
          </div>
        </div>
      </div>
    </section>
  );
}
