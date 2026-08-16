import { useState } from "react";

import type { DocumentSummary } from "../types";
import { ConfirmDialog } from "./ConfirmDialog";
import { TrashIcon } from "./TrashIcon";

type DocumentListProps = {
  documents: DocumentSummary[];
  selectedId: string | null;
  onSelect: (id: string | null) => void;
  onDelete: (id: string) => void;
};

export function DocumentList({
  documents,
  selectedId,
  onSelect,
  onDelete,
}: DocumentListProps) {
  const [pending, setPending] = useState<DocumentSummary | null>(null);

  if (documents.length === 0) {
    return <p className="text-sm text-on-surface-variant">No documents yet.</p>;
  }
  return (
    <>
      <ul className="space-y-2">
        {documents.map((doc) => {
          const selected = selectedId === doc.id;
          return (
            <li
              key={doc.id}
              className={`glass-panel relative overflow-hidden rounded-xl py-2 pr-2 ${
                selected ? "bg-surface-container-highest pl-4" : "pl-3"
              }`}
            >
              {selected ? (
                <div className="absolute bottom-0 left-0 top-0 w-1 bg-primary-container" />
              ) : null}
              <div className="flex items-start gap-2">
                <button
                  type="button"
                  className="min-w-0 flex-1 cursor-pointer text-left"
                  onClick={() => onSelect(selected ? null : doc.id)}
                >
                  <p className="truncate text-sm font-medium text-on-surface">
                    {doc.filename}
                  </p>
                  <p className="text-xs text-on-surface-variant">
                    {selected ? "Selected · ready to chat" : "Click to select"}
                    {" · "}
                    {doc.page_count} pages
                  </p>
                </button>
                <button
                  type="button"
                  className="mt-0.5 shrink-0 cursor-pointer rounded-md p-1.5 text-error transition-transform duration-200 hover:-translate-y-0.5 hover:bg-error/10 hover:text-on-error-container"
                  aria-label={`Delete ${doc.filename}`}
                  title="Delete document"
                  onClick={() => setPending(doc)}
                >
                  <TrashIcon />
                </button>
              </div>
            </li>
          );
        })}
      </ul>
      <ConfirmDialog
        open={pending !== null}
        title="Delete this document?"
        message={
          pending
            ? `Remove ${pending.filename} from your workspace? Indexed chunks for this file will be deleted.`
            : ""
        }
        confirmLabel="Delete document"
        onCancel={() => setPending(null)}
        onConfirm={() => {
          if (pending) {
            onDelete(pending.id);
          }
          setPending(null);
        }}
      />
    </>
  );
}
