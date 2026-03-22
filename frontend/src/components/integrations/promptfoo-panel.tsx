"use client";

import { Download, Upload, CheckCircle, XCircle } from "lucide-react";

interface PromptfooPanelProps {
  projectId: string;
  lastRunDate?: string;
  lastPassRate?: number;
  onExport: (projectId: string) => void;
  onImport: (projectId: string) => void;
}

export function PromptfooPanel({
  projectId,
  lastRunDate,
  lastPassRate,
  onExport,
  onImport,
}: PromptfooPanelProps) {
  const passRatePct = lastPassRate !== undefined ? Math.round(lastPassRate * 100) : null;

  return (
    <div data-testid="promptfoo-panel" className="space-y-3">
      <h4 className="text-sm font-semibold">promptfoo</h4>

      <div className="flex gap-2">
        <button
          onClick={() => onExport(projectId)}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
          data-testid="promptfoo-export-btn"
        >
          <Download size={14} />
          Export Config
        </button>
        <button
          onClick={() => onImport(projectId)}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
          data-testid="promptfoo-import-btn"
        >
          <Upload size={14} />
          Import Results
        </button>
      </div>

      {lastRunDate && passRatePct !== null && (
        <div className="flex items-center gap-2 text-xs" style={{ color: "var(--color-text-secondary)" }}>
          {passRatePct >= 90 ? (
            <CheckCircle size={14} style={{ color: "var(--color-governance-pass)" }} />
          ) : (
            <XCircle size={14} style={{ color: "var(--color-governance-fail)" }} />
          )}
          <span>Last run: {lastRunDate} — {passRatePct}% pass</span>
        </div>
      )}
    </div>
  );
}
