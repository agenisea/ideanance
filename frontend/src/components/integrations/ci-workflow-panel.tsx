"use client";

import { GitBranch, Eye } from "lucide-react";

interface CIWorkflowPanelProps {
  projectId: string;
  configured: boolean;
  onGenerate: (projectId: string) => void;
  onPreview: (projectId: string) => void;
}

export function CIWorkflowPanel({
  projectId,
  configured,
  onGenerate,
  onPreview,
}: CIWorkflowPanelProps) {
  return (
    <div data-testid="ci-workflow-panel" className="space-y-3">
      <h4 className="text-sm font-semibold">GitHub Actions</h4>

      <div className="flex gap-2">
        <button
          onClick={() => onGenerate(projectId)}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
          data-testid="ci-generate-btn"
        >
          <GitBranch size={14} />
          Generate Workflow
        </button>
        <button
          onClick={() => onPreview(projectId)}
          className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
          data-testid="ci-preview-btn"
        >
          <Eye size={14} />
          Preview
        </button>
      </div>

      <div className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
        Status: {configured ? "Configured" : "Not configured"}
      </div>
    </div>
  );
}
