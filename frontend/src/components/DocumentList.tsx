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
    return <p className="text-sm text-slate-400">No documents yet.</p>;
  }
  return (
    <>
      <ul className="space-y-2">
        {documents.map((doc) => {
          const selected = selectedId === doc.id;
          return (
            <li
              key={doc.id}
              className={`rounded-xl border px-3 py-2 ${
                selected ? "border-cyan-500 bg-slate-800" : "border-slate-800 bg-slate-950"
              }`}
            >
              <button
                type="button"
                className="w-full text-left"
                onClick={() => onSelect(selected ? null : doc.id)}
              >
                <p className="truncate text-sm font-medium text-slate-100">{doc.filename}</p>
                <p className="text-xs text-slate-400">
                  {selected ? "Selected · ready to chat" : "Click to select"}
                  {" · "}
                  {doc.page_count} pages
                </p>
              </button>
              <button
                type="button"
                className="mt-2 text-xs text-rose-400 hover:text-rose-300"
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
