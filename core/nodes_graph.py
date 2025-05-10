from typing import TypedDict, List, Dict
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_ollama import OllamaLLM
from langgraph.graph import START, END
from langchain_core.output_parsers import JsonOutputParser
from core.multiple_command_model import CommandSequence
import os

os.environ["LANGCHAIN_API_KEY"] = "api-key"
os.environ["LANGSMITH_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = "AI_LINUX"
os.environ["LANGSMITH_TRACING"] = "true"

class ChatState(TypedDict):
    messages: List[BaseMessage]
    command: CommandSequence
    status: str
    context: Dict[str, any]

def get_response_content(response) -> str:
    """Extract content from different types of LLM responses"""
    if hasattr(response, 'content'):
        return response.content
    return str(response)

def generate_command(state: ChatState, llm: OllamaLLM):
    """Generate Linux commands in JSON format"""
    messages = state["messages"]
    context = state.get("context", {})
    print(f"Nodes graph entry: {context}")  

    command_history = context.get("command_history", [])
    if "last_sequence" in context:
        command_history.append({
            "instruction": messages[-2].content if len(messages) > 1 else "",
            "commands": context["last_sequence"]
        })
        command_history = command_history[-5:]
    
    system_prompt = '''You are a Linux command generator. Convert user requests into JSON-formatted command sequences.
    Previous commands history (for context):
    {history}
    Format your response EXACTLY as a JSON object with this structure:
    {{
        "commands": [
            {{
                "order": 1,
                "command": "actual command here",
                "needs_dir_change": 0,
                "needs_file_check": 0
            }}
        ],
        "total_commands": 1
    }}

    Rules:
    - Return ONLY the JSON, no other text
    - Order must start from 1
    - Split chained commands (using &&) into separate command entries
    - needs_dir_change must be 1 for cd commands, 0 otherwise
    - needs_file_check must be 1 for file operations, 0 otherwise
    - Each command must be a single, complete, executable bash command
    - DO NOT use &&, ||, or ; to chain commands - use separate entries instead

    Example:
    Instead of:
    "command": "touch file.txt && echo 'text' > file.txt"
    
    Use:
    "commands": [
        {{"order": 1, "command": "touch file.txt", "needs_dir_change": 0, "needs_file_check": 1}},
        {{"order": 2, "command": "echo 'text' > file.txt", "needs_dir_change": 0, "needs_file_check": 1}}
    ]

    Context: {context}
    Command History: {history}
    Request: {user_input}
    '''

    history_text = "\n".join([
        f"Instruction: {entry['instruction']}\n"
        f"Commands: {entry['commands']}"
        for entry in command_history
    ])

    prompt = system_prompt.format(
        context=str(context),
        history=history_text,
        user_input=messages[-1].content
    )

    parser = JsonOutputParser(pydantic_object=CommandSequence)
    response = llm.invoke(prompt)
    print(f"Nodes graph LLM response: {response}")  
    cleaned_response = get_response_content(response)
    print(f"Nodes graph Cleaned response: {cleaned_response}") 
    try:
        command_sequence = parser.parse(cleaned_response)
        print(f"Parsed command sequence: {command_sequence}")  
        return {
            "command": command_sequence,
            "context": {
                **context,
                "last_sequence": command_sequence,
                "command_history": command_history

            }
        }
    except Exception as e:
        print(f"Parsing error: {e}")  
        print(f"Raw response: {cleaned_response}")

        return {
            "command": "",
            "context": {
                **context,
                "command_history": command_history
            }
        }

def validate_command(state: ChatState):
    """Check if command sequence is valid"""
    command = state.get("command")
    print(f"Validating command: {command}")  
    
    if not command or not hasattr(command, "commands"):
        return "invalid"
        
    if not command.commands or len(command.commands) == 0:
        return "invalid"
        
    for cmd in command.commands:
        if not cmd.command or not isinstance(cmd.command, str):
            return "invalid"
            
        if cmd.command.startswith("echo 'Error"):
            return "invalid"
            
    return "valid"

def process_command(state: ChatState):
    """Process the valid command"""
    print(f"nodes graph Processing command: {state['command']}")  
    return {
        "command": state["command"],
        "status": "completed",
        "context": state.get("context", {})  
    }