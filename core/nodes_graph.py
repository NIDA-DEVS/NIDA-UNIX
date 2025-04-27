from typing import TypedDict, List, Dict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_ollama import OllamaLLM
from langgraph.graph import START, END

class ChatState(TypedDict):
    messages: List[BaseMessage]
    command: str
    status: str
    context: Dict  

def generate_command(state: ChatState, llm: OllamaLLM):
    """Generate Linux command from user input"""
    messages = state["messages"]
    context = state.get("context", {})
    
    system_prompt = """You are a helpful Linux assistant. Convert requests into bash commands.
    Context of recent actions: {context}
    Request: {user_input}
    Generate only the command, no explanations."""
    
    prompt = system_prompt.format(
        context=str(context),
        user_input=messages[-1].content
    )
    
    response = llm.invoke(prompt)
    return {
        "command": response.strip(),
        "context": {
            **context,
            "last_command": response.strip(),
            "last_file": response.strip().split()[-1] if "touch" in response or "echo" in response else context.get("last_file")
        }
    }

def validate_command(state: ChatState):
    """Check if command is valid"""
    command = state["command"]
    if not command or command.startswith("echo 'Error"):
        return "invalid"
    return "valid"

def process_command(state: ChatState):
    """Process the valid command"""
    return {
        "command": state["command"],
        "status": "completed",
        "context": state.get("context", {})  
    }