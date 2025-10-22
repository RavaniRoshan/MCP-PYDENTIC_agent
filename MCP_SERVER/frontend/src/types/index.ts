// src/types/index.ts

/**
 * @interface UserPrompt
 * @description Represents a user's prompt for an automation task.
 */
export interface UserPrompt {
  prompt: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  timeout?: number;
  metadata?: Record<string, any>;
}

/**
 * @interface TaskRequest
 * @description Represents a request for an automation task.
 */
export interface TaskRequest {
  id: string;
  user_prompt: UserPrompt;
  target_urls: string[];
  expected_outputs: string[];
  safety_preferences?: Record<string, any>;
  created_at: Date;
}

/**
 * @interface ElementSelector
 * @description Represents a selector for an element on a web page.
 */
export interface ElementSelector {
  type: string;
  value: string;
  description?: string;
}

/**
 * @interface BrowserAction
 * @description Represents an action to be performed in a browser.
 */
export interface BrowserAction {
  id: string;
  type: string;
  element?: ElementSelector;
  value?: string | number;
  description?: string;
  timeout?: number;
  created_at: Date;
  metadata?: Record<string, any>;
}

/**
 * @interface BrowserState
 * @description Represents the state of a browser at a given time.
 */
export interface BrowserState {
  url: string;
  title: string;
  dom_content: string;
  screenshot_path?: string;
  viewport_size?: { width: number; height: number };
  page_info?: Record<string, any>;
  timestamp: Date;
}

/**
 * @interface TaskExecutionPlan
 * @description Represents a plan for executing an automation task.
 */
export interface TaskExecutionPlan {
  id: string;
  task_id: string;
  actions: BrowserAction[];
  estimated_duration?: number;
  created_at: Date;
  status: string;
  metadata?: Record<string, any>;
}

/**
 * @interface ActionResult
 * @description Represents the result of a browser action.
 */
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

/**
 * @interface TaskResponse
 * @description Represents the response for an automation task.
 */
export interface TaskResponse {
  task_id: string;
  status: string;
  request: TaskRequest;
  plan?: TaskExecutionPlan;
  results: ActionResult[];
  final_state?: BrowserState;
  error?: string;
  started_at?: Date;
  completed_at?: Date;
  execution_time?: number;
}

/**
 * @interface ApiTaskResponse
 * @description Represents the response for an automation task from the API.
 */
export interface ApiTaskResponse {
  task_id: string;
  status: string;
  request: TaskRequest;
  plan?: TaskExecutionPlan;
  results: ActionResult[];
  final_state?: BrowserState;
  error?: string;
  started_at?: string;
  completed_at?: string;
  execution_time?: number;
}