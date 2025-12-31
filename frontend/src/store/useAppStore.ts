/**
 * Zustand store for application state
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AnalyzeResponse, AnalysisHistory } from '../types/api';

interface CVData {
  filename: string | null;
  content: string | null;
  uploadedAt: string | null;
}

interface JobData {
  description: string;
  lastModified: string | null;
}

interface AnalysisState {
  isLoading: boolean;
  error: string | null;
  result: AnalyzeResponse | null;
}

interface AppState {
  // CV state
  currentCV: CVData;
  uploadCV: (filename: string, content: string) => void;
  clearCV: () => void;

  // Job description state
  currentJob: JobData;
  updateJobDescription: (description: string) => void;
  clearJob: () => void;

  // Analysis state
  analysis: AnalysisState;
  startAnalysis: () => void;
  completeAnalysis: (result: AnalyzeResponse) => void;
  failAnalysis: (error: string) => void;
  clearAnalysis: () => void;

  // Analysis history
  history: AnalysisHistory[];
  addToHistory: (result: AnalyzeResponse, cvFilename: string) => void;
  clearHistory: () => void;

  // UI state
  currentView: 'upload' | 'results' | 'history';
  setCurrentView: (view: 'upload' | 'results' | 'history') => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial CV state
      currentCV: {
        filename: null,
        content: null,
        uploadedAt: null,
      },

      uploadCV: (filename, content) =>
        set({
          currentCV: {
            filename,
            content,
            uploadedAt: new Date().toISOString(),
          },
        }),

      clearCV: () =>
        set({
          currentCV: {
            filename: null,
            content: null,
            uploadedAt: null,
          },
        }),

      // Initial job description state
      currentJob: {
        description: '',
        lastModified: null,
      },

      updateJobDescription: (description) =>
        set({
          currentJob: {
            description,
            lastModified: new Date().toISOString(),
          },
        }),

      clearJob: () =>
        set({
          currentJob: {
            description: '',
            lastModified: null,
          },
        }),

      // Initial analysis state
      analysis: {
        isLoading: false,
        error: null,
        result: null,
      },

      startAnalysis: () =>
        set({
          analysis: {
            isLoading: true,
            error: null,
            result: null,
          },
        }),

      completeAnalysis: (result) =>
        set((state) => {
          // Add to history
          const historyEntry: AnalysisHistory = {
            id: result.analysis_id,
            timestamp: new Date().toISOString(),
            cvFilename: state.currentCV.filename || 'Unknown',
            score: result.overall_score,
            result,
          };

          return {
            analysis: {
              isLoading: false,
              error: null,
              result,
            },
            history: [historyEntry, ...state.history].slice(0, 10), // Keep last 10
            currentView: 'results',
          };
        }),

      failAnalysis: (error) =>
        set({
          analysis: {
            isLoading: false,
            error,
            result: null,
          },
        }),

      clearAnalysis: () =>
        set({
          analysis: {
            isLoading: false,
            error: null,
            result: null,
          },
        }),

      // History state
      history: [],

      addToHistory: (result, cvFilename) =>
        set((state) => {
          const historyEntry: AnalysisHistory = {
            id: result.analysis_id,
            timestamp: new Date().toISOString(),
            cvFilename,
            score: result.overall_score,
            result,
          };

          return {
            history: [historyEntry, ...state.history].slice(0, 10),
          };
        }),

      clearHistory: () => set({ history: [] }),

      // UI state
      currentView: 'upload',
      setCurrentView: (view) => set({ currentView: view }),
    }),
    {
      name: 'cv-checker-storage',
      partialize: (state) => ({
        currentCV: state.currentCV,
        currentJob: state.currentJob,
        history: state.history,
      }),
    }
  )
);
