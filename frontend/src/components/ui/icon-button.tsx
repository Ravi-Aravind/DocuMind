"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface IconButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  "aria-label": string;
}

export function IconButton({ className, ...props }: IconButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex h-8 w-8 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--card)] text-xs text-[var(--text-muted)] hover:bg-[var(--surface)] focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent)]",
        className
      )}
      {...props}
    />
  );
}