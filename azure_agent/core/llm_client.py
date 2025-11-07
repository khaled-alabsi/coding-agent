"""LLM client wrapper supporting both Azure OpenAI and local LLM."""
from openai import OpenAI, AzureOpenAI
from typing import List, Dict, Any, Optional, TYPE_CHECKING
from ..config import AgentConfig

if TYPE_CHECKING:
    from ..utils.logger import AgentLogger


class LLMClient:
    """Unified client for Azure OpenAI and local LLM."""

    def __init__(self, config: AgentConfig, logger: Optional['AgentLogger'] = None):
        """
        Initialize LLM client.

        Args:
            config: Agent configuration
            logger: Optional logger for tracking LLM interactions
        """
        self.config = config
        self.logger = logger
        self.client = self._initialize_client()

    def _initialize_client(self):
        """Initialize the appropriate LLM client based on configuration."""
        if self.config.use_local_llm:
            print(f"🏠 Using Local LLM")
            print(f"   API Base: {self.config.local_api_base}")
            print(f"   Model: {self.config.local_model}")

            return OpenAI(
                api_key="lm-studio",
                base_url=self.config.local_api_base
            )
        else:
            if not all([
                self.config.azure_api_key,
                self.config.azure_endpoint,
                self.config.azure_deployment
            ]):
                raise ValueError(
                    "Missing Azure OpenAI configuration. Set:\n"
                    "- AZURE_OPENAI_API_KEY\n"
                    "- AZURE_OPENAI_ENDPOINT\n"
                    "- AZURE_OPENAI_DEPLOYMENT\n"
                    "\nOr use use_local_llm=True"
                )

            print(f"☁️  Using Azure OpenAI")
            print(f"   Endpoint: {self.config.azure_endpoint}")
            print(f"   Deployment: {self.config.azure_deployment}")

            return AzureOpenAI(
                api_key=self.config.azure_api_key,
                api_version=self.config.azure_api_version,
                azure_endpoint=self.config.azure_endpoint
            )

    @property
    def model_name(self) -> str:
        """Get the model name for API calls."""
        if self.config.use_local_llm:
            return self.config.local_model
        return self.config.azure_deployment

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None,
        agent_name: str = "unknown"
    ) -> str:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            system_message: Optional system message to prepend
            agent_name: Name of the agent making the request (for logging)

        Returns:
            Assistant's response content
        """
        # Prepare messages
        api_messages = []
        if system_message:
            api_messages.append({"role": "system", "content": system_message})
        api_messages.extend(messages)

        # Use config defaults if not specified
        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        # Log the request
        request_id = None
        if self.logger:
            request_id = self.logger.log_llm_request(
                agent_name=agent_name,
                messages=messages,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            response_content = response.choices[0].message.content

            # Log the response
            if self.logger and request_id:
                tokens_used = getattr(response.usage, 'total_tokens', None) if hasattr(response, 'usage') else None
                self.logger.log_llm_response(
                    request_id=request_id,
                    agent_name=agent_name,
                    response=response_content,
                    tokens_used=tokens_used
                )

            return response_content
        except Exception as e:
            raise RuntimeError(f"Error calling LLM: {str(e)}")

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_message: Optional[str] = None
    ):
        """
        Stream a chat completion request.

        Args:
            messages: List of message dicts
            temperature: Override default temperature
            max_tokens: Override default max tokens
            system_message: Optional system message to prepend

        Yields:
            Response chunks
        """
        api_messages = []
        if system_message:
            api_messages.append({"role": "system", "content": system_message})
        api_messages.extend(messages)

        temperature = temperature if temperature is not None else self.config.temperature
        max_tokens = max_tokens if max_tokens is not None else self.config.max_tokens

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise RuntimeError(f"Error streaming from LLM: {str(e)}")
