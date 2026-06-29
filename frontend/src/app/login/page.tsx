"use client";

import { apiClient } from "../../lib/api";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";

export default function LoginPage() {
  const handleGoogleLogin = async () => {
    try {
      const res = await apiClient.post("/auth/google/login", {
        provider: "google",
      });
      const url = res.data.authorization_url;
      window.location.href = url;
    } catch (err) {
      console.error("Google login failed", err);
      alert("Unable to start Google login. Please try again.");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="w-full max-w-sm card px-6 py-5"
      >
        <div className="mb-4 flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-lg border border-[var(--border)]">
            <span className="text-xs font-semibold text-[var(--accent)]">
              DM
            </span>
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-semibold">Sign in to DocuMind</h1>
            <p className="text-xs text-[var(--text-muted)]">
              Use your Google account to continue.
            </p>
          </div>
        </div>

        <Button
          variant="primary"
          size="lg"
          className="w-full mt-2"
          onClick={handleGoogleLogin}
        >
          Continue with Google
        </Button>
      </motion.div>
    </div>
  );
}