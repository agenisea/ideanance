/**
 * Evaluation service — suggestions, criteria management.
 * Hydrates evaluation Zustand store.
 */

import { apiFetch } from "@/lib/api/client";
import type { EvalSuggestion } from "@/lib/api/types";
import { useEvaluationStore } from "@/stores/evaluation-store";

export async function getSuggestions(
  projectId: string
): Promise<EvalSuggestion[]> {
  const suggestions = await apiFetch<EvalSuggestion[]>(
    `/api/v1/governance/projects/${projectId}/suggestions`
  );
  useEvaluationStore.getState().setCriteria(
    suggestions.map((s) => ({
      id: s.criterion_id,
      policyId: s.policy_id,
      description: s.description,
      metric: s.metric,
      threshold: s.threshold,
    }))
  );
  return suggestions;
}
