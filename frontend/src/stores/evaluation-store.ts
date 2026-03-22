import { create } from "zustand";

interface EvalCriterion {
  id: string;
  policyId: string;
  description: string;
  metric: string;
  threshold: string;
}

interface EvaluationState {
  criteria: EvalCriterion[];
  setCriteria: (criteria: EvalCriterion[]) => void;
  addCriterion: (criterion: EvalCriterion) => void;
  removeCriterion: (id: string) => void;
}

export const useEvaluationStore = create<EvaluationState>((set) => ({
  criteria: [],
  setCriteria: (criteria) => set({ criteria }),
  addCriterion: (criterion) =>
    set((state) => ({ criteria: [...state.criteria, criterion] })),
  removeCriterion: (id) =>
    set((state) => ({
      criteria: state.criteria.filter((c) => c.id !== id),
    })),
}));

export type { EvalCriterion };
