"use client";

interface ScoreCoverageProps {
  score: number;
  coverage: Record<string, number>;
}

export function ScoreCoverage({
  score,
  coverage,
}: ScoreCoverageProps) {
  const pct = Math.round(score * 100);
  const statusColor =
    pct >= 80
      ? "var(--color-governance-pass)"
      : pct >= 50
        ? "var(--color-governance-warn)"
        : "var(--color-governance-fail)";

  return (
    <div data-testid="score-coverage" className="space-y-3">
      <div className="flex items-baseline gap-2">
        <span className="text-sm font-medium">Score:</span>
        <span
          className="text-xl font-bold"
          style={{ color: statusColor }}
        >
          {pct}%
        </span>
      </div>

      <div
        className="h-2 rounded-full overflow-hidden"
        style={{ backgroundColor: "var(--color-surface-hover)" }}
        role="meter"
        aria-valuenow={pct}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Governance score: ${pct}%`}
      >
        <div
          className="h-full rounded-full"
          style={{
            width: `${pct}%`,
            backgroundColor: statusColor,
          }}
        />
      </div>

      {Object.keys(coverage).length > 0 && (
        <div className="space-y-1 mt-2">
          <p
            className="text-xs font-medium"
            style={{ color: "var(--color-muted-foreground)" }}
          >
            Coverage by framework
          </p>
          {Object.entries(coverage).map(([fw, cov]) => (
            <div key={fw} className="flex justify-between text-xs">
              <span>{fw}</span>
              <span>{Math.round(cov * 100)}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
