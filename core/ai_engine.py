from langchain_core.messages import HumanMessage
from core.command_graph import create_command_graph

class CommandProcessor:
    def __init__(self, config: dict):
        self.config = config
        self.graph = create_command_graph(
            provider=config["provider"],
            model_name=config.get("model_name"),
            api_key=config.get("api_key")
        )
        self.context = {}
    
    def generate_command(self, prompt: str) -> str:
        config = {
            "messages": [HumanMessage(content=prompt)],  
            "command": "",
            "status": "",
            "context": self.context  
        }
        
        result = self.graph.invoke(config)
        if result["status"] == "completed":
            self.context = result.get("context", {})
            return result["command"]
        return f"echo 'Error: Invalid command'"

_processor = None

def generate_command(prompt: str, model: str = "llama2") -> str:
    global _processor
    if _processor is None:
        _processor = CommandProcessor(model)
    return _processor.generate_command(prompt)