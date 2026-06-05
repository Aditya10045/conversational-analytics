"use client";

import { Card } from "@/components/ui/card";

interface SQLPanelProps {
  sql: string;
  explanation?: string;
}

export function SQLPanel({ sql, explanation }: SQLPanelProps) {
  return (
    <details className="group w-full">
      <summary className="cursor-pointer list-none rounded-xl border border-border bg-muted/50 px-3 py-2 text-sm font-medium">
        <span className="group-open:hidden">Show SQL</span>
        <span className="hidden group-open:inline">Hide SQL</span>
      </summary>
      <Card className="mt-2 p-3">
        <p className="mb-2 text-xs text-foreground/60">{explanation}</p>
        <pre className="mono overflow-x-auto text-xs leading-relaxed text-foreground/90">{sql}</pre>
      </Card>
    </details>
  );
}
