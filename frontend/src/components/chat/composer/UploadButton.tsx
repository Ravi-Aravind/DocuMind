"use client";

import { ChangeEvent, useRef } from "react";
import { IconButton } from "@/components/ui/icon-button";

export interface UploadButtonProps {
  onUpload: (file: File) => void;
  disabled?: boolean;
}

export function UploadButton({ onUpload, disabled }: UploadButtonProps) {
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const handleAttachClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    onUpload(file);
  };

  return (
    <>
      <IconButton
        aria-label="Attach document"
        onClick={handleAttachClick}
        disabled={disabled}
        className="
          h-10
          w-10
          rounded-full
          border
          border-[#3A3A3A]
          bg-[#262626]
          text-[#FFFFFF]
          hover:bg-[#303030]
          hover:border-[#4A4A4A]
          disabled:opacity-40
          disabled:cursor-not-allowed
          transition
          duration-150
          ease-out
          active:scale-95
        "
      >
        <svg
          aria-hidden="true"
          width={18}
          height={18}
          viewBox="0 0 20 20"
          className="text-[#111111]"
        >
          <path
            d="M6.5 10.75L11.44 5.81C12.35 4.9 13.83 4.9 14.74 5.81C15.65 6.72 15.65 8.2 14.74 9.11L9.22 14.63C7.69 16.16 5.2 16.16 3.67 14.63C2.14 13.1 2.14 10.61 3.67 9.08L8.59 4.16"
            fill="none"
            stroke="#000000"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </IconButton>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md"
        className="hidden"
        onChange={handleFileChange}
      />
    </>
  );
}