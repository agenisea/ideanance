"use client";

import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { useWorkspaceEvents } from "@/hooks/use-workspace-events";
import { useWorkspaceStore } from "@/stores/workspace-store";

export function StatusBar() {
  const { activeWorkspaceId } = useWorkspaceStore();
  const { isStreaming } = useWorkspaceEvents(
    activeWorkspaceId || "default"
  );

  return (
    <footer
      className="flex items-center px-4 h-6 text-xs border-t"
      style={{
        background: "var(--color-card)",
        borderColor: "var(--color-border)",
        color: "var(--color-muted-foreground)",
      }}
    >
      <span>Ideanance v0.1.0</span>
      <span className="ml-auto flex items-center gap-1">
        {isStreaming ? (
          <>
            <Wifi
              size={10}
              style={{
                color: "var(--color-governance-pass)",
              }}
            />
            Connected
          </>
        ) : (
          <>
            <WifiOff size={10} />
            Disconnected
          </>
        )}
      </span>
    </footer>
  );
}
