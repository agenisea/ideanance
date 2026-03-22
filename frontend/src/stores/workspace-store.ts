import { create } from "zustand";

interface WorkspaceState {
  activeWorkspaceId: string | null;
  activeProjectId: string | null;
  sidebarCollapsed: boolean;
  propertiesPanelOpen: boolean;
  setActiveWorkspace: (id: string) => void;
  setActiveProject: (id: string) => void;
  toggleSidebar: () => void;
  toggleProperties: () => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
  activeWorkspaceId: null,
  activeProjectId: null,
  sidebarCollapsed: false,
  propertiesPanelOpen: true,
  setActiveWorkspace: (id) => set({ activeWorkspaceId: id }),
  setActiveProject: (id) => set({ activeProjectId: id }),
  toggleSidebar: () =>
    set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  toggleProperties: () =>
    set((s) => ({ propertiesPanelOpen: !s.propertiesPanelOpen })),
}));
