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
    
    def generate_command(self, prompt: str):
        config = {
            "messages": [HumanMessage(content=prompt)],  
            "command": "",
            "status": "",
            "context": self.context  
        }
        result = self.graph.invoke(config)
        self.context = result.get("context", {})
        return result.get("command")

_processor = None

def generate_command(prompt: str, config: dict):
    global _processor
    if _processor is None:
        _processor = CommandProcessor(config)
    return _processor.generate_command(prompt)