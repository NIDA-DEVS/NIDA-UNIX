from typing import TypedDict, List, Dict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import OllamaLLM
from langgraph.graph import START, END
from langchain_core.output_parsers import StrOutputParser

class ChatState(TypedDict):
    messages: List[BaseMessage]
    command: str
    status: str
    context: Dict  

def get_response_content(response) -> str:
    """Extract content from different types of LLM responses"""
    if hasattr(response, 'content'):
        return response.content
    return str(response)

def generate_command(state: ChatState, llm: OllamaLLM):
    """Generate Linux command from user input using LangChain Output Parser"""
    messages = state["messages"]
    context = state.get("context", {})

    system_prompt = """You are a helpful Linux assistant. Convert requests into bash commands.

    Context of recent actions: {context}
    Request: {user_input}
    Generate only the command without any leading or ending '`'. Do not paas any '$' pr anything other than the command, no explanations."""

    prompt = system_prompt.format(
        context=str(context),
        user_input=messages[-1].content
    )

    parser = StrOutputParser()
    response = llm.invoke(prompt)
    cleaned_response = get_response_content(response)
    command = parser.parse(cleaned_response)

    return {
        "command": command.strip(),
        "context": {
            **context,
            "last_command": command.strip(),
            "last_file": command.strip().split()[-1] if "touch" in command or "echo" in command else context.get("last_file")
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