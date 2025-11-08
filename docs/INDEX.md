# Azure Code Agent - Documentation Index

**Welcome to the Azure Code Agent documentation!**

This is your entry point for understanding and working with the multi-agent coding system.

---

## 📚 Quick Start

- **New Users**: Start with [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
- **Developers**: Check [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for setup and contribution
- **System Designers**: See [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) for core concepts

---

## 🗂️ Documentation Structure

### Core Documentation

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - System Architecture
   - Component overview
   - Agent workflow
   - Data flow
   - File organization

2. **[DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md)** - Design Principles
   - Why we made certain decisions
   - Core philosophies
   - Trade-offs and rationale

3. **[COMPACTOR_DESIGN.md](COMPACTOR_DESIGN.md)** - Memory Compaction Design
   - Why compactor exists
   - Why it's in `utils/` not `agents/`
   - How it works
   - When to use it

### Feature Documentation

4. **[AGENT_PROCESS_FLOW.md](AGENT_PROCESS_FLOW.md)** - Agent Process & Memory
   - Workflow diagrams
   - Memory architecture
   - Enhancement opportunities

5. **[TRUNCATION_FIX_PLAN.md](TRUNCATION_FIX_PLAN.md)** - Truncation Detection & Fix
   - Dynamic detection strategy
   - Auto-fix implementation plan
   - Testing approach

6. **[TRUNCATION_IMPLEMENTATION_SUMMARY.md](TRUNCATION_IMPLEMENTATION_SUMMARY.md)** - Implementation Details
   - What was implemented
   - How to use it
   - Configuration options

### Guides

7. **[DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)** - Development Guide
   - Setup instructions
   - Contributing guidelines
   - Testing procedures
   - Code style

8. **[CONFIGURATION.md](CONFIGURATION.md)** - Configuration Reference
   - All settings explained
   - Environment variables
   - Defaults and overrides

9. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Troubleshooting
   - Common issues
   - Error messages
   - Solutions

---

## 🏗️ Project Structure

```
coding-agent/
├── docs/                          # 📚 Documentation (YOU ARE HERE)
│   ├── INDEX.md                   # This file
│   ├── ARCHITECTURE.md            # System architecture
│   ├── COMPACTOR_DESIGN.md        # Compactor design rationale
│   └── ...
│
├── azure_agent/                   # 🤖 Main package
│   ├── agents/                    # Agent implementations
│   │   ├── base_agent.py         # Base agent class
│   │   ├── prompt_enhancer.py    # Prompt enhancement agent
│   │   ├── planner.py            # Planning agent
│   │   ├── plan_enhancer.py      # Plan validation agent
│   │   ├── coder.py              # Code generation agent
│   │   └── result_validator.py   # Validation agent
│   │
│   ├── core/                      # Core components
│   │   ├── llm_client.py         # LLM API wrapper
│   │   ├── file_operations.py    # File I/O operations
│   │   └── orchestrator.py       # Workflow orchestration
│   │
│   ├── utils/                     # Utilities
│   │   ├── history_compactor.py  # History compaction
│   │   ├── helpers.py            # Helper functions
│   │   ├── logger.py             # Logging system
│   │   ├── sound.py              # Sound notifications
│   │   ├── context_analyzer.py   # Token analysis
│   │   └── llm_tester.py         # LLM testing
│   │
│   ├── config/                    # Configuration
│   │   └── settings.py           # Config dataclass
│   │
│   ├── prompts/                   # Agent system prompts
│   │   ├── prompt_enhancer.md
│   │   ├── planner.md
│   │   ├── plan_enhancer.md
│   │   ├── coder.md
│   │   └── result_validator.md
│   │
│   └── output/                    # 📁 All outputs go here
│       ├── logs/                  # Agent logs
│       │   ├── agent_log_*.json
│       │   └── workflow_steps_*/
│       ├── fail_logs/             # Failure reports
│       └── generated_code/        # Generated projects
│
└── README.md                      # Main README

```

---

## 🎯 Key Concepts

### 1. Multi-Agent System
The system uses 5 specialized agents working in sequence:
- Each agent has a specific role
- Agents communicate through text
- Workflow is orchestrated centrally

### 2. Memory Management
- **Conversational agents** (Coder, Validator) maintain history
- **Stateless agents** (Enhancers, Planner) work in isolation
- **Compactor** summarizes old history to fit context window

### 3. Auto-Correction
- Validator checks code quality
- Failed validation triggers automatic fixes
- Up to N iterations (configurable)

---

## 🚀 Common Tasks

### Running the System

```python
from azure_agent import run

# Basic usage
results = run(
    prompt="Create a TODO app",
    use_local_llm=True
)
```

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for more examples.

### Analyzing Logs

```python
from utils.context_analyzer import ContextAnalyzer

analyzer = ContextAnalyzer()
stats = analyzer.analyze_log_file('output/logs/agent_log_*.json')
analyzer.print_analysis(stats)
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for debugging.

### Testing LLM Settings

```python
from utils.llm_tester import test_llm_context

result = test_llm_context(
    max_tokens=50000,
    context_window=262144
)
```

See [CONFIGURATION.md](CONFIGURATION.md) for tuning.

---

## 📖 How to Read This Documentation

**If you want to...**

| Goal | Start Here |
|------|------------|
| Understand the system | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Know why it's designed this way | [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) |
| Understand memory/compaction | [COMPACTOR_DESIGN.md](COMPACTOR_DESIGN.md) |
| Set up development environment | [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) |
| Configure the system | [CONFIGURATION.md](CONFIGURATION.md) |
| Fix truncation issues | [TRUNCATION_IMPLEMENTATION_SUMMARY.md](../TRUNCATION_IMPLEMENTATION_SUMMARY.md) |
| Debug problems | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Understand agent workflow | [AGENT_PROCESS_FLOW.md](../AGENT_PROCESS_FLOW.md) |

---

## 🔄 Documentation Updates

This documentation is maintained alongside the code. When making changes:

1. **Code changes** → Update relevant docs
2. **New features** → Add to INDEX.md and create dedicated doc
3. **Bug fixes** → Update TROUBLESHOOTING.md if needed
4. **Design changes** → Update ARCHITECTURE.md and DESIGN_PRINCIPLES.md

---

## 🤝 Contributing

See [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for:
- Setup instructions
- Code style guidelines
- Testing requirements
- Pull request process

---

## 📞 Getting Help

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Review relevant documentation above
3. Check agent logs in `output/logs/`
4. Check fail logs in `output/fail_logs/`
5. Open an issue with logs attached

---

**Last Updated**: 2025-11-08
**Version**: 1.0.0
