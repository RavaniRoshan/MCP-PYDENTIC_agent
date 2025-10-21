# AutomateAI Agent

**Tagline:** The First AI That Works the Web For You. Hands-Free.

## Mission

Build a browser-native AI assistant that uses vision-language models to understand web interfaces and perform tasks based on simple English instructions.

## Overview

AutomateAI is a hobbyist project to create an AI assistant that can automate web tasks. It uses a vision-language model to understand and interact with web pages, allowing users to give instructions in plain English. The project is open for contributions.

## Core Architecture

*   **MCP (Model Context Protocol) Server:** The core server that handles communication between the AI model and the browser.
*   **Pydantic-based data validation:** Ensures data integrity and validation.
*   **Browser automation engine:** Uses Playwright for robust browser automation.
*   **Vision-language AI integration:** Leverages the Gemini 2.5 Computer Use API for understanding web interfaces.
*   **Safety-first design principles:** Prioritizes user safety with features like action validation and permission controls.

## Development Phases

The project is divided into the following development phases:

1.  **Foundation:** Setting up the core infrastructure, including the MCP server and browser automation.
2.  **AI Integration & Backend:** Integrating the vision-language model and building the backend logic.
3.  **Frontend Development:** Creating a user-friendly interface for interacting with the AI assistant.
4.  **Core Automation Features:** Implementing key automation features like data extraction and form filling.
5.  **Suggested Automations & Use Cases:** Providing users with pre-built automation suggestions and templates.
6.  **Safety & Security:** Enhancing the safety and security features of the assistant.
7.  **Validation & Testing:** Thoroughly testing the application before deployment.

## Technical Stack

### Backend

*   Python 3.10+
*   FastAPI
*   Pydantic
*   Playwright
*   Asyncio
*   Redis
*   PostgreSQL

### Frontend

*   React 18+ with TypeScript
*   Tailwind CSS
*   Socket.io
*   React Query
*   React Router

### Infrastructure

*   Docker
*   Docker Compose
*   Nginx
*   Let's Encrypt

## How to Contribute

This is a hobby project and we welcome contributions from the community. If you're interested in contributing, please feel free to fork the repository and submit a pull request.

## License

This project is not yet licensed.
