import { useEffect } from "react";

type ConfirmDialogProps = {
  open: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  onCancel: () => void;
  onConfirm: () => void;
};

export function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = "Delete",
  onCancel,
  onConfirm,
}: ConfirmDialogProps) {
  useEffect(() => {
    if (!open) {
      return;
    }
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onCancel();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onCancel]);

  if (!open) {
    return null;
  }
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4 backdrop-blur-sm"
      role="presentation"
      onClick={onCancel}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        className="w-full max-w-md rounded-2xl border border-cyan-400/40 bg-slate-900 p-6 shadow-2xl shadow-cyan-950/40"
        onClick={(event) => event.stopPropagation()}
      >
        <h3 id="confirm-title" className="text-lg font-semibold text-white">
          {title}
        </h3>
        <p className="mt-3 text-sm leading-6 text-slate-300">{message}</p>
        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            className="rounded-xl border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:border-cyan-400 hover:text-white"
            onClick={onCancel}
          >
            Keep
          </button>
          <button
            type="button"
            className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-medium text-white hover:bg-rose-500"
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
