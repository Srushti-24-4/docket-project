"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { Nav } from "@/components/Nav";
import { TextField } from "@/components/ui/text-field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function RegisterPage() {
  const { signUp } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const { error, needsVerification } = await signUp(email, password);
    setSubmitting(false);
    if (error) {
      setError(error);
      return;
    }
    if (needsVerification) {
      setSent(true);
    } else {
      // Email confirmation is off in this Supabase project — session is already active.
      window.location.href = "/ask";
    }
  }

  if (sent) {
    return (
      <main>
        <Nav />
        <div className="max-w-[420px] mx-auto px-7 py-20">
          <h1 className="font-grotesk text-2xl mb-3">Check your email</h1>
          <p className="text-text-lo text-sm leading-relaxed">
            We sent a verification link to <span className="text-white">{email}</span>. Click it to
            activate your account, then come back and log in.
          </p>
          <Link href="/login" className="inline-block mt-6 font-mono text-sm text-amber">
            Back to login
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main>
      <Nav />
      <div className="max-w-[420px] mx-auto px-7 py-20">
        <h1 className="font-grotesk text-2xl mb-1">Create an account</h1>
        <p className="text-text-lo text-sm mb-8">Takes about ten seconds.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <TextField
            type="email"
            placeholder="Email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            type="password"
            placeholder="Password (min. 6 characters)"
            required
            minLength={6}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-red text-sm">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Creating account…" : "Sign up"}
          </Button>
        </form>

        <p className="mt-6 text-sm font-mono text-text-lo">
          Already have an account?{" "}
          <Link href="/login" className="text-amber">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
