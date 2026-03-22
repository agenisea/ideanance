import { useWorkspaceStore } from "@/stores/workspace-store";

describe("useWorkspaceStore", () => {
  beforeEach(() => {
    // Reset store between tests
    useWorkspaceStore.setState({
      activeWorkspaceId: null,
      activeProjectId: null,
      sidebarCollapsed: false,
      propertiesPanelOpen: true,
    });
  });

  it("initializes with null workspace and project", () => {
    const state = useWorkspaceStore.getState();
    expect(state.activeWorkspaceId).toBeNull();
    expect(state.activeProjectId).toBeNull();
  });

  it("initializes with sidebar expanded", () => {
    const state = useWorkspaceStore.getState();
    expect(state.sidebarCollapsed).toBe(false);
  });

  it("initializes with properties panel open", () => {
    const state = useWorkspaceStore.getState();
    expect(state.propertiesPanelOpen).toBe(true);
  });

  it("sets active workspace", () => {
    useWorkspaceStore.getState().setActiveWorkspace("ws-1");
    expect(useWorkspaceStore.getState().activeWorkspaceId).toBe("ws-1");
  });

  it("sets active project", () => {
    useWorkspaceStore.getState().setActiveProject("proj-1");
    expect(useWorkspaceStore.getState().activeProjectId).toBe("proj-1");
  });

  it("toggles sidebar", () => {
    expect(useWorkspaceStore.getState().sidebarCollapsed).toBe(false);
    useWorkspaceStore.getState().toggleSidebar();
    expect(useWorkspaceStore.getState().sidebarCollapsed).toBe(true);
    useWorkspaceStore.getState().toggleSidebar();
    expect(useWorkspaceStore.getState().sidebarCollapsed).toBe(false);
  });

  it("toggles properties panel", () => {
    expect(useWorkspaceStore.getState().propertiesPanelOpen).toBe(true);
    useWorkspaceStore.getState().toggleProperties();
    expect(useWorkspaceStore.getState().propertiesPanelOpen).toBe(false);
    useWorkspaceStore.getState().toggleProperties();
    expect(useWorkspaceStore.getState().propertiesPanelOpen).toBe(true);
  });
});
