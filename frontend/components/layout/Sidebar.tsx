"use client";

import React from "react";
import {
  LayoutDashboard,
  UploadCloud,
  FileSpreadsheet,
  ShieldCheck,
  BarChart3,
  Calculator,
  Cpu,
  Zap,
  Lightbulb,
  FileDown,
  Target,
  X,
} from "lucide-react";
import { DatasetSession } from "@/types";

export type NavTab =
  | "overview"
  | "upload"
  | "profile"
  | "quality"
  | "eda"
  | "statistics"
  | "ml"
  | "predict"
  | "insights"
  | "reports";

interface SidebarProps {
  currentTab: NavTab;
  onSelectTab: (tab: NavTab) => void;
  session: DatasetSession | null;
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

const NAV_ITEMS: Array<{
  id: NavTab;
  label: string;
  icon: React.ElementType;
  badge?: string;
}> = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "upload", label: "Dataset Upload", icon: UploadCloud },
  { id: "profile", label: "Data Profile", icon: FileSpreadsheet },
  { id: "quality", label: "Data Quality", icon: ShieldCheck },
  { id: "eda", label: "EDA Dashboard", icon: BarChart3 },
  { id: "statistics", label: "Statistics", icon: Calculator },
  { id: "ml", label: "ML Lab", icon: Cpu, badge: "Core" },
  { id: "predict", label: "Predictions", icon: Zap },
  { id: "insights", label: "AI Insights & Chat", icon: Lightbulb },
  { id: "reports", label: "PDF Reports", icon: FileDown },
];

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  session,
  mobileOpen = false,
  onCloseMobile,
}) => {
  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          className="fixed inset-0 z-40 bg-black/60"
          onClick={onCloseMobile}
          aria-label="Close navigation"
        />
      )}
      <aside className={`fixed inset-y-[57px] left-0 z-50 flex h-auto w-[min(20rem,85vw)] flex-col justify-between border-r border-surface-border bg-surface/95 backdrop-blur-md transition-transform duration-200 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
      {/* Navigation List */}
      <div className="py-5 px-3 space-y-1 overflow-y-auto">
        <div className="mb-2 flex items-center justify-between px-3">
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">Navigation Flow</span>
          <button type="button" onClick={onCloseMobile} className="rounded-md p-1 text-slate-400 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d3a86c]" aria-label="Close navigation">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
          Navigation Flow
        </div>
        {NAV_ITEMS.map((item, idx) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          const isEnabled = item.id === "overview" || item.id === "upload" || !!session;

          return (
            <button
              key={item.id}
              disabled={!isEnabled}
              onClick={() => {
                onSelectTab(item.id);
                onCloseMobile?.();
              }}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition group ${
                isActive
                  ? "bg-gradient-to-r from-brand-blue/20 to-brand-cyan/15 text-brand-sky border border-brand-cyan/30 shadow-sm"
                  : isEnabled
                  ? "text-slate-300 hover:text-white hover:bg-surface-hover/80"
                  : "text-slate-600 cursor-not-allowed opacity-50"
              }`}
            >
              <div className="flex items-center space-x-3">
                <span className={`text-[11px] font-mono ${isActive ? "text-brand-cyan" : "text-slate-500"}`}>
                  0{idx + 1}
                </span>
                <Icon
                  className={`w-4 h-4 transition ${
                    isActive ? "text-brand-cyan" : "text-slate-400 group-hover:text-slate-200"
                  }`}
                />
                <span className="truncate">{item.label}</span>
              </div>

              {item.badge && (
                <span className="text-[9px] uppercase font-extrabold px-1.5 py-0.5 rounded bg-brand-cyan/20 text-brand-sky border border-brand-cyan/30">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Bottom Session Summary Card */}
      {session && (
        <div className="p-3 border-t border-surface-border bg-surface-card/40 m-2 rounded-xl">
          <div className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
            <span>Session Status</span>
            <span className="w-1.5 h-1.5 rounded-full bg-status-success animate-pulse" />
          </div>

          <div className="space-y-1 text-xs">
            <div className="text-slate-200 font-medium truncate" title={session.filename}>
              {session.filename}
            </div>
            <div className="text-[11px] text-slate-400 flex items-center justify-between">
              <span>Shape:</span>
              <span className="font-mono text-slate-300">
                {session.rows}r × {session.columns}c
              </span>
            </div>
            {session.target_col && (
              <div className="text-[11px] text-slate-400 flex items-center justify-between">
                <span>Target:</span>
                <span className="font-semibold text-brand-cyan truncate max-w-[100px]">
                  {session.target_col}
                </span>
              </div>
            )}
            {session.problem_type && (
              <div className="text-[11px] text-slate-400 flex items-center justify-between">
                <span>Task:</span>
                <span className="text-slate-300 font-medium truncate max-w-[105px]">
                  {session.problem_type}
                </span>
              </div>
            )}
          </div>
        </div>
      )}
      </aside>
    </>
  );
};
