"use client";

import { CheckCircle, AlertTriangle, XCircle, MinusCircle } from "lucide-react";

interface GovernanceBadgeProps {
  status: "pass" | "warn" | "fail" | "na";
  score?: number;
}

const STATUS_CONFIG = {
  pass: {
    color: "var(--color-governance-pass)",
    icon: CheckCircle,
    label: "Pass",
  },
  warn: {
    color: "var(--color-governance-warn)",
    icon: AlertTriangle,
    label: "Warning",
  },
  fail: {
    color: "var(--color-governance-fail)",
    icon: XCircle,
    label: "Fail",
  },
  na: {
    color: "var(--color-governance-na)",
    icon: MinusCircle,
    label: "N/A",
  },
};

/**
 * Triple-encoded governance badge: color + icon + text.
 * Per WCAG and CLAUDE.md requirements.
 */
export function GovernanceBadge({ status, score }: GovernanceBadgeProps) {
  const config = STATUS_CONFIG[status];
  const Icon = config.icon;

  return (
    <span
      data-testid="governance-badge"
      role="status"
      aria-label={`Governance status: ${config.label}${score !== undefined ? ` (${Math.round(score * 100)}%)` : ""}`}
      className="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full"
      style={{ color: config.color, borderColor: config.color, border: "1px solid" }}
    >
      <Icon size={12} role="img" aria-label={config.label} />
      <span>{config.label}</span>
      {score !== undefined && (
        <span>{Math.round(score * 100)}%</span>
      )}
    </span>
  );
}
