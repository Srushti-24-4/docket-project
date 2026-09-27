"use client";

import { useCallback, useState } from "react";
import { clsx } from "clsx";
import { uploadDocument } from "@/lib/api";
import type { UploadedDocument } from "@/lib/types";

export function UploadDropzone({ onUploaded }: { onUploaded: (doc: UploadedDocument) => void }) {
  const [dragging, setDragging] = useState(false);
  const [pending, setPending] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleFiles = useCallback(
    async (fileList: FileList | null) => {
      if (!fileList) return;
      setError(null);
      for (const file of Array.from(fileList)) {
        setPending((p) => [...p, file.name]);
        try {
          const doc = await uploadDocument(file);
          onUploaded(doc);
        } catch (e) {
          setError(`Failed to process ${file.name}. Check the backend is running and env vars are set.`);
        } finally {
          setPending((p) => p.filter((n) => n !== file.name));
        }
      }
    },
    [onUploaded]
  );

  return (
    <div>
      <label
        className={clsx(
          "block border-2 border-dashed border-line/40 text-center px-6 py-10 cursor-pointer transition-colors",
          dragging && "border-amber bg-amber/10"
        )}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
      >
        <p className="font-grotesk text-lg">Drag files here, or click to browse</p>
        <p className="text-text-lo text-xs mt-1">PDF, Word, images, or text — routed automatically</p>
        <input
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.md,.png,.jpg,.jpeg,.webp,.bmp,.tiff"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
      </label>

      {pending.length > 0 && (
        <ul className="mt-4 space-y-1 font-mono text-xs text-text-lo">
          {pending.map((name) => (
            <li key={name}>processing {name}…</li>
          ))}
        </ul>
      )}

      {error && <p className="mt-3 text-red text-sm">{error}</p>}
    </div>
  );
}
