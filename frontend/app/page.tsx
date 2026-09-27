"use client";

import Link from "next/link";
import { Nav } from "@/components/Nav";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth-context";

export default function HomePage() {
  const { user, loading } = useAuth();

  return (
    <main>
      <Nav />
      <div className="max-w-[1100px] mx-auto px-7 py-24">
        <h1 className="font-grotesk font-semibold text-4xl md:text-5xl leading-tight max-w-[16ch] mb-5">
          Every answer traces back to a page.
        </h1>
        <p className="text-text-lo text-lg max-w-[46ch] mb-10 leading-relaxed">
          Upload PDFs, scanned images, Word docs, or plain text. Docket routes each one to the right
          extractor, indexes it, and answers your questions with the exact source and page attached.
        </p>

        {!loading && (
          <div className="flex gap-4">
            {user ? (
              <Link href="/ask">
                <Button>Go to your documents</Button>
              </Link>
            ) : (
              <>
                <Link href="/register">
                  <Button>Create a free account</Button>
                </Link>
                <Link href="/login">
                  <Button variant="ghost">Log in</Button>
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
