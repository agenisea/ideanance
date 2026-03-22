import { useGovernanceStore } from "@/stores/governance-store";

describe("useGovernanceStore", () => {
  beforeEach(() => {
    useGovernanceStore.setState({
      activeFrameworks: [],
      filterStatus: null,
    });
  });

  it("initializes with empty frameworks", () => {
    const state = useGovernanceStore.getState();
    expect(state.activeFrameworks).toEqual([]);
  });

  it("initializes with null filter (show all)", () => {
    const state = useGovernanceStore.getState();
    expect(state.filterStatus).toBeNull();
  });

  it("sets active frameworks", () => {
    useGovernanceStore.getState().setActiveFrameworks(["nist-ai-rmf"]);
    expect(useGovernanceStore.getState().activeFrameworks).toEqual([
      "nist-ai-rmf",
    ]);
  });

  it("replaces frameworks list entirely", () => {
    useGovernanceStore.getState().setActiveFrameworks(["nist-ai-rmf"]);
    useGovernanceStore
      .getState()
      .setActiveFrameworks(["nist-ai-rmf", "eu-ai-act"]);
    expect(useGovernanceStore.getState().activeFrameworks).toEqual([
      "nist-ai-rmf",
      "eu-ai-act",
    ]);
  });

  it("sets filter status", () => {
    useGovernanceStore.getState().setFilterStatus("fail");
    expect(useGovernanceStore.getState().filterStatus).toBe("fail");
  });

  it("clears filter status to null", () => {
    useGovernanceStore.getState().setFilterStatus("pass");
    useGovernanceStore.getState().setFilterStatus(null);
    expect(useGovernanceStore.getState().filterStatus).toBeNull();
  });
});
