"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export function Nav() {
  const { user, signOut } = useAuth();
  const router = useRouter();

  async function handleSignOut() {
    await signOut();
    router.push("/login");
  }

  return (
    <header className="border-b border-line/40">
      <div className="max-w-[1100px] mx-auto px-7 py-5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2 font-grotesk text-lg">
          <span className="w-[22px] h-[22px] border border-amber text-amber flex items-center justify-center text-[11px] font-mono">
            D
          </span>
          DOCKET
        </Link>
        <nav className="flex items-center gap-6 font-mono text-sm text-text-lo">
          {user ? (
            <>
              <Link href="/ask" className="hover:text-white transition-colors">
                Ask
              </Link>
              <span className="hidden sm:inline">{user.email}</span>
              <button onClick={handleSignOut} className="hover:text-white transition-colors">
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-white transition-colors">
                Log in
              </Link>
              <Link href="/register" className="hover:text-white transition-colors">
                Sign up
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
