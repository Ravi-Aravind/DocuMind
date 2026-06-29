"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface AvatarProps {
  initials: string;
  className?: string;
}

export function Avatar({ initials, className }: AvatarProps) {
  return (
    <div
      className={cn(
        "flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs font-semibold text-[var(--accent)]",
        className
      )}
      aria-label="User avatar"
    >
      {initials}
    </div>
  );
}