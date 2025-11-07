"""Configuration settings for the agent system."""
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """Configuration for the multi-agent system."""

    # Paths
    project_dir: Path = Path(__file__).parent.parent
    output_dir: Path = project_dir / "output"
    history_file: Path = project_dir / "agent_history.json"
    prompt_file: Path = project_dir / "prompt.md"

    # LLM Configuration
    use_local_llm: bool = False

    # Azure OpenAI
    azure_api_key: Optional[str] = None
    azure_endpoint: Optional[str] = None
    azure_deployment: Optional[str] = None
    azure_api_version: str = "2024-02-15-preview"

    # Local LLM
    local_api_base: str = "http://localhost:1234/v1"
    local_model: str = "local-model"

    # Generation parameters
    context_window: int = 8000
    max_tokens: int = 2000
    temperature: float = 0.7

    # Agent settings
    max_iterations: int = 50
    max_retry_attempts: int = 3

    # Timeouts
    command_timeout: int = 300  # 5 minutes
    inactivity_timeout: Optional[int] = None
    auto_save_interval: int = 30

    def __post_init__(self):
        """Load environment variables and ensure directories exist."""
        # Load from environment if not set
        if not self.use_local_llm:
            self.azure_api_key = self.azure_api_key or os.getenv("AZURE_OPENAI_API_KEY")
            self.azure_endpoint = self.azure_endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
            self.azure_deployment = self.azure_deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        else:
            self.local_api_base = os.getenv("LOCAL_LLM_API_BASE", self.local_api_base)
            self.local_model = os.getenv("LOCAL_LLM_MODEL", self.local_model)

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_dict(cls, config_dict: dict) -> 'AgentConfig':
        """Create config from dictionary."""
        return cls(**{k: v for k, v in config_dict.items() if k in cls.__annotations__})
