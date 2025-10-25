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


async def test_detailed_workflow():
    """
    Tests detailed workflow functionality with more comprehensive examples.
    """
    print("Testing Detailed Workflow Functionality")
    print("="*60)
    
    # Create a mock browser controller and action execution framework
    browser_controller = MockBrowserController()
    framework = ActionExecutionFramework(browser_controller)
    
    # Create the workflow engine
    workflow_engine = AdvancedWorkflowEngine(framework)
    
    print("1. Creating an email signup workflow")
    
    # Create a more complex workflow: navigate → fill form → submit → verify
    signup_template = (WorkflowBuilder()
        .create_template("Email Signup Workflow", "Automates email signup process")
        .add_action_node(
            "Navigate to signup page",
            BrowserAction(
                id="nav_signup",
                type=ActionType.NAVIGATE,
                value="https://example.com/signup"
            )
        )
        .add_delay_node("Wait for page load", 1)
        .add_action_node(
            "Fill name field",
            BrowserAction(
                id="fill_name",
                type=ActionType.TYPE,
                element=ElementSelector(type="css", value="input[name='name']"),
                value="John Doe"
            )
        )
        .add_action_node(
            "Fill email field",
            BrowserAction(
                id="fill_email",
                type=ActionType.TYPE,
                element=ElementSelector(type="css", value="input[name='email']"),
                value="john@example.com"
            )
        )
        .add_action_node(
            "Click signup button",
            BrowserAction(
                id="click_signup",
                type=ActionType.CLICK,
                element=ElementSelector(type="css", value="button[type='submit']")
            )
        )
        .add_delay_node("Wait for response", 2)
        .add_action_node(
            "Verify signup success",
            ExtractAction(
                id="verify_success",
                method=ExtractMethod.TEXT_CONTENT,
                element=ElementSelector(type="css", value=".success-message")
            )
        )
        .build())
    
    # Connect nodes properly
    for i in range(len(signup_template.nodes) - 1):
        signup_template.nodes[i].next_node_id = signup_template.nodes[i + 1].id
    
    signup_registration = workflow_engine.register_template(signup_template)
    print(f"   Signup template registration: {signup_registration}")
    
    # Create and execute the signup workflow
    signup_instance_id = workflow_engine.create_instance(signup_template.id)
    print(f"   Created signup instance: {signup_instance_id}")
    
    signup_result = await workflow_engine.execute_workflow(signup_instance_id)
    print(f"   Signup workflow execution: {signup_result.success}")
    print(f"   Execution time: {signup_result.execution_time:.2f}s")
    print(f"   Number of results: {len(signup_result.results)}")
    
    print("\n2. Creating a data scraping workflow with conditionals")
    
    # Create a workflow that extracts data and processes it conditionally
    scraping_template = (WorkflowBuilder()
        .create_template("Data Scraping Workflow", "Scrapes data and processes conditionally")
        .add_action_node(
            "Navigate to data page",
            BrowserAction(
                id="nav_data",
                type=ActionType.NAVIGATE,
                value="https://example.com/data"
            )
        )
        .add_action_node(
            "Extract product count",
            ExtractAction(
                id="extract_count",
                method=ExtractMethod.TEXT_CONTENT,
                element=ElementSelector(type="css", value=".product-count")
            )
        )
        .add_delay_node("Small delay", 1)
        .build())
    
    # Connect scraping workflow nodes
    for i in range(len(scraping_template.nodes) - 1):
        scraping_template.nodes[i].next_node_id = scraping_template.nodes[i + 1].id
    
    scraping_registration = workflow_engine.register_template(scraping_template)
    print(f"   Scraping template registration: {scraping_registration}")
    
    # Execute the scraping workflow
    scraping_instance_id = workflow_engine.create_instance(scraping_template.id)
    print(f"   Created scraping instance: {scraping_instance_id}")
    
    scraping_result = await workflow_engine.execute_workflow(scraping_instance_id)
    print(f"   Scraping workflow execution: {scraping_result.success}")
    print(f"   Execution time: {scraping_result.execution_time:.2f}s")
    
    print("\n3. Testing workflow variables functionality")
    
    # Create a workflow that demonstrates variable usage
    var_template = (WorkflowBuilder()
        .create_template("Variable Usage Workflow", "Demonstrates variable usage in workflows")
        .add_action_node(
            "Set initial value",
            BrowserAction(
                id="set_initial",
                type=ActionType.NAVIGATE,
                value="about:blank"
            )
        )
        .build())
    
    # Manually set up variable handling
    for node in var_template.nodes:
        if node.type == WorkflowNodeType.ACTION:
            node.metadata = {'store_result_in': 'initial_step_result'}
    
    var_registration = workflow_engine.register_template(var_template)
    print(f"   Variable workflow registration: {var_registration}")
    
    # Create instance with initial variables and execute
    var_instance_id = workflow_engine.create_instance(
        var_template.id, 
        {"user_name": "Test User", "target_url": "https://example.com"}
    )
    var_result = await workflow_engine.execute_workflow(var_instance_id)
    
    print(f"   Variable workflow execution: {var_result.success}")
    print(f"   Initial variables: {{user_name: 'Test User', target_url: 'https://example.com'}}")
    print(f"   Final variables: {dict(var_result.final_variables)}")
    
    print("\n4. Summary of all templates and their usage")
    
    total_nodes = 0
    total_workflows = len(workflow_engine.templates)
    
    for template_id, template in workflow_engine.templates.items():
        print(f"   - {template.name}: {len(template.nodes)} nodes")
        total_nodes += len(template.nodes)
    
    print(f"\n   Total workflows: {total_workflows}")
    print(f"   Total nodes across all workflows: {total_nodes}")
    
    print("\n" + "="*60)
    print("Detailed workflow functionality test completed!")


async def main():
    await test_detailed_workflow()


if __name__ == "__main__":
    asyncio.run(main())