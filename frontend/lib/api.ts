import { supabase } from "./supabaseClient";
import type { UploadedDocument, ChatResponse } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function authHeaders(): Promise<HeadersInit> {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  if (!token) throw new Error("Not signed in");
  return { Authorization: `Bearer ${token}` };
}

export async function uploadDocument(file: File): Promise<UploadedDocument> {
  const form = new FormData();
  form.append("file", file);
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents`, { method: "POST", headers, body: form });
  if (!res.ok) throw new Error(await describeError(res));
  return res.json();
}

export async function listDocuments(): Promise<UploadedDocument[]> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents`, { headers });
  if (!res.ok) throw new Error(await describeError(res));
  return res.json();
}

export async function getDocument(id: string): Promise<UploadedDocument> {
  const headers = await authHeaders();
  const res = await fetch(`${API_BASE}/documents/${id}`, { headers });
  if (!res.ok) throw new Error(await describeError(res));
  return res.json();
}

export async function askQuestion(question: string, documentIds?: string[]): Promise<ChatResponse> {
  const authHdrs = await authHeaders();
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHdrs },
    body: JSON.stringify({ question, document_ids: documentIds }),
  });
  if (!res.ok) throw new Error(await describeError(res));
  return res.json();
}

async function describeError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body.detail ?? `Request failed: ${res.status}`;
  } catch {
    return `Request failed: ${res.status}`;
  }
}
