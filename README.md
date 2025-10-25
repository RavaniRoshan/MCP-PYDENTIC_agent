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

## Getting Started

### Prerequisites

*   Python 3.10+
*   Node.js 16+
*   Poetry
*   Docker

### Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/AutomateAI-Agent.git
    cd AutomateAI-Agent
    ```
2.  **Install backend dependencies:**
    ```bash
    cd MCP_SERVER
    poetry install
    ```
3.  **Install frontend dependencies:**
    ```bash
    cd frontend
    npm install
    ```
4.  **Set up environment variables:**
    Create a `.env` file in the `MCP_SERVER` directory and add the following:
    ```
    GEMINI_API_KEY=your_api_key
    ```
5.  **Run the application:**
    ```bash
    cd ..
    poetry run uvicorn main:app --reload
    ```
    In a separate terminal, run the frontend:
    ```bash
    cd frontend
    npm start
    ```

## Usage

1.  Open your browser and navigate to `http://localhost:3000`.
2.  Use the chat interface to enter a prompt for a web task. For example:
    *   "Navigate to https://example.com"
    *   "Click on the 'More information...' link"
    *   "Type 'hello world' into the search bar"
3.  The agent will process your request and execute the task in a new browser window.
4.  You can monitor the task's progress in the chat interface.

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
