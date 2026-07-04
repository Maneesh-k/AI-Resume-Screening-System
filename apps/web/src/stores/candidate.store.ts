"use client";

import { create } from "zustand";

interface CandidateState {
  comparisonList: string[];
  addToComparison: (id: string) => void;
  removeFromComparison: (id: string) => void;
  clearComparison: () => void;
  isInComparison: (id: string) => boolean;
}

export const useCandidateStore = create<CandidateState>((set, get) => ({
  comparisonList: [],

  addToComparison: (id) =>
    set((state) => {
      if (state.comparisonList.includes(id) || state.comparisonList.length >= 4) return state;
      return { comparisonList: [...state.comparisonList, id] };
    }),

  removeFromComparison: (id) =>
    set((state) => ({ comparisonList: state.comparisonList.filter((c) => c !== id) })),

  clearComparison: () => set({ comparisonList: [] }),

  isInComparison: (id) => get().comparisonList.includes(id),
}));
