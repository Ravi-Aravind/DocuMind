"use client";

import { ArrowUp, Loader2 } from "lucide-react";

interface Props {
  disabled: boolean;
  loading?: boolean;
  onClick: () => void;
}

export function SendButton({
  disabled,
  loading = false,
  onClick,
}: Props) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={onClick}
      className={`
        flex
        h-11
        w-11
        items-center
        justify-center
        rounded-full
        transition-all
        duration-200

        ${
          disabled
            ? "bg-[#3A3A3A] text-[#777777] cursor-not-allowed"
            : "bg-white text-black hover:scale-[1.05] active:scale-95"
        }
      `}
    >
      {loading ? (
        <Loader2
          className="animate-spin"
          size={18}
        />
      ) : (
        <ArrowUp size={18} strokeWidth={2.5} />
      )}
    </button>
  );
}