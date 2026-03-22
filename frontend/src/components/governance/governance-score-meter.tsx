"use client";

interface GovernanceScoreMeterProps {
  score: number; // 0.0 to 1.0
  label?: string;
}

/**
 * ARIA role=meter governance score display.
 * Triple-encoded: color + bar + text.
 */
export function GovernanceScoreMeter({
  score,
  label = "Governance Score",
}: GovernanceScoreMeterProps) {
  const percent = Math.round(score * 100);
  const status = score >= 0.8 ? "pass" : score >= 0.5 ? "warn" : "fail";
  const color = `var(--color-governance-${status})`;

  return (
    <div className="flex items-center gap-2">
      <div
        role="meter"
        aria-valuenow={percent}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`${label}: ${percent}%`}
        className="w-24 h-2 rounded-full overflow-hidden"
        style={{ background: "var(--color-muted)" }}
      >
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${percent}%`, background: color }}
        />
      </div>
      <span className="text-xs font-medium" style={{ color }}>
        {percent}%
      </span>
    </div>
  );
}
