"use client";

import { Download, Upload, Package } from "lucide-react";

interface TemplatePanelProps {
  onExport: (frameworkId: string) => void;
  onImport: (file: File) => void;
}

export function TemplatePanel({
  onExport,
  onImport,
}: TemplatePanelProps) {
  function handleFileSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (file) onImport(file);
  }

  return (
    <div data-testid="template-panel" className="space-y-4">
      <h3
        className="text-sm font-semibold"
        style={{ fontFamily: "var(--font-heading)" }}
      >
        Templates
      </h3>

      <div className="space-y-2">
        <button
          onClick={() => onExport("nist-ai-rmf")}
          className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <Download size={14} />
          Export NIST AI RMF
        </button>

        <button
          onClick={() => onExport("eu-ai-act")}
          className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <Download size={14} />
          Export EU AI Act
        </button>

        <label
          className="w-full flex items-center gap-2 px-3 py-2 rounded text-sm cursor-pointer"
          style={{
            backgroundColor: "var(--color-surface)",
            border: "1px solid var(--color-border)",
          }}
        >
          <Upload size={14} />
          Import Template
          <input
            type="file"
            accept=".zip"
            onChange={handleFileSelect}
            className="hidden"
            aria-label="Import governance template ZIP"
          />
        </label>
      </div>
    </div>
  );
}
