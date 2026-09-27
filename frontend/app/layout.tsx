import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

export const metadata: Metadata = {
  title: "Docket — Document Intelligence",
  description: "Upload documents, route them to the right extractor, and ask cited questions.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans min-h-screen">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
