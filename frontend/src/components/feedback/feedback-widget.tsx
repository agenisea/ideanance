"use client";

import { useState, useEffect } from "react";
import { ThumbsUp, ThumbsDown } from "lucide-react";

interface FeedbackWidgetProps {
  interactionId?: string;
  initialRating?: "up" | "down" | null;
  onRate?: (rating: "up" | "down" | null) => void;
  disabled?: boolean;
}

/**
 * Thumbs up/down feedback widget for agent outputs.
 *
 * Triple-encoded: icon + text + color per WCAG.
 * Generic callback — parent handles persistence.
 */
export function FeedbackWidget({
  interactionId,
  initialRating = null,
  onRate,
  disabled = false,
}: FeedbackWidgetProps) {
  const [rating, setRating] = useState<"up" | "down" | null>(initialRating);

  useEffect(() => {
    setRating(initialRating);
  }, [initialRating]);

  function handleRate(value: "up" | "down") {
    if (disabled) return;
    const newRating = rating === value ? null : value;
    setRating(newRating);
    onRate?.(newRating);
  }

  return (
    <div
      role="group"
      aria-label="Rate this response"
      className="flex items-center gap-1"
      style={{ opacity: disabled ? 0.5 : 1 }}
    >
      <button
        onClick={() => handleRate("up")}
        disabled={disabled}
        className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs transition-all active:scale-95 focus-visible:outline-none focus-visible:ring-1"
        style={{
          color:
            rating === "up"
              ? "var(--color-governance-pass)"
              : "var(--color-muted-foreground)",
          backgroundColor:
            rating === "up"
              ? "oklch(0.65 0.15 145 / 0.15)"
              : "transparent",
        }}
        aria-label="Rate as helpful"
        aria-pressed={rating === "up"}
      >
        <ThumbsUp
          size={14}
          fill={rating === "up" ? "currentColor" : "none"}
        />
        <span className="hidden sm:inline">Helpful</span>
      </button>

      <button
        onClick={() => handleRate("down")}
        disabled={disabled}
        className="flex items-center gap-1 px-2 py-1.5 rounded-lg text-xs transition-all active:scale-95 focus-visible:outline-none focus-visible:ring-1"
        style={{
          color:
            rating === "down"
              ? "var(--color-governance-fail)"
              : "var(--color-muted-foreground)",
          backgroundColor:
            rating === "down"
              ? "oklch(0.55 0.20 25 / 0.15)"
              : "transparent",
        }}
        aria-label="Rate as not helpful"
        aria-pressed={rating === "down"}
      >
        <ThumbsDown
          size={14}
          fill={rating === "down" ? "currentColor" : "none"}
        />
        <span className="hidden sm:inline">Not helpful</span>
      </button>
    </div>
  );
}
