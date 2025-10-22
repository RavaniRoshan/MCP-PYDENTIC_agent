import asyncio
from models import UserPrompt
from ai_services.natural_language import NaturalLanguageProcessor, IntentType
from ai_services.vision_language import VisionLanguageProcessor


async def test_nlp_module():
    """
    Tests the natural language processing module.

    This function initializes a NaturalLanguageProcessor and a
    VisionLanguageProcessor, and then tests various user prompts to ensure that
    intents, entities, and actions are correctly identified.
    """
    print("Testing Natural Language Processing Module")
    print("="*50)
    
    nlp = NaturalLanguageProcessor()
    vlp = VisionLanguageProcessor()
    
    test_prompts = [
        "Navigate to https://example.com",
        "Click on the search button",
        "Type 'hello world' into the search box",
        "Extract the title from this page",
        "Schedule this task for tomorrow at 3 PM",
        "Monitor this website for any changes"
    ]
    
    for prompt_text in test_prompts:
        print(f"\nTesting prompt: '{prompt_text}'")
        
        user_prompt = UserPrompt(
            prompt=prompt_text,
            priority="normal",
            timeout=60
        )
        
        # Process with NLP module
        result = await nlp.process_prompt(user_prompt)
        
        print(f"  Intent: {result.intent}")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Action Type: {result.action_type}")
        print(f"  Target: {result.target}")
        print(f"  Value: {result.value}")
        
        if result.entities:
            print(f"  Entities: {[(e.text, e.label) for e in result.entities]}")
        
        # Generate browser action
        action = await nlp.generate_browser_action(result)
        if action:
            print(f"  Generated Action: {action.type} - {action.description}")
        else:
            print(f"  Generated Action: None")
    
    print("\n" + "="*50)
    print("Testing Vision-Language Processing")
    
    # Test vision-language processing with a mock browser state
    from models import BrowserState
    
    mock_state = BrowserState(
        url="https://example.com",
        title="Example Domain",
        dom_content="<html><body><input type='text' id='search'>"
    )
    
    test_vl_prompt = UserPrompt(
        prompt="Find the search box and type 'test' into it",
        priority="normal",
        timeout=60
    )
    
    # Note: This will fail without API key but will show the structure
    try:
        plan = await vlp.process_user_request(test_vl_prompt, mock_state)
        print(f"Vision-language plan created with {len(plan.actions)} actions")
        for i, action in enumerate(plan.actions):
            print(f"  Action {i+1}: {action.type} - {action.description}")
    except Exception as e:
        print(f"Vision-language processing (expected to fail without API key): {e}")


if __name__ == "__main__":
    asyncio.run(test_nlp_module())