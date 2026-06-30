"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface ErrorStateProps {
  message: string;
  className?: string;
}

export function ErrorState({ message, className }: ErrorStateProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-[var(--danger)] bg-red-50 px-4 py-3 text-sm text-[var(--danger)]",
        className
      )}
      role="alert"
    >
      {message}
    </div>
  );
}