"use client";

import { GovernanceBadge } from "./governance-badge";

interface PolicyCardProps {
  policyId: string;
  name: string;
  category: string;
  severity: string;
  ruleCount: number;
  wiringCount: number;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export function PolicyCard({
  policyId,
  name,
  category,
  severity,
  ruleCount,
  wiringCount,
  enabled,
  onToggle,
}: PolicyCardProps) {
  return (
    <div
      className="p-3 rounded-lg border"
      style={{ borderColor: "var(--color-border)", background: "var(--color-card)" }}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => onToggle(e.target.checked)}
              aria-label={`${enabled ? "Deactivate" : "Activate"} ${name}`}
            />
            <span className="font-medium text-sm">{name}</span>
          </div>
          <div className="flex items-center gap-2 mt-1 text-xs" style={{ color: "var(--color-muted-foreground)" }}>
            <span>{ruleCount} rules</span>
            <span>·</span>
            <span>severity: {severity}</span>
          </div>
        </div>
        {wiringCount > 0 ? (
          <GovernanceBadge status="pass" score={1} />
        ) : enabled ? (
          <GovernanceBadge status="warn" />
        ) : (
          <GovernanceBadge status="na" />
        )}
      </div>
      {wiringCount > 0 && (
        <div className="mt-2 text-xs" style={{ color: "var(--color-governance-pass)" }}>
          {wiringCount} eval{wiringCount > 1 ? "s" : ""} wired
        </div>
      )}
    </div>
  );
}
