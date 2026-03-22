/**
 * Agent streaming hook via @agenisea/sse-kit useSSEStream.
 *
 * Handles POST-based SSE, automatic reconnection, circuit breaker,
 * and typed event routing for agent responses.
 */

import { useSSEStream } from "@agenisea/sse-kit/client";

type AgentStreamEvent =
  | "idle"
  | "token"
  | "result"
  | "governance"
  | "done"
  | "error";

interface AgentRunInput {
  prompt: string;
  workspace_id: string;
  project_id: string;
}

interface AgentResult {
  [key: string]: unknown;
}

interface AgentUpdate {
  text?: string;
  message?: string;
  [key: string]: unknown;
}

export function useAgentStream(agentId: string) {
  return useSSEStream<
    AgentRunInput,
    AgentResult,
    AgentUpdate,
    AgentStreamEvent
  >({
    endpoint: `/api/v1/agents/${agentId}/run`,
    method: "POST",
    headers: { "Content-Type": "application/json" },
    initialEvent: "idle",
    completeEvent: "done",
    errorEvent: "error",
  });
}
