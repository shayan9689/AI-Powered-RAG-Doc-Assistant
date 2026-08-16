import { useState } from "react";

import type { DocumentSummary } from "../types";
import { ConfirmDialog } from "./ConfirmDialog";

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
              className={`glass-panel relative overflow-hidden rounded-xl py-2 pr-3 ${
                selected ? "bg-surface-container-highest pl-4" : "pl-3"
              }`}
            >
              {selected ? (
                <div className="absolute bottom-0 left-0 top-0 w-1 bg-primary-container" />
              ) : null}
              <button
                type="button"
                className="w-full text-left"
                onClick={() => onSelect(selected ? null : doc.id)}
              >
                <p className="truncate text-sm font-medium text-on-surface">{doc.filename}</p>
                <p className="text-xs text-on-surface-variant">
                  {selected ? "Selected · ready to chat" : "Click to select"}
                  {" · "}
                  {doc.page_count} pages
                </p>
              </button>
              <button
                type="button"
                className="mt-2 text-xs text-error hover:text-on-error-container"
                onClick={() => setPending(doc)}
              >
                Delete
              </button>
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
