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
  sourceType: 'manual' | 'linkedin_url';
  sourceUrl: string | null;
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
  jobInputMode: 'manual' | 'linkedin_url';
  setJobInputMode: (mode: 'manual' | 'linkedin_url') => void;
  updateJobDescription: (description: string, sourceType?: 'manual' | 'linkedin_url', sourceUrl?: string | null) => void;
  clearJob: () => void;

  // Analysis state
  analysis: AnalysisState;
  startAnalysis: () => void;
  completeAnalysis: (result: AnalyzeResponse) => void;
  failAnalysis: (error: string) => void;
  clearAnalysis: () => void;

  // UI state
  currentView: 'upload' | 'results' | 'history';
  setCurrentView: (view: 'upload' | 'results' | 'history') => void;

  // Reset all state
  resetState: () => void;
}

const STORAGE_VERSION = 2; // Increment when store structure changes

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
        sourceType: 'manual',
        sourceUrl: null,
      },

      jobInputMode: 'manual',

      setJobInputMode: (mode) =>
        set({
          jobInputMode: mode,
        }),

      updateJobDescription: (description, sourceType = 'manual', sourceUrl = null) =>
        set({
          currentJob: {
            description,
            lastModified: new Date().toISOString(),
            sourceType,
            sourceUrl,
          },
        }),

      clearJob: () =>
        set({
          currentJob: {
            description: '',
            lastModified: null,
            sourceType: 'manual',
            sourceUrl: null,
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
        set({
          analysis: {
            isLoading: false,
            error: null,
            result,
          },
          currentView: 'results',
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

      // UI state
      currentView: 'upload',
      setCurrentView: (view) => set({ currentView: view }),

      // Reset all state
      resetState: () =>
        set({
          currentCV: {
            filename: null,
            content: null,
            uploadedAt: null,
          },
          currentJob: {
            description: '',
            lastModified: null,
            sourceType: 'manual',
            sourceUrl: null,
          },
          jobInputMode: 'manual',
          analysis: {
            isLoading: false,
            error: null,
            result: null,
          },
          currentView: 'upload',
        }),
    }),
    {
      name: 'cv-checker-storage',
      version: STORAGE_VERSION,
      // Don't persist any state to avoid navigation issues
      partialize: () => ({}),
      // Migrate old storage versions
      migrate: (persistedState: any, version: number) => {
        if (version < STORAGE_VERSION) {
          // Clear old state and return defaults
          return {
            currentCV: { filename: null, content: null, uploadedAt: null },
            currentJob: { description: '', lastModified: null, sourceType: 'manual', sourceUrl: null },
            jobInputMode: 'manual',
            analysis: { isLoading: false, error: null, result: null },
            currentView: 'upload',
          };
        }
        return persistedState;
      },
    }
  )
);
