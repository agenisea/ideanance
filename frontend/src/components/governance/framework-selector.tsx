"use client";

import { Check, Plus } from "lucide-react";
import { useGovernanceStore } from "@/stores/governance-store";

interface Framework {
  id: string;
  name: string;
  policyCount: number;
  isCustom: boolean;
}

interface FrameworkSelectorProps {
  frameworks: Framework[];
  onActivate: (frameworkId: string) => void;
  onDeactivate: (frameworkId: string) => void;
  onCreateCustom?: () => void;
}

export function FrameworkSelector({
  frameworks,
  onActivate,
  onDeactivate,
  onCreateCustom,
}: FrameworkSelectorProps) {
  const activeFrameworks = useGovernanceStore(
    (state) => state.activeFrameworks
  );

  const builtIn = frameworks.filter((f) => !f.isCustom);
  const custom = frameworks.filter((f) => f.isCustom);

  function handleToggle(framework: Framework) {
    if (activeFrameworks.includes(framework.id)) {
      onDeactivate(framework.id);
    } else {
      onActivate(framework.id);
    }
  }

  return (
    <div data-testid="framework-selector" className="space-y-4">
      <h3 className="text-sm font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
        Governance Frameworks
      </h3>

      <div className="space-y-1">
        {builtIn.map((fw) => (
          <FrameworkRow
            key={fw.id}
            framework={fw}
            active={activeFrameworks.includes(fw.id)}
            onToggle={() => handleToggle(fw)}
          />
        ))}
      </div>

      {custom.length > 0 && (
        <>
          <div className="border-t" style={{ borderColor: "var(--color-border)" }} />
          <h4 className="text-xs font-medium" style={{ color: "var(--color-text-secondary)" }}>
            Custom Frameworks
          </h4>
          <div className="space-y-1">
            {custom.map((fw) => (
              <FrameworkRow
                key={fw.id}
                framework={fw}
                active={activeFrameworks.includes(fw.id)}
                onToggle={() => handleToggle(fw)}
              />
            ))}
          </div>
        </>
      )}

      {onCreateCustom && (
        <button
          onClick={onCreateCustom}
          className="flex items-center gap-1 text-xs px-2 py-1 rounded"
          style={{ color: "var(--color-primary)" }}
          data-testid="create-framework-btn"
        >
          <Plus size={14} />
          Create Framework
        </button>
      )}
    </div>
  );
}

function FrameworkRow({
  framework,
  active,
  onToggle,
}: {
  framework: Framework;
  active: boolean;
  onToggle: () => void;
}) {
  return (
    <button
      onClick={onToggle}
      className="w-full flex items-center justify-between px-2 py-1.5 rounded text-sm hover:bg-[var(--color-surface-hover)]"
      data-testid={`framework-${framework.id}`}
      role="switch"
      aria-checked={active}
      aria-label={`${framework.name}: ${framework.policyCount} policies`}
    >
      <span className="flex items-center gap-2">
        <span
          className="w-4 h-4 rounded border flex items-center justify-center"
          style={{
            borderColor: active ? "var(--color-primary)" : "var(--color-border)",
            backgroundColor: active ? "var(--color-primary)" : "transparent",
          }}
        >
          {active && <Check size={12} style={{ color: "var(--color-on-primary)" }} />}
        </span>
        <span>{framework.name}</span>
      </span>
      <span className="text-xs" style={{ color: "var(--color-text-secondary)" }}>
        {framework.policyCount} policies
      </span>
    </button>
  );
}
