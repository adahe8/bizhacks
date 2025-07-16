// frontend/lib/types.ts - FIXED VERSION

export interface Company {
  id: string;
  company_name?: string;  // Made optional to match SQLModel definition
  industry?: string;
  brand_voice?: string;
  created_at?: string;    // Made optional to match SQLModel definition
}

export interface Product {
  id: string;
  company_id?: string;
  product_name?: string;  // Made optional to match SQLModel definition
  description?: string;
  launch_date?: string;
  target_skin_type?: string;
}

export interface User {
  id: string;
  age?: number;
  location?: string;
  skin_type?: string;
  channels_engaged?: string;  // JSON string
  purchase_history?: string;  // JSON string
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

export interface Metric {
  id: string;
  campaign_id?: string;
  platform?: string;
  clicks?: number;      // Made optional to match SQLModel definition
  impressions?: number; // Made optional to match SQLModel definition
  engagement_rate?: number;
  conversion_rate?: number;
  cpa?: number;
  timestamp?: string;   // Made optional to match SQLModel definition
}

export interface CustomerSegment {
  id: string;           // ✅ Backend sends UUID serialized as string
  name: string;
  description?: string;
  criteria?: string | any;  // JSON string or parsed object
  size?: number;        // ✅ Backend sends float, frontend receives as number
  channel_distribution?: string | any;  // JSON string or parsed object
  cluster_centroid?: string;  // JSON string
  created_at?: string;
}

export interface CampaignMetrics {
  id: string;
  campaign_id: string;
  channel: string;
  metrics_config: string;  // JSON string
  created_at: string;
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

export interface SetupConfiguration {
  id: string;
  product_id?: string;
  company_id?: string;
  market_details?: string;  // JSON string
  strategic_goals?: string;
  monthly_budget: number;
  guardrails?: string;
  rebalancing_frequency: string;
  campaign_count: number;
  is_active: boolean;
  created_at?: string;
}

export interface GameState {
  id: string;
  current_date: string;
  game_speed: 'slow' | 'medium' | 'fast';
  is_running: boolean;
  total_reach_optimal: number;
  total_reach_non_optimal: number;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  user_id: string;
  product_id: string;
  amount: number;
  transaction_date: string;
  channel?: string;
  campaign_id?: string;
}

// Additional types for form data and API responses
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

export interface CampaignIdea {
  name: string;
  description: string;
  channel: string;
  customer_segment: string;
  suggested_budget: number;
  frequency: string;
  messaging?: string[];
  objectives?: {
    primary_goal: string;
    target_metrics: Record<string, number>;
    success_criteria: string[];
  };
  expected_outcomes?: string;
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

export interface OptimizationData {
  date: string;
  optimal: number;
  nonOptimal: number;
}

// Alias for backward compatibility if needed
export type SetupConfig = SetupConfiguration;