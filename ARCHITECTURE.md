# AutomateAI Agent Architecture

## Overview

AutomateAI Agent is designed to be a browser-native AI assistant that uses vision-language models to perform tasks on web interfaces based on English instructions. The architecture is built around a few core components that work together to provide a seamless and powerful user experience.

## Core Components

The core architecture of AutomateAI Agent consists of the following components:

- **MCP (Model Context Protocol) Server:** The central nervous system of the assistant, responsible for handling communication between the AI model and the browser.
- **Pydantic-based Data Validation:** Ensures that all data flowing through the system is valid and well-structured.
- **Browser Automation Engine:** Uses Playwright to perform actions on web pages, such as clicking buttons, filling out forms, and navigating to different pages.
- **Vision-Language AI Integration:** Leverages the Gemini 2.5 Computer Use API to understand web interfaces and generate actions based on user instructions.

## MCP Server

The MCP Server is a FastAPI-based application that exposes a set of endpoints for interacting with the AI assistant. The key responsibilities of the MCP Server include:

- **Handling User Prompts:** Receiving user prompts and passing them to the AI model for processing.
- **Executing Browser Actions:** Receiving actions from the AI model and executing them using the browser automation engine.
- **Observing Browser State:** Capturing the state of the browser, including the DOM and screenshots, and passing it to the AI model.
- **Safety Validation:** Ensuring that all actions are safe and do not violate user permissions.
- **Session Management:** Managing user sessions and ensuring that they are isolated from each other.

## Pydantic Models

Pydantic is used throughout the system to define and validate data models. This ensures that all data is consistent and well-structured, which helps to prevent errors and improve the overall reliability of the system. The key Pydantic models used in the system include:

- **User Input Models:** Models for representing user prompts, task requests, and safety preferences.
- **Browser Action Models:** Models for representing browser actions, such as clicking, typing, and navigating.
- **State Models:** Models for representing the state of the browser, task execution plans, and action results.
- **Response Models:** Models for representing responses from the system, including task responses, action responses, and error responses.

## Browser Automation Engine

The browser automation engine is responsible for performing actions on web pages. It uses Playwright to interact with the browser, which provides a robust and reliable way to automate web tasks. The key features of the browser automation engine include:

- **Cross-Browser Support:** Supports all major web browsers, including Chrome, Firefox, and Safari.
- **Headless Mode:** Can run in headless mode, which is useful for running tests and automating tasks in the background.
- **Rich Set of APIs:** Provides a rich set of APIs for interacting with web pages, including clicking, typing, and navigating.

## Vision-Language AI Integration

The vision-language AI integration is responsible for understanding web interfaces and generating actions based on user instructions. It uses the Gemini 2.5 Computer Use API to process user prompts and generate a sequence of actions that can be executed by the browser automation engine. The key features of the vision-language AI integration include:

- **Natural Language Processing:** Can understand natural language instructions and translate them into actions.
- **Visual Understanding:** Can understand the visual layout of web pages and identify elements that can be interacted with.
- **Action Generation:** Can generate a sequence of actions that can be executed by the browser automation engine to complete a task.

## Technical Stack

The technical stack used in AutomateAI Agent is as follows:

- **Backend:** Python, FastAPI, Pydantic, Playwright, Asyncio, Redis, PostgreSQL
- **Frontend:** React, TypeScript, Tailwind CSS, Socket.io, React Query, React Router
- **Infrastructure:** Docker, Docker Compose, Nginx, Let's Encrypt
