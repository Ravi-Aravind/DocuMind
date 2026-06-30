"use client";

import { useRef, useState } from "react";

import { ChatTextarea } from "./ChatTextarea";
import { ComposerToolbar } from "./ComposerToolbar";
import { AttachedFileChip } from "./AttachedFileChip";
import { SendButton } from "./SendButton";
import { UploadStatus } from "./UploadStatus";

interface ChatComposerProps {
  question: string;
  setQuestion: (value: string) => void;

  isAsking: boolean;

  onAsk: () => void;

  onUpload: (file: File) => void;

  isUploading: boolean;

  uploadStatus?: string;
}

export function ChatComposer({
  question,
  setQuestion,
  isAsking,
  onAsk,
  onUpload,
  isUploading,
  uploadStatus,
}: ChatComposerProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [attachedFile, setAttachedFile] =
    useState<File | null>(null);

  function openFileDialog() {
    fileInputRef.current?.click();
  }

  function handleFileSelected(
    e: React.ChangeEvent<HTMLInputElement>
  ) {
    const file = e.target.files?.[0];

    if (!file) return;

    setAttachedFile(file);

    onUpload(file);
  }

  function removeAttachment() {
    setAttachedFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }

  const disabled =
    isAsking ||
    (
      question.trim().length === 0 &&
      attachedFile === null
    );

  return (
    <div className="flex flex-col gap-3">

      {/* Composer */}

      <div
        className="
          flex
          flex-col

          rounded-[32px]

          border

          border-[#4A4A4A]

          bg-[#2B2B2B]

          shadow-[0_12px_40px_rgba(0,0,0,.35)]

          transition-all

          duration-200

          ease-out

          focus-within:border-[#666666]
        "
      >

        {/* Text Area */}

        <div
          className="
            px-6

            pt-5

            pb-3
          "
        >
          <ChatTextarea
            value={question}
            onChange={setQuestion}
            onSubmit={onAsk}
            disabled={isAsking}
          />
        </div>

        {/* Attachment */}

        {attachedFile && (

          <div className="px-6 pb-3">

            <AttachedFileChip
              file={attachedFile}
              onRemove={removeAttachment}
            />

          </div>

        )}

        {/* Toolbar */}

        <div
          className="
            flex

            items-center

            justify-between

            border-t

            border-[#3B3B3B]

            px-5

            py-4
          "
        >

          <ComposerToolbar
            disabled={isUploading}
            onAttach={openFileDialog}
          />

          <SendButton
            disabled={disabled}
            loading={isAsking}
            onClick={onAsk}
          />

        </div>

      </div>

      <UploadStatus
        uploading={isUploading}
        status={uploadStatus}
      />

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.txt,.md"
        className="hidden"
        onChange={handleFileSelected}
      />

    </div>
  );
}