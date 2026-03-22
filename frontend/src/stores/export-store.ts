import { create } from "zustand";

interface ExportArtifact {
  name: string;
  type: string;
  size: number;
}

interface ExportState {
  generating: boolean;
  artifacts: ExportArtifact[];
  error: string | null;
  setGenerating: (v: boolean) => void;
  setArtifacts: (artifacts: ExportArtifact[]) => void;
  setError: (error: string | null) => void;
}

export const useExportStore = create<ExportState>((set) => ({
  generating: false,
  artifacts: [],
  error: null,
  setGenerating: (generating) => set({ generating }),
  setArtifacts: (artifacts) => set({ artifacts }),
  setError: (error) => set({ error }),
}));

export type { ExportArtifact };
