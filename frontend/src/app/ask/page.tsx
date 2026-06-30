"use client";

import {
  useState,
  useRef,
  useEffect,
  useCallback,
} from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/auth-context";
import { apiClient } from "@/lib/api";
import { useCollections, useQASessions } from "@/lib/hooks";
import type { Collection, QASession } from "@/lib/hooks";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { BrandAvatar } from "@/constants/BrandAvatar";

type SourceCitation = {
  document_id: string;
  chunk_text: string;
  score: number;
  page?: number;
  section?: string;
  title?: string;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  citations?: SourceCitation[];
  confidence?: string;
};

export default function AskPage() {
  const router = useRouter();
  const { user, loading, authenticated } = useAuth();

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

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const { data: collections = [] } = useCollections();
  const { data: sessions = [], refetch: refetchSessions } = useQASessions();

  // Protected route guard: redirect unauthenticated users
  useEffect(() => {
    if (!loading && !authenticated) {
      router.replace("/login");
    }
  }, [loading, authenticated, router]);

  // While auth is loading, show a loading shell
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4">
        <div className="card px-4 py-3">
          <p className="text-sm text-[var(--text-muted)]">
            Loading your workspace…
          </p>
        </div>
      </div>
    );
  }

  // Scroll to latest message when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isAsking]);

  // -- Ask --------------------------------------------------------------
  const handleAsk = useCallback(async () => {
    const q = question.trim();
    if (!q || isAsking) return;

    setQuestion("");
    setAskError(null);
    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setIsAsking(true);

    try {
      const { data } = await apiClient.post("/qa/ask", {
        question: q,
        // Backend expects collection_name; we pass selectedCollectionId here.
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

      refetchSessions();
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : "Something went wrong. Please try again.";
      setAskError(msg);
    } finally {
      setIsAsking(false);
    }
  }, [question, isAsking, selectedCollectionId, refetchSessions]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  // -- Upload -----------------------------------------------------------
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

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
  };

  // -- Sessions ---------------------------------------------------------
  const handleSelectSession = async (sessionId: string | null) => {
    if (!sessionId) {
      setActiveSessionId(null);
      setMessages([]);
      return;
    }

    setActiveSessionId(sessionId);
    try {
      const { data } = await apiClient.get(`/qa/sessions/${sessionId}`);
      const newMessages: ChatMessage[] = Array.isArray(data.messages)
        ? data.messages.map((m: any) => ({
            role: m.role,
            content: m.content,
            // Session messages currently do not include citations field
            citations: [],
            confidence: m.confidence,
          }))
        : [];
      setMessages(newMessages);
    } catch (err) {
      console.error(err);
    }
  };

  // -- Render -----------------------------------------------------------

  return (
    <div className="flex min-h-screen flex-col bg-[var(--background)] text-[var(--text)]">
      <header className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--card)] px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--border)]">
            <span className="text-xs font-semibold text-[var(--accent)]"><BrandAvatar /></span>
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-semibold tracking-tight">DocuMind</h1>
            <p className="text-xs text-[var(--text-muted)]">
              Ask questions grounded in your documents.
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs text-[var(--text-muted)]">
          {user ? (
            <>
              <span className="hidden sm:inline">{user.email}</span>
              <div className="flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs font-semibold text-[var(--accent)]">
                {(user.email?.[0] ?? "U").toUpperCase()}
              </div>
            </>
          ) : (
            <Button
              size="sm"
              onClick={() => router.push("/login")}
            >
              Sign in
            </Button>
          )}
        </div>
      </header>

      <main className="flex flex-1 gap-0 overflow-hidden">
        {/* Left sidebar: collections & sessions */}
        <aside
          className="flex w-72 flex-col border-r border-[var(--border)] bg-[var(--surface)]"
        >
          <div className="px-4 py-3">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
              Collections
            </h2>
            <div className="mt-2 space-y-1">
              <button
                type="button"
                className={cn(
                  "w-full rounded-md px-2 py-1 text-left text-xs transition",
                  selectedCollectionId === null
                    ? "bg-[var(--accent)] text-white"
                    : "hover:bg-[var(--hover)] text-[var(--text-muted)]"
                )}
                onClick={() => setSelectedCollectionId(null)}
              >
                All documents
              </button>
              {collections.map((c: Collection) => (
                <button
                  key={c.id}
                  type="button"
                  className={cn(
                    "w-full rounded-md px-2 py-1 text-left text-xs transition",
                    selectedCollectionId === c.id
                      ? "bg-[var(--accent)] text-white"
                      : "hover:bg-[var(--hover)] text-[var(--text-muted)]"
                  )}
                  onClick={() =>
                    setSelectedCollectionId((prev) => (prev === c.id ? null : c.id))
                  }
                >
                  {c.name}
                </button>
              ))}
              {collections.length === 0 && (
                <p className="mt-1 text-xs text-[var(--text-muted)]">
                  No collections yet.
                </p>
              )}
            </div>
          </div>

          <div className="px-4 py-3 border-t border-[var(--border)]">
            <h2 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
              Sessions
            </h2>
            <div className="mt-2 space-y-1">
              <button
                type="button"
                className="w-full rounded-md px-2 py-1 text-left text-xs text-[var(--text-muted)] hover:bg-[var(--hover)]"
                onClick={() => {
                  setActiveSessionId(null);
                  setMessages([]);
                }}
              >
                + New session
              </button>
              {sessions.map((s: QASession) => (
                <button
                  key={s.id}
                  type="button"
                  className={cn(
                    "w-full rounded-md px-2 py-1 text-left text-xs transition",
                    activeSessionId === s.id
                      ? "bg-[var(--accent)] text-white"
                      : "hover:bg-[var(--hover)] text-[var(--text-muted)]"
                  )}
                  onClick={() => handleSelectSession(s.id)}
                >
                  {s.title || "Untitled session"}
                </button>
              ))}
              {sessions.length === 0 && (
                <p className="mt-1 text-xs text-[var(--text-muted)]">
                  No sessions yet.
                </p>
              )}
            </div>
          </div>
        </aside>

        {/* Chat area */}
        <section className="flex flex-1 flex-col bg-[var(--background)]">
          <div className="flex-1 overflow-y-auto px-4 py-4">
            <div className="mx-auto max-w-3xl space-y-4">
              {uploadStatus && (
                <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2 text-xs text-[var(--text-muted)]">
                  {uploadStatus}
                </div>
              )}

              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={cn(
                    "flex gap-3",
                    msg.role === "assistant" ? "justify-start" : "justify-end"
                  )}
                >
                  {msg.role === "assistant" && (
                    <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs font-semibold text-[var(--accent)]">
                      D
                    </div>
                  )}

                  <div
                    className="max-w-[80%] rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3 text-sm leading-relaxed"
                  >
                    <p>{msg.content}</p>

                    {msg.citations && msg.citations.length > 0 && (
                      <div className="mt-3 space-y-2 border-top border-[var(--border)] pt-3">
                        <p className="text-xs font-medium text-[var(--text-muted)]">
                          Sources
                        </p>
                        {msg.citations.slice(0, 3).map((c, ci) => (
                          <div
                            key={ci}
                            className="rounded-md bg-[var(--surface)] px-3 py-2 text-xs"
                          >
                            {c.title && (
                              <p className="mb-0.5 font-medium">
                                {c.title +
                                  (c.page != null ? " p. " + String(c.page) : "") +
                                  (c.section ? " - " + c.section : "")}
                              </p>
                            )}
                            <p className="line-clamp-2 text-[var(--text-muted)]">
                              {c.chunk_text}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}

                    {msg.confidence && (
                      <p className="mt-2 text-xs text-[var(--text-muted)]">
                        {"Confidence: " + msg.confidence}
                      </p>
                    )}
                  </div>

                  {msg.role === "user" && (
                    <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs font-semibold text-[var(--accent)]">
                      {(user?.email?.[0] ?? "U").toUpperCase()}
                    </div>
                  )}
                </div>
              ))}

              {isAsking && (
                <div className="flex gap-3 justify-start">
                  <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs font-semibold text-[var(--accent)]">
                    D
                  </div>
                  <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <span className="h-1.5 w-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" />
                      <span className="h-1.5 w-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" />
                      <span className="h-1.5 w-1.5 rounded-full bg-[var(--text-muted)] animate-bounce" />
                    </div>
                  </div>
                </div>
              )}

              {askError && (
                <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-sm text-red-600">
                  {askError}
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input + upload */}
          <div className="border-t border-[var(--border)] bg-[var(--card)] px-4 py-3">
            <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-3 py-2">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question about your documents..."
                rows={1}
                className="flex-1 resize-none bg-transparent text-sm outline-none"
              />
              <Button
                size="sm"
                onClick={handleAsk}
                disabled={!question.trim() || isAsking}
              >
                Send
              </Button>
              <Button
                size="sm"
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading}
              >
                {isUploading ? "Uploading…" : "Upload"}
              </Button>
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt,.md"
                className="hidden"
                onChange={handleUpload}
              />
            </div>
            <p className="mt-1.5 text-center text-xs text-[var(--text-muted)]">
              Enter to send · Shift+Enter for newline
            </p>
          </div>
        </section>
      </main>

      {/* Empty state hint */}
      {!messages.length && !askError && !isUploading && !uploadStatus && (
        <div className="pointer-events-none fixed inset-x-0 bottom-6 flex justify-center">
          <div className="rounded-lg border border-[var(--border)] bg-[var(--card)] px-4 py-2 text-xs text-[var(--text-muted)] shadow-subtle">
            Upload a document to begin, then ask a question.
          </div>
        </div>
      )}
    </div>
  );
}