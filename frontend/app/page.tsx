"use client";

import { useEffect, useState, type ReactNode } from "react";
import dynamic from "next/dynamic";
import { AlertCircle, FileDown, Loader2, Menu, MessageCircle, Send } from "lucide-react";
import { EdaDashboard } from "@/components/eda/EdaDashboard";
import { Header } from "@/components/layout/Header";
import { NavTab, Sidebar } from "@/components/layout/Sidebar";
import { MlLabView } from "@/components/ml/MlLabView";
import { MetricOverview } from "@/components/overview/MetricOverview";
import { PipelineProgress } from "@/components/overview/PipelineProgress";
import { BatchPredictionView } from "@/components/predictions/BatchPredictionView";
import { SinglePredictionView } from "@/components/predictions/SinglePredictionView";
import { DataProfileView } from "@/components/profile/DataProfileView";
import { DataQualityView } from "@/components/profile/DataQualityView";
import { StatisticsView } from "@/components/statistics/StatisticsView";
import { DatasetUpload } from "@/components/upload/DatasetUpload";
import { PipelineStageId } from "@/components/data-universe/types";
import { ExperienceShell } from "@/components/experience/ExperienceShell";
import {
  fetchSamples,
  generateInsights,
  generateReport,
  getReportDownloadUrl,
  sendChatMessage,
} from "@/lib/api";
import {
  AiInsightsData,
  ChatMessage,
  DatasetSession,
  MlBenchmarkResults,
  SampleDataset,
} from "@/types";

const TAB_TITLES: Record<NavTab, string> = {
  overview: "Analysis Overview",
  upload: "Dataset Upload",
  profile: "Data Profile",
  quality: "Data Quality",
  eda: "Exploratory Data Analysis",
  statistics: "Statistical Analysis",
  ml: "Machine Learning Lab",
  predict: "Predictions",
  insights: "AI Insights & Chat",
  reports: "Executive Reports",
};

const DataUniverseShell = dynamic(
  () => import("@/components/data-universe/DataUniverseShell").then((module) => module.DataUniverseShell),
  {
    ssr: false,
    loading: () => <div className="mb-8 h-[500px] animate-pulse border-y border-[#304548] bg-[#142126]" />,
  },
);

