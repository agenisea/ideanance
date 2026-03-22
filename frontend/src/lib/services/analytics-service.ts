/**
 * Analytics service — North Star metric, scores, coverage.
 * All API calls go through apiFetch(). Uses typed API responses.
 */

import { apiFetch } from "@/lib/api/client";
import type {
  CoverageResponse,
  NorthStarResponse,
  ScoreResponse,
  SnapshotResponse,
} from "@/lib/api/types";

export async function getNorthStar(): Promise<NorthStarResponse> {
  return apiFetch<NorthStarResponse>("/api/v1/analytics/north-star");
}

export async function getProjectScore(
  projectId: string
): Promise<ScoreResponse> {
  return apiFetch<ScoreResponse>(
    `/api/v1/analytics/projects/${projectId}/score`
  );
}

export async function getProjectCoverage(
  projectId: string
): Promise<CoverageResponse> {
  return apiFetch<CoverageResponse>(
    `/api/v1/analytics/projects/${projectId}/coverage`
  );
}

export async function createSnapshot(
  projectId: string
): Promise<SnapshotResponse> {
  return apiFetch<SnapshotResponse>(
    `/api/v1/analytics/projects/${projectId}/snapshot`,
    { method: "POST" }
  );
}
