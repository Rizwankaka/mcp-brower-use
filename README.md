# Advanced MCP Agent Streamlit App

A modern Streamlit application demonstrating the capabilities of the MCPAgent with built-in conversation memory.

## Features

- 🤖 Interactive chat interface with the MCPAgent
- 🧠 Built-in conversation memory for contextual interactions
- 🌐 Web browsing and search capabilities
- 🔄 Model selection from available models
- 📱 Responsive design with modern UI

## Setup and Installation

1. Make sure you have Python 3.11 or newer installed
2. Install dependencies:

```bash
pip install -e .
```

Or using uv:

```bash
uv pip install -e .
```

3. Set up your environment variables in `.env` file:

```
GROQ_API_KEY=your_api_key_here
```

## Running the App

To run the Streamlit app:

```bash
streamlit run app.py
```

## Configuration

The app uses the `browser_mcp.json` file for configuration. You can modify the available models and other settings in this file.

## Notes

- The app uses Streamlit's session state to maintain the conversation history during the session
- The agent is initialized when the app starts, which may take a few seconds
- You can start a new conversation at any time using the "New Conversation" button in the sidebar
