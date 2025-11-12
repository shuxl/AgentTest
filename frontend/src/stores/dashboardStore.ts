/**
 * 数据展示状态管理（Zustand）
 */
import { create } from 'zustand';
import { DatabaseHealthResponse } from '../types/api';

interface DashboardState {
  healthStatus: DatabaseHealthResponse | null;
  isLoading: boolean;
  error: string | null;
  autoRefresh: boolean;
  lastUpdateTime: number | null;
}

interface DashboardStore extends DashboardState {
  // Actions
  setHealthStatus: (status: DatabaseHealthResponse) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setAutoRefresh: (enabled: boolean) => void;
  setLastUpdateTime: (time: number) => void;
}

export const useDashboardStore = create<DashboardStore>((set) => ({
  // State
  healthStatus: null,
  isLoading: false,
  error: null,
  autoRefresh: true,
  lastUpdateTime: null,

  // Actions
  setHealthStatus: (status) => {
    set({ healthStatus: status, error: null, lastUpdateTime: Date.now() });
  },

  setLoading: (isLoading) => {
    set({ isLoading });
  },

  setError: (error) => {
    set({ error });
  },

  setAutoRefresh: (autoRefresh) => {
    set({ autoRefresh });
  },

  setLastUpdateTime: (time) => {
    set({ lastUpdateTime: time });
  },
}));

