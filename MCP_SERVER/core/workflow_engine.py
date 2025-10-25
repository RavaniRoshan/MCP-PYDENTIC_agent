from typing import Dict, List, Optional, Any, Union, Callable
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import logging
import uuid
from dataclasses import dataclass
from pydantic import BaseModel, Field
from models import (
    UserPrompt, 
    TaskRequest, 
    BrowserAction, 
    ElementSelector, 
    ActionType,
    ExtractAction,
    FormActionModel,
    BrowserState,
    ActionResult
)
from ai_services.action_execution import ActionExecutionFramework
from core.browser_controller import BrowserControllerInterface


class WorkflowNodeType(str, Enum):
    """
    Types of nodes in a workflow.
    """
    ACTION = "action"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    DELAY = "delay"
    BRANCH = "branch"
    SUBWORKFLOW = "subworkflow"


class ConditionalOperator(str, Enum):
    """
    Operators for conditional logic.
    """
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


@dataclass
class WorkflowVariable:
    """
    A variable that can be used in workflows.
    
    Attributes:
        name: Name of the variable
        value: Current value of the variable
        type_hint: Expected type of the variable
        scope: Scope of the variable (global, workflow, task)
    """
    name: str
    value: Any
    type_hint: str = "string"
    scope: str = "workflow"


class WorkflowNode(BaseModel):
    """
    Represents a node in a workflow.
    
    Attributes:
        id: Unique identifier for the node
        type: Type of the node
        name: Human-readable name for the node
        action: Browser action to execute (for action nodes)
        condition: Conditional expression (for conditional nodes)
        children: Child nodes for the current node
        next_node_id: ID of the next node in the workflow
        metadata: Additional metadata for the node
    """
    id: str = Field(default_factory=lambda: f"node_{uuid.uuid4().hex[:8]}")
    type: WorkflowNodeType
    name: str
    action: Optional[BrowserAction] = None
    condition: Optional[Dict[str, Any]] = None  # For conditionals, contains field, operator, value
    children: List['WorkflowNode'] = Field(default_factory=list)
    next_node_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class WorkflowTemplate(BaseModel):
    """
    Represents a template for a workflow.
    
    Attributes:
        id: Unique identifier for the template
        name: Name of the workflow template
        description: Description of what the workflow does
        start_node_id: ID of the starting node
        nodes: All nodes in the workflow
        variables: Variables used in the workflow
        author: Author of the template
        created_at: When the template was created
        updated_at: When the template was last updated
    """
    id: str = Field(default_factory=lambda: f"template_{uuid.uuid4().hex[:8]}")
    name: str
    description: str = ""
    start_node_id: str
    nodes: List[WorkflowNode] = Field(default_factory=list)
    variables: List[WorkflowVariable] = Field(default_factory=list)
    author: str = "system"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class WorkflowInstance(BaseModel):
    """
    Represents an executing instance of a workflow.
    
    Attributes:
        id: Unique identifier for the instance
        template_id: ID of the template this instance is based on
        status: Current status of the instance (pending, running, completed, failed)
        variables: Current values of variables for this instance
        current_node_id: ID of the currently executing node
        started_at: When the instance was started
        completed_at: When the instance was completed (if applicable)
        error: Error message if the workflow failed
    """
    id: str = Field(default_factory=lambda: f"instance_{uuid.uuid4().hex[:8]}")
    template_id: str
    status: str = "pending"
    variables: Dict[str, Any] = Field(default_factory=dict)
    current_node_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class WorkflowExecutionResult(BaseModel):
    """
    Represents the result of executing a workflow.
    
    Attributes:
        instance_id: ID of the workflow instance
        success: Whether the workflow executed successfully
        results: Results of individual node executions
        final_variables: Final values of workflow variables
        execution_time: Time taken to execute the workflow in seconds
        error: Error message if the workflow failed
    """
    instance_id: str
    success: bool
    results: List[ActionResult] = Field(default_factory=list)
    final_variables: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    error: Optional[str] = None


