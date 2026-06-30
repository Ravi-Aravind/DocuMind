"use client";

import {
  Copy,
  RotateCcw,
  ThumbsUp,
  ThumbsDown,
  BookOpen,
  MoreHorizontal,
} from "lucide-react";

import { motion } from "framer-motion";

interface MessageActionsProps {
  text: string;

  hasSources?: boolean;

  onCopy?: () => void;

  onRegenerate?: () => void;
}

export function MessageActions({
  text,

  hasSources = false,

  onCopy,

  onRegenerate,
}: MessageActionsProps) {
  async function copy() {
    try {
      await navigator.clipboard.writeText(text);

      onCopy?.();
    } catch {
      console.error("Copy failed");
    }
  }

  const buttonStyle =
    "flex h-8 w-8 items-center justify-center rounded-md text-[#8A8A8A] transition-all duration-150 hover:bg-[#2F2F2F] hover:text-white";

  return (
    <motion.div
      initial={{
        opacity: 0,
        y: 4,
      }}
      whileHover={{
        opacity: 1,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      className="
        mt-2
        flex
        items-center
        gap-1
      "
    >
      <button
        className={buttonStyle}
        onClick={copy}
        aria-label="Copy"
      >
        <Copy size={15} />
      </button>

      <button
        disabled
        className={buttonStyle}
        title="Coming Soon"
      >
        <RotateCcw size={15} />
      </button>

      <button
        disabled
        className={buttonStyle}
        title="Coming Soon"
      >
        <ThumbsUp size={15} />
      </button>

      <button
        disabled
        className={buttonStyle}
        title="Coming Soon"
      >
        <ThumbsDown size={15} />
      </button>

      {hasSources && (
        <button
          disabled
          className={buttonStyle}
          title="Sources"
        >
          <BookOpen size={15} />
        </button>
      )}

      <button
        disabled
        className={buttonStyle}
        title="More"
      >
        <MoreHorizontal size={15} />
      </button>
    </motion.div>
  );
}