"use client";

import { useWorkspaceStore } from "@/stores/workspace-store";
import { PanelLeft, PanelRight } from "lucide-react";

export function TopBar() {
  const { toggleSidebar, toggleProperties } = useWorkspaceStore();

  return (
    <header
      className="flex items-center justify-between px-4 h-12 border-b"
      style={{
        background: "var(--color-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-1 rounded hover:bg-[var(--color-accent)]"
          aria-label="Toggle sidebar"
        >
          <PanelLeft size={18} />
        </button>
        <span className="font-heading font-semibold">
          Ideanance
        </span>
      </div>

      <div className="flex items-center gap-3">
        <button
          onClick={toggleProperties}
          className="p-1 rounded hover:bg-[var(--color-accent)]"
          aria-label="Toggle properties panel"
        >
          <PanelRight size={18} />
        </button>
      </div>
    </header>
  );
}
