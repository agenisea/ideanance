import { create } from "zustand";

interface PolicyConflict {
  policyA: string;
  frameworkA: string;
  policyB: string;
  frameworkB: string;
  conflictType: string;
  description: string;
  resolution: string;
}

interface CustomFramework {
  id: string;
  name: string;
  version: string;
  policyCount: number;
}

interface GovernanceState {
  activeFrameworks: string[];
  customFrameworks: CustomFramework[];
  conflicts: PolicyConflict[];
  compositeScore: number;
  perFrameworkScores: Record<string, number>;
  filterStatus: string | null;
  setActiveFrameworks: (frameworks: string[]) => void;
  addCustomFramework: (framework: CustomFramework) => void;
  removeCustomFramework: (id: string) => void;
  setConflicts: (conflicts: PolicyConflict[]) => void;
  setCompositeScore: (score: number) => void;
  setPerFrameworkScores: (scores: Record<string, number>) => void;
  setFilterStatus: (status: string | null) => void;
}

export const useGovernanceStore = create<GovernanceState>((set) => ({
  activeFrameworks: [],
  customFrameworks: [],
  conflicts: [],
  compositeScore: 0,
  perFrameworkScores: {},
  filterStatus: null,
  setActiveFrameworks: (frameworks) =>
    set({ activeFrameworks: frameworks }),
  addCustomFramework: (framework) =>
    set((state) => ({
      customFrameworks: [...state.customFrameworks, framework],
    })),
  removeCustomFramework: (id) =>
    set((state) => ({
      customFrameworks: state.customFrameworks.filter((f) => f.id !== id),
    })),
  setConflicts: (conflicts) => set({ conflicts }),
  setCompositeScore: (score) => set({ compositeScore: score }),
  setPerFrameworkScores: (scores) => set({ perFrameworkScores: scores }),
  setFilterStatus: (status) => set({ filterStatus: status }),
}));

export type { PolicyConflict, CustomFramework, GovernanceState };
