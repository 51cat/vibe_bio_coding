import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterator
from langchain_openai import ChatOpenAI

class LLM:
    """LLM wrapper class for managing model configuration and initialization."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """Initialize LLM with config file or explicit parameters.
        
        Args:
            config_path: Path to config JSON file.
            model: Model name (overrides config).
            temperature: Temperature value (overrides config).
            api_key: API key (overrides config).
            base_url: API base URL (overrides config).
        """
        config = self._load_config(config_path)
        llm_config = config.get("llm", {})
        
        self.model = model or llm_config.get("model", "gpt-4")
        self.temperature = temperature if temperature is not None else llm_config.get("temperature", 0.7)
        self.api_key = api_key or llm_config.get("api_key")
        self.base_url = base_url or llm_config.get("base_url")
        
        self._client = None
        self._stream_client = None
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                return json.load(f)
        return {}
    
    @property
    def client(self) -> ChatOpenAI:
        """Get or create ChatOpenAI client."""
        if self._client is None:
            kwargs = {
                "model": self.model,
                "temperature": self.temperature,
            }
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            
            self._client = ChatOpenAI(**kwargs)
        return self._client
    
    @property
    def stream_client(self) -> ChatOpenAI:
        """Get or create streaming ChatOpenAI client."""
        if self._stream_client is None:
            kwargs = {
                "model": self.model,
                "temperature": self.temperature,
                "streaming": True,
            }
            if self.api_key:
                kwargs["api_key"] = self.api_key
            if self.base_url:
                kwargs["base_url"] = self.base_url
            
            self._stream_client = ChatOpenAI(**kwargs)
        return self._stream_client
    
    def invoke(self, messages: List[Dict[str, str]]) -> Any:
        """Invoke the LLM with messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
        
        Returns:
            LLM response.
        """
        return self.client.invoke(messages)
    
    def stream(self, messages: List[Dict[str, str]]) -> Iterator[str]:
        """Stream LLM response token by token.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
        
        Yields:
            Token strings from the LLM.
        """
        for chunk in self.stream_client.stream(messages):
            content = chunk.content
            if content:
                if isinstance(content, str):
                    yield content
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            yield item["text"]
                        elif isinstance(item, str):
                            yield item
    
    def print_stream(
        self,
        messages: List[Dict[str, str]],
        prefix: str = "",
        color: str = "green"
    ) -> str:
        """Stream LLM response and print to console with formatting.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'.
            prefix: Prefix to print before each line.
            color: Color for output (green, blue, yellow, red, cyan, white).
        
        Returns:
            Complete response text.
        """
        colors = {
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "red": "\033[91m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m",
        }
        
        color_code = colors.get(color, colors["green"])
        reset_code = colors["reset"]
        
        full_response = []
        
        if prefix:
            print(f"{color_code}{prefix}{reset_code}", end="", flush=True)
        
        for token in self.stream(messages):
            print(f"{color_code}{token}{reset_code}", end="", flush=True)
            full_response.append(token)
        
        print()
        
        return "".join(full_response)
    
    @classmethod
    def from_config(cls, config_path: str) -> "LLM":
        """Create LLM instance from config file.
        
        Args:
            config_path: Path to config JSON file.
        
        Returns:
            LLM instance.
        """
        return cls(config_path=config_path)


def get_default_config_path() -> str:
    """Get default config path (config_base.json in agents directory)."""
    agents_dir = Path(__file__).parent.parent
    return str(agents_dir / "config_base.json")
