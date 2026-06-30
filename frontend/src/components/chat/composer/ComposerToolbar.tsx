"use client";

import {
  Paperclip,
  Globe,
  Mic,
} from "lucide-react";

interface ComposerToolbarProps {
  disabled?: boolean;
  onAttach: () => void;
}

export function ComposerToolbar({
  disabled,
  onAttach,
}: ComposerToolbarProps) {
  const buttonClass = `
    flex
    h-9
    w-9
    items-center
    justify-center
    rounded-full
    text-[#9CA3AF]
    transition-all
    duration-200
    hover:bg-[#3A3A3A]
    hover:text-white
    disabled:opacity-50
    disabled:cursor-not-allowed
  `;

  return (
    <div className="flex items-center gap-1">
      <button
        type="button"
        onClick={onAttach}
        disabled={disabled}
        className={buttonClass}
        title="Upload document"
      >
        <Paperclip size={18} />
      </button>

      <button
        type="button"
        disabled
        className={buttonClass}
        title="Web Search (Coming Soon)"
      >
        <Globe size={18} />
      </button>

      <button
        type="button"
        disabled
        className={buttonClass}
        title="Voice (Coming Soon)"
      >
        <Mic size={18} />
      </button>
    </div>
  );
}