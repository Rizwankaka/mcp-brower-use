"""
Advanced Streamlit app using MCPAgent with built-in conversation memory.

This app demonstrates how to use the MCPAgent with its built-in
conversation history capabilities for better contextual interactions in a
modern Streamlit interface.

Special thanks to https://github.com/microsoft/playwright-mcp for the server.
"""

import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from mcp_use import MCPAgent, MCPClient
from streamlit_chat import message
import json
import atexit

# App configuration and styling
st.set_page_config(
    page_title="Advanced MCP Agent Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7f9;
    }
    .chat-container {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        min-height: 300px;
    }
    .stButton>button {
        background-color: #4e54c8;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #3a3f9e;
    }
    .stMarkdown {
        color: #333333;
    }
    .stChatMessage {
        background-color: #f0f2f6;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        color: #333333;
    }
    .stChatMessage.user {
        background-color: #e6f7ff;
    }
    /* Make message text clearly visible */
    div[data-testid="stChatMessageContent"] p {
        color: #333333 !important;
        font-size: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# Load environment variables
load_dotenv()

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = None
if "client" not in st.session_state:
    st.session_state.client = None

async def initialize_agent():
    """Initialize the MCP client and agent"""
    try:
        # Config file path - change this to your config file
        config_file = "browser_mcp.json"
        
        # Create MCP client and agent with memory enabled
        client = MCPClient.from_config_file(config_file)
        
        # Get the selected model from session state
        model = st.session_state.selected_model
        
        # Create the LLM
        if "groq" in model:
            llm = ChatGroq(model=model)
        else:
            # Add support for other providers as needed
            llm = ChatGroq(model="qwen-qwq-32b")  # Default fallback
        
        # Create agent with memory enabled
        agent = MCPAgent(
            llm=llm,
            client=client,
            max_steps=15,
            memory_enabled=True,
        )
        
        return client, agent
    except Exception as e:
        st.error(f"Error initializing agent: {str(e)}")
        return None, None

@st.cache_data
def load_models():
    """Load available models from configuration"""
    try:
        with open("browser_mcp.json", "r") as f:
            config = json.load(f)
            return config.get("models", ["qwen-qwq-32b"])
    except:
        return ["qwen-qwq-32b", "llama3-8b-8192", "llama3-70b-8192"]

# Sidebar for settings
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Model selection
    available_models = load_models()
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = available_models[0]
    
    selected_model = st.selectbox(
        "Select a model:",
        options=available_models,
        index=available_models.index(st.session_state.selected_model),
        key="model_selector"
    )
    st.session_state.selected_model = selected_model
    
    # Session management
    st.subheader("Session Management")
    if st.button("New Conversation"):
        st.session_state.messages = []
        if st.session_state.agent:
            st.session_state.agent.clear_conversation_history()
    
    # About section
    st.markdown("---")
    st.subheader("About")
    st.markdown("""
    This app demonstrates the capabilities of the MCPAgent with built-in conversation
    memory for contextual interactions.
    
    The agent can browse the web, search for information, and maintain
    context throughout the conversation.
    """)

# Main app container
st.title("🤖 Advanced MCP Agent Chat")
st.markdown("Ask questions, request web searches, or have the agent perform tasks for you!")

# Initialize the agent when needed
if st.session_state.agent is None or st.session_state.client is None:
    with st.spinner("Initializing agent..."):
        st.session_state.client, st.session_state.agent = asyncio.run(initialize_agent())
    if st.session_state.agent:
        st.success("Agent initialized successfully!")
    else:
        st.error("Failed to initialize agent. Please check your configuration.")

# Display chat messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
if len(st.session_state.messages) == 0:
    st.info("Send a message to start the conversation!")
else:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            message(msg["content"], is_user=True, key=f"user_{i}")
        else:
            message(msg["content"], is_user=False, key=f"ai_{i}")
st.markdown('</div>', unsafe_allow_html=True)

# Chat input
with st.container():
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response from agent
        with st.spinner("Thinking..."):
            try:
                if st.session_state.agent:
                    # Run the agent with the user input
                    response = asyncio.run(st.session_state.agent.run(user_input))
                    
                    # Add agent response to chat
                    st.session_state.messages.append({"role": "assistant", "content": response})
                else:
                    st.error("Agent is not initialized. Please try restarting the app.")
                
                # Force a rerun to update the chat display
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Clean up function for app shutdown
def cleanup():
    if "client" in st.session_state and st.session_state.client and st.session_state.client.sessions:
        asyncio.run(st.session_state.client.close_all_sessions())

# Register the cleanup function with atexit
atexit.register(cleanup)