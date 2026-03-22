"use client";

import { Handle, Position } from "@xyflow/react";
import { GovernanceBadge } from "@/components/governance/governance-badge";

interface AgentNodeData {
  name: string;
  model: string;
  governanceScore: number;
  latency: string;
  status: "pass" | "warn" | "fail" | "na";
}

export function AgentNode({ data }: { data: AgentNodeData }) {
  return (
    <div
      className="rounded-lg border-2 p-3 min-w-[160px]"
      style={{
        borderColor: `var(--color-governance-${data.status})`,
        background: "var(--color-card)",
      }}
    >
      <Handle type="target" position={Position.Top} />

      <div className="font-heading font-semibold text-sm">
        {data.name}
      </div>
      <div
        className="text-xs"
        style={{ color: "var(--color-muted-foreground)" }}
      >
        {data.model}
      </div>

      <div className="flex items-center gap-2 mt-2">
        <GovernanceBadge
          status={data.status}
          score={data.governanceScore}
        />
        <span className="text-xs">● {data.latency}</span>
      </div>

      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
