import type {
  ChatResponse,
  ConversationMessage,
  ConversationSummary,
  DocumentSummary,
} from "../types";

function resolveApiBase(): string {
  const fromEnv = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");
  const railway = "https://ai-powered-rag-doc-assistant-production.up.railway.app";
  if (import.meta.env.PROD) {
    if (!fromEnv || fromEnv.includes("localhost")) {
      return railway;
    }
    return fromEnv;
  }
  return fromEnv || "http://localhost:8000";
}

const API_BASE_URL = resolveApiBase();

function authHeaders(json = false): HeadersInit {
  const headers: Record<string, string> = {};
  if (json) {
    headers["Content-Type"] = "application/json";
  }
  const token = window.localStorage.getItem("access_token");
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  return headers;
}

async function parseError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { detail?: string };
    return payload.detail ?? response.statusText;
  } catch {
    return response.statusText;
  }
}

async function request(input: string, init?: RequestInit): Promise<Response> {
  try {
    return await fetch(input, { cache: "no-store", ...init });
  } catch {
    throw new Error(`Cannot reach the API at ${API_BASE_URL}.`);
  }
}

async function sleep(ms: number): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, ms));
}

export async function getHealth(): Promise<{ status: string }> {
  let lastError: unknown;
  for (let attempt = 0; attempt < 4; attempt += 1) {
    try {
      const response = await request(`${API_BASE_URL}/health`);
      if (!response.ok) {
        throw new Error("Health check failed");
      }
      return response.json() as Promise<{ status: string }>;
    } catch (err) {
      lastError = err;
      await sleep(1200 * (attempt + 1));
    }
  }
  throw lastError instanceof Error ? lastError : new Error("Health check failed");
}

export async function uploadDocument(file: File): Promise<DocumentSummary & { document_id?: string }> {
  const body = new FormData();
  body.append("file", file);
  const response = await request(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    headers: authHeaders(),
    body,
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<DocumentSummary & { document_id?: string }>;
}

export async function listDocuments(): Promise<DocumentSummary[]> {
  const response = await request(`${API_BASE_URL}/documents`, { headers: authHeaders() });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<DocumentSummary[]>;
}

export async function fetchPagePreview(
  documentId: string,
  pageNumber: number,
): Promise<string> {
  const response = await request(
    `${API_BASE_URL}/documents/${documentId}/pages/${pageNumber}`,
    { headers: authHeaders() },
  );
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

export async function deleteDocument(id: string): Promise<void> {
  const response = await request(`${API_BASE_URL}/documents/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
}

export async function listConversations(): Promise<ConversationSummary[]> {
  const response = await request(`${API_BASE_URL}/conversations`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<ConversationSummary[]>;
}

export async function getConversation(id: string): Promise<{
  messages: ConversationMessage[];
}> {
  const response = await request(`${API_BASE_URL}/conversations/${id}`, {
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<{ messages: ConversationMessage[] }>;
}

export async function deleteConversation(id: string): Promise<void> {
  const response = await request(`${API_BASE_URL}/conversations/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
}

export async function sendChat(payload: {
  query: string;
  conversation_id?: string | null;
  document_id?: string | null;
}): Promise<ChatResponse> {
  const response = await request(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: authHeaders(true),
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error(await parseError(response));
  }
  return response.json() as Promise<ChatResponse>;
}

export async function streamChat(
  payload: {
    query: string;
    conversation_id?: string | null;
    document_id?: string | null;
  },
  onToken: (text: string) => void,
): Promise<ChatResponse> {
  const response = await request(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: authHeaders(true),
    body: JSON.stringify(payload),
  });
  if (!response.ok || !response.body) {
    throw new Error(await parseError(response));
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalPayload: ChatResponse | null = null;
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const line = part.replace(/^data:\s*/, "").trim();
      if (!line) {
        continue;
      }
      const event = JSON.parse(line) as {
        type: string;
        text?: string;
        payload?: ChatResponse;
      };
      if (event.type === "token" && event.text) {
        onToken(event.text);
      }
      if (event.type === "done" && event.payload) {
        finalPayload = event.payload;
      }
    }
  }
  if (!finalPayload) {
    throw new Error("Stream ended without a complete answer.");
  }
  return finalPayload;
}
