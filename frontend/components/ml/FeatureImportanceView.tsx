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
  features: Array<{ feature: string; importance: number }>;
  modelName: string;
}

export const FeatureImportanceView: React.FC<FeatureImportanceViewProps> = ({
  features,
  modelName,
}) => {
  const isLinear = modelName.includes("Logistic") || modelName.includes("Ridge") || modelName.includes("Linear");
  const metricLabel = isLinear ? "Normalized Absolute Coefficient (|β|)" : "Mean Impurity / Gini Gain";

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
            Ranked by {metricLabel}. Higher scores reflect stronger predictive influence in decision boundaries.
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
                formatter={(val: any) => [formatNumber(val, 4), metricLabel]}
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
          Feature importances not available for this model architecture.
        </div>
      )}

      <div className="p-3 rounded-lg bg-surface-card border border-surface-border flex items-start space-x-2 text-[11px] text-slate-400">
        <Info className="w-4 h-4 text-brand-cyan shrink-0 mt-0.5" />
        <span>
          <strong className="text-slate-300 font-semibold">Attribution Note: </strong>
          {isLinear
            ? "Weights represent standardized regression coefficients. They measure relative predictive sensitivity within the model, not external causal intervention effects."
            : "Tree importance reflects total reduction in node impurity (Gini / MSE) contributed by splits on each feature across all estimators."}
        </span>
      </div>
    </div>
  );
};
