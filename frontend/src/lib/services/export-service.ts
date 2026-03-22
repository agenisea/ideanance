/**
 * Export service — handoff package generation + download.
 * Hydrates export Zustand store.
 */

import { apiFetch, API_BASE } from "@/lib/api/client";
import { useExportStore } from "@/stores/export-store";

export async function generateHandoff(
  projectId: string
): Promise<unknown> {
  const store = useExportStore.getState();
  store.setGenerating(true);
  store.setError(null);
  try {
    const result = await apiFetch(
      `/api/v1/exports/projects/${projectId}/generate`,
      { method: "POST" }
    );
    return result;
  } catch (e) {
    store.setError(String(e));
    throw e;
  } finally {
    store.setGenerating(false);
  }
}

export function getDownloadUrl(projectId: string): string {
  return `${API_BASE}/api/v1/exports/projects/${projectId}/download`;
}
