import { clsx } from "clsx";
import { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
}

export function Button({ variant = "primary", className, ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "font-mono text-sm px-5 py-3 transition-transform hover:-translate-y-0.5 disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:translate-y-0",
        variant === "primary" && "bg-amber text-blueprint-deep border border-amber",
        variant === "ghost" && "bg-transparent text-white border border-line/40 hover:border-text-lo",
        className
      )}
      {...props}
    />
  );
}
