import { ChatRequest, ChatResponse } from "@/lib/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000/api/v1";

export async function sendChatMessage(payload: ChatRequest): Promise<ChatResponse> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch {
    throw new Error(
      `Cannot reach backend API at ${API_BASE}. Make sure FastAPI is running and CORS_ORIGINS allows your frontend origin.`
    );
  }

  if (!response.ok) {
    const detailText = await response.text();
    try {
      const parsed = JSON.parse(detailText) as { detail?: string };
      throw new Error(parsed.detail || detailText || "Failed to process chat request.");
    } catch {
      throw new Error(detailText || "Failed to process chat request.");
    }
  }

  return response.json();
}
