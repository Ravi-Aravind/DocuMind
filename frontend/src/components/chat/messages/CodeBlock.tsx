"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";

interface CodeBlockProps {
  language?: string;
  code: string;
}

export function CodeBlock({
  language = "text",
  code,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(code);

    setCopied(true);

    setTimeout(() => {
      setCopied(false);
    }, 2000);
  }

  return (
    <div
      className="
        my-5
        overflow-hidden
        rounded-2xl
        border
        border-[#3A3A3A]
        bg-[#1B1B1B]
      "
    >
      <div
        className="
          flex
          items-center
          justify-between
          border-b
          border-[#343434]
          bg-[#242424]
          px-4
          py-2
        "
      >
        <span
          className="
            text-xs
            uppercase
            tracking-wide
            text-[#B4B4B4]
          "
        >
          {language}
        </span>

        <button
          onClick={copy}
          className="
            flex
            items-center
            gap-1
            rounded-md
            px-2
            py-1
            text-xs
            text-[#A0A0A0]
            transition
            hover:bg-[#353535]
            hover:text-white
          "
        >
          {copied ? (
            <>
              <Check size={14} />
              Copied
            </>
          ) : (
            <>
              <Copy size={14} />
              Copy
            </>
          )}
        </button>
      </div>

      <pre className="overflow-x-auto p-4">
        <code>{code}</code>
      </pre>
    </div>
  );
}