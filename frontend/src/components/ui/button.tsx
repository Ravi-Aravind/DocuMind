"use client";

import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cn } from "../../lib/utils";

type ButtonVariant = "primary" | "secondary" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: ButtonVariant;
  size?: ButtonSize;
}

const baseClasses =
  "inline-flex items-center justify-center rounded-lg border transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-[var(--accent)] disabled:opacity-60 disabled:cursor-not-allowed";

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "border-transparent bg-[var(--accent)] text-white hover:bg-black/85",
  secondary:
    "border-[var(--border)] bg-[var(--card)] text-[var(--text)] hover:bg-[var(--hover)]",
  ghost:
    "border-transparent bg-transparent text-[var(--text-muted)] hover:bg-[var(--hover)]",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-3.5 py-2 text-sm",
  lg: "px-4 py-2.5 text-sm",
};

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(
    { className, variant = "secondary", size = "md", asChild, ...props },
    ref
  ) {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        ref={ref}
        className={cn(baseClasses, variantClasses[variant], sizeClasses[size], className)}
        {...props}
      />
    );
  }
);