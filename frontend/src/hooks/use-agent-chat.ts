"use client";

import { useState, useEffect, useCallback } from "react";
import { useAgentStream } from "@/hooks/use-agent-stream";
import { useChatStore, type Message } from "@/stores/chat-store";

export function useAgentChat(projectId: string, agentId: string) {
  const { addMessage } = useChatStore();
  const messages = useChatStore((s) => s.messages[projectId] || []);
  const [streamingText, setStreamingText] = useState("");

  const { state, start, cancel, isStreaming } = useAgentStream(agentId);

  // Handle SSE events
  useEffect(() => {
    if (!state) return;

    if (state.event === "token" && state.result) {
      const raw = (state.result as Record<string, unknown>).text;
      if (typeof raw === "string") {
        setStreamingText((prev) => prev + raw);
      }
    }

    if (state.event === "result" || state.event === "done") {
      if (streamingText) {
        addMessage(projectId, {
          id: crypto.randomUUID(),
          role: "assistant",
          content: streamingText,
          timestamp: Date.now(),
          agentId,
        });
        setStreamingText("");
      } else if (state.result) {
        const msg =
          (state.result as Record<string, string>).message ||
          JSON.stringify(state.result);
        addMessage(projectId, {
          id: crypto.randomUUID(),
          role: "assistant",
          content: msg,
          timestamp: Date.now(),
          agentId,
        });
      }
    }

    if (state.event === "error") {
      addMessage(projectId, {
        id: crypto.randomUUID(),
        role: "assistant",
        content: String(state.error || "Agent unavailable."),
        timestamp: Date.now(),
      });
      setStreamingText("");
    }
  }, [state?.event, state?.result, state?.error, addMessage, projectId, agentId]);

  const sendMessage = useCallback(
    (input: string) => {
      if (!input.trim() || isStreaming) return;
      addMessage(projectId, {
        id: crypto.randomUUID(),
        role: "user",
        content: input,
        timestamp: Date.now(),
      });
      setStreamingText("");
      start({
        prompt: input,
        workspace_id: "default",
        project_id: projectId,
      });
    },
    [isStreaming, projectId, addMessage, start]
  );

  return {
    messages,
    streamingText,
    isStreaming,
    sendMessage,
    cancel,
  };
}
