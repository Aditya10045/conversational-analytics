"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { Loader2, Send } from "lucide-react";

import { MessageBubble } from "@/components/chat/message-bubble";
import { Sidebar } from "@/components/chat/sidebar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { sendChatMessage } from "@/lib/api";
import { ChatResponse, UIMessage, UISession } from "@/lib/types";

function makeId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `id-${Date.now()}-${Math.floor(Math.random() * 100000)}`;
}

function createSession(): UISession {
  return {
    id: makeId(),
    title: "New analysis",
    messages: [],
  };
}

function makeAssistantMessage(response: ChatResponse): UIMessage {
  return {
    id: makeId(),
    role: "assistant",
    content: response.answer,
    response,
    createdAt: Date.now(),
  };
}

export function AnalyticsChat() {
  const initialSession = useMemo(() => createSession(), []);
  const [sessions, setSessions] = useState<UISession[]>([initialSession]);
  const [activeSessionId, setActiveSessionId] = useState(initialSession.id);
  const [draft, setDraft] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement | null>(null);

  const activeSession = sessions.find((session) => session.id === activeSessionId) ?? sessions[0];

  useEffect(() => {
    const saved = localStorage.getItem("analytics-theme");
    const shouldUseDark = saved === "dark";
    setDarkMode(shouldUseDark);
    document.documentElement.classList.toggle("dark", shouldUseDark);
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
    localStorage.setItem("analytics-theme", darkMode ? "dark" : "light");
  }, [darkMode]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [sessions, isLoading]);

  function updateActiveSession(updater: (session: UISession) => UISession) {
    setSessions((prev) => prev.map((session) => (session.id === activeSessionId ? updater(session) : session)));
  }

  function createNewSession() {
    const session = createSession();
    setSessions((prev) => [session, ...prev]);
    setActiveSessionId(session.id);
    setDraft("");
    setError(null);
  }

  async function submitMessage(content: string) {
    const text = content.trim();
    if (!text || isLoading) return;

    setError(null);
    setDraft("");
    setIsLoading(true);

    const userMessage: UIMessage = {
      id: makeId(),
      role: "user",
      content: text,
      createdAt: Date.now(),
    };

    updateActiveSession((session) => {
      const title = session.messages.length ? session.title : text.slice(0, 44);
      return {
        ...session,
        title: title || "New analysis",
        messages: [...session.messages, userMessage],
      };
    });

    try {
      const response = await sendChatMessage({
        session_id: activeSessionId,
        message: text,
      });

      updateActiveSession((session) => ({
        ...session,
        messages: [...session.messages, makeAssistantMessage(response)],
      }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Request failed.");
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitMessage(draft);
  }

  function handleTextareaKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void submitMessage(draft);
    }
  }

  return (
    <main className="min-h-screen px-4 py-5 md:px-7 md:py-6">
      <div className="mx-auto grid w-full max-w-[1450px] gap-4 md:grid-cols-[300px_1fr]">
        <Sidebar
          sessions={sessions}
          activeSessionId={activeSessionId}
          onSelectSession={setActiveSessionId}
          onCreateSession={createNewSession}
          darkMode={darkMode}
          onToggleDarkMode={() => setDarkMode((prev) => !prev)}
        />

        <Card className="flex min-h-[520px] flex-col p-3 md:p-4">
          <div className="mb-3 rounded-xl border border-border bg-muted/40 px-3 py-2">
            <p className="text-xs uppercase tracking-[0.2em] text-foreground/55">Conversational Analytics</p>
            <p className="text-sm text-foreground/85">
              Ask business questions and get SQL, charts, and executive-ready insights from your warehouse.
            </p>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto pr-1">
            {activeSession.messages.map((message) => (
              <MessageBubble key={message.id} message={message} onFollowUpSelect={(q) => setDraft(q)} />
            ))}

            {isLoading && (
              <div className="flex items-center gap-2 rounded-xl border border-border bg-card px-4 py-3 text-sm text-foreground/80">
                <Loader2 className="h-4 w-4 animate-spin" />
                Generating SQL and insights...
              </div>
            )}

            {error && (
              <div className="rounded-xl border border-red-300 bg-red-50 px-4 py-3 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-200">
                {error}
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          <form onSubmit={handleSubmit} className="mt-4 space-y-2">
            <Textarea
              placeholder="Example: Which regions had the highest growth last quarter?"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              onKeyDown={handleTextareaKeyDown}
              disabled={isLoading}
            />
            <div className="flex items-center justify-between">
              <p className="text-xs text-foreground/55">Shift+Enter for new line. Enter to send.</p>
              <Button type="submit" disabled={isLoading || !draft.trim()}>
                <Send className="mr-2 h-4 w-4" />
                Ask
              </Button>
            </div>
          </form>
        </Card>
      </div>
    </main>
  );
}
