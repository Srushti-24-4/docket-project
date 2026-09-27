"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { Nav } from "@/components/Nav";
import { TextField } from "@/components/ui/text-field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function ForgotPasswordPage() {
  const { requestPasswordReset } = useAuth();
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const { error } = await requestPasswordReset(email);
    setSubmitting(false);
    if (error) {
      setError(error);
      return;
    }
    setSent(true);
  }

  return (
    <main>
      <Nav />
      <div className="max-w-[420px] mx-auto px-7 py-20">
        <h1 className="font-grotesk text-2xl mb-1">Reset your password</h1>
        <p className="text-text-lo text-sm mb-8">
          We'll email you a link to set a new one.
        </p>

        {sent ? (
          <p className="text-sm leading-relaxed">
            If an account exists for <span className="text-white">{email}</span>, a reset link is on
            its way. Click it to continue — the link opens{" "}
            <span className="text-white">/reset-password</span> in this app.
          </p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <TextField
              type="email"
              placeholder="Email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            {error && <p className="text-red text-sm">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? "Sending…" : "Send reset link"}
            </Button>
          </form>
        )}

        <Link href="/login" className="inline-block mt-6 font-mono text-sm text-text-lo hover:text-white">
          Back to login
        </Link>
      </div>
    </main>
  );
}
