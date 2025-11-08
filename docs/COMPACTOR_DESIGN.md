# History Compactor Design Rationale

**Why the compactor is in `history/` and NOT in `agents/`**

---

## TL;DR

The `HistoryCompactor` is a **utility service**, not an agent. It belongs in `history/` because it's a shared infrastructure component used BY agents, not a decision-making agent itself.

---

## Design Question

> "Why is `HistoryCompactor` in `azure_agent/history/compactor.py` instead of `azure_agent/agents/compactor.py`?"

## Answer: Separation of Concerns

### 1. What Makes Something an Agent?

An **agent** in this system has these characteristics:
- Makes autonomous decisions
- Has a specific domain expertise (planning, coding, validation)
- Uses LLM for reasoning and problem-solving
- Communicates with users or other agents
- Has a defined role in the workflow

**Examples**: `Planner`, `Coder`, `ResultValidator`

### 2. What Makes Something a Utility?

A **utility** is a service component that:
- Performs a specific technical task
- Is used BY agents, not acting AS an agent
- Has no decision-making authority
- Is infrastructure, not intelligence
- Is shared across multiple agents

**Examples**: `LLMClient`, `FileOperations`, `HistoryCompactor`

---

## Why HistoryCompactor is a Utility

### Evidence from Code

#### Location: `azure_agent/history/compactor.py`

```python
class HistoryCompactor:
    """Summarizes older conversation turns to stay within the context window."""

    def compact(self, messages, *, system_prompt, context_window) -> CompactionResult:
        """Return a compacted version of messages if needed."""
        # 1. Calculate tokens
        # 2. Decide if compaction needed
        # 3. Summarize old messages
        # 4. Preserve recent messages
        # 5. Return result
```

**Key observations:**
1. It's a **pure function** - given messages, return compacted messages
2. No autonomous decision-making - just token math
3. No workflow participation - doesn't talk to users
4. No domain expertise - just memory management

#### Usage: `azure_agent/agents/base_agent.py`

```python
class BaseAgent(ABC):
    def __init__(self, config: AgentConfig, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client
        self.messages: List[Dict[str, str]] = []
        self.history_compactor = HistoryCompactor(config, llm_client)  # ← Utility service

    def _compact_history_if_needed(self):
        """Summarize older history if the context window is at risk."""
        result = self.history_compactor.compact(
            self.messages,
            system_prompt=self.system_prompt,
            context_window=self.config.context_window
        )
        if result.compacted:
            self.messages = result.messages
```

**Key observations:**
1. **Composition, not inheritance** - BaseAgent HAS-A compactor, not IS-A compactor
2. **Shared by all agents** - Every agent gets the same compactor
3. **Called automatically** - Agents don't "talk to" the compactor, they USE it
4. **Infrastructure service** - Like using a database or cache

---

## Design Principle: Single Responsibility

### Agents are responsible for:
- Understanding their domain (planning, coding, validation)
- Making decisions within their expertise
- Producing valuable output for the workflow

### Compactor is responsible for:
- Managing memory constraints
- Summarizing conversation history
- Keeping agents within context limits

**If compactor was an agent**, it would need to:
- Participate in the workflow
- Communicate with other agents
- Have its own system prompt and role
- Make autonomous decisions

**This is wrong** because:
- Memory management is infrastructure, not intelligence
- All agents need compaction - it's not a specialized role
- It's a technical constraint, not a business capability

---

## Architectural Analogy

Think of the system like a company:

| Component | Role | Type |
|-----------|------|------|
| **Planner** | Project Manager | Agent (Person) |
| **Coder** | Software Engineer | Agent (Person) |
| **ResultValidator** | QA Engineer | Agent (Person) |
| **LLMClient** | Email System | Utility (Tool) |
| **FileOperations** | File Cabinet | Utility (Tool) |
| **HistoryCompactor** | Notepad/Memory | Utility (Tool) |

You wouldn't hire a "Memory Manager" as a person on your team - you'd give everyone a notepad. The compactor is the notepad.

---

## Alternative Designs Considered

### ❌ Option 1: Put compactor in `agents/`

**Why rejected:**
- Confuses the agent abstraction
- Implies compactor participates in workflow
- Breaks separation of concerns
- Makes it harder to understand what an "agent" is

