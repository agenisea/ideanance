"use client";

import { Layout, Menu } from "antd";
import {
  Shield,
  Bot,
  CheckCircle,
  GitBranch,
  Settings,
  BookOpen,
  FolderOpen,
} from "lucide-react";
import Link from "next/link";
import { useWorkspaceStore } from "@/stores/workspace-store";

const { Sider } = Layout;

export function Sidebar() {
  const { sidebarCollapsed, activeProjectId } = useWorkspaceStore();

  const projectItems = activeProjectId
    ? [
        {
          key: "governance",
          icon: <Shield size={16} />,
          label: (
            <Link href={`/projects/${activeProjectId}/governance`}>
              Governance
            </Link>
          ),
        },
        {
          key: "agents",
          icon: <Bot size={16} />,
          label: (
            <Link href={`/projects/${activeProjectId}/agents`}>
              Agents
            </Link>
          ),
        },
        {
          key: "evals",
          icon: <CheckCircle size={16} />,
          label: (
            <Link href={`/projects/${activeProjectId}/evals`}>
              Evals
            </Link>
          ),
        },
        {
          key: "pipeline",
          icon: <GitBranch size={16} />,
          label: (
            <Link href={`/projects/${activeProjectId}/pipeline`}>
              Pipeline
            </Link>
          ),
        },
      ]
    : [];

  const menuItems = [
    {
      key: "projects",
      icon: <FolderOpen size={16} />,
      label: <Link href="/projects">Projects</Link>,
    },
    ...(projectItems.length > 0
      ? [
          { type: "divider" as const },
          ...projectItems,
        ]
      : []),
    { type: "divider" as const },
    {
      key: "policies",
      icon: <BookOpen size={16} />,
      label: "Policy Library",
    },
    {
      key: "settings",
      icon: <Settings size={16} />,
      label: "Settings",
    },
  ];

  return (
    <Sider
      width={240}
      collapsedWidth={64}
      collapsed={sidebarCollapsed}
      className="border-r"
      style={{
        background: "var(--color-card)",
        borderColor: "var(--color-border)",
      }}
    >
      <div className="p-4 font-heading font-bold text-lg">
        {sidebarCollapsed ? "I" : "Ideanance"}
      </div>
      <Menu
        mode="inline"
        items={menuItems}
        style={{ border: "none", background: "transparent" }}
      />
    </Sider>
  );
}