class AdvancedWorkflowEngine:
    """
    Advanced workflow automation engine supporting conditionals, loops, and scheduling.
    """
    
    def __init__(self, action_execution_framework: ActionExecutionFramework):
        self.action_execution_framework = action_execution_framework
        self.browser_controller = action_execution_framework.browser_controller
        self.logger = logging.getLogger(__name__)
        self.templates: Dict[str, WorkflowTemplate] = {}
        self.instances: Dict[str, WorkflowInstance] = {}
        self.active_executions: Dict[str, asyncio.Task] = {}
    
    def register_template(self, template: WorkflowTemplate) -> bool:
        """
        Registers a workflow template.
        
        Args:
            template: The workflow template to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            self.templates[template.id] = template
            self.logger.info(f"Registered workflow template: {template.id} - {template.name}")
            return True
        except Exception as e:
            self.logger.error(f"Error registering workflow template {template.id}: {e}")
            return False
    
    def create_instance(self, template_id: str, initial_variables: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Creates a new instance of a workflow template.
        
        Args:
            template_id: ID of the template to create an instance from
            initial_variables: Initial values for workflow variables
            
        Returns:
            ID of the created instance, or None if creation failed
        """
        if template_id not in self.templates:
            self.logger.error(f"Template {template_id} not found")
            return None
        
        template = self.templates[template_id]
        instance = WorkflowInstance(
            template_id=template_id,
            current_node_id=template.start_node_id,
            variables=initial_variables or {},
            started_at=datetime.utcnow()
        )
        
        self.instances[instance.id] = instance
        self.logger.info(f"Created workflow instance: {instance.id} from template {template_id}")
        return instance.id
    
    async def execute_workflow(self, instance_id: str) -> WorkflowExecutionResult:
        """
        Executes a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance to execute
            
        Returns:
            Workflow execution result
        """
        start_time = datetime.utcnow()
        
        if instance_id not in self.instances:
            error_msg = f"Workflow instance {instance_id} not found"
            self.logger.error(error_msg)
            return WorkflowExecutionResult(
                instance_id=instance_id,
                success=False,
                execution_time=0.0,
                error=error_msg
            )
        
        instance = self.instances[instance_id]
        instance.status = "running"
        
        try:
            results = []
            
            # Start from the initial node
            current_node_id = instance.current_node_id
            while current_node_id:
                # Get the current node
                node = self._get_node_by_id(instance.template_id, current_node_id)
                if not node:
                    error_msg = f"Node {current_node_id} not found in template"
                    instance.status = "failed"
                    instance.error = error_msg
                    break
                
                # Execute the node based on its type
                node_result = await self._execute_node(instance, node)
                results.extend(node_result)
                
                # Check if execution should continue
                if instance.status in ["failed", "completed"]:
                    break
                
                # Move to the next node
                current_node_id = node.next_node_id
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            if instance.status != "failed":
                instance.status = "completed"
                instance.completed_at = datetime.utcnow()
            
            return WorkflowExecutionResult(
                instance_id=instance_id,
                success=instance.status == "completed",
                results=results,
                final_variables=instance.variables,
                execution_time=execution_time,
                error=instance.error
            )
                
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Error executing workflow: {str(e)}"
            instance.status = "failed"
            instance.error = error_msg
            self.logger.error(error_msg)
            
            return WorkflowExecutionResult(
                instance_id=instance_id,
                success=False,
                results=[],
                final_variables=instance.variables,
                execution_time=execution_time,
                error=str(e)
            )
    
    async def _execute_node(self, instance: WorkflowInstance, node: WorkflowNode) -> List[ActionResult]:
        """
        Executes a single workflow node.
        
        Args:
            instance: The workflow instance being executed
            node: The node to execute
            
        Returns:
            List of action results from the node execution
        """
        results = []
        
        if node.type == WorkflowNodeType.ACTION:
            if node.action:
                result = await self.action_execution_framework.execute_action(node.action)
                results.append(result)
                
                # Update variables if the action result should be stored
                if 'store_result_in' in node.metadata:
                    var_name = node.metadata['store_result_in']
                    instance.variables[var_name] = result.result
            
        elif node.type == WorkflowNodeType.CONDITIONAL:
            # Evaluate the condition
            condition_met = await self._evaluate_condition(instance, node.condition)
            
            # Set the next node based on condition result
            if condition_met and 'true_next' in node.metadata:
                node.next_node_id = node.metadata['true_next']
            elif not condition_met and 'false_next' in node.metadata:
                node.next_node_id = node.metadata['false_next']
        
        elif node.type == WorkflowNodeType.DELAY:
            # Handle delay node
            delay_seconds = node.metadata.get('delay_seconds', 1)
            await asyncio.sleep(delay_seconds)
        
        elif node.type == WorkflowNodeType.LOOP:
            # Handle loop node
            results.extend(await self._execute_loop(instance, node))
        
        # Update instance variables if needed
        instance.current_node_id = node.next_node_id
        
        return results
    
    async def _evaluate_condition(self, instance: WorkflowInstance, condition: Optional[Dict[str, Any]]) -> bool:
        """
        Evaluates a conditional expression.
        
        Args:
            instance: The workflow instance
            condition: The condition to evaluate
            
        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return True  # If no condition, treat as true
        
        field = condition.get('field')
        operator = condition.get('operator')
        expected_value = condition.get('value')
        
        # Get the actual value from instance variables or extract from page
        actual_value = instance.variables.get(field, None)
        
        if actual_value is None:
            # If not in variables, might need to extract from current page
            # For now, we'll return False if value not found
            return False
        
        # Apply the operator
        if operator == ConditionalOperator.EQUALS:
            return actual_value == expected_value
        elif operator == ConditionalOperator.NOT_EQUALS:
            return actual_value != expected_value
        elif operator == ConditionalOperator.CONTAINS:
            return expected_value in str(actual_value)
        elif operator == ConditionalOperator.GREATER_THAN:
            return actual_value > expected_value
        elif operator == ConditionalOperator.LESS_THAN:
            return actual_value < expected_value
        elif operator == ConditionalOperator.EXISTS:
            return actual_value is not None
        elif operator == ConditionalOperator.NOT_EXISTS:
            return actual_value is None
        
        return False
    
    async def _execute_loop(self, instance: WorkflowInstance, node: WorkflowNode) -> List[ActionResult]:
        """
        Executes a loop node - this is a simplified implementation.
        
        Args:
            instance: The workflow instance
            node: The loop node to execute
            
        Returns:
            List of action results from the loop execution
        """
        results = []
        
        # Get loop parameters
        max_iterations = node.metadata.get('max_iterations', 10)
        counter_var = node.metadata.get('counter_variable', 'loop_counter')
        
        # Initialize counter
        instance.variables[counter_var] = 0
        
        # Execute loop body
        for i in range(max_iterations):
            instance.variables[counter_var] = i + 1
            
            # Execute child nodes of the loop
            for child_node in node.children:
                child_results = await self._execute_node(instance, child_node)
                results.extend(child_results)
                
                # Check if we should break from the loop
                if instance.status in ["failed", "completed"]:
                    break
            
            # If there's a condition to break early, check it
            if 'break_condition' in node.metadata:
                should_break = await self._evaluate_condition(instance, node.metadata['break_condition'])
                if should_break:
                    break
        
        return results
    
    def _get_node_by_id(self, template_id: str, node_id: str) -> Optional[WorkflowNode]:
        """
        Gets a node by its ID from a template.
        
        Args:
            template_id: ID of the template
            node_id: ID of the node
            
        Returns:
            The node if found, None otherwise
        """
        if template_id not in self.templates:
            return None
        
        template = self.templates[template_id]
        for node in template.nodes:
            if node.id == node_id:
                return node
        
        return None
    
    async def execute_workflow_async(self, instance_id: str) -> str:
        """
        Executes a workflow asynchronously and returns a task ID.
        
        Args:
            instance_id: ID of the workflow instance to execute
            
        Returns:
            Task ID for tracking the asynchronous execution
        """
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        
        async def run_workflow():
            return await self.execute_workflow(instance_id)
        
        task = asyncio.create_task(run_workflow())
        self.active_executions[task_id] = task
        
        # Clean up the task when it's done
        def cleanup(task):
            if task_id in self.active_executions:
                del self.active_executions[task_id]
        
        task.add_done_callback(cleanup)
        
        return task_id
    
    def get_workflow_result(self, task_id: str) -> Optional[WorkflowExecutionResult]:
        """
        Gets the result of an asynchronously executed workflow.
        
        Args:
            task_id: ID of the async task
            
        Returns:
            Workflow execution result if available, None otherwise
        """
        if task_id not in self.active_executions:
            return None
        
        task = self.active_executions[task_id]
        if task.done():
            try:
                result = task.result()
                return result
            except Exception as e:
                return WorkflowExecutionResult(
                    instance_id="unknown",
                    success=False,
                    execution_time=0.0,
                    error=str(e)
                )
        else:
            # Task is still running
            return None


# Workflow template builder utility
class WorkflowBuilder:
    """
    Utility class for building workflow templates programmatically.
    """
    
    def __init__(self):
        self.current_template: Optional[WorkflowTemplate] = None
        self.current_node: Optional[WorkflowNode] = None
    
    def create_template(self, name: str, description: str = "") -> 'WorkflowBuilder':
        """
        Creates a new workflow template.
        
        Args:
            name: Name of the template
            description: Description of the template
            
        Returns:
            The workflow builder instance
        """
        self.current_template = WorkflowTemplate(
            name=name,
            description=description,
            start_node_id=""
        )
        return self
    
    def add_action_node(self, name: str, action: BrowserAction) -> 'WorkflowBuilder':
        """
        Adds an action node to the workflow.
        
        Args:
            name: Name of the node
            action: Browser action to execute
            
        Returns:
            The workflow builder instance
        """
        if not self.current_template:
            raise ValueError("No template created. Call create_template first.")
        
        node = WorkflowNode(
            type=WorkflowNodeType.ACTION,
            name=name,
            action=action
        )
        
        self.current_template.nodes.append(node)
        if not self.current_template.start_node_id:
            self.current_template.start_node_id = node.id
        
        self.current_node = node
        return self
    
    def add_conditional_node(self, name: str, condition: Dict[str, Any]) -> 'WorkflowBuilder':
        """
        Adds a conditional node to the workflow.
        
        Args:
            name: Name of the node
            condition: Conditional expression
            
        Returns:
            The workflow builder instance
        """
        if not self.current_template:
            raise ValueError("No template created. Call create_template first.")
        
        node = WorkflowNode(
            type=WorkflowNodeType.CONDITIONAL,
            name=name,
            condition=condition
        )
        
        self.current_template.nodes.append(node)
        if not self.current_template.start_node_id:
            self.current_template.start_node_id = node.id
        
        self.current_node = node
        return self
    
    def add_delay_node(self, name: str, delay_seconds: int) -> 'WorkflowBuilder':
        """
        Adds a delay node to the workflow.
        
        Args:
            name: Name of the node
            delay_seconds: Number of seconds to delay
            
        Returns:
            The workflow builder instance
        """
        if not self.current_template:
            raise ValueError("No template created. Call create_template first.")
        
        node = WorkflowNode(
            type=WorkflowNodeType.DELAY,
            name=name,
            metadata={'delay_seconds': delay_seconds}
        )
        
        self.current_template.nodes.append(node)
        if not self.current_template.start_node_id:
            self.current_template.start_node_id = node.id
        
        self.current_node = node
        return self
    
    def connect_nodes(self, from_node_id: str, to_node_id: str) -> 'WorkflowBuilder':
        """
        Connects two nodes in the workflow.
        
        Args:
            from_node_id: ID of the source node
            to_node_id: ID of the target node
            
        Returns:
            The workflow builder instance
        """
        if not self.current_template:
            raise ValueError("No template created. Call create_template first.")
        
        for node in self.current_template.nodes:
            if node.id == from_node_id:
                node.next_node_id = to_node_id
                break
        
        return self
    
    def connect_current_to(self, to_node_id: str) -> 'WorkflowBuilder':
        """
        Connects the current node to the specified node.
        
        Args:
            to_node_id: ID of the target node
            
        Returns:
            The workflow builder instance
        """
        if not self.current_node:
            raise ValueError("No current node. Add a node first.")
        
        self.current_node.next_node_id = to_node_id
        return self
    
    def build(self) -> WorkflowTemplate:
        """
        Builds and returns the workflow template.
        
        Returns:
            The completed workflow template
        """
        if not self.current_template:
            raise ValueError("No template created. Call create_template first.")
        
        template = self.current_template
        self.current_template = None
        self.current_node = None
        return template