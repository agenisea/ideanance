"use client";

import { useState, useCallback } from "react";
import {
  createWorkspaceAndProject,
  type Project,
} from "@/lib/services/project-service";

export function useProjectManager() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");

  const createProject = useCallback(async () => {
    if (!newName.trim()) return;
    setLoading(true);
    try {
      const project = await createWorkspaceAndProject(newName);
      setProjects((p) => [...p, project]);
      setNewName("");
      setShowCreate(false);
    } finally {
      setLoading(false);
    }
  }, [newName]);

  return {
    projects,
    loading,
    showCreate,
    newName,
    setNewName,
    setShowCreate,
    createProject,
  };
}
