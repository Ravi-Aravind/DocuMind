"use client";

import React, { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { apiClient } from "@/lib/api";
import Sidebar from "@/components/layout/sidebar";
import MainChatArea, { type ChatMessage } from "@/components/chat/main-chat-area";

type SourceCitation = {
  document_id: string;
  chunk_text: string;
  score: number;
  page?: number;
  section?: string;
  title?: string;
};

export default function HomePage() {
  const router = useRouter();
  const { user } = useAuth();

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isAsking, setIsAsking] = useState(false);
  const [askError, setAskError] = useState<string | null>(null);
  const [selectedCollectionId, setSelectedCollectionId] = useState<string | null>(
    null
  );
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const authGuard = (action: "ask" | "upload" | "session") => {
    if (!user) {
      const message =
        action === "ask"
          ? "Please sign in to ask questions."
          : action === "upload"
          ? "Please sign in to upload documents."
          : "Please sign in to view your sessions.";
      alert(message);
      router.push("/login");
      return false;
    }
    return true;
  };

  const handleAsk = useCallback(async () => {
    const q = question.trim();
    if (!q || isAsking) return;

    if (!authGuard("ask")) return;

    setQuestion("");
    setAskError(null);
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setIsAsking(true);

    try {
      const { data } = await apiClient.post("/qa/ask", {
        question: q,
        // For now, we pass collection_name derived from selectedCollectionId if needed.
        collection_name: selectedCollectionId ?? undefined,
      });

      const sources = Array.isArray(data.sources) ? data.sources : [];
      const citations: SourceCitation[] = sources.map((s: any) => ({
        document_id: s.document_id,
        chunk_text: s.snippet,
        score: s.score,
        page: s.page,
        section: s.section,
        title: s.document_title,
      }));

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer ?? "",
          citations,
          confidence: data.confidence,
        },
      ]);
    } catch (err: unknown) {
      const msg =
        err instanceof Error
          ? err.message
          : "Something went wrong. Please try again.";
      setAskError(msg);
      console.error(err);
    } finally {
      setIsAsking(false);
    }
  }, [question, isAsking, selectedCollectionId, router, user]);

  const handleUpload = useCallback(
    async (file: File) => {
      if (!file) return;
      if (!authGuard("upload")) return;

      setIsUploading(true);
      setUploadStatus("Uploading...");

      const formData = new FormData();
      formData.append("file", file);

      try {
        const { data } = await apiClient.post("/documents/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        setUploadStatus("Processing...");
        let attempts = 0;

        const docId = data.id;
        const poll = setInterval(async () => {
          attempts++;
          try {
            const res = await apiClient.get(`/documents/${docId}/status`);
            const s = res.data;
            if (s.status === "ready") {
              clearInterval(poll);
              setUploadStatus(`Ready: ${file.name}`);
              setTimeout(() => setUploadStatus(null), 3000);
              setIsUploading(false);
            } else if (s.status === "failed") {
              clearInterval(poll);
              setUploadStatus(`Failed: ${s.error_message ?? "unknown error"}`);
              setIsUploading(false);
            } else if (attempts > 30) {
              clearInterval(poll);
              setUploadStatus("Still processing...");
              setIsUploading(false);
            }
          } catch {
            clearInterval(poll);
            setUploadStatus("Status check failed.");
            setIsUploading(false);
          }
        }, 2000);
      } catch {
        setUploadStatus("Upload failed.");
        setIsUploading(false);
      }
    },
    [router, user]
  );

  const handleSelectSession = useCallback(
    async (sessionId: string | null) => {
      if (!sessionId) {
        setActiveSessionId(null);
        setMessages([]);
        return;
      }

      if (!authGuard("session")) return;

      setActiveSessionId(sessionId);
      try {
        const { data } = await apiClient.get(`/qa/sessions/${sessionId}`);
        const newMessages: ChatMessage[] = Array.isArray(data.messages)
          ? data.messages.map((m: any) => ({
              role: m.role,
              content: m.content,
              citations: [],
              confidence: m.confidence,
            }))
          : [];
        setMessages(newMessages);
      } catch (err) {
        console.error(err);
      }
    },
    [router, user]
  );

  return (
    <div className="flex min-h-screen bg-[var(--background)] text-[var(--text)]">
      {/* Sidebar */}
      <aside
        className="flex h-screen flex-col border-r border-[var(--border)] bg-[var(--surface)]"
        style={{ width: sidebarCollapsed ? 72 : 260 }}
      >
        <Sidebar
          activeSessionId={activeSessionId}
          onSelectSession={handleSelectSession}
          onNewChat={() => {
            setMessages([]);
            setActiveSessionId(null);
            setQuestion("");
          }}
          collapsed={sidebarCollapsed}
        />
      </aside>

      {/* Main area */}
      <main className="flex flex-1 flex-col">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--card)] px-6 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl border border-[var(--border)]">
              <span className="text-xs font-semibold text-[var(--accent)]">
                DM
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-semibold tracking-tight">
                DocuMind
              </span>
              <span className="text-xs text-[var(--text-muted)]">
                Academic RAG assistant
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="hidden text-xs text-[var(--text-muted)] sm:inline">
                  {user.email}
                </span>
                <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs font-semibold text-[var(--accent)]">
                  {(user.email?.[0] ?? "U").toUpperCase()}
                </div>
              </>
            ) : (
              <button
                type="button"
                className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-3 py-1.5 text-xs text-[var(--text-muted)] hover:bg-[var(--hover)]"
                onClick={() => router.push("/login")}
              >
                Sign in
              </button>
            )}
          </div>
        </header>

        {/* Chat area */}
        <div className="flex flex-1 flex-col">
          <MainChatArea
            question={question}
            setQuestion={setQuestion}
            messages={messages}
            isAsking={isAsking}
            onAsk={handleAsk}
            onUpload={handleUpload}
            isUploading={isUploading}
            uploadStatus={uploadStatus ?? askError ?? undefined}
            onToggleSidebar={() => setSidebarCollapsed((c) => !c)}
          />
        </div>
      </main>
    </div>
  );
}