export interface Company {
  id: string;
  company_name: string;
  industry?: string;
  brand_voice?: string;
  created_at: string;
}

export interface Product {
  id: string;
  company_id?: string;
  product_name: string;
  description?: string;
  launch_date?: string;
  target_skin_type?: string;
}

export interface Campaign {
  id: string;
  product_id?: string;
  name: string;
  description?: string;
  channel: 'facebook' | 'email' | 'google_seo';
  customer_segment?: string;
  frequency?: 'daily' | 'weekly' | 'monthly';
  budget: number;
  status: 'draft' | 'active' | 'paused' | 'completed';
  created_at: string;
  updated_at: string;
}

export interface SetupConfig {
  id: string;
  product_id?: string;
  company_id?: string;
  market_details?: string;
  strategic_goals?: string;
  monthly_budget: number;
  guardrails?: string;
  rebalancing_frequency: string;
  campaign_count: number;
  is_active: boolean;
}

export interface CustomerSegment {
  id: string;
  name: string;
  description?: string;
  criteria?: string;
  size?: number;
}

export interface CampaignIdea {
  name: string;
  description: string;
  channel: string;
  customer_segment: string;
  suggested_budget: number;
  frequency: string;
  messaging?: string[];
  expected_outcomes?: string;
}

export interface Metric {
  id: string;
  campaign_id?: string;
  platform?: string;
  clicks: number;
  impressions: number;
  engagement_rate: number;
  conversion_rate: number;
  cpa: number;
  timestamp: string;
}

export interface Schedule {
  id: string;
  campaign_id: string;
  scheduled_time: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  job_id?: string;
  created_at: string;
  executed_at?: string;
}

export interface ContentAsset {
  id: string;
  campaign_id?: string;
  platform?: string;
  asset_type?: string;
  copy_text?: string;
  visual_url?: string;
  status?: string;
  created_at: string;
  published_at?: string;
}

export interface SetupFormData {
  product_id: string;
  company_id: string;
  market_details: {
    target_demographics: string;
    market_size: string;
    competition_level: string;
    key_trends: string;
  };
  strategic_goals: string;
  monthly_budget: number;
  guardrails: string;
  rebalancing_frequency: 'daily' | 'weekly' | 'monthly';
  campaign_count: number;
}

export interface ChannelMetrics {
  channel: string;
  total_campaigns: number;
  total_clicks: number;
  total_impressions: number;
  avg_engagement_rate: number;
  avg_conversion_rate: number;
  total_spend: number;
}