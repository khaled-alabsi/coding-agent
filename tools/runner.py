"""Tool runner and parser for coder-invoked tools.

Centralizes parsing, dispatch, and optional snapshotting of tool calls.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from config import AgentConfig
from tools.prompt_tools import enhance_prompt, create_plan, enhance_plan


ToolFunc = Callable[["LLMClient", AgentConfig, str], str]


class ToolRunner:
    """Parses and executes tool calls embedded in model responses.

    Supported tools:
      - ENHANCE_PROMPT
      - CREATE_PLAN
      - ENHANCE_PLAN
    """

    # TOOL: NAME then INPUT: block until next marker or end
    TOOL_PATTERN = re.compile(
        r"TOOL:\s*(ENHANCE_PROMPT|CREATE_PLAN|ENHANCE_PLAN)\s*\nINPUT:\s*(.+?)(?=\n(?:BASH:|WRITE_FILE:|READ_FILE:|TOOL:|COMPLETE|$))",
        re.DOTALL,
    )

    def __init__(
        self,
        llm_client: "LLMClient",
        config: AgentConfig,
        *,
        tools_dir: Optional[Path] = None,
        agent_name: str = "Coder",
    ) -> None:
        self.llm_client = llm_client
        self.config = config
        self.tools_dir = Path(tools_dir) if tools_dir else None
        self.agent_name = agent_name
        self._tool_counter = 0

        self._registry: Dict[str, ToolFunc] = {
            "ENHANCE_PROMPT": enhance_prompt,
            "CREATE_PLAN": create_plan,
            "ENHANCE_PLAN": enhance_plan,
        }

    def set_tools_dir(self, tools_dir: Path) -> None:
        self.tools_dir = Path(tools_dir)
        self.tools_dir.mkdir(parents=True, exist_ok=True)

    def parse_calls(self, text: str) -> List[Tuple[str, str]]:
        matches = self.TOOL_PATTERN.findall(text)
        return [(name.strip().upper(), inp.strip()) for name, inp in matches]

    def run_calls(self, text: str) -> List[Dict[str, object]]:
        """Parse and execute all tool calls contained in text.

        Returns a list of result dicts compatible with coder's action results.
        """
        results: List[Dict[str, object]] = []
        for tool_name, tool_input in self.parse_calls(text):
            result: Dict[str, object] = {
                "type": "tool",
                "tool": tool_name,
                "input_len": len(tool_input),
            }
            try:
                func = self._registry.get(tool_name)
                if not func:
                    raise ValueError(f"Unknown tool: {tool_name}")
                # Log tool call if logger available
                logger = getattr(self.llm_client, "logger", None)
                call_id = None
                if logger is not None:
                    call_id = logger.log_tool_call(
                        agent_name=self.agent_name,
                        tool_name=tool_name,
                        tool_input={"input": tool_input},
                    )

                output = func(self.llm_client, self.config, tool_input)
                result["output"] = output
                self._save_snapshot(tool_name, tool_input, output=output)
                if logger is not None and call_id is not None:
                    logger.log_tool_result(
                        call_id=call_id,
                        agent_name=self.agent_name,
                        tool_name=tool_name,
                        tool_output={"output": output},
                        success=True,
                    )
            except Exception as e:
                result["error"] = str(e)
                self._save_snapshot(tool_name, tool_input, error=str(e))
                logger = getattr(self.llm_client, "logger", None)
                if logger is not None:
                    # If we didn't get a call_id above, create a synthetic one for error logging
                    call_id = logger.log_tool_call(
                        agent_name=self.agent_name,
                        tool_name=tool_name,
                        tool_input={"input": tool_input},
                    )
                    logger.log_tool_result(
                        call_id=call_id,
                        agent_name=self.agent_name,
                        tool_name=tool_name,
                        tool_output=None,
                        success=False,
                        error=str(e),
                    )
            results.append(result)
        return results

    def _save_snapshot(self, tool: str, tool_input: str, *, output: Optional[str] = None, error: Optional[str] = None) -> None:
        if not self.tools_dir:
            return
        try:
            self._tool_counter += 1
            filename = f"tool_{self._tool_counter:03d}_{tool}.md"
            path = self.tools_dir / filename
            parts = [
                f"# Tool: {tool}",
                "",
                f"Agent: {self.agent_name}",
                "",
                "## INPUT",
                "",
                tool_input,
                "",
            ]
            if output is not None:
                parts.extend(["## OUTPUT", "", output, ""])
            if error is not None:
                parts.extend(["## ERROR", "", error, ""])
            path.write_text("\n".join(parts), encoding="utf-8")
        except Exception:
            # Snapshot failures must not break the workflow
            pass
