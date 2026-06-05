"use client";

import { ChartView } from "@/components/chat/chart-view";
import { DataTable } from "@/components/chat/data-table";
import { FollowUps } from "@/components/chat/follow-ups";
import { SQLPanel } from "@/components/chat/sql-panel";
import { Card } from "@/components/ui/card";
import { UIMessage } from "@/lib/types";
import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  message: UIMessage;
  onFollowUpSelect: (question: string) => void;
}

function SectionList({ title, items }: { title: string; items: string[] }) {
  if (!items.length) {
    return null;
  }

  return (
    <div className="space-y-1">
      <p className="text-xs uppercase tracking-[0.16em] text-foreground/55">{title}</p>
      <ul className="list-disc space-y-1 pl-4 text-sm text-foreground/85">
        {items.slice(0, 6).map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export function MessageBubble({ message, onFollowUpSelect }: MessageBubbleProps) {
  if (message.role === "user") {
    return (
      <div className="flex justify-end">
        <Card className="max-w-[78%] border-none bg-accent px-4 py-3 text-white shadow-md">
          <p className="text-sm leading-relaxed">{message.content}</p>
        </Card>
      </div>
    );
  }

  const response = message.response;
  if (!response) {
    return null;
  }

  return (
    <div className="flex justify-start">
      <Card className="w-full max-w-[94%] space-y-4 p-4 animate-fade-in">
        <div className="space-y-2">
          <p className="text-xs uppercase tracking-[0.18em] text-foreground/55">Executive Summary</p>
          <p className="text-sm font-medium leading-relaxed">{response.executive_summary}</p>
          <p className="text-sm leading-relaxed text-foreground/90">{response.answer}</p>
        </div>

        <div className={cn("grid gap-3", "md:grid-cols-2")}>
          <SectionList title="Key Findings" items={response.key_findings} />
          <SectionList title="Trends" items={response.trends} />
          <SectionList title="Anomalies" items={response.anomalies} />
          <SectionList title="Recommendations" items={response.recommendations} />
        </div>

        <SQLPanel sql={response.sql} explanation={response.sql_explanation} />
        <ChartView rows={response.rows} columns={response.columns} recommendation={response.chart_recommendation} />
        <DataTable rows={response.rows} columns={response.columns} />
        <FollowUps questions={response.follow_up_questions} onSelect={onFollowUpSelect} />
      </Card>
    </div>
  );
}
