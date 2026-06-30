"use client";

import {
  KeyboardEvent,
  useEffect,
  useLayoutEffect,
  useRef,
} from "react";

interface AutoGrowTextareaProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled?: boolean;
}

const MIN_HEIGHT = 28;
const MAX_HEIGHT = 240;

export default function AutoGrowTextarea({
  value,
  onChange,
  onSubmit,
  disabled = false,
}: AutoGrowTextareaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const resize = () => {
    const textarea = textareaRef.current;

    if (!textarea) return;

    textarea.style.height = "auto";

    const nextHeight = Math.min(
      textarea.scrollHeight,
      MAX_HEIGHT
    );

    textarea.style.height = `${Math.max(
      MIN_HEIGHT,
      nextHeight
    )}px`;

    textarea.style.overflowY =
      textarea.scrollHeight > MAX_HEIGHT
        ? "auto"
        : "hidden";
  };

  useLayoutEffect(() => {
    resize();
  }, [value]);

  useEffect(() => {
    resize();
  }, []);

  function handleKeyDown(
    e: KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();

      if (value.trim()) {
        onSubmit();
      }
    }
  }

  return (
    <textarea
      ref={textareaRef}
      rows={1}
      value={value}
      disabled={disabled}
      spellCheck
      placeholder="Message DocuMind..."

      onKeyDown={handleKeyDown}

      onChange={(e) =>
        onChange(e.target.value)
      }

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

        appearance-none

        p-0

        text-[17px]

        leading-8

        font-normal

        tracking-normal

        text-[#ECECEC]

        caret-white

        placeholder:text-[#8A8A8A]

        focus:outline-none

        focus:ring-0

        focus:border-transparent

        disabled:opacity-60
      "
    />
  );
}