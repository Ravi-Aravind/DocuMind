"use client";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 justify-start">
      <div className="flex h-7 w-7 flex-shrink-0 items-center justify-center rounded-full border border-[#E5E7EB] bg-[#FFFFFF] text-xs font-semibold text-[#111827]">
        D
      </div>
      <div className="rounded-lg border border-[#E5E7EB] bg-[#FFFFFF] px-4 py-3">
        <div className="flex items-center gap-1.5">
          <span className="h-1.5 w-1.5 rounded-full bg-[#6B7280] animate-bounce" />
          <span className="h-1.5 w-1.5 rounded-full bg-[#6B7280] animate-bounce" />
          <span className="h-1.5 w-1.5 rounded-full bg-[#6B7280] animate-bounce" />
        </div>
      </div>
    </div>
  );
}