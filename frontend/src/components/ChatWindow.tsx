import { useState } from "react";
import Markdown from "react-markdown";

import type { ChatMessage, Citation } from "../types";
import { PagePreviewModal } from "./PagePreviewModal";

type ChatWindowProps = {
  messages: ChatMessage[];
  loading: boolean;
  error: string;
  hasDocuments: boolean;
  selectedFilename: string | null;
  onSend: (text: string) => Promise<void>;
};

function uniquePages(sources: Citation[]): Citation[] {
  const seen = new Set<string>();
  const unique: Citation[] = [];
  for (const source of sources) {
    const key = `${source.document_id}:${source.page_number}`;
    if (seen.has(key)) {
      continue;
    }
    seen.add(key);
    unique.push(source);
  }
  return unique;
}

export function ChatWindow({
  messages,
  loading,
  error,
  hasDocuments,
  selectedFilename,
  onSend,
}: ChatWindowProps) {
  const [draft, setDraft] = useState("");
  const [preview, setPreview] = useState<Citation | null>(null);
  const canChat = Boolean(selectedFilename);
  const needsScroll = messages.length > 0 || loading;

  return (
    <section className="flex h-full min-h-0 flex-col overflow-hidden">
      <div
        className={`min-h-0 flex-1 ${
          needsScroll ? "overflow-y-auto" : "overflow-hidden"
        }`}
      >
        {!canChat && messages.length === 0 && (
          <div className="flex h-full items-center justify-center">
            <div className="max-w-md rounded-2xl border border-cyan-400/40 bg-slate-900 px-6 py-8 text-center shadow-lg shadow-cyan-950/40">
              <p className="text-xs font-semibold uppercase tracking-wide text-cyan-300">
                Select a PDF first
              </p>
              <h2 className="mt-2 text-lg font-semibold text-white">
                {hasDocuments
                  ? "Choose a document to start chatting"
                  : "Upload a PDF, then select it"}
              </h2>
              <p className="mt-3 text-sm leading-6 text-slate-300">
                {hasDocuments
                  ? "Click one file in the Documents list on the left. Chat only answers questions about the PDF you select."
                  : "Drop a PDF on the left, then click that file so the assistant knows which document to use."}
              </p>
            </div>
          </div>
        )}
        {!canChat && messages.length > 0 && (
          <div className="rounded-2xl border border-cyan-400/40 bg-slate-900 px-4 py-3 text-sm text-slate-200">
            Select a PDF on the left to continue this chat.
          </div>
        )}
        {canChat && messages.length === 0 && (
          <div className="rounded-2xl border border-slate-800 bg-slate-900 px-4 py-3">
            <p className="text-xs uppercase tracking-wide text-cyan-300">Chatting with</p>
            <p className="mt-1 truncate text-sm font-medium text-white">{selectedFilename}</p>
            <p className="mt-2 text-sm text-slate-400">Ask a question about this PDF.</p>
          </div>
        )}
        {messages.length > 0 && (
          <div className="space-y-4">
            {messages.map((message) => (
              <article
                key={message.id}
                className={`rounded-2xl p-4 ${
                  message.role === "user"
                    ? "ml-8 bg-cyan-950/70 text-cyan-50"
                    : "mr-8 bg-slate-900 text-slate-100"
                }`}
              >
                <p className="text-xs uppercase tracking-wide text-slate-400">{message.role}</p>
                <div className="prose prose-invert mt-2 max-w-none text-sm">
                  <Markdown>{message.content}</Markdown>
                </div>
                {message.role === "assistant" &&
                  uniquePages(message.sources ?? []).length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {uniquePages(message.sources ?? []).map((source) => (
                        <button
                          type="button"
                          key={`${source.document_id}-${source.page_number}`}
                          className="rounded-lg border border-cyan-500/40 bg-slate-950 px-2.5 py-1.5 text-left hover:border-cyan-300"
                          onClick={() => setPreview(source)}
                        >
                          <span className="text-xs font-semibold text-cyan-300">
                            Page {source.page_number}
                          </span>
                          <span className="ml-2 text-xs text-slate-300">{source.filename}</span>
                        </button>
                      ))}
                    </div>
                  )}
              </article>
            ))}
            {loading && <p className="text-sm text-cyan-400">Thinking...</p>}
          </div>
        )}
      </div>
        {error && <p className="mt-3 shrink-0 text-sm text-rose-400">{error}</p>}
      <form
        className="mt-4 flex shrink-0 gap-2"
        onSubmit={(event) => {
          event.preventDefault();
          const text = draft.trim();
          if (!text || loading || !canChat) {
            return;
          }
          setDraft("");
          void onSend(text);
        }}
      >
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          disabled={!canChat || loading}
          className="flex-1 rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-slate-100 outline-none focus:border-cyan-500 disabled:cursor-not-allowed disabled:opacity-50"
          placeholder={
            canChat
              ? `Ask about ${selectedFilename}`
              : "Select a PDF on the left to start chatting"
          }
          aria-label="Chat message"
        />
        <button
          type="submit"
          disabled={loading || !canChat}
          className="rounded-xl bg-cyan-600 px-4 py-3 font-medium text-white disabled:opacity-50"
        >
          Send
        </button>
      </form>
      <PagePreviewModal citation={preview} onClose={() => setPreview(null)} />
    </section>
  );
}
