"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Play } from "lucide-react";
import { FrameworkSelector } from "@/components/governance/framework-selector";
import { CompositeScore } from "@/components/governance/composite-score";
import { ConflictPanel } from "@/components/governance/conflict-panel";
import { useGovernanceStore } from "@/stores/governance-store";
import {
  activateFramework,
  runGovernanceCheck,
} from "@/lib/services/governance-service";
import type { GovernanceCheckResult } from "@/lib/api/types";

const FRAMEWORKS = [
  { id: "nist-ai-rmf", name: "NIST AI RMF", policyCount: 20, isCustom: false },
  { id: "eu-ai-act", name: "EU AI Act", policyCount: 21, isCustom: false },
];

export default function GovernancePage() {
  const params = useParams();
  const projectId = params.id as string;
  const { perFrameworkScores, conflicts } = useGovernanceStore();
  const [checkResult, setCheckResult] = useState<GovernanceCheckResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleActivate(frameworkId: string) {
    try {
      setError(null);
      await activateFramework(projectId, frameworkId);
    } catch (e) {
      setError(String(e));
    }
  }

  async function handleCheck() {
    try {
      setError(null);
      const result = await runGovernanceCheck(projectId, {
        design: { purpose: "AI agent" },
      });
      setCheckResult(result);
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          Governance Policies
        </h1>
        <button onClick={handleCheck} className="flex items-center gap-2 px-3 py-2 rounded text-sm font-medium" style={{ backgroundColor: "var(--color-primary)", color: "var(--color-primary-foreground)" }}>
          <Play size={16} /> Run Check
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <FrameworkSelector frameworks={FRAMEWORKS} onActivate={handleActivate} onDeactivate={() => {}} />
        </div>

        <div className="lg:col-span-2 space-y-4">
          {checkResult && (
            <div className="p-4 rounded" style={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)" }}>
              <CompositeScore compositeScore={checkResult.overall_score} perFrameworkScores={perFrameworkScores} />
            </div>
          )}

          <ConflictPanel conflicts={conflicts} />

          {checkResult && (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold">Results ({checkResult.results.length})</h3>
              {checkResult.results.map((r, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded text-sm" style={{ backgroundColor: "var(--color-surface)", border: "1px solid var(--color-border)" }}>
                  <span>{r.policy_id}</span>
                  <span style={{ color: r.status === "pass" ? "var(--color-governance-pass)" : r.status === "fail" ? "var(--color-governance-fail)" : "var(--color-governance-warn)" }}>
                    {r.status.toUpperCase()} ({Math.round(r.score * 100)}%)
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
