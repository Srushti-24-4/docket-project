"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { Nav } from "@/components/Nav";
import { RequireAuth } from "@/components/RequireAuth";
import { getDocument } from "@/lib/api";
import type { UploadedDocument } from "@/lib/types";

const ROUTE_LABEL: Record<string, string> = {
  normal_pdf: "Normal PDF — extracted with PyMuPDF",
  scanned_pdf: "Scanned PDF — extracted with OpenCV + PaddleOCR",
  table_heavy: "Table-heavy PDF — extracted with pdfplumber / Camelot",
  image: "Image — extracted with OpenCV + PaddleOCR",
  docx: "Word document — extracted with python-docx",
  plain_text: "Plain text",
};

function DocumentDetail() {
  const params = useParams<{ id: string }>();
  const [doc, setDoc] = useState<UploadedDocument | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getDocument(params.id)
      .then(setDoc)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load document"));
  }, [params.id]);

  return (
    <main>
      <Nav />
      <div className="max-w-[700px] mx-auto px-7 py-14">
        {error && <p className="text-red text-sm">{error}</p>}
        {!doc && !error && <p className="font-mono text-sm text-text-lo">Loading…</p>}
        {doc && (
          <div className="border border-line/40 p-6">
            <h1 className="font-grotesk text-2xl mb-4 break-words">{doc.filename}</h1>
            <dl className="space-y-3 font-mono text-sm">
              <div className="flex justify-between border-b border-line/20 pb-2">
                <dt className="text-text-lo">Extraction route</dt>
                <dd>{ROUTE_LABEL[doc.route] ?? doc.route}</dd>
              </div>
              <div className="flex justify-between border-b border-line/20 pb-2">
                <dt className="text-text-lo">Pages indexed</dt>
                <dd>{doc.page_count}</dd>
              </div>
              <div className="flex justify-between border-b border-line/20 pb-2">
                <dt className="text-text-lo">Storage path</dt>
                <dd className="truncate max-w-[300px]" title={doc.storage_path}>
                  {doc.storage_path}
                </dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-text-lo">Document ID</dt>
                <dd className="truncate max-w-[300px]" title={doc.id}>
                  {doc.id}
                </dd>
              </div>
            </dl>
          </div>
        )}
      </div>
    </main>
  );
}

export default function DocumentDetailPage() {
  return (
    <RequireAuth>
      <DocumentDetail />
    </RequireAuth>
  );
}
