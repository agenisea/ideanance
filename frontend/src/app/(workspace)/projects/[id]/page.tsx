"use client";

import { useParams } from "next/navigation";

export default function ProjectDashboard() {
  const params = useParams();
  const projectId = params.id as string;

  return (
    <div>
      <h1 className="text-2xl font-heading font-bold mb-4">
        Project Dashboard
      </h1>
      <p style={{ color: "var(--color-muted-foreground)" }}>
        Project ID: {projectId}
      </p>
    </div>
  );
}
