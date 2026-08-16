import { useEffect, useState } from "react";

import { fetchPagePreview } from "../lib/api";
import type { Citation } from "../types";

type PagePreviewModalProps = {
  citation: Citation | null;
  onClose: () => void;
};

export function PagePreviewModal({ citation, onClose }: PagePreviewModalProps) {
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!citation) {
      return;
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [citation, onClose]);

  useEffect(() => {
    if (!citation) {
      setImageUrl("");
      setError("");
      return;
    }
    let objectUrl = "";
    let cancelled = false;
    setLoading(true);
    setError("");
    void fetchPagePreview(citation.document_id, citation.page_number)
      .then((url) => {
        if (cancelled) {
          URL.revokeObjectURL(url);
          return;
        }
        objectUrl = url;
        setImageUrl(url);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Could not load this page.");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [citation]);

  if (!citation) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-surface-container-lowest/85 p-4 backdrop-blur-sm"
      role="presentation"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="page-preview-title"
        className="glass-panel flex max-h-[90vh] w-full max-w-3xl flex-col rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.5)]"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b border-outline-variant px-5 py-4">
          <div className="min-w-0">
            <p className="font-label text-xs font-medium uppercase tracking-wider text-primary-fixed-dim">
              Page {citation.page_number}
            </p>
            <h3
              id="page-preview-title"
              className="mt-1 truncate font-display text-base font-semibold text-on-surface"
            >
              {citation.filename}
            </h3>
          </div>
          <button
            type="button"
            className="rounded-lg border border-outline-variant px-3 py-1.5 text-sm text-on-surface hover:border-primary-container"
            onClick={onClose}
          >
            Close
          </button>
        </div>
        <div className="min-h-0 flex-1 overflow-auto bg-surface-container-lowest p-4">
          {loading && (
            <p className="py-16 text-center font-label text-sm text-primary-fixed-dim">
              Loading page...
            </p>
          )}
          {error && (
            <p className="py-16 text-center text-sm text-error">{error}</p>
          )}
          {imageUrl && !loading && (
            <img
              src={imageUrl}
              alt={`${citation.filename} page ${citation.page_number}`}
              className="mx-auto max-w-full rounded-lg border border-outline-variant"
            />
          )}
        </div>
        {citation.snippet ? (
          <p className="border-t border-outline-variant px-5 py-3 text-sm leading-6 text-on-surface-variant">
            {citation.snippet}
          </p>
        ) : null}
      </div>
    </div>
  );
}
