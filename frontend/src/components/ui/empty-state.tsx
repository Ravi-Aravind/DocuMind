"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface EmptyStateProps {
  title: string;
  description?: string;
  className?: string;
}

export function EmptyState({ title, description, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-dashed border-[var(--border)] bg-[var(--surface)] px-4 py-6 text-center",
        className
      )}
    >
      <p className="text-sm font-medium text-[var(--text)]">{title}</p>
      {description && (
        <p className="mt-1 text-xs text-[var(--text-muted)]">{description}</p>
      )}
    </div>
  );
}