export default function HomePage() {
  const [currentTab, setCurrentTab] = useState<NavTab>("overview");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [session, setSession] = useState<DatasetSession | null>(null);
  const [samples, setSamples] = useState<SampleDataset[]>([]);
  const [mlResults, setMlResults] = useState<MlBenchmarkResults | null>(null);
  const [insights, setInsights] = useState<AiInsightsData | null>(null);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [chatMessage, setChatMessage] = useState("");
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [loadingReport, setLoadingReport] = useState(false);
  const [reportReady, setReportReady] = useState(false);
  const [sendingChat, setSendingChat] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSamples().then(setSamples).catch((requestError: Error) => setError(requestError.message));
  }, []);

  const handleDatasetLoaded = (nextSession: DatasetSession) => {
    setSession(nextSession);
    setMlResults(null);
    setInsights(null);
    setChatHistory([]);
    setReportReady(false);
    setError(null);
    setCurrentTab("overview");
  };

  const handleReset = () => {
    setSession(null);
    setMlResults(null);
    setInsights(null);
    setChatHistory([]);
    setReportReady(false);
    setError(null);
    setCurrentTab("upload");
  };

  const handleNavigate = (tab: NavTab) => {
    setCurrentTab(tab);
    setMobileNavOpen(false);
  };

  const handleResultsUpdated = (results: MlBenchmarkResults) => {
    setMlResults(results);
    setInsights(null);
  };

  const handleUniverseStageSelect = (stage: PipelineStageId) => {
    const stageTabs: Record<PipelineStageId, NavTab> = {
      data: "upload",
      profile: "profile",
      clean: "quality",
      explore: "eda",
      statistics: "statistics",
      target: "quality",
      ml: "ml",
      predict: "predict",
      insights: "insights",
      report: "reports",
    };
    handleNavigate(stageTabs[stage]);
  };

  const handleLoadInsights = async () => {
    if (!session) return;
    setLoadingInsights(true);
    setError(null);
    try {
      setInsights(await generateInsights(session.session_id));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to generate insights");
    } finally {
      setLoadingInsights(false);
    }
  };

  const handleSendChat = async () => {
    if (!session || !chatMessage.trim()) return;
    setSendingChat(true);
    setError(null);
    try {
      const response = await sendChatMessage(session.session_id, chatMessage.trim());
      setChatHistory(response.history);
      setChatMessage("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to send message");
    } finally {
      setSendingChat(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!session) return;
    setLoadingReport(true);
    setError(null);
    try {
      await generateReport(session.session_id);
      setReportReady(true);
      window.location.assign(getReportDownloadUrl(session.session_id));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Failed to generate report");
    } finally {
      setLoadingReport(false);
    }
  };

  const frameView = (content: ReactNode, showHero = false) => (
    <ExperienceShell
      session={session}
      mlResults={mlResults}
      activeTab={currentTab}
      onNavigate={handleNavigate}
      insightsReady={Boolean(insights)}
      reportReady={reportReady}
      showHero={showHero}
    >
      {content}
    </ExperienceShell>
  );

  const renderContent = () => {
    if (currentTab === "upload") {
      return frameView(<DatasetUpload onDatasetLoaded={handleDatasetLoaded} samples={samples} />, true);
    }

    if (!session && currentTab === "overview") {
      return (
        <ExperienceShell
          session={null}
          mlResults={null}
          activeTab={currentTab}
          onNavigate={handleNavigate}
          showHero
        >
          <DatasetUpload onDatasetLoaded={handleDatasetLoaded} samples={samples} />
        </ExperienceShell>
      );
    }

    if (!session) {
      return (
        <div className="glass-panel rounded-2xl border border-surface-border p-12 text-center">
          <h2 className="text-lg font-bold text-slate-100">Load a dataset to begin</h2>
          <p className="mt-2 text-sm text-slate-400">Upload a CSV/XLSX file or choose one of the available sample datasets.</p>
          <button
            type="button"
            onClick={() => setCurrentTab("upload")}
            className="mt-5 rounded-xl bg-brand-blue px-4 py-2 text-xs font-bold text-white hover:bg-blue-500"
          >
            Open Dataset Upload
          </button>
        </div>
      );
    }

    switch (currentTab) {
      case "overview":
        return (
          <ExperienceShell
            session={session}
            mlResults={mlResults}
            activeTab={currentTab}
            onNavigate={handleNavigate}
            insightsReady={Boolean(insights)}
            reportReady={reportReady}
          >
            <DataUniverseShell
              session={session}
              mlResults={mlResults}
              performanceMode="full"
              onStageSelect={handleUniverseStageSelect}
            />
            <MetricOverview session={session} mlResults={mlResults} />
            <PipelineProgress session={session} mlResults={mlResults} onNavigate={handleNavigate} />
          </ExperienceShell>
        );
      case "profile":
        return frameView(<DataProfileView session={session} />);
      case "quality":
        return frameView(<DataQualityView session={session} onSessionUpdated={setSession} />);
      case "eda":
        return frameView(<EdaDashboard session={session} />);
      case "statistics":
        return frameView(<StatisticsView session={session} />);
      case "ml":
        return frameView(<MlLabView session={session} mlResults={mlResults} onResultsUpdated={handleResultsUpdated} />);
      case "predict":
        return frameView(
          <div className="space-y-6">
            <SinglePredictionView session={session} />
            <BatchPredictionView session={session} />
          </div>
        );
      case "insights":
        return frameView(
          <div className="space-y-6">
            <section className="glass-panel rounded-2xl border border-surface-border p-6">
              <div className="flex items-center justify-between gap-4 border-b border-surface-border pb-4">
                <div>
                  <h2 className="text-base font-bold text-slate-100">Grounded Dataset Insights</h2>
                  <p className="mt-1 text-xs text-slate-400">Generated from the active dataset and trained model state.</p>
                </div>
                <button
                  type="button"
                  onClick={handleLoadInsights}
                  disabled={loadingInsights}
                  className="flex items-center gap-2 rounded-xl bg-brand-blue px-4 py-2 text-xs font-bold text-white hover:bg-blue-500 disabled:opacity-50"
                >
                  {loadingInsights ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <MessageCircle className="h-3.5 w-3.5" />}
                  Generate Insights
                </button>
              </div>
              {insights ? (
                <div className="mt-5 grid gap-5 md:grid-cols-2">
                  <InsightList title="Executive Insights" items={insights.executive_insights} />
                  <InsightList title="Technical Insights" items={insights.technical_insights} />
                </div>
              ) : (
                <p className="py-10 text-center text-xs text-slate-500">Generate insights to inspect the active analysis.</p>
              )}
            </section>
            <section className="glass-panel rounded-2xl border border-surface-border p-6">
              <div className="flex items-center gap-2 border-b border-surface-border pb-4">
                <MessageCircle className="h-4 w-4 text-brand-cyan" />
                <h2 className="text-base font-bold text-slate-100">Ask DataPilot</h2>
              </div>
              <div className="mt-4 max-h-80 space-y-3 overflow-y-auto">
                {chatHistory.map((message, index) => (
                  <div key={`${message.role}-${index}`} className={`rounded-xl p-3 text-xs ${message.role === "user" ? "ml-8 bg-brand-blue/10 text-sky-200" : "mr-8 bg-surface-card text-slate-300"}`}>
                    <span className="mb-1 block text-[10px] font-bold uppercase text-slate-500">{message.role}</span>
                    {message.content}
                  </div>
                ))}
              </div>
              <div className="mt-4 flex gap-2">
                <input
                  value={chatMessage}
                  onChange={(event) => setChatMessage(event.target.value)}
                  onKeyDown={(event) => { if (event.key === "Enter") void handleSendChat(); }}
                  placeholder="Ask about the active dataset"
                  className="min-w-0 flex-1 rounded-xl border border-surface-border bg-surface-card px-3 py-2 text-xs text-slate-100 outline-none focus:border-brand-cyan"
                />
                <button type="button" onClick={() => void handleSendChat()} disabled={sendingChat || !chatMessage.trim()} className="rounded-xl bg-brand-cyan px-3 text-white disabled:opacity-50" aria-label="Send question">
                  {sendingChat ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                </button>
              </div>
            </section>
          </div>
        );
      case "reports":
        return frameView(
          <section className="glass-panel rounded-2xl border border-surface-border p-6">
            <div className="flex items-center justify-between gap-4 border-b border-surface-border pb-4">
              <div>
                <h2 className="text-base font-bold text-slate-100">Executive PDF Report</h2>
                <p className="mt-1 text-xs text-slate-400">Generate a report from the active profiling, quality, ML, and insight results.</p>
              </div>
              <button type="button" onClick={() => void handleGenerateReport()} disabled={loadingReport} className="flex items-center gap-2 rounded-xl bg-brand-blue px-4 py-2 text-xs font-bold text-white hover:bg-blue-500 disabled:opacity-50">
                {loadingReport ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <FileDown className="h-3.5 w-3.5" />}
                Generate & Download
              </button>
            </div>
            <p className="py-10 text-center text-xs text-slate-500">The report uses only results calculated for {session.filename}.</p>
          </section>
        );
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <Header session={session} onReset={handleReset} />
      <div className="flex min-h-0 flex-1">
        <Sidebar
          currentTab={currentTab}
          onSelectTab={setCurrentTab}
          session={session}
          mobileOpen={mobileNavOpen}
          onCloseMobile={() => setMobileNavOpen(false)}
        />
        <main className="min-w-0 flex-1 overflow-y-auto bg-[radial-gradient(circle_at_top,rgba(14,165,233,0.12),transparent_38%)] p-4 sm:p-6 lg:p-8">
          <div className="mx-auto max-w-[1500px]">
            <div className="mb-6 flex items-center justify-between gap-4">
              <div>
                <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-brand-cyan">DataPilot workspace</p>
                <h1 className="mt-1 text-2xl font-extrabold text-slate-100">{TAB_TITLES[currentTab]}</h1>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setMobileNavOpen(true)}
                  className="rounded-lg border border-surface-border bg-surface-card p-2 text-slate-300 hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#d3a86c]"
                  aria-label="Open navigation"
                  aria-expanded={mobileNavOpen}
                >
                  <Menu className="h-4 w-4" />
                </button>
                {session && <span className="hidden rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-xs text-slate-400 sm:inline">{session.filename}</span>}
              </div>
            </div>
            {error && (
              <div className="mb-5 flex items-start gap-2 rounded-xl border border-status-error/40 bg-red-950/30 p-3 text-xs text-red-200">
                <AlertCircle className="h-4 w-4 shrink-0 text-status-error" />
                <span>{error}</span>
              </div>
            )}
            {renderContent()}
          </div>
        </main>
      </div>
    </div>
  );
}

function InsightList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">{title}</h3>
      <ul className="mt-3 space-y-2 text-xs text-slate-400">
        {items.map((item, index) => <li key={`${title}-${index}`} className="rounded-lg border border-surface-border bg-surface-card p-3">{item}</li>)}
      </ul>
    </div>
  );
}
