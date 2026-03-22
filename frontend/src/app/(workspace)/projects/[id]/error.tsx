"use client";

import { AlertTriangle } from "lucide-react";

export default function ProjectError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <AlertTriangle size={48} style={{ color: "var(--color-destructive)" }} />
      <h2 className="text-lg font-semibold">Something went wrong</h2>
      <p className="text-sm" style={{ color: "var(--color-muted-foreground)" }}>
        {error.message || "An unexpected error occurred."}
      </p>
      <button
        onClick={reset}
        className="px-4 py-2 rounded text-sm font-medium"
        style={{
          backgroundColor: "var(--color-primary)",
          color: "var(--color-primary-foreground)",
        }}
      >
        Try again
      </button>
    </div>
  );
}
