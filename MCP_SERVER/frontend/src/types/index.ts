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

<<<<<<< HEAD
export interface ApiUserPrompt {
  prompt: string;
  priority: 'low' | 'normal' | 'high' | 'critical';
  timeout?: number;
  metadata?: Record<string, any>;
}

=======
/**
 * @interface TaskRequest
 * @description Represents a request for an automation task.
 */
>>>>>>> f37de6ae00bbacc9c5649a206245e6bde2543ecf
export interface TaskRequest {
  id: string;
  user_prompt: UserPrompt;
  target_urls: string[];
  expected_outputs: string[];
  safety_preferences?: Record<string, any>;
  created_at: Date;
}

<<<<<<< HEAD
export interface ApiTaskRequest {
  id: string;
  user_prompt: ApiUserPrompt;
  target_urls: string[];
  expected_outputs: string[];
  safety_preferences?: Record<string, any>;
  created_at: string; // ISO date string from API
}

=======
/**
 * @interface ElementSelector
 * @description Represents a selector for an element on a web page.
 */
>>>>>>> f37de6ae00bbacc9c5649a206245e6bde2543ecf
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

<<<<<<< HEAD
export interface ApiBrowserAction {
  id: string;
  type: string; // 'click', 'type', 'navigate', 'extract', etc.
  element?: ElementSelector;
  value?: string | number;
  description?: string;
  timeout?: number;
  created_at: string; // ISO date string from API
  metadata?: Record<string, any>;
}

=======
/**
 * @interface BrowserState
 * @description Represents the state of a browser at a given time.
 */
>>>>>>> f37de6ae00bbacc9c5649a206245e6bde2543ecf
export interface BrowserState {
  url: string;
  title: string;
  dom_content: string;
  screenshot_path?: string;
  viewport_size?: { width: number; height: number };
  page_info?: Record<string, any>;
  timestamp: Date;
}

<<<<<<< HEAD
export interface ApiBrowserState {
  url: string;
  title: string;
  dom_content: string;
  screenshot_path?: string;
  viewport_size?: { width: number; height: number };
  page_info?: Record<string, any>;
  timestamp: string; // ISO date string from API
}

=======
/**
 * @interface TaskExecutionPlan
 * @description Represents a plan for executing an automation task.
 */
>>>>>>> f37de6ae00bbacc9c5649a206245e6bde2543ecf
export interface TaskExecutionPlan {
  id: string;
  task_id: string;
  actions: BrowserAction[];
  estimated_duration?: number;
  created_at: Date;
  status: string;
  metadata?: Record<string, any>;
}

<<<<<<< HEAD
export interface ApiTaskExecutionPlan {
  id: string;
  task_id: string;
  actions: ApiBrowserAction[];
  estimated_duration?: number;
  created_at: string; // ISO date string from API
  status: string; // 'pending', 'executing', 'completed', 'failed'
  metadata?: Record<string, any>;
}

=======
/**
 * @interface ActionResult
 * @description Represents the result of a browser action.
 */
>>>>>>> f37de6ae00bbacc9c5649a206245e6bde2543ecf
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

<<<<<<< HEAD
export interface ApiActionResult {
  action_id: string;
  success: boolean;
  result?: any;
  error?: string;
  execution_time?: number;
  screenshot_after?: string;
  dom_diff?: Record<string, any>;
  timestamp: string; // ISO date string from API
}

=======
/**
 * @interface TaskResponse
 * @description Represents the response for an automation task.
 */
>>>>>>> f37de6ae00bbacc9c5649a206245e6bde2543ecf
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
  request: ApiTaskRequest;
  plan?: ApiTaskExecutionPlan;
  results: ApiActionResult[];
  final_state?: ApiBrowserState;
  error?: string;
  started_at?: string;
  completed_at?: string;
  execution_time?: number;
}

// Utility functions to convert API responses to internal format
export const convertApiTaskResponse = (apiResponse: ApiTaskResponse): TaskResponse => {
  return {
    task_id: apiResponse.task_id,
    status: apiResponse.status,
    request: convertApiTaskRequest(apiResponse.request),
    plan: apiResponse.plan ? convertApiTaskExecutionPlan(apiResponse.plan) : undefined,
    results: apiResponse.results.map(result => convertApiActionResult(result)),
    final_state: apiResponse.final_state ? convertApiBrowserState(apiResponse.final_state) : undefined,
    error: apiResponse.error,
    started_at: apiResponse.started_at ? new Date(apiResponse.started_at) : undefined,
    completed_at: apiResponse.completed_at ? new Date(apiResponse.completed_at) : undefined,
    execution_time: apiResponse.execution_time
  };
};

export const convertApiTaskRequest = (apiRequest: ApiTaskRequest): TaskRequest => {
  return {
    id: apiRequest.id,
    user_prompt: apiRequest.user_prompt,
    target_urls: apiRequest.target_urls,
    expected_outputs: apiRequest.expected_outputs,
    safety_preferences: apiRequest.safety_preferences,
    created_at: new Date(apiRequest.created_at)
  };
};

export const convertApiTaskExecutionPlan = (apiPlan: ApiTaskExecutionPlan): TaskExecutionPlan => {
  return {
    id: apiPlan.id,
    task_id: apiPlan.task_id,
    actions: apiPlan.actions.map(action => convertApiBrowserAction(action)),
    estimated_duration: apiPlan.estimated_duration,
    created_at: new Date(apiPlan.created_at),
    status: apiPlan.status,
    metadata: apiPlan.metadata
  };
};

export const convertApiBrowserAction = (apiAction: ApiBrowserAction): BrowserAction => {
  return {
    id: apiAction.id,
    type: apiAction.type,
    element: apiAction.element,
    value: apiAction.value,
    description: apiAction.description,
    timeout: apiAction.timeout,
    created_at: new Date(apiAction.created_at),
    metadata: apiAction.metadata
  };
};

export const convertApiActionResult = (apiResult: ApiActionResult): ActionResult => {
  return {
    action_id: apiResult.action_id,
    success: apiResult.success,
    result: apiResult.result,
    error: apiResult.error,
    execution_time: apiResult.execution_time,
    screenshot_after: apiResult.screenshot_after,
    dom_diff: apiResult.dom_diff,
    timestamp: new Date(apiResult.timestamp)
  };
};

export const convertApiBrowserState = (apiState: ApiBrowserState): BrowserState => {
  return {
    url: apiState.url,
    title: apiState.title,
    dom_content: apiState.dom_content,
    screenshot_path: apiState.screenshot_path,
    viewport_size: apiState.viewport_size,
    page_info: apiState.page_info,
    timestamp: new Date(apiState.timestamp)
  };
};