"use client";

import { useState } from "react";
import { Bot, Send } from "lucide-react";
import { useAgentChat } from "@/hooks/use-agent-chat";

interface AgentChatProps {
  projectId: string;
  workspaceId: string;
}

/**
 * Agent chat component — consumes useAgentChat hook.
 * No duplicate SSE logic — all streaming handled by hook.
 */
export function AgentChat({ projectId }: AgentChatProps) {
  const [selectedAgent, setSelectedAgent] = useState("design_advisor");
  const [input, setInput] = useState("");

  const { messages, streamingText, isStreaming, sendMessage } =
    useAgentChat(projectId, selectedAgent);

  function handleSend() {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex gap-2 p-2 border-b" style={{ borderColor: "var(--color-border)" }}>
        {["design_advisor", "policy_interpreter"].map((agent) => (
          <button
            key={agent}
            onClick={() => setSelectedAgent(agent)}
            className="px-3 py-1 rounded text-xs"
            style={{
              background: selectedAgent === agent ? "var(--color-primary)" : "var(--color-secondary)",
              color: selectedAgent === agent ? "var(--color-primary-foreground)" : "var(--color-secondary-foreground)",
            }}
          >
            {agent.replace("_", " ")}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3" role="log" aria-live="polite">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`p-3 rounded-lg text-sm ${m.role === "user" ? "ml-8" : "mr-8"}`}
            style={{
              background: m.role === "user" ? "var(--color-primary)" : "var(--color-card)",
              color: m.role === "user" ? "var(--color-primary-foreground)" : "var(--color-foreground)",
            }}
          >
            {m.content}
          </div>
        ))}
        {(streamingText || isStreaming) && (
          <div className="p-3 rounded-lg mr-8 text-sm" style={{ background: "var(--color-card)" }}>
            {streamingText || <span className="animate-pulse">Thinking...</span>}
          </div>
        )}
      </div>

      <div className="p-3 border-t flex gap-2" style={{ borderColor: "var(--color-border)" }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about governance..."
          className="flex-1 px-3 py-2 rounded border text-sm"
          style={{ borderColor: "var(--color-border)", background: "var(--color-background)" }}
          disabled={isStreaming}
        />
        <button
          onClick={handleSend}
          disabled={isStreaming || !input.trim()}
          className="px-4 py-2 rounded text-sm"
          style={{ background: "var(--color-primary)", color: "var(--color-primary-foreground)" }}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
