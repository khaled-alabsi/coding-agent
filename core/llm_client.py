"""LLM client wrapper supporting both Azure OpenAI and local LLM."""
from openai import OpenAI, AzureOpenAI
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from config import AgentConfig
from utils import play_truncation_sound, play_fix_attempt_sound

if TYPE_CHECKING:
    from utils.logger import AgentLogger


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
                max_tokens=max_tokens,
                model=self.model_name,
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            response_content = response.choices[0].message.content

            # Detect truncation if enabled
            if self.config.truncation_detection_enabled:
                truncation_info = self._detect_truncation(response, max_tokens, agent_name, response_content)

                # Auto-fix if truncation detected
                if truncation_info['truncated'] and self.config.auto_fix_truncation:
                    response_content = self._handle_truncation(
                        truncation_info,
                        api_messages,
                        system_message,
                        temperature,
                        max_tokens,
                        agent_name
                    )

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

    def _detect_truncation(
        self,
        response: Any,
        max_tokens: int,
        agent_name: str,
        response_text: str
    ) -> Dict[str, Any]:
        """
        Detect if response was truncated using Response Ending Analysis (Method 2).

        Args:
            response: LLM response object
            max_tokens: Maximum tokens allowed
            agent_name: Name of the agent
            response_text: Response content

        Returns:
            Dict with truncation info
        """
        truncated = False
        used_tokens = None

        # Get actual token usage if available
        if hasattr(response, 'usage') and hasattr(response.usage, 'completion_tokens'):
            used_tokens = response.usage.completion_tokens
            # Check token usage threshold
            if used_tokens >= max_tokens * self.config.truncation_threshold:
                truncated = True

        # Method 2: Response Ending Analysis (fallback if no usage info)
        if not truncated and not used_tokens:
            truncated = self._check_response_ending(response_text, agent_name)

        return {
            'truncated': truncated,
            'used_tokens': used_tokens,
            'max_tokens': max_tokens,
            'response_text': response_text,
            'agent_name': agent_name
        }

    def _check_response_ending(self, text: str, agent_name: str) -> bool:
        """
        Check if response ends naturally (Method 2: Response Ending Analysis).

        Args:
            text: Response text to check
            agent_name: Name of the agent

        Returns:
            True if response appears truncated
        """
        text = text.strip()

        # Agent-specific completion markers
        agent_markers = {
            'Coder': ['COMPLETE'],
            'Plan Enhancer': ['```\n```', '```'],
            'Planner': ['IMPLEMENTATION PHASE'],
            'Prompt Enhancer': ['.', '!', '?']
        }

        # Check for expected markers
        expected_markers = agent_markers.get(agent_name, [])
        if expected_markers:
            has_marker = any(marker in text for marker in expected_markers)
            if not has_marker:
                return True  # Missing expected marker, likely truncated

        # Check if ends with natural sentence ending
        natural_endings = ('.', '!', '?', '```', '}', ')', ']', '"', "'")
        if not text.endswith(natural_endings):
            return True  # Doesn't end naturally

        return False

    def _handle_truncation(
        self,
        truncation_info: Dict[str, Any],
        original_messages: List[Dict[str, str]],
        system_message: Optional[str],
        temperature: float,
        max_tokens: int,
        agent_name: str
    ) -> str:
        """
        Handle truncation using Strategy 1: Continuation Request.

        Args:
            truncation_info: Truncation detection info
            original_messages: Original message list
            system_message: System message
            temperature: Temperature setting
            max_tokens: Max tokens setting
            agent_name: Agent name

        Returns:
            Complete response (original + continuations)
        """
        # Play truncation sound
        play_truncation_sound()

        print(f"\n⚠️  TRUNCATION DETECTED!")
        print(f"   Agent: {agent_name}")
        if truncation_info['used_tokens']:
            print(f"   Used: {truncation_info['used_tokens']:,} / {max_tokens:,} tokens "
                  f"({truncation_info['used_tokens']/max_tokens*100:.1f}%)")
        else:
            print(f"   Response ending analysis indicates incomplete response")
        print(f"   Attempting auto-fix with continuation...")

        # Play fix attempt sound
        play_fix_attempt_sound()

        full_response = truncation_info['response_text']
        max_attempts = self.config.max_continuation_attempts

        for attempt in range(1, max_attempts + 1):
            print(f"\n🔄 Continuation attempt {attempt}/{max_attempts}...")

            # Build continuation messages
            continuation_messages = original_messages.copy()
            continuation_messages.append({
                "role": "assistant",
                "content": full_response
            })
            continuation_messages.append({
                "role": "user",
                "content": "Continue from where you left off. Complete the remaining content. Do not repeat what you already wrote."
            })

            # Prepare API messages
            api_messages = []
            if system_message:
                api_messages.append({"role": "system", "content": system_message})
            api_messages.extend(continuation_messages)

            try:
                # Request continuation
                continuation_response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=api_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                continuation_text = continuation_response.choices[0].message.content
                full_response += "\n" + continuation_text

                # Check if continuation is also truncated
                still_truncated = False
                if hasattr(continuation_response, 'usage') and hasattr(continuation_response.usage, 'completion_tokens'):
                    used = continuation_response.usage.completion_tokens
                    if used >= max_tokens * self.config.truncation_threshold:
                        still_truncated = True
                        print(f"   ⚠️  Continuation also truncated ({used:,} tokens)")
                else:
                    # Check ending
                    still_truncated = self._check_response_ending(continuation_text, agent_name)

                if not still_truncated:
                    print(f"   ✅ Successfully completed after {attempt} continuation(s)")
                    print(f"   Total response length: ~{len(full_response):,} chars")
                    return full_response

            except Exception as e:
                print(f"   ❌ Continuation attempt {attempt} failed: {e}")
                break

        # Failed after all attempts
        print(f"\n⚠️  Could not fully complete response after {max_attempts} continuation attempts")
        print(f"   Returning partial response (~{len(full_response):,} chars)")
        print(f"   💡 Consider increasing max_tokens in config (current: {max_tokens:,})")

        return full_response
