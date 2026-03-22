"use client";

interface CompositeScoreProps {
  compositeScore: number;
  perFrameworkScores: Record<string, number>;
}

export function CompositeScore({
  compositeScore,
  perFrameworkScores,
}: CompositeScoreProps) {
  const pct = Math.round(compositeScore * 100);
  const statusColor =
    pct >= 80
      ? "var(--color-governance-pass)"
      : pct >= 50
        ? "var(--color-governance-warn)"
        : "var(--color-governance-fail)";

  return (
    <div data-testid="composite-score" className="space-y-3">
      <div className="flex items-baseline gap-2">
        <span className="text-sm font-medium">Governance Score:</span>
        <span
          className="text-lg font-bold"
          style={{ color: statusColor }}
          data-testid="composite-score-value"
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
        aria-label={`Overall governance score: ${pct}%`}
      >
        <div
          className="h-full rounded-full transition-all duration-300"
          style={{
            width: `${pct}%`,
            backgroundColor: statusColor,
          }}
        />
      </div>

      {Object.keys(perFrameworkScores).length > 0 && (
        <div className="space-y-2">
          {Object.entries(perFrameworkScores).map(([framework, score]) => {
            const fwPct = Math.round(score * 100);
            const fwColor =
              fwPct >= 80
                ? "var(--color-governance-pass)"
                : fwPct >= 50
                  ? "var(--color-governance-warn)"
                  : "var(--color-governance-fail)";

            return (
              <div key={framework} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span>{framework}</span>
                  <span style={{ color: fwColor }}>{fwPct}%</span>
                </div>
                <div
                  className="h-1.5 rounded-full overflow-hidden"
                  style={{ backgroundColor: "var(--color-surface-hover)" }}
                  role="meter"
                  aria-valuenow={fwPct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${framework} governance score: ${fwPct}%`}
                >
                  <div
                    className="h-full rounded-full transition-all duration-300"
                    style={{
                      width: `${fwPct}%`,
                      backgroundColor: fwColor,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
