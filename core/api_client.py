from langchain_groq import ChatGroq
from langchain_ollama import OllamaLLM
from typing import Union, Tuple

class LLMClient:
    DEFAULT_GROQ_MODEL = "llama3-8b-8192" 
    
    @staticmethod
    def validate_groq_key(api_key: str) -> Tuple[bool, str]:
        """Validate Groq API key by attempting to create a client"""
        try:
            client = ChatGroq(
                api_key=api_key,
                model=LLMClient.DEFAULT_GROQ_MODEL
            )
            response = client.invoke("test")
            if response:
                return True, "API key is valid"
            return False, "Could not validate API key"
        except Exception as e:
            if "authentication" in str(e).lower():
                return False, "Invalid API key"
            elif "quota" in str(e).lower():
                return False, "API quota exceeded"
            return False, f"API error: {str(e)}"
        
    @staticmethod
    def get_llm(provider: str, **kwargs) -> Union[OllamaLLM, ChatGroq]:
        if provider == "ollama":
            return OllamaLLM(model=kwargs.get("model_name", "llama2"))
        elif provider == "groq":
            return ChatGroq(
                api_key=kwargs.get("api_key"),
                model_name=LLMClient.DEFAULT_GROQ_MODEL
            )
        raise ValueError(f"Unsupported provider: {provider}")