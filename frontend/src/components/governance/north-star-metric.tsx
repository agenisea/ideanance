"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface NorthStarMetricProps {
  count: number;
  previousCount?: number;
}

export function NorthStarMetric({
  count,
  previousCount,
}: NorthStarMetricProps) {
  const trend =
    previousCount === undefined
      ? "flat"
      : count > previousCount
        ? "up"
        : count < previousCount
          ? "down"
          : "flat";

  const TrendIcon =
    trend === "up"
      ? TrendingUp
      : trend === "down"
        ? TrendingDown
        : Minus;

  const trendColor =
    trend === "up"
      ? "var(--color-governance-pass)"
      : trend === "down"
        ? "var(--color-governance-fail)"
        : "var(--color-muted-foreground)";

  return (
    <div
      data-testid="north-star-metric"
      className="p-4 rounded"
      style={{
        backgroundColor: "var(--color-card)",
        border: "1px solid var(--color-border)",
      }}
    >
      <p
        className="text-xs font-medium uppercase tracking-wide mb-1"
        style={{ color: "var(--color-muted-foreground)" }}
      >
        Governance-Wired Projects
      </p>
      <div className="flex items-baseline gap-2">
        <span
          className="text-3xl font-bold"
          style={{ fontFamily: "var(--font-heading)" }}
        >
          {count}
        </span>
        <TrendIcon
          size={18}
          style={{ color: trendColor }}
          aria-label={`Trend: ${trend}`}
        />
      </div>
    </div>
  );
}
