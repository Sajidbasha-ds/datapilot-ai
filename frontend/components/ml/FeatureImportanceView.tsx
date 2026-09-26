"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { BarChart2, Info } from "lucide-react";
import { formatNumber } from "@/lib/utils";

interface FeatureImportanceViewProps {
  features: Array<{
    feature: string;
    importance: number;
    method?: string;
    coefficient?: number;
    direction?: string;
    decision_class?: string;
    class_coefficients?: Array<{ class: string; coefficient: number }>;
  }>;
  modelName: string;
}

export const FeatureImportanceView: React.FC<FeatureImportanceViewProps> = ({
  features,
  modelName,
}) => {
  const isLogistic = modelName.includes("Logistic");
  const isLinear = isLogistic || modelName.includes("Ridge") || modelName.includes("Linear");
  const metricLabel = isLogistic
    ? "Absolute model coefficient (|β|)"
    : isLinear
      ? "Absolute model coefficient"
      : "Tree-based feature importance";

  const chartData = [...features]
    .sort((a, b) => a.importance - b.importance)
    .slice(-10);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-surface-border space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-surface-border">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-200 flex items-center space-x-2">
            <BarChart2 className="w-4 h-4 text-brand-cyan" />
            <span>Top Predictive Feature Attribution ({modelName})</span>
          </h3>
          <p className="text-xs text-slate-400 mt-0.5">
            Ranked by {metricLabel}. These model attributions describe associations, not causal effects.
          </p>
        </div>

        <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 border border-slate-700 text-slate-300">
          Top {chartData.length} Features
        </span>
      </div>

      {chartData.length > 0 ? (
        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
              <XAxis type="number" stroke="#64748B" fontSize={11} tickLine={false} />
              <YAxis
                type="category"
                dataKey="feature"
                stroke="#CBD5E1"
                fontSize={11}
                tickLine={false}
                width={95}
              />
              <Tooltip
                formatter={(val: any, _name: string, item: any) => {
                  const feature = item?.payload;
                  if (isLogistic && typeof feature?.coefficient === "number") {
                    const sign = feature.coefficient > 0 ? "positive" : feature.coefficient < 0 ? "negative" : "zero";
                    return [`β ${feature.coefficient.toFixed(4)} (${sign}; |β| ${formatNumber(val, 4)})`, `Decision score for ${feature.decision_class ?? "positive class"}`];
                  }
                  if (isLogistic && feature?.class_coefficients?.length) {
                    const classes = feature.class_coefficients
                      .map((entry: { class: string; coefficient: number }) => `${entry.class}: ${entry.coefficient.toFixed(4)}`)
                      .join(", ");
                    return [`Max |β| ${formatNumber(val, 4)}; ${classes}`, "Class-specific coefficients"];
                  }
                  return [formatNumber(val, 4), metricLabel];
                }}
                contentStyle={{
                  backgroundColor: "#0F172A",
                  borderColor: "rgba(148, 163, 184, 0.2)",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
              />
              <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={index === chartData.length - 1 ? "#38bdf8" : "#0284c7"}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="py-8 text-center text-xs text-slate-500">
          Model feature attribution is not available for this model architecture.
        </div>
      )}

      <div className="p-3 rounded-lg bg-surface-card border border-surface-border flex items-start space-x-2 text-[11px] text-slate-400">
        <Info className="w-4 h-4 text-brand-cyan shrink-0 mt-0.5" />
        <span>
          <strong className="text-slate-300 font-semibold">Attribution Note: </strong>
          {isLinear
            ? isLogistic
              ? "For binary Logistic Regression, coefficient sign indicates whether a transformed feature raises or lowers the decision score/log-odds for the positive class. Magnitudes depend on preprocessing and encoding; neither sign nor magnitude establishes causation."
              : "Absolute coefficient magnitudes describe the fitted model in transformed feature space. Their scale depends on preprocessing and they do not establish causation."
            : "Tree-based feature importance summarizes impurity reduction attributed to splits on each feature. It is model-specific and does not establish causation."}
        </span>
      </div>
    </div>
  );
};
