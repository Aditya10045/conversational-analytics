"use client";

import { Button } from "@/components/ui/button";

interface FollowUpsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

export function FollowUps({ questions, onSelect }: FollowUpsProps) {
  if (!questions.length) {
    return null;
  }

  return (
    <div className="space-y-2">
      <p className="text-xs uppercase tracking-[0.16em] text-foreground/60">Suggested Follow-ups</p>
      <div className="flex flex-wrap gap-2">
        {questions.slice(0, 6).map((question) => (
          <Button key={question} variant="outline" size="sm" onClick={() => onSelect(question)}>
            {question}
          </Button>
        ))}
      </div>
    </div>
  );
}
