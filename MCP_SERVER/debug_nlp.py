import asyncio
from models import UserPrompt
from ai_services.natural_language import NaturalLanguageProcessor, IntentType


async def debug_nlp_type():
    """
    Debug the TYPE intent extraction
    """
    nlp = NaturalLanguageProcessor()
    
    # Test the specific pattern that's not working
    test_prompt = "Type 'hello world' into the search box"
    
    print(f"Testing: {test_prompt}")
    
    user_prompt = UserPrompt(
        prompt=test_prompt,
        priority="normal",
        timeout=60
    )
    
    # Check patterns in our intents
    print("Type patterns:", nlp.intents_patterns[IntentType.TYPE])
    
    # Process step by step
    text = user_prompt.prompt.lower().strip()
    print(f"Processed text: {text}")
    
    for pattern in nlp.intents_patterns[IntentType.TYPE]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            print(f"Pattern '{pattern}' matched with groups: {match.groups()}")
            break
    
    # Process with NLP module
    result = await nlp.process_prompt(user_prompt)
    
    print(f"Intent: {result.intent}")
    print(f"Target: {result.target}")
    print(f"Value: {result.value}")
    print(f"Action Type: {result.action_type}")
    
    # Generate browser action
    action = await nlp.generate_browser_action(result)
    print(f"Generated Action: {action}")


if __name__ == "__main__":
    import re
    asyncio.run(debug_nlp_type())