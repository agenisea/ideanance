"use client";

import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { AgentNode } from "./nodes/agent-node";

const nodeTypes = {
  agent: AgentNode,
};

const initialNodes: Node[] = [
  {
    id: "input",
    type: "input",
    position: { x: 250, y: 0 },
    data: { label: "User Input" },
  },
  {
    id: "router",
    type: "agent",
    position: { x: 220, y: 100 },
    data: {
      name: "Query Router",
      model: "Haiku 4.5",
      governanceScore: 1.0,
      latency: "<300ms",
      status: "pass",
    },
  },
  {
    id: "policy",
    type: "agent",
    position: { x: 50, y: 250 },
    data: {
      name: "Policy Interpreter",
      model: "Sonnet 4.6",
      governanceScore: 0.92,
      latency: "<2s",
      status: "pass",
    },
  },
  {
    id: "design",
    type: "agent",
    position: { x: 220, y: 250 },
    data: {
      name: "Design Advisor",
      model: "Sonnet 4.6",
      governanceScore: 0.78,
      latency: "<2s",
      status: "warn",
    },
  },
  {
    id: "eval",
    type: "agent",
    position: { x: 400, y: 250 },
    data: {
      name: "Eval Generator",
      model: "Sonnet 4.6",
      governanceScore: 0.95,
      latency: "<2s",
      status: "pass",
    },
  },
  {
    id: "filter",
    position: { x: 220, y: 400 },
    data: { label: "Governance Filter (deterministic)" },
    style: {
      border: "2px dashed var(--color-governance-pass)",
      background: "var(--color-accent)",
      padding: 12,
      borderRadius: 8,
    },
  },
  {
    id: "export",
    type: "agent",
    position: { x: 220, y: 520 },
    data: {
      name: "Export Formatter",
      model: "Sonnet 4.6",
      governanceScore: 0.88,
      latency: "<3s",
      status: "pass",
    },
  },
];

const initialEdges: Edge[] = [
  { id: "e-input-router", source: "input", target: "router" },
  { id: "e-router-policy", source: "router", target: "policy" },
  { id: "e-router-design", source: "router", target: "design" },
  { id: "e-router-eval", source: "router", target: "eval" },
  { id: "e-policy-filter", source: "policy", target: "filter" },
  { id: "e-design-filter", source: "design", target: "filter" },
  { id: "e-eval-filter", source: "eval", target: "filter" },
  { id: "e-filter-export", source: "filter", target: "export" },
];

export function AgentCanvas() {
  return (
    <div
      className="w-full h-[600px] rounded-lg border"
      style={{ borderColor: "var(--color-border)" }}
      aria-label="Agent topology diagram showing 5 agents and their governance status"
    >
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        nodeTypes={nodeTypes}
        fitView
        attributionPosition="bottom-left"
      >
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
