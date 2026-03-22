/**
 * Governance service — activate frameworks, run checks.
 * All API calls go through apiFetch(). Updates Zustand stores.
 */

import { apiFetch } from "@/lib/api/client";
import type {
  GovernanceCheckResult,
  GovernancePolicy,
} from "@/lib/api/types";
import { useGovernanceStore } from "@/stores/governance-store";

export async function activateFramework(
  projectId: string,
  frameworkId: string
): Promise<GovernancePolicy[]> {
  const policies = await apiFetch<GovernancePolicy[]>(
    `/api/v1/governance/projects/${projectId}/activate`,
    {
      method: "POST",
      body: JSON.stringify({ framework_id: frameworkId }),
    }
  );
  const store = useGovernanceStore.getState();
  store.setActiveFrameworks([...store.activeFrameworks, frameworkId]);
  return policies;
}

export function deactivateFramework(
  frameworkId: string
): void {
  const store = useGovernanceStore.getState();
  store.setActiveFrameworks(
    store.activeFrameworks.filter((f) => f !== frameworkId)
  );
}

export async function runGovernanceCheck(
  projectId: string,
  designContent: object
): Promise<GovernanceCheckResult> {
  return apiFetch<GovernanceCheckResult>("/api/v1/governance/check", {
    method: "POST",
    body: JSON.stringify({
      project_id: projectId,
      design_content: designContent,
    }),
  });
}
