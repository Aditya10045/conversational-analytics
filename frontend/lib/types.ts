export type ChartType = "bar" | "line" | "pie" | "table";

export interface ChatRequest {
  session_id?: string | null;
  message: string;
  user_id?: string | null;
}

export interface ChartRecommendation {
  type: ChartType;
  x_axis?: string | null;
  y_axis?: string | null;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  executive_summary: string;
  sql: string;
  sql_explanation: string;
  chart_recommendation: ChartRecommendation;
  rows: Record<string, unknown>[];
  columns: string[];
  stats: {
    rows_returned: number;
    execution_ms: number;
    timed_out: boolean;
  };
  key_findings: string[];
  trends: string[];
  anomalies: string[];
  recommendations: string[];
  follow_up_questions: string[];
  caveats: string[];
}

export interface UIMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
  createdAt: number;
}

export interface UISession {
  id: string;
  title: string;
  messages: UIMessage[];
}
