"use client";

import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface UploadDropzoneProps {
  isUploading: boolean;
  uploadStatus?: string;
  onUpload: (file: File) => void;
}

export function UploadDropzone({
  isUploading,
  uploadStatus,
  onUpload,
}: UploadDropzoneProps) {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    onUpload(file);
  };

  return (
    <div
      className={cn(
        "flex flex-col items-center justify-between rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface)] px-4 py-3 text-xs text-[var(--text-muted)] sm:flex-row"
      )}
    >
      <div className="mb-2 sm:mb-0">
        <p className="font-medium text-[var(--text)]">Upload documents</p>
        <p className="mt-0.5 text-[var(--text-muted)]">
          PDF, DOCX, TXT, MD up to 10MB.
        </p>
        {uploadStatus && (
          <p className="mt-1 text-[var(--text-muted)]">
            Status: {uploadStatus}
          </p>
        )}
      </div>
      <div className="flex items-center gap-2">
        <Button
          size="sm"
          onClick={() => inputRef.current?.click()}
          disabled={isUploading}
        >
          {isUploading ? "Uploading…" : "Choose file"}
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.txt,.md"
          className="hidden"
          onChange={handleFileChange}
        />
      </div>
    </div>
  );
}