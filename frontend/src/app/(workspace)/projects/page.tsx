"use client";

import { Plus, FolderOpen } from "lucide-react";
import { useProjectManager } from "@/hooks/use-project-manager";

export default function ProjectsPage() {
  const {
    projects, loading, showCreate, newName,
    setNewName, setShowCreate, createProject,
  } = useProjectManager();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold" style={{ fontFamily: "var(--font-heading)" }}>
          Projects
        </h1>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 px-3 py-2 rounded text-sm font-medium"
          style={{ backgroundColor: "var(--color-primary)", color: "var(--color-primary-foreground)" }}
        >
          <Plus size={16} /> New Project
        </button>
      </div>

      {showCreate && (
        <div className="flex gap-2 p-4 rounded" style={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)" }}>
          <input
            type="text" value={newName} onChange={(e) => setNewName(e.target.value)}
            placeholder="Project name" autoFocus
            className="flex-1 px-3 py-2 rounded text-sm"
            style={{ backgroundColor: "var(--color-background)", border: "1px solid var(--color-border)" }}
            onKeyDown={(e) => e.key === "Enter" && createProject()}
          />
          <button onClick={createProject} className="px-4 py-2 rounded text-sm font-medium" style={{ backgroundColor: "var(--color-primary)", color: "var(--color-primary-foreground)" }}>
            Create
          </button>
        </div>
      )}

      {projects.length === 0 && !loading ? (
        <div className="flex flex-col items-center gap-3 py-12" style={{ color: "var(--color-muted-foreground)" }}>
          <FolderOpen size={48} />
          <p className="text-sm">No projects yet. Create one to start wiring governance.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map((project) => (
            <a key={project.id} href={`/projects/${project.id}`} className="p-4 rounded hover:shadow-sm transition-shadow" style={{ backgroundColor: "var(--color-card)", border: "1px solid var(--color-border)" }}>
              <h3 className="font-medium">{project.name}</h3>
              <p className="text-xs mt-1" style={{ color: "var(--color-muted-foreground)" }}>
                {new Date(project.created_at).toLocaleDateString()}
              </p>
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
