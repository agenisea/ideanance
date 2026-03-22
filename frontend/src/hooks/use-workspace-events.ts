/**
 * Workspace SSE events hook via @agenisea/sse-kit useSSEStream.
 *
 * Long-lived GET-based stream for real-time workspace updates:
 * design.updated, governance.check.completed, etc.
 */

import { useSSEStream } from "@agenisea/sse-kit/client";

type WorkspaceEvent =
  | "idle"
  | "design.updated"
  | "governance.check.started"
  | "governance.check.completed"
  | "evaluation.run.progress"
  | "evaluation.run.completed"
  | "export.progress"
  | "export.completed"
  | "error"
  | "__never__"; // Long-lived stream sentinel

interface WorkspaceUpdate {
  type: string;
  payload: Record<string, unknown>;
}

export function useWorkspaceEvents(workspaceId: string) {
  return useSSEStream<
    void,
    void,
    WorkspaceUpdate,
    WorkspaceEvent
  >({
    endpoint: `/api/v1/events/stream/${workspaceId}`,
    method: "GET",
    initialEvent: "idle",
    completeEvent: "__never__", // Long-lived stream, never completes
    errorEvent: "error",
  });
}
