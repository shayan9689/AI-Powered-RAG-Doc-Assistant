import { useState } from "react";

type UploaderProps = {
  disabled?: boolean;
  onUpload: (file: File) => Promise<void>;
};

export function Uploader({ disabled, onUpload }: UploaderProps) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleFile(file: File | undefined) {
    if (!file) {
      return;
    }
    setError("");
    setBusy(true);
    try {
      await onUpload(file);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <label
        className="flex cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-slate-700 bg-slate-950/70 px-4 py-8 text-center text-slate-300"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          void handleFile(event.dataTransfer.files[0]);
        }}
      >
        <span className="font-medium text-slate-100">Drop a PDF here</span>
        <span className="mt-1 text-sm text-slate-400">or click to browse</span>
        <input
          type="file"
          accept="application/pdf"
          className="sr-only"
          disabled={disabled || busy}
          onChange={(event) => {
            void handleFile(event.target.files?.[0]);
            event.currentTarget.value = "";
          }}
        />
      </label>
      {busy && (
        <p className="mt-2 text-sm text-cyan-400">
          Indexing the PDF (this is usually a few seconds)...
        </p>
      )}
      {error && <p className="mt-2 text-sm text-rose-400">{error}</p>}
    </div>
  );
}
