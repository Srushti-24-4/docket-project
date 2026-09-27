"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Nav } from "@/components/Nav";
import { TextField } from "@/components/ui/text-field";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { signIn } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    const { error } = await signIn(email, password);
    setSubmitting(false);
    if (error) {
      setError(error);
      return;
    }
    router.push("/ask");
  }

  return (
    <main>
      <Nav />
      <div className="max-w-[420px] mx-auto px-7 py-20">
        <h1 className="font-grotesk text-2xl mb-1">Log in</h1>
        <p className="text-text-lo text-sm mb-8">Welcome back.</p>

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
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <p className="text-red text-sm">{error}</p>}
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? "Logging in…" : "Log in"}
          </Button>
        </form>

        <div className="mt-6 flex justify-between text-sm font-mono text-text-lo">
          <Link href="/forgot-password" className="hover:text-white transition-colors">
            Forgot password?
          </Link>
          <Link href="/register" className="hover:text-white transition-colors">
            Create account
          </Link>
        </div>
      </div>
    </main>
  );
}
