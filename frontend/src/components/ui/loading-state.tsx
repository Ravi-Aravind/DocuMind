"use client";

import * as React from "react";
import { Card } from "./card";
import { Spinner } from "./spinner";

export interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = "Loading…" }: LoadingStateProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--background)] px-4">
      <Card className="px-4 py-3 flex items-center gap-2">
        <Spinner />
        <p className="text-sm text-[var(--text-muted)]">{message}</p>
      </Card>
    </div>
  );
}