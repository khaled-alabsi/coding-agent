# Agent Prompts

This directory contains the system prompts for each agent in the multi-agent system. Each prompt is stored as a separate markdown file, making it easy to view, edit, and version control the agent instructions without touching the code.

## Files

- **prompt_enhancer.md** - Instructions for the Prompt Enhancer Agent
- **planner.md** - Instructions for the Planner Agent
- **plan_enhancer.md** - Instructions for the Plan Enhancer Agent
- **coder.md** - Instructions for the Coder Agent
- **result_validator.md** - Instructions for the Result Validator Agent

## How It Works

The agents load their prompts using the `load_prompt()` utility function:

```python
from ..utils import load_prompt

@property
def system_prompt(self) -> str:
    return load_prompt("prompt_enhancer")  # Loads prompts/prompt_enhancer.md
```

### Benefits

1. **Easy to Edit**: Modify agent behavior by editing markdown files, no code changes needed
2. **Version Control**: Track prompt changes separately from code changes
3. **Readability**: Markdown format is easier to read and format than Python strings
4. **Caching**: Prompts are cached in memory after first load for performance
5. **Validation**: Missing prompts will raise clear error messages

## Editing Prompts

To modify an agent's behavior:

1. Open the corresponding `.md` file
2. Edit the instructions, examples, or guidelines
3. Save the file
4. Restart the agent (prompts are cached, so need to reload)

To force reload all prompts without restarting:

```python
from azure_agent.utils import reload_prompts
reload_prompts()
```

## Prompt Structure

Each prompt file should include:

- **Role Description**: What the agent does
- **Responsibilities**: List of specific tasks
- **Guidelines**: How to approach the task
- **Output Format**: Expected response format
- **Examples**: Sample inputs and outputs (if applicable)

## Adding New Prompts

To add a new agent with its own prompt:

1. Create a new `.md` file in this directory
2. Write the prompt following the structure above
3. Create an agent class that loads it: `load_prompt("your_prompt_name")`
4. The prompt loader will automatically find and cache it

## Tips

- Use clear headings and bullet points for better readability
- Include specific examples to guide the agent's behavior
- Test prompt changes with simple tasks before full runs
- Keep prompts focused on one responsibility per agent
- Document any critical checks or validation steps clearly
