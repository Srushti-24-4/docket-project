import type { Citation } from "@/lib/types";

export function CitationChip({ citation }: { citation: Citation }) {
  return (
    <span
      className="font-mono text-[11px] text-green border border-green px-2 py-1 inline-block"
      title={citation.snippet}
    >
      {citation.filename} · p.{citation.page} · {Math.round(citation.confidence * 100)}%
    </span>
  );
}
