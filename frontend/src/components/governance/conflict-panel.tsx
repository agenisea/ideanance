"use client";

import { AlertTriangle } from "lucide-react";
import type { PolicyConflict } from "@/stores/governance-store";

interface ConflictPanelProps {
  conflicts: PolicyConflict[];
}

const CONFLICT_TYPE_LABELS: Record<string, string> = {
  overlap: "Overlap",
  equivalent: "Equivalent",
  subset: "Subset",
  partial: "Partial",
  contradiction: "Contradiction",
  gap: "Gap",
};

export function ConflictPanel({ conflicts }: ConflictPanelProps) {
  if (conflicts.length === 0) {
    return (
      <div
        data-testid="conflict-panel-empty"
        className="text-sm p-3 rounded"
        style={{
          color: "var(--color-text-secondary)",
          backgroundColor: "var(--color-surface)",
        }}
      >
        No cross-framework conflicts detected.
      </div>
    );
  }

  return (
    <div data-testid="conflict-panel" className="space-y-3">
      <div className="flex items-center gap-2 text-sm font-medium">
        <AlertTriangle size={16} style={{ color: "var(--color-governance-warn)" }} />
        <span>{conflicts.length} Cross-Framework Conflict{conflicts.length !== 1 ? "s" : ""}</span>
      </div>

      <div className="space-y-2">
        {conflicts.map((conflict, idx) => (
          <div
            key={`${conflict.policyA}-${conflict.policyB}-${idx}`}
            data-testid={`conflict-${idx}`}
            className="p-3 rounded text-sm space-y-1"
            style={{
              backgroundColor: "var(--color-surface)",
              border: "1px solid var(--color-border)",
            }}
          >
            <div className="font-medium">
              {conflict.policyA}
              <span style={{ color: "var(--color-text-secondary)" }}> ↔ </span>
              {conflict.policyB}
            </div>
            <div className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
              Type: {CONFLICT_TYPE_LABELS[conflict.conflictType] ?? conflict.conflictType}
            </div>
            <div className="text-xs">{conflict.description}</div>
            {conflict.resolution && (
              <div className="text-xs" style={{ color: "var(--color-primary)" }}>
                Resolution: {conflict.resolution}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
