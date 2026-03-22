"use client";

import { useEffect, useCallback } from "react";
import { Layout } from "antd";
import { Sidebar } from "./sidebar";
import { TopBar } from "./top-bar";
import { StatusBar } from "./status-bar";
import { useWorkspaceStore } from "@/stores/workspace-store";

const { Content, Sider } = Layout;

const PANEL_IDS = ["sidebar-panel", "main-content", "properties-panel"] as const;

export function WorkspaceShell({
  children,
}: {
  children: React.ReactNode;
}) {
  const { propertiesPanelOpen } = useWorkspaceStore();

  // F6 panel cycling (WCAG)
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "F6") {
      e.preventDefault();
      const panels = PANEL_IDS.map((id) => document.getElementById(id)).filter(Boolean);
      const current = document.activeElement;
      const currentIdx = panels.findIndex((p) => p?.contains(current));
      const nextIdx = (currentIdx + 1) % panels.length;
      const target = panels[nextIdx];
      if (target) {
        const focusable = target.querySelector<HTMLElement>(
          'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        (focusable || target).focus();
      }
    }
  }, []);

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  return (
    <Layout className="h-screen">
      <TopBar />
      <Layout>
        <div id="sidebar-panel" data-panel="sidebar">
          <Sidebar />
        </div>
        <Content
          id="main-content"
          data-panel="main"
          className="flex-1 overflow-auto p-4"
          style={{ background: "var(--color-background)" }}
          tabIndex={-1}
        >
          {children}
        </Content>
        {propertiesPanelOpen && (
          <Sider
            id="properties-panel"
            data-panel="properties"
            width={320}
            className="border-l overflow-auto"
            style={{
              background: "var(--color-card)",
              borderColor: "var(--color-border)",
            }}
          >
            <div
              className="p-4 text-sm"
              style={{ color: "var(--color-muted-foreground)" }}
            >
              Properties panel
            </div>
          </Sider>
        )}
      </Layout>
      <StatusBar />
    </Layout>
  );
}
