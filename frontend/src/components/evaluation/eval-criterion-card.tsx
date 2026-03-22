"use client";

import { GovernanceBadge } from "@/components/governance/governance-badge";

interface EvalCriterionCardProps {
  criterionId: string;
  description: string;
  metric: string;
  threshold: string;
  priority: string;
  wiredPolicyName?: string;
  wiredFramework?: string;
}

export function EvalCriterionCard({
  criterionId,
  description,
  metric,
  threshold,
  priority,
  wiredPolicyName,
  wiredFramework,
}: EvalCriterionCardProps) {
  return (
    <div
      className="p-3 rounded-lg border"
      style={{ borderColor: "var(--color-border)", background: "var(--color-card)" }}
    >
      <div className="flex items-start justify-between">
        <div>
          <span className="font-mono text-xs" style={{ color: "var(--color-muted-foreground)" }}>
            {criterionId}
          </span>
          <p className="text-sm mt-1">{description}</p>
          <div className="flex gap-3 mt-1 text-xs" style={{ color: "var(--color-muted-foreground)" }}>
            <span>metric: {metric}</span>
            <span>threshold: {threshold}</span>
          </div>
        </div>
        <span className="text-xs px-2 py-0.5 rounded" style={{ background: "var(--color-secondary)" }}>
          {priority}
        </span>
      </div>

      {wiredPolicyName && (
        <div
          className="mt-2 p-2 rounded text-xs flex items-center gap-1"
          style={{ background: "var(--color-accent)" }}
        >
          <span>🔗</span>
          <span>
            {wiredFramework} — {wiredPolicyName}
          </span>
          <GovernanceBadge status="pass" />
        </div>
      )}
    </div>
  );
}
