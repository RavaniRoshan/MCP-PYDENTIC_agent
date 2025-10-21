// src/types/index.ts
export interface UserPrompt {
  prompt: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  timeout?: number;
  metadata?: Record<string, any>;
}

export interface TaskRequest {
  id: string;
  user_prompt: UserPrompt;
  target_urls: string[];
  expected_outputs: string[];
  safety_preferences?: Record<string, any>;
  created_at: Date;
}

export interface ElementSelector {
  type: string;
  value: string;
  description?: string;
}

export interface BrowserAction {
  id: string;
  type: string; // 'click', 'type', 'navigate', 'extract', etc.
  element?: ElementSelector;
  value?: string | number;
  description?: string;
  timeout?: number;
  created_at: Date;
  metadata?: Record<string, any>;
}

export interface BrowserState {
  url: string;
  title: string;
  dom_content: string;
  screenshot_path?: string;
  viewport_size?: { width: number; height: number };
  page_info?: Record<string, any>;
  timestamp: Date;
}

export interface TaskExecutionPlan {
  id: string;
  task_id: string;
  actions: BrowserAction[];
  estimated_duration?: number;
  created_at: Date;
  status: string; // 'pending', 'executing', 'completed', 'failed'
  metadata?: Record<string, any>;
}

export interface ActionResult {
  action_id: string;
  success: boolean;
  result?: any;
  error?: string;
  execution_time?: number;
  screenshot_after?: string;
  dom_diff?: Record<string, any>;
  timestamp: Date;
}

export interface TaskResponse {
  task_id: string;
  status: string; // 'pending', 'processing', 'completed', 'failed', 'cancelled'
  request: TaskRequest;
  plan?: TaskExecutionPlan;
  results: ActionResult[];
  final_state?: BrowserState;
  error?: string;
  started_at?: Date;
  completed_at?: Date;
  execution_time?: number;
}

// Define the shape of our API responses
export interface ApiTaskResponse {
  task_id: string;
  status: string;
  request: TaskRequest;
  plan?: TaskExecutionPlan;
  results: ActionResult[];
  final_state?: BrowserState;
  error?: string;
  started_at?: string; // ISO date string
  completed_at?: string; // ISO date string
  execution_time?: number;
}