### ❌ Option 2: Make each agent compact its own history

**Why rejected:**
- Code duplication across 5 agents
- Harder to maintain and update
- Inconsistent behavior across agents
- Violates DRY principle

### ✅ Option 3: Compactor as shared utility in `history/` (CURRENT)

**Why chosen:**
- Clear separation: agents = intelligence, history = infrastructure
- Reusable across all agents
- Easy to test in isolation
- Follows single responsibility principle
- Natural location: `history/` contains history management utilities

---

## Folder Structure Rationale

```
azure_agent/
├── agents/              # 🧠 Intelligence - Decision makers
│   ├── base_agent.py   # All agents USE utilities
│   ├── planner.py
│   ├── coder.py
│   └── result_validator.py
│
├── core/                # 🔧 Core Services - Infrastructure
│   ├── llm_client.py   # LLM communication
│   ├── file_operations.py
│   └── orchestrator.py
│
├── history/             # 💾 Memory Management - History utilities
│   ├── compactor.py    # ← YOU ARE HERE
│   └── __init__.py
│
└── utils/               # 🛠️ General Utilities - Helpers
    ├── helpers.py
    ├── logger.py
    └── context_analyzer.py
```

### Why `history/` folder exists:

Memory management is a **cross-cutting concern** that affects all agents but isn't core business logic. It deserves its own module because:

1. **Specialized domain** - Managing conversation memory is complex
2. **Future expansion** - May add more memory strategies (RAG, vector stores, etc.)
3. **Clear boundaries** - Separates memory concerns from agent logic
4. **Easy to find** - Developers know where to look for history-related code

---

## Benefits of Current Design

### 1. Maintainability
- One place to update compaction logic
- Changes don't affect agent implementations
- Easy to add new compaction strategies

### 2. Testability
- Can test compactor independently
- Mock compactor for agent tests
- Clear interfaces

### 3. Clarity
- Developers immediately understand "this is infrastructure, not intelligence"
- New team members don't confuse utilities with agents
- Architecture is self-documenting

### 4. Extensibility
- Easy to add new memory management utilities
- Can swap compaction strategies without changing agents
- Future: add RAG, vector stores, caching, etc. all in `history/`

---

## Real-World Usage Flow

Here's how compaction actually works in practice:

```
1. User sends request to Coder agent
   ↓
2. Coder.chat() is called
   ↓
3. Coder adds user message to self.messages
   ↓
4. Coder calls self._compact_history_if_needed()
   ↓
5. BaseAgent._compact_history_if_needed() checks token count
   ↓
6. HistoryCompactor.compact() is called
   ↓
7. Compactor:
   - Estimates current token usage
   - Decides if compaction needed (>85% of context_window)
   - Summarizes old messages using LLM
   - Preserves recent messages (last 6)
   - Returns compacted message list
   ↓
8. BaseAgent updates self.messages = compacted_messages
   ↓
9. Coder sends compacted messages to LLM
   ↓
10. User gets response within context limits
```

**Key insight**: The agent USES the compactor transparently. It's plumbing, not a participant.

---

## When to Add to `agents/` vs `history/`

### Add to `agents/` when:
- It makes autonomous decisions
- It has domain expertise
- It participates in the workflow
- It communicates with users or other agents
- It's a role in the system (Planner, Coder, etc.)

### Add to `history/` when:
- It manages conversation memory
- It's used BY agents, not acting AS an agent
- It's infrastructure for memory constraints
- It's shared across multiple agents
- It's about token limits, summarization, context windows

---

## Conclusion

The `HistoryCompactor` is correctly placed in `azure_agent/history/` because:

1. **It's a utility service**, not an autonomous agent
2. **It's used BY agents** through composition, not as a workflow participant
3. **It manages infrastructure concerns** (memory/tokens), not business logic
4. **It's shared across all agents**, not a specialized role
5. **It follows the Single Responsibility Principle** - agents decide, utilities serve

Moving it to `agents/` would:
- Confuse the agent abstraction
- Blur architectural boundaries
- Make the codebase harder to understand
- Violate separation of concerns

The current design is clean, maintainable, and follows software engineering best practices.

---

**Last Updated**: 2025-11-08
**Related Docs**: [ARCHITECTURE.md](ARCHITECTURE.md), [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)
