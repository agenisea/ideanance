/**
 * Project service — create, list, manage projects.
 * All API calls go through apiFetch().
 */

import { apiFetch } from "@/lib/api/client";
import type { Project, Workspace } from "@/lib/api/types";

export type { Project };

export async function createWorkspaceAndProject(
  name: string
): Promise<Project> {
  const ws = await apiFetch<Workspace>("/api/v1/workspaces/", {
    method: "POST",
    body: JSON.stringify({ name: "Default Workspace" }),
  });
  return apiFetch<Project>(`/api/v1/workspaces/${ws.id}/projects`, {
    method: "POST",
    body: JSON.stringify({ name }),
  });
}

export async function listProjects(
  workspaceId: string
): Promise<Project[]> {
  return apiFetch<Project[]>(`/api/v1/workspaces/${workspaceId}/projects`);
}
