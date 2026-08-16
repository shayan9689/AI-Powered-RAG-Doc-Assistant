import { useState } from "react";

import type { ConversationSummary } from "../types";
import { ConfirmDialog } from "./ConfirmDialog";
import { TrashIcon } from "./TrashIcon";

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
        className="btn-primary mb-3 w-full cursor-pointer rounded-lg px-3 py-2 text-sm font-semibold hover:opacity-90"
        onClick={onNew}
      >
        New chat
      </button>
      <ul className="space-y-2">
        {conversations.map((item) => (
          <li key={item.id}>
            <div
              className={`glass-panel flex items-start gap-2 rounded-xl px-3 py-2 ${
                selectedId === item.id
                  ? "bg-surface-container-highest text-on-surface"
                  : "text-on-surface-variant"
              }`}
            >
              <button
                type="button"
                className="min-w-0 flex-1 cursor-pointer truncate text-left text-sm"
                onClick={() => onSelect(item.id)}
              >
                {item.title}
              </button>
              <button
                type="button"
                className="mt-0.5 shrink-0 cursor-pointer rounded-md p-1 text-error transition-transform duration-200 hover:-translate-y-0.5 hover:bg-error/10 hover:text-on-error-container"
                aria-label={`Delete ${item.title}`}
                title="Delete chat"
                onClick={() => setPending(item)}
              >
                <TrashIcon className="h-3.5 w-3.5" />
              </button>
            </div>
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
