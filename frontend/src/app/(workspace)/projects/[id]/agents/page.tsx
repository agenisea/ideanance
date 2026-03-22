"use client";

import React, { useState, useRef, useEffect } from "react";
import { useParams } from "next/navigation";
import { Send, Bot, User, Wifi } from "lucide-react";
import { useAgentChat } from "@/hooks/use-agent-chat";
import { FeedbackWidget } from "@/components/feedback/feedback-widget";

export default function AgentsPage() {
  const params = useParams();
  const projectId = params.id as string;
  const [input, setInput] = useState("");
  const endRef = useRef<HTMLDivElement>(null);

  const { messages, streamingText, isStreaming, sendMessage, cancel } =
    useAgentChat(projectId, "design_advisor");

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  function handleSend() {
    if (!input.trim()) return;
    sendMessage(input);
    setInput("");
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          Agent Design
        </h1>
        {isStreaming && (
          <span className="flex items-center gap-1 text-xs" style={{ color: "var(--color-info)" }}>
            <Wifi size={12} /> Streaming
          </span>
        )}
      </div>

      <div
        className="flex-1 overflow-auto space-y-3 p-4 rounded mb-4"
        style={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)" }}
        role="log"
        aria-label="Agent conversation"
        aria-live="polite"
      >
        {messages.length === 0 && !streamingText && (
          <div className="flex flex-col items-center gap-2 py-12" style={{ color: "var(--color-muted-foreground)" }}>
            <Bot size={48} />
            <p className="text-sm">Ask the governance-aware design advisor.</p>
          </div>
        )}

        {messages.map((msg) => (
          <React.Fragment key={msg.id}>
            <div className={`flex gap-2 ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              {msg.role === "assistant" && <Bot size={20} style={{ color: "var(--color-primary)", flexShrink: 0, marginTop: 2 }} />}
              <div
                className="max-w-[80%] p-3 rounded text-sm whitespace-pre-wrap"
                style={{
                  backgroundColor: msg.role === "user" ? "var(--color-primary)" : "var(--color-surface)",
                  color: msg.role === "user" ? "var(--color-on-primary)" : "var(--color-foreground)",
                }}
              >
                {msg.content}
              </div>
              {msg.role === "user" && <User size={20} style={{ color: "var(--color-muted-foreground)", flexShrink: 0, marginTop: 2 }} />}
            </div>
            {msg.role === "assistant" && (
              <div className="ml-7">
                <FeedbackWidget interactionId={msg.id} onRate={(r) => console.log("[feedback]", { id: msg.id, agentId: msg.agentId, rating: r })} />
              </div>
            )}
          </React.Fragment>
        ))}

        {streamingText && (
          <div className="flex gap-2">
            <Bot size={20} style={{ color: "var(--color-primary)" }} />
            <div className="max-w-[80%] p-3 rounded text-sm whitespace-pre-wrap" style={{ backgroundColor: "var(--color-surface)" }}>
              {streamingText}<span className="animate-pulse">|</span>
            </div>
          </div>
        )}
        {isStreaming && !streamingText && (
          <div className="flex gap-2">
            <Bot size={20} style={{ color: "var(--color-primary)" }} />
            <div className="p-3 rounded text-sm" style={{ backgroundColor: "var(--color-surface)" }}>
              <span className="animate-pulse">Thinking...</span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about governance, design, or evaluations..."
          className="flex-1 px-4 py-3 rounded text-sm"
          style={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)" }}
          disabled={isStreaming}
          aria-label="Message input"
        />
        {isStreaming ? (
          <button onClick={cancel} className="px-4 py-3 rounded text-sm" style={{ backgroundColor: "var(--color-destructive)", color: "var(--color-on-primary)" }} aria-label="Cancel">
            Stop
          </button>
        ) : (
          <button onClick={handleSend} disabled={!input.trim()} className="px-4 py-3 rounded" style={{ backgroundColor: "var(--color-primary)", color: "var(--color-primary-foreground)", opacity: !input.trim() ? 0.5 : 1 }} aria-label="Send">
            <Send size={18} />
          </button>
        )}
      </div>
    </div>
  );
}
