import { useCallback, useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";

import { AuthPanel } from "./components/AuthPanel";
import { ChatWindow } from "./components/ChatWindow";
import { ConversationList } from "./components/ConversationList";
import { DocumentList } from "./components/DocumentList";
import { Uploader } from "./components/Uploader";
import {
  deleteConversation,
  deleteDocument,
  getConversation,
  getHealth,
  listConversations,
  listDocuments,
  streamChat,
  uploadDocument,
} from "./lib/api";
import { isSupabaseConfigured, supabase } from "./lib/supabase";
import type { ChatMessage, ConversationSummary, DocumentSummary } from "./types";

function persistToken(session: Session | null) {
  if (session?.access_token) {
    window.localStorage.setItem("access_token", session.access_token);
  } else {
    window.localStorage.removeItem("access_token");
  }
}

function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [authReady, setAuthReady] = useState(!isSupabaseConfigured);
  const [health, setHealth] = useState("checking");
  const [documents, setDocuments] = useState<DocumentSummary[]>([]);
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [selectedDoc, setSelectedDoc] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const refresh = useCallback(async () => {
    const [docs, convos] = await Promise.all([listDocuments(), listConversations()]);
    setDocuments(docs);
    setConversations(convos);
  }, []);

  useEffect(() => {
    if (!supabase) {
      return;
    }
    void supabase.auth.getSession().then(({ data }) => {
      persistToken(data.session);
      setSession(data.session);
      setAuthReady(true);
    });
    const { data } = supabase.auth.onAuthStateChange((_event, next) => {
      persistToken(next);
      setSession(next);
    });
    return () => data.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    getHealth()
      .then(() => setHealth("ok"))
      .catch(() => setHealth("error"));
  }, []);

  useEffect(() => {
    if (isSupabaseConfigured && !session) {
      return;
    }
    void refresh().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : "Failed to load data");
    });
  }, [refresh, session]);

  async function handleUpload(file: File) {
    await uploadDocument(file);
    await refresh();
  }

  async function handleSend(text: string) {
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: "user",
      content: text,
    };
    const assistantId = `assistant-${Date.now()}`;
    setMessages((current) => [
      ...current,
      userMessage,
      { id: assistantId, role: "assistant", content: "" },
    ]);
    setLoading(true);
    setError("");
    try {
      const result = await streamChat(
        {
          query: text,
          conversation_id: conversationId,
          document_id: selectedDoc,
        },
        (token) => {
          setMessages((current) =>
            current.map((item) =>
              item.id === assistantId ? { ...item, content: token } : item,
            ),
          );
        },
      );
      setConversationId(result.conversation_id);
      setMessages((current) =>
        current.map((item) =>
          item.id === assistantId
            ? {
                ...item,
                content: result.answer,
                sources: result.sources,
                refused: result.refused,
              }
            : item,
        ),
      );
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed");
    } finally {
      setLoading(false);
    }
  }

  if (isSupabaseConfigured && !authReady) {
    return (
      <main className="canvas-glow flex min-h-screen items-center justify-center font-body text-on-surface-variant">
        Loading auth...
      </main>
    );
  }

  if (isSupabaseConfigured && !session) {
    return <AuthPanel onSignedIn={() => undefined} />;
  }

  return (
    <div className="flex h-screen flex-col overflow-hidden bg-background font-body text-on-background">
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-outline-variant bg-background/80 px-gutter backdrop-blur-xl">
        <div>
          <h1 className="font-display text-2xl font-bold leading-tight tracking-tight text-primary-fixed-dim">
            RAG Document Assistant
          </h1>
          <p className="font-label text-xs uppercase tracking-wider text-on-surface-variant">
            API {health === "ok" ? "reachable" : health === "checking" ? "checking..." : "offline"}
            {session?.user.email ? ` · ${session.user.email}` : ""}
          </p>
        </div>
        {supabase ? (
          <button
            type="button"
            className="text-sm font-medium text-on-surface-variant transition-colors hover:text-primary"
            onClick={() => {
              void supabase?.auth.signOut();
            }}
          >
            Sign out
          </button>
        ) : null}
      </header>
      <div className="grid min-h-0 flex-1 overflow-hidden lg:grid-cols-[320px_1fr_320px]">
        <aside className="overflow-y-auto border-r border-outline-variant bg-surface-container-low/60 p-4 backdrop-blur-lg">
          <h2 className="mb-1 font-display text-2xl font-semibold tracking-tight text-primary">
            The Vault
          </h2>
          <p className="mb-4 font-label text-xs uppercase tracking-wider text-on-surface-variant">
            Click a PDF to select it before you chat.
          </p>
          <Uploader onUpload={handleUpload} />
          <div className="mt-4">
            <DocumentList
              documents={documents}
              selectedId={selectedDoc}
              onSelect={setSelectedDoc}
              onDelete={(id) => {
                setDocuments((current) => current.filter((doc) => doc.id !== id));
                if (selectedDoc === id) {
                  setSelectedDoc(null);
                }
                void deleteDocument(id).catch((err: unknown) => {
                  setError(
                    err instanceof Error ? err.message : "Failed to delete document",
                  );
                  void refresh();
                });
              }}
            />
          </div>
        </aside>
        <main className="canvas-glow min-h-0 overflow-hidden p-gutter">
          <ChatWindow
            messages={messages}
            loading={loading}
            error={error}
            hasDocuments={documents.length > 0}
            selectedFilename={
              documents.find((doc) => doc.id === selectedDoc)?.filename ?? null
            }
            onSend={handleSend}
          />
        </main>
        <aside className="overflow-y-auto border-l border-outline-variant bg-surface-container-low/60 p-4 backdrop-blur-lg">
          <h2 className="mb-3 font-label text-xs font-medium uppercase tracking-wider text-on-surface-variant">
            Conversations
          </h2>
          <ConversationList
            conversations={conversations}
            selectedId={conversationId}
            onNew={() => {
              setConversationId(null);
              setMessages([]);
            }}
            onSelect={async (id) => {
              setConversationId(id);
              const detail = await getConversation(id);
              setMessages(
                detail.messages.map((item) => ({
                  id: item.id,
                  role: item.role === "assistant" ? "assistant" : "user",
                  content: item.content,
                  sources: item.sources,
                })),
              );
            }}
            onDelete={(id) => {
              setConversations((current) =>
                current.filter((item) => item.id !== id),
              );
              if (conversationId === id) {
                setConversationId(null);
                setMessages([]);
              }
              void deleteConversation(id).catch((err: unknown) => {
                setError(
                  err instanceof Error
                    ? err.message
                    : "Failed to delete conversation",
                );
                void refresh();
              });
            }}
          />
        </aside>
      </div>
    </div>
  );
}

export default App;
