"use client";

import { useState, FormEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Nav } from "@/components/Nav";
import { TextField } from "@/components/ui/text-field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function ResetPasswordPage() {
  const { user, loading, updatePassword } = useAuth();
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    // Supabase's email link lands here with a recovery session already set
    // (supabase-js parses it from the URL automatically). If there's no
    // session at all after loading finishes, the link was invalid or expired.
  }, [loading, user]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const { error } = await updatePassword(password);
    setSubmitting(false);
    if (error) {
      setError(error);
      return;
    }
    setDone(true);
    setTimeout(() => router.push("/ask"), 1500);
  }

  return (
    <main>
      <Nav />
      <div className="max-w-[420px] mx-auto px-7 py-20">
        <h1 className="font-grotesk text-2xl mb-1">Set a new password</h1>

        {loading ? (
          <p className="text-text-lo text-sm mt-8">Checking your reset link…</p>
        ) : !user ? (
          <p className="text-red text-sm mt-8">
            This reset link is invalid or has expired. Request a new one from the forgot-password page.
          </p>
        ) : done ? (
          <p className="text-green text-sm mt-8">Password updated — taking you to your documents…</p>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 mt-8">
            <TextField
              type="password"
              placeholder="New password (min. 6 characters)"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && <p className="text-red text-sm">{error}</p>}
            <Button type="submit" disabled={submitting} className="w-full">
              {submitting ? "Updating…" : "Update password"}
            </Button>
          </form>
        )}
      </div>
    </main>
  );
}
