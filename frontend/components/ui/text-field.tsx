import { InputHTMLAttributes } from "react";
import { clsx } from "clsx";

export function TextField({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={clsx(
        "w-full bg-transparent border border-line/40 px-4 py-3 text-sm outline-none focus:border-amber transition-colors",
        className
      )}
      {...props}
    />
  );
}
