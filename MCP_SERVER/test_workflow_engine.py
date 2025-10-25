import asyncio
from models import (
    BrowserAction, 
    ElementSelector, 
    ActionType,
    ExtractAction,
    ExtractMethod
)
from core.browser_controller import MockBrowserController
from ai_services.action_execution import ActionExecutionFramework
from core.workflow_engine import (
    AdvancedWorkflowEngine, 
    WorkflowBuilder,
    WorkflowNodeType,
    ConditionalOperator,
    WorkflowTemplate,
    WorkflowInstance
)


async def test_workflow_engine():
    """
    Tests the advanced workflow automation tools.
    """
    print("Testing Advanced Workflow Automation Tools")
    print("="*60)
    
    # Create a mock browser controller and action execution framework
    browser_controller = MockBrowserController()
    framework = ActionExecutionFramework(browser_controller)
    
    # Create the workflow engine
    workflow_engine = AdvancedWorkflowEngine(framework)
    
    print("1. Creating a simple workflow using the builder")
    
    # Create a simple workflow: navigate -> extract text -> delay -> extract again
    workflow_template = (WorkflowBuilder()
        .create_template("Simple Extraction Workflow", "Extracts text with delays")
        .add_action_node(
            "Navigate to example",
            BrowserAction(
                id="nav_example",
                type=ActionType.NAVIGATE,
                value="https://example.com"
            )
        )
        .add_action_node(
            "Extract heading",
            ExtractAction(
                id="extract_heading",
                method=ExtractMethod.TEXT_CONTENT,
                element=ElementSelector(type="css", value="h1", description="Main heading")
            )
        )
        .add_delay_node("Wait 2 seconds", 2)
        .add_action_node(
            "Extract links",
            ExtractAction(
                id="extract_links",
                method=ExtractMethod.LINKS
            )
        )
        .build())
    
    print(f"   Created workflow template: {workflow_template.name}")
    print(f"   Template ID: {workflow_template.id}")
    print(f"   Number of nodes: {len(workflow_template.nodes)}")
    
    print("\n2. Registering the workflow template")
    registration_result = workflow_engine.register_template(workflow_template)
    print(f"   Registration result: {registration_result}")
    
    print("\n3. Creating a workflow instance")
    instance_id = workflow_engine.create_instance(workflow_template.id)
    print(f"   Created instance: {instance_id}")
    
    print("\n4. Testing conditional workflow")
    
    # Create a workflow with conditionals
    conditional_template = (WorkflowBuilder()
        .create_template("Conditional Workflow", "Workflow with conditional logic")
        .add_action_node(
            "Navigate to site",
            BrowserAction(
                id="nav_site",
                type=ActionType.NAVIGATE,
                value="https://example.com"
            )
        )
        .add_action_node(
            "Check element exists",
            ExtractAction(
                id="check_element",
                method=ExtractMethod.TEXT_CONTENT,
                element=ElementSelector(type="css", value="h1", description="Main heading")
            )
        )
        .add_conditional_node(
            "Check if heading found",
            {
                "field": "heading_result",
                "operator": ConditionalOperator.EXISTS,
                "value": None
            }
        )
        .build())
    
    # Set up metadata for the conditional node
    for node in conditional_template.nodes:
        if node.type == WorkflowNodeType.CONDITIONAL:
            node.metadata = {
                'true_next': conditional_template.nodes[-1].id,  # Connect to next node if true
                'false_next': conditional_template.nodes[-1].id  # Connect to next node if false
            }
    
    cond_registration = workflow_engine.register_template(conditional_template)
    print(f"   Conditional template registration: {cond_registration}")
    
    print("\n5. Executing the simple workflow")
    
    # Execute the workflow asynchronously
    task_id = await workflow_engine.execute_workflow_async(instance_id)
    print(f"   Started execution task: {task_id}")
    
    # Wait for the task to complete (with timeout)
    import time
    start_time = time.time()
    result = None
    while time.time() - start_time < 10:  # 10 second timeout
        result = workflow_engine.get_workflow_result(task_id)
        if result:
            break
        await asyncio.sleep(0.5)
    
    if result:
        print(f"   Execution completed: {result.success}")
        print(f"   Execution time: {result.execution_time:.2f}s")
        print(f"   Number of action results: {len(result.results)}")
        if result.error:
            print(f"   Error: {result.error}")
    else:
        print("   Execution still in progress or timed out")
    
    print("\n6. Testing workflow with variables")
    
    # Create a workflow that uses variables
    var_template = (WorkflowBuilder()
        .create_template("Variable Workflow", "Workflow that uses variables")
        .add_action_node(
            "Navigate",
            BrowserAction(
                id="nav_var",
                type=ActionType.NAVIGATE,
                value="https://httpbin.org"
            )
        )
        .add_action_node(
            "Extract title",
            ExtractAction(
                id="extract_title",
                method=ExtractMethod.TEXT_CONTENT,
                element=ElementSelector(type="css", value="title", description="Page title")
            )
        )
        .build())
    
    # Set up variable storage for the extract action
    for node in var_template.nodes:
        if node.type == WorkflowNodeType.ACTION and node.action and hasattr(node.action, 'method'):
            node.metadata = {'store_result_in': 'page_title'}
    
    var_registration = workflow_engine.register_template(var_template)
    print(f"   Variable template registration: {var_registration}")
    
    # Create instance with initial variables
    var_instance_id = workflow_engine.create_instance(var_template.id, {"base_url": "https://httpbin.org"})
    print(f"   Created variable workflow instance: {var_instance_id}")
    
    # Execute and get result
    var_result = await workflow_engine.execute_workflow(var_instance_id)
    print(f"   Variable workflow execution: {var_result.success}")
    print(f"   Final variables: {list(var_result.final_variables.keys())}")
    
    print("\n7. Testing loop workflow")
    
    # Create a simple workflow with a loop concept (simulated)
    loop_template = (WorkflowBuilder()
        .create_template("Loop Simulation", "Simulates a loop operation")
        .add_delay_node("Initial delay", 1)
        .add_action_node(
            "First action",
            BrowserAction(
                id="first_action",
                type=ActionType.NAVIGATE,
                value="https://example.com"
            )
        )
        .build())
    
    loop_registration = workflow_engine.register_template(loop_template)
    print(f"   Loop template registration: {loop_registration}")
    
    loop_instance_id = workflow_engine.create_instance(loop_template.id)
    loop_result = await workflow_engine.execute_workflow(loop_instance_id)
    print(f"   Loop workflow execution: {loop_result.success}")
    print(f"   Execution time: {loop_result.execution_time:.2f}s")
    
    print("\n8. Listing all registered templates")
    print(f"   Total templates registered: {len(workflow_engine.templates)}")
    for template_id, template in workflow_engine.templates.items():
        print(f"     - {template.name} (ID: {template_id})")
    
    print("\n" + "="*60)
    print("Advanced workflow automation tools test completed!")


if __name__ == "__main__":
    asyncio.run(test_workflow_engine())