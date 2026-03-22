"use client";

import { GovernanceScoreMeter } from "@/components/governance/governance-score-meter";

interface ExportPanelProps {
  projectId: string;
  governanceScore: number;
  artifactCount: number;
}

export function ExportPanel({
  projectId,
  governanceScore,
  artifactCount,
}: ExportPanelProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-heading font-bold">
        Export Handoff Package
      </h2>

      {/* Compliance Report */}
      <div
        className="p-4 rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          background: "var(--color-card)",
        }}
      >
        <h3 className="text-sm font-semibold mb-2">
          Compliance Report
        </h3>
        <GovernanceScoreMeter
          score={governanceScore}
          label="Overall governance coverage"
        />
      </div>

      {/* Package Contents */}
      <div
        className="p-4 rounded-lg border"
        style={{
          borderColor: "var(--color-border)",
          background: "var(--color-card)",
        }}
      >
        <h3 className="text-sm font-semibold mb-2">
          Package Contents ({artifactCount} files)
        </h3>
        <ul className="space-y-1 text-sm">
          {[
            "ai-context.yml",
            "agent-specs.yml",
            "eval-criteria.yml",
            "governance-report.md",
            "wiring-map.json",
            "CLAUDE.md",
            "README.md",
          ].map((file) => (
            <li
              key={file}
              className="flex items-center justify-between py-1 px-2 rounded"
              style={{ background: "var(--color-accent)" }}
            >
              <span>📄 {file}</span>
              <button className="text-xs underline">Preview</button>
            </li>
          ))}
        </ul>
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          className="px-4 py-2 rounded text-sm"
          style={{
            background: "var(--color-primary)",
            color: "var(--color-primary-foreground)",
          }}
        >
          Generate Package
        </button>
        <button
          className="px-4 py-2 rounded text-sm border"
          style={{ borderColor: "var(--color-border)" }}
        >
          Download ZIP
        </button>
      </div>
    </div>
  );
}
