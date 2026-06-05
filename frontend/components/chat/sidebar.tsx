"use client";

import { Moon, Plus, Sun } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { UISession } from "@/lib/types";
import { cn } from "@/lib/utils";

interface SidebarProps {
  sessions: UISession[];
  activeSessionId: string;
  onSelectSession: (sessionId: string) => void;
  onCreateSession: () => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
}

export function Sidebar({
  sessions,
  activeSessionId,
  onSelectSession,
  onCreateSession,
  darkMode,
  onToggleDarkMode,
}: SidebarProps) {
  return (
    <Card className="flex h-full min-h-[520px] flex-col gap-3 p-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.22em] text-foreground/50">Workspaces</p>
          <h2 className="text-lg font-semibold">Analytics Chat</h2>
        </div>
        <Button variant="outline" size="icon" onClick={onToggleDarkMode} aria-label="Toggle theme">
          {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
      </div>

      <Button className="w-full" onClick={onCreateSession}>
        <Plus className="mr-2 h-4 w-4" />
        New Chat
      </Button>

      <div className="space-y-2 overflow-y-auto pr-1">
        {sessions.map((session) => {
          const active = session.id === activeSessionId;
          return (
            <button
              key={session.id}
              type="button"
              onClick={() => onSelectSession(session.id)}
              className={cn(
                "w-full rounded-xl border px-3 py-3 text-left transition-colors",
                active ? "border-accent bg-accent/10" : "border-border bg-card hover:bg-muted/60"
              )}
            >
              <p className="truncate text-sm font-medium">{session.title}</p>
              <p className="text-xs text-foreground/55">{session.messages.length} messages</p>
            </button>
          );
        })}
      </div>
    </Card>
  );
}
