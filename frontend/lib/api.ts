import axios from 'axios';
import { Campaign, SetupConfig, CustomerSegment, CampaignIdea, Metric, Schedule } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Setup APIs
export const setupApi = {
  getCompanies: async () => {
    const response = await api.get('/api/setup/companies');
    return response.data;
  },
  
  getProducts: async (companyId?: string) => {
    const response = await api.get('/api/setup/products', {
      params: { company_id: companyId }
    });
    return response.data;
  },
  
  initialize: async (setupData: any) => {
    const response = await api.post('/api/setup/initialize', setupData);
    return response.data;
  },
  
  getCurrent: async (): Promise<SetupConfig | null> => {
    const response = await api.get('/api/setup/current');
    return response.data;
  },
};

// Campaign APIs
export const campaignApi = {
  list: async (filters?: { channel?: string; status?: string }) => {
    const response = await api.get<Campaign[]>('/api/campaigns', { params: filters });
    return response.data;
  },
  
  get: async (id: string) => {
    const response = await api.get<Campaign>(`/api/campaigns/${id}`);
    return response.data;
  },
  
  getContent: async (id: string) => {
    const response = await api.get(`/api/campaigns/${id}/content`);
    return response.data;
  },
  
  create: async (campaignData: any) => {
    const response = await api.post<Campaign>('/api/campaigns', campaignData);
    return response.data;
  },
  
  update: async (id: string, updateData: any) => {
    const response = await api.put<Campaign>(`/api/campaigns/${id}`, updateData);
    return response.data;
  },
  
  activate: async (id: string) => {
    const response = await api.post<Campaign>(`/api/campaigns/${id}/activate`);
    return response.data;
  },
  
  pause: async (id: string) => {
    const response = await api.post<Campaign>(`/api/campaigns/${id}/pause`);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/api/campaigns/${id}`);
    return response.data;
  },
};

// Agent APIs
export const agentApi = {
  generateSegments: async () => {
    const response = await api.post('/api/agents/segment');
    return response.data;
  },
  
  getSegments: async (): Promise<CustomerSegment[]> => {
    const response = await api.get('/api/agents/segments');
    return response.data;
  },
  
  generateCampaignIdeas: async (data: {
    segments: string[];
    channels: string[];
  }): Promise<CampaignIdea[]> => {
    const response = await api.post('/api/agents/create-campaigns', data);
    return response.data;
  },
  
  rebalanceBudgets: async () => {
    const response = await api.post('/api/agents/rebalance-budgets');
    return response.data;
  },
  
  executeCampaign: async (campaignId: string) => {
    const response = await api.post(`/api/agents/execute-campaign/${campaignId}`);
    return response.data;
  },
};

// Metrics APIs
export const metricsApi = {
  getCampaignMetrics: async (campaignId: string, startDate?: Date, endDate?: Date) => {
    const response = await api.get<Metric[]>(`/api/metrics/campaign/${campaignId}`, {
      params: {
        start_date: startDate?.toISOString(),
        end_date: endDate?.toISOString(),
      },
    });
    return response.data;
  },
  
  getSummary: async (days: number = 7) => {
    const response = await api.get('/api/metrics/summary', {
      params: { days },
    });
    return response.data;
  },
  
  getChannelMetrics: async (days: number = 7) => {
    const response = await api.get('/api/metrics/channels', {
      params: { days },
    });
    return response.data;
  },
  
  collectMetrics: async () => {
    const response = await api.post('/api/metrics/collect');
    return response.data;
  },
};

// Schedule APIs
export const scheduleApi = {
  list: async (filters?: { campaign_id?: string; status?: string }) => {
    const response = await api.get<Schedule[]>('/api/schedules', { params: filters });
    return response.data;
  },
  
  create: async (scheduleData: any) => {
    const response = await api.post<Schedule>('/api/schedules', scheduleData);
    return response.data;
  },
  
  getUpcoming: async (days: number = 7) => {
    const response = await api.get<Schedule[]>('/api/schedules/upcoming', {
      params: { days },
    });
    return response.data;
  },
  
  update: async (id: string, updateData: any) => {
    const response = await api.put<Schedule>(`/api/schedules/${id}`, updateData);
    return response.data;
  },
  
  delete: async (id: string) => {
    const response = await api.delete(`/api/schedules/${id}`);
    return response.data;
  },
};

export default api;