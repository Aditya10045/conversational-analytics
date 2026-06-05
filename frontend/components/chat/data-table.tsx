"use client";

import { Card } from "@/components/ui/card";

interface DataTableProps {
  rows: Record<string, unknown>[];
  columns: string[];
}

export function DataTable({ rows, columns }: DataTableProps) {
  if (!rows.length) {
    return (
      <Card className="p-3">
        <p className="text-sm text-foreground/70">Query returned no rows.</p>
      </Card>
    );
  }

  const visibleRows = rows.slice(0, 100);
  const isTrimmed = rows.length > visibleRows.length;

  return (
    <Card className="overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full min-w-[580px] text-left text-sm">
          <thead className="bg-muted/70 text-xs uppercase tracking-[0.16em] text-foreground/60">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-3 py-2 font-medium">
                  {column}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleRows.map((row, idx) => (
              <tr key={idx} className="border-t border-border/60 align-top">
                {columns.map((column) => (
                  <td key={`${idx}-${column}`} className="px-3 py-2 text-foreground/90">
                    {String(row[column] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {isTrimmed && (
        <div className="border-t border-border px-3 py-2 text-xs text-foreground/60">
          Showing first {visibleRows.length} of {rows.length} rows.
        </div>
      )}
    </Card>
  );
}
