export type ToolTrace = {
  tool: string;
  status: "success" | "error" | "partial";
  duration_ms: number;
  source: string;
  endpoint?: string;
  params: Record<string, unknown>;
};

export type ChatResponse = {
  answer: string;
  language: "fr" | "en";
  intent: string;
  traces: ToolTrace[];
  data: Record<string, unknown>;
  followups: string[];
};

const API_BASE_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";
const API_KEY = import.meta.env.VITE_API_KEY;

export async function sendChatMessage(
  message: string,
  language?: "fr" | "en",
  context: Record<string, unknown> = {},
): Promise<ChatResponse> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (API_KEY) {
    headers["X-API-Key"] = API_KEY;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers,
      body: JSON.stringify({ message, language, context }),
    });
  } catch {
    throw new Error("BACKEND_UNREACHABLE");
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  return response.json();
}
