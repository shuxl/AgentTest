/**
 * 健康检查服务
 */
import api from './api';
import { HealthResponse, DatabaseHealthResponse } from '../types/api';
import { API_TIMEOUT } from '../utils/constants';

export const healthService = {
  /**
   * 检查服务健康状态
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await api.get<HealthResponse>('/health', {
      timeout: API_TIMEOUT.HEALTH,
    });
    return response.data;
  },

  /**
   * 检查数据库健康状态
   */
  async checkDatabaseHealth(): Promise<DatabaseHealthResponse> {
    const response = await api.get<DatabaseHealthResponse>('/health/db', {
      timeout: API_TIMEOUT.HEALTH,
    });
    return response.data;
  },
};

