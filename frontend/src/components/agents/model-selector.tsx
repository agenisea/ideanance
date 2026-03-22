"use client";

import { CheckCircle, AlertTriangle, XCircle } from "lucide-react";

interface ModelOption {
  id: string;
  provider: string;
  quality: "validated" | "recommended" | "experimental" | "not_recommended";
  costPerQuery: number;
}

interface ModelSelectorProps {
  models: ModelOption[];
  selected: string;
  onSelect: (modelId: string) => void;
}

const QUALITY_CONFIG = {
  validated: {
    color: "var(--color-governance-pass)",
    icon: CheckCircle,
    label: "Validated",
  },
  recommended: {
    color: "var(--color-info)",
    icon: CheckCircle,
    label: "Recommended",
  },
  experimental: {
    color: "var(--color-governance-warn)",
    icon: AlertTriangle,
    label: "Experimental",
  },
  not_recommended: {
    color: "var(--color-governance-fail)",
    icon: XCircle,
    label: "Not Recommended",
  },
};

export function ModelSelector({
  models,
  selected,
  onSelect,
}: ModelSelectorProps) {
  return (
    <div data-testid="model-selector" className="space-y-2">
      <label
        className="text-xs font-medium"
        style={{ color: "var(--color-muted-foreground)" }}
      >
        Model
      </label>
      <div className="space-y-1">
        {models.map((model) => {
          const config = QUALITY_CONFIG[model.quality];
          const Icon = config.icon;
          const isSelected = model.id === selected;

          return (
            <button
              key={model.id}
              onClick={() => onSelect(model.id)}
              className="w-full flex items-center justify-between px-3 py-2 rounded text-sm"
              style={{
                backgroundColor: isSelected
                  ? "var(--color-surface-hover)"
                  : "var(--color-surface)",
                border: isSelected
                  ? "2px solid var(--color-primary)"
                  : "1px solid var(--color-border)",
              }}
              aria-pressed={isSelected}
              aria-label={`${model.id} — ${config.label}, $${model.costPerQuery.toFixed(4)}/query`}
            >
              <span className="flex items-center gap-2">
                <Icon size={14} style={{ color: config.color }} />
                <span>{model.id.split(":")[1]}</span>
                <span
                  className="text-xs px-1 rounded"
                  style={{
                    color: config.color,
                    border: `1px solid ${config.color}`,
                  }}
                >
                  {config.label}
                </span>
              </span>
              <span
                className="text-xs"
                style={{ color: "var(--color-muted-foreground)" }}
              >
                ${model.costPerQuery.toFixed(4)}/q
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
