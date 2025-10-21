# AutomateAI - The First AI That Works the Web For You. Hands-Free.

AutomateAI is a browser-native assistant that uses a state-of-the-art vision-language model to understand any web interface and perform tasks based on your simple English instructions.

## Project Structure

```
MCP_SERVER/
├── agents/
│   └── automateai_agent.py      # Core AI agent implementation
├── core/
│   ├── config.py                # Application settings
│   ├── browser_controller.py    # Browser controller interface
│   ├── playwright_controller.py # Playwright-based controller
│   └── safety.py                # Safety validation and logging
├── models/
│   ├── user_input.py            # User prompt and request models
│   ├── browser_action.py        # Browser action models
│   ├── state.py                 # Browser state models
│   └── response.py              # Response models
├── utils/
│   └── browser_init.py          # Browser initialization utilities
├── main.py                      # MCP server entry point
├── requirements.txt             # Dependencies
├── test_*.py                    # Test files
└── __init__.py                  # Package initialization
```

## Features

- **Pydantic-based validation**: All inputs and outputs are strictly validated
- **MCP Server**: REST API for handling user prompts and executing tasks
- **Browser Automation**: Playwright-based browser control with mock fallback
- **Safety-First Design**: Comprehensive validation of prompts, actions, and plans
- **Extensible Architecture**: Easy to add new action types and capabilities

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install
```

3. Set up your environment variables (see `.env` file)

## Usage

Run the server:
```bash
python main.py
```

The server will start at `http://127.0.0.1:8000` by default.

## Safety Features

AutomateAI includes comprehensive safety measures:

- Prompt validation to detect malicious intent
- Action validation to prevent unsafe operations
- Plan validation to ensure execution safety
- User confirmation for sensitive operations
- Audit logging for all actions

## API Endpoints

- `POST /prompt` - Submit a user prompt for processing
- `POST /execute` - Execute a specific browser action
- `GET /observe` - Get current browser state
- `GET /tasks/{id}` - Get status of a specific task
- `GET /tasks` - Get all active tasks

## Development

The project follows a safety-first design philosophy. All new features should include appropriate safety validations before implementation.