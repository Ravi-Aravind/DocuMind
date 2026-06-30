import "./globals.css";
import { Inter } from "next/font/google";
import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { ThemeProvider } from "@/components/theme-provider";
import { Providers } from "@/components/providers";
import { LOGO } from "@/config/logo";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "DocuMind",
  description: "AI workspace for document intelligence",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className + " min-h-screen bg-[#0d0d0d] text-[#ECECEC]"}>
        <ThemeProvider>
          <Providers>
            <div className="flex min-h-screen flex-col">
              {/* Global Header */}
              <header className="border-b border-[#3A3A3A] bg-[#141414]">
                <div className="flex items-center justify-between px-4 py-3 sm:px-6">
                  <Link href="/" className="flex items-center gap-2">
                    <Image
                      src={LOGO.icon}
                      alt={LOGO.alt}
                      width={LOGO.width}
                      height={LOGO.height}
                    />
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold tracking-tight text-[#ECECEC]">
                        DocuMind
                      </span>
                      <span className="text-xs text-[#A1A1AA]">
                        AI workspace for document intelligence
                      </span>
                    </div>
                  </Link>
                  {/* Right side (search/theme/profile) can remain page-level for now */}
                </div>
              </header>

              {/* Main content area (Sidebar + Workspace) */}
              <main className="flex flex-1 bg-[#0d0d0d]">
                {children}
              </main>
            </div>
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}