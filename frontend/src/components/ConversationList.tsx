import { useState } from "react";

import type { ConversationSummary } from "../types";
import { ConfirmDialog } from "./ConfirmDialog";

type ConversationListProps = {
  conversations: ConversationSummary[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
};

export function ConversationList({
  conversations,
  selectedId,
  onSelect,
  onNew,
  onDelete,
}: ConversationListProps) {
  const [pending, setPending] = useState<ConversationSummary | null>(null);

  return (
    <div>
      <button
        type="button"
        className="mb-3 w-full rounded-lg bg-cyan-600 px-3 py-2 text-sm font-medium text-white hover:bg-cyan-500"
        onClick={onNew}
      >
        New chat
      </button>
      <ul className="space-y-2">
        {conversations.map((item) => (
          <li key={item.id}>
            <button
              type="button"
              className={`w-full rounded-xl border px-3 py-2 text-left text-sm ${
                selectedId === item.id
                  ? "border-cyan-500 bg-slate-800 text-white"
                  : "border-slate-800 bg-slate-950 text-slate-200"
              }`}
              onClick={() => onSelect(item.id)}
            >
              {item.title}
            </button>
            <button
              type="button"
              className="mt-1 text-xs text-rose-400"
              onClick={() => setPending(item)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
      <ConfirmDialog
        open={pending !== null}
        title="Delete this conversation?"
        message={
          pending
            ? `Remove “${pending.title}” from your chats? The messages in this thread will be gone.`
            : ""
        }
        confirmLabel="Delete chat"
        onCancel={() => setPending(null)}
        onConfirm={() => {
          if (pending) {
            onDelete(pending.id);
          }
          setPending(null);
        }}
      />
    </div>
  );
}
