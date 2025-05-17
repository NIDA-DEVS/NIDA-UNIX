from langchain_ollama import OllamaLLM
from core.api_client import LLMClient
from langgraph.graph import StateGraph, START, END
from core.nodes_graph import ChatState, generate_command, validate_command, process_command

def create_command_graph(provider: str, **kwargs) -> StateGraph:
    workflow = StateGraph(ChatState)
    
    llm = LLMClient.get_llm(provider, **kwargs)
    workflow.add_node("generate", lambda x: generate_command(x, llm))
    workflow.add_node("process", process_command)
    workflow.add_edge(START, "generate")
    workflow.add_conditional_edges(
        "generate",
        validate_command,
        {
            "valid": "process",
            "invalid": END
        }
    )
    workflow.add_edge("process", END)

    return workflow.compile()