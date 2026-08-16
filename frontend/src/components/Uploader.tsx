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
        className="btn-primary flex cursor-pointer flex-col items-center justify-center rounded-lg px-4 py-3 text-center font-semibold hover:opacity-90"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          void handleFile(event.dataTransfer.files[0]);
        }}
      >
        <span>Drop a PDF here</span>
        <span className="mt-1 text-sm font-medium opacity-80">or click to browse</span>
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
        <p className="mt-2 font-label text-sm text-primary-fixed-dim">
          Indexing the PDF (this is usually a few seconds)...
        </p>
      )}
      {error && <p className="mt-2 text-sm text-error">{error}</p>}
    </div>
  );
}
