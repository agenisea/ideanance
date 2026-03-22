"use client";

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api/client";
import type { Project } from "@/lib/api/types";

export function useProjectsQuery(workspaceId: string) {
  return useQuery({
    queryKey: ["projects", workspaceId],
    queryFn: () =>
      apiFetch<Project[]>(
        `/api/v1/workspaces/${workspaceId}/projects`
      ),
    enabled: !!workspaceId,
  });
}
