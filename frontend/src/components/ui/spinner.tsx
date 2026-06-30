"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface SpinnerProps {
  size?: number;
  className?: string;
}

export function Spinner({ size = 16, className }: SpinnerProps) {
  const style: React.CSSProperties = {
    width: size,
    height: size,
    borderWidth: 2,
  };
  return (
    <span
      className={cn(
        "inline-block animate-spin rounded-full border border-[var(--border)] border-t-[var(--accent)]",
        className
      )}
      style={style}
      aria-label="Loading"
    />
  );
}