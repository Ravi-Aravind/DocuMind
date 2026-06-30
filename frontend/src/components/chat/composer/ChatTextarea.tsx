"use client";

import {
  KeyboardEvent,
  useLayoutEffect,
  useRef,
} from "react";

interface ChatTextareaProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
}

const MIN_HEIGHT = 32;
const MAX_HEIGHT = 240;

export function ChatTextarea({
  value,
  onChange,
  onSubmit,
  disabled = false,
}: ChatTextareaProps) {
  const textareaRef =
    useRef<HTMLTextAreaElement>(null);

  useLayoutEffect(() => {
    const textarea = textareaRef.current;

    if (!textarea) return;

    // Reset first so scrollHeight is recalculated correctly
    textarea.style.height = "0px";

    const scrollHeight = textarea.scrollHeight;

    const nextHeight = Math.max(
      MIN_HEIGHT,
      Math.min(scrollHeight, MAX_HEIGHT)
    );

    textarea.style.height = `${nextHeight}px`;

    textarea.style.overflowY =
      scrollHeight > MAX_HEIGHT
        ? "auto"
        : "hidden";
  }, [value]);

  function handleKeyDown(
    e: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (
      e.key === "Enter" &&
      !e.shiftKey
    ) {
      e.preventDefault();

      if (value.trim()) {
        onSubmit();
      }

      return;
    }
  }

  return (
    <textarea
      ref={textareaRef}
      value={value}
      rows={1}
      spellCheck
      disabled={disabled}
      placeholder="Message DocuMind..."

      onChange={(e) =>
        onChange(e.target.value)
      }

      onKeyDown={handleKeyDown}

      className="
        block

        w-full

        resize-none

        overflow-hidden

        bg-transparent

        border-0

        outline-none

        ring-0

        shadow-none

        p-0

        text-[17px]

        leading-8

        font-normal

        text-[#ECECEC]

        placeholder:text-[#8A8A8A]

        caret-white

        focus:outline-none

        focus:ring-0

        focus:border-0

        disabled:opacity-60
      "

      style={{
        minHeight: MIN_HEIGHT,
        maxHeight: MAX_HEIGHT,
      }}
    />
  );
}