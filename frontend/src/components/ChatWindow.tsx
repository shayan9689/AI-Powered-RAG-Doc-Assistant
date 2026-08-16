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

const SUGGESTIONS = [
  "Summarize this document",
  "What are the key points?",
  "Who or what is this about?",
];

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
            <div className="glass-panel glass-panel-hover flex w-full max-w-md flex-col items-center gap-4 rounded-xl p-10 text-center shadow-[0_20px_50px_rgba(0,0,0,0.5)]">
              <p className="font-label text-xs uppercase tracking-wider text-primary-fixed-dim">
                Select a PDF first
              </p>
              <h2 className="font-display text-2xl font-bold tracking-tight text-primary-fixed-dim">
                {hasDocuments
                  ? "Choose a document to start chatting"
                  : "Upload a PDF, then select it"}
              </h2>
              <p className="max-w-xs text-sm leading-6 text-on-surface-variant">
                {hasDocuments
                  ? "Click one file in the Documents list on the left. Chat only answers questions about the PDF you select."
                  : "Drop a PDF on the left, then click that file so the assistant knows which document to use."}
              </p>
            </div>
          </div>
        )}
        {!canChat && messages.length > 0 && (
          <div className="glass-panel rounded-xl px-4 py-3 text-sm text-on-surface">
            Select a PDF on the left to continue this chat.
          </div>
        )}
        {canChat && messages.length === 0 && (
          <div className="flex h-full flex-col justify-center">
            <article className="mr-8 border-l border-primary-container/50 py-1 pl-4">
              <p className="font-label text-[10px] uppercase tracking-widest text-outline">
                assistant
              </p>
              <p className="mt-2 text-[15px] leading-[22px] text-on-surface">
                Welcome. I can answer questions about{" "}
                <span className="text-primary-fixed-dim">{selectedFilename}</span>. Ask
                for a summary, the key points, or any detail in this PDF.
              </p>
              <div className="mt-4 flex flex-wrap gap-2">
                {SUGGESTIONS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    disabled={loading}
                    className="rounded-lg border border-outline-variant bg-surface-container-lowest px-3 py-1.5 text-left text-xs text-on-surface-variant hover:border-primary-container hover:text-primary-fixed-dim disabled:opacity-50"
                    onClick={() => {
                      void onSend(prompt);
                    }}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </article>
          </div>
        )}
        {messages.length > 0 && (
          <div className="space-y-4">
            {messages.map((message) => (
              <article
                key={message.id}
                className={
                  message.role === "user"
                    ? "ml-8 rounded-xl border border-outline-variant bg-surface-container-lowest p-4 text-on-surface"
                    : "mr-8 border-l border-primary-container/50 py-1 pl-4 text-on-surface"
                }
              >
                <p className="font-label text-[10px] uppercase tracking-widest text-outline">
                  {message.role}
                </p>
                <div className="prose-chat mt-2 max-w-none text-[15px] leading-[22px]">
                  <Markdown>{message.content}</Markdown>
                </div>
                {message.role === "assistant" &&
                  uniquePages(message.sources ?? []).length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {uniquePages(message.sources ?? []).map((source) => (
                        <button
                          type="button"
                          key={`${source.document_id}-${source.page_number}`}
                          className="rounded-lg border border-outline-variant bg-surface-container-lowest px-2.5 py-1.5 text-left font-label hover:border-primary-container"
                          onClick={() => setPreview(source)}
                        >
                          <span className="text-xs font-medium text-primary-fixed-dim">
                            Page {source.page_number}
                          </span>
                          <span className="ml-2 text-xs text-on-surface-variant">
                            {source.filename}
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
              </article>
            ))}
            {loading && (
              <p className="font-label text-sm tracking-wide text-primary-fixed-dim">
                Thinking...
              </p>
            )}
          </div>
        )}
      </div>
        {error && <p className="mt-3 shrink-0 text-sm text-error">{error}</p>}
      <form
        className="glass-panel mt-4 flex shrink-0 items-center gap-3 rounded-xl p-2 pl-4 focus-within:ring-1 focus-within:ring-primary-container"
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
          className="flex-1 border-none bg-transparent px-1 py-3 text-[15px] leading-[22px] text-on-surface outline-none placeholder:text-outline disabled:cursor-not-allowed disabled:opacity-50"
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
          className="rounded-lg bg-primary-container px-4 py-3 font-semibold text-on-primary-container shadow-[0_0_10px_rgba(0,229,255,0.15)] disabled:cursor-not-allowed disabled:opacity-50"
        >
          Send
        </button>
      </form>
      <PagePreviewModal citation={preview} onClose={() => setPreview(null)} />
    </section>
  );
}
