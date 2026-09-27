"use client";

import { useState } from "react";
import Link from "next/link";
import { Nav } from "@/components/Nav";
import { RequireAuth } from "@/components/RequireAuth";
import { UploadDropzone } from "@/components/UploadDropzone";
import { CitationChip } from "@/components/CitationChip";
import { Button } from "@/components/ui/button";
import { askQuestion } from "@/lib/api";
import type { UploadedDocument, ChatResponse } from "@/lib/types";

const ROUTE_LABEL: Record<string, string> = {
  normal_pdf: "Normal PDF",
  scanned_pdf: "Scanned PDF",
  table_heavy: "Table-heavy",
  image: "Image",
  docx: "Word doc",
  plain_text: "Text",
};

const ROUTE_COLOR: Record<string, string> = {
  normal_pdf: "text-green border-green",
  scanned_pdf: "text-amber border-amber",
  table_heavy: "text-[#8E7CC3] border-[#8E7CC3]",
  image: "text-amber border-amber",
  docx: "text-green border-green",
  plain_text: "text-text-lo border-line/40",
};

function AskDashboard() {
  const [docs, setDocs] = useState<UploadedDocument[]>([]);
  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [response, setResponse] = useState<ChatResponse | null>(null);
  const [askError, setAskError] = useState<string | null>(null);

  async function handleAsk() {
    if (!question.trim()) return;
    setAsking(true);
    setAskError(null);
    try {
      const res = await askQuestion(
        question,
        docs.map((d) => d.id)
      );
      setResponse(res);
    } catch (e) {
      setAskError(e instanceof Error ? e.message : "Something went wrong asking that.");
    } finally {
      setAsking(false);
    }
  }

  return (
    <main>
      <Nav />
      <div className="max-w-[1100px] mx-auto px-7 py-14">
        <h1 className="font-grotesk font-semibold text-3xl mb-10">Your documents</h1>

        <section className="grid md:grid-cols-2 gap-8">
          <div>
            <h2 className="font-grotesk text-xl mb-4">Upload documents</h2>
            <UploadDropzone onUploaded={(doc) => setDocs((d) => [...d, doc])} />

            {docs.length > 0 && (
              <ul className="mt-5 space-y-2">
                {docs.map((doc) => (
                  <li
                    key={doc.id}
                    className="flex items-center justify-between border border-line/40 px-3 py-2 text-sm"
                  >
                    <Link href={`/documents/${doc.id}`} className="font-mono truncate max-w-[55%] hover:text-amber">
                      {doc.filename}
                    </Link>
                    <span
                      className={`font-mono text-[10.5px] border px-2 py-0.5 ${ROUTE_COLOR[doc.route]}`}
                    >
                      {ROUTE_LABEL[doc.route]}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="border border-line/40 flex flex-col">
            <div className="flex-1 p-5 space-y-4 min-h-[220px]">
              {askError && <p className="text-red text-sm">{askError}</p>}
              {response ? (
                <div>
                  <p className="text-sm leading-relaxed">{response.answer}</p>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {response.citations.map((c, i) => (
                      <CitationChip key={i} citation={c} />
                    ))}
                  </div>
                  {response.verified && (
                    <p className="font-mono text-[11px] text-green mt-3 flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-green inline-block" />
                      evidence verified
                    </p>
                  )}
                </div>
              ) : (
                !askError && (
                  <p className="font-mono text-xs text-text-lo">
                    Upload a document, then ask a question about it.
                  </p>
                )
              )}
            </div>
            <div className="flex border-t border-line/40">
              <input
                className="flex-1 bg-transparent px-4 py-4 text-sm outline-none"
                placeholder="Ask a question…"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAsk()}
              />
              <Button onClick={handleAsk} disabled={asking} className="px-6">
                {asking ? "…" : "Ask"}
              </Button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

export default function AskPage() {
  return (
    <RequireAuth>
      <AskDashboard />
    </RequireAuth>
  );
}
