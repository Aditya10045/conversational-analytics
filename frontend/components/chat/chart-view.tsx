"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Card } from "@/components/ui/card";
import { ChartRecommendation } from "@/lib/types";

const PIE_COLORS = ["#ea580c", "#2563eb", "#0f766e", "#ca8a04", "#be123c", "#4f46e5"];

interface ChartViewProps {
  rows: Record<string, unknown>[];
  columns: string[];
  recommendation: ChartRecommendation;
}

function isNumber(value: unknown) {
  return typeof value === "number" && Number.isFinite(value);
}

export function ChartView({ rows, columns, recommendation }: ChartViewProps) {
  if (!rows.length || recommendation.type === "table") {
    return null;
  }

  const numericColumns = columns.filter((column) => rows.some((row) => isNumber(row[column])));
  const categoricalColumns = columns.filter((column) => !numericColumns.includes(column));

  const xAxis = recommendation.x_axis || categoricalColumns[0] || columns[0];
  const yAxis = recommendation.y_axis || numericColumns[0] || columns[1];

  if (!xAxis || !yAxis) {
    return null;
  }

  const normalized = rows.slice(0, 60).map((row) => ({
    [xAxis]: String(row[xAxis] ?? ""),
    [yAxis]: Number(row[yAxis] ?? 0),
  }));

  const pieData = normalized
    .slice(0, 12)
    .filter((entry) => Number.isFinite(entry[yAxis as keyof typeof entry] as number))
    .map((entry) => ({
      name: entry[xAxis as keyof typeof entry] as string,
      value: entry[yAxis as keyof typeof entry] as number,
    }));

  return (
    <Card className="p-3">
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-foreground/55">Suggested Chart</p>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <>
            {recommendation.type === "bar" && (
              <BarChart data={normalized}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.35)" />
                <XAxis dataKey={xAxis} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey={yAxis} fill="#ea580c" radius={[6, 6, 0, 0]} />
              </BarChart>
            )}
            {recommendation.type === "line" && (
              <LineChart data={normalized}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.35)" />
                <XAxis dataKey={xAxis} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey={yAxis} stroke="#2563eb" strokeWidth={3} dot={false} />
              </LineChart>
            )}
            {recommendation.type === "pie" && (
              <PieChart>
                <Tooltip />
                <Legend />
                <Pie data={pieData} dataKey="value" nameKey="name" outerRadius={98}>
                  {pieData.map((_, idx) => (
                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            )}
          </>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}
