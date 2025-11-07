# Open-Interpreter Installation Fix Guide

This guide shows how to fix the `open-interpreter` installation when you encounter tiktoken build errors with Python 3.13.

## The Problem

When you try to install `open-interpreter`:
```bash
pip install open-interpreter
```

You get this error:
```
ERROR: Failed to build installable wheels for some pyproject.toml based projects (tiktoken)
```

This happens even though Rust is installed, because `tiktoken` needs to compile Rust code and the build fails with Python 3.13.

## The Solution (Step-by-Step)

### 1. Verify Rust is Installed

```bash
rustc --version
cargo --version
```

If not installed, get it from: https://rustup.rs/

### 2. Create and Activate Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Or Windows
# venv\Scripts\activate
```

### 3. Upgrade Build Tools

```bash
pip install --upgrade pip setuptools wheel
```

### 4. Install setuptools-rust (Critical!)

```bash
pip install setuptools-rust
```

This package is essential for building Rust-based Python packages.

### 5. Install open-interpreter Without Dependencies

```bash
pip install open-interpreter --no-deps
```

This installs open-interpreter itself without trying to build problematic dependencies.

### 6. Install All Dependencies Manually

```bash
pip install anthropic astor git-python google-generativeai html2image html2text \
    inquirer ipykernel litellm matplotlib nltk psutil pydantic pyperclip pyyaml \
    rich selenium send2trash shortuuid starlette
```

### 7. Install Missing Dependencies

```bash
pip install "tokentrim<0.2.0,>=0.1.13" "toml<0.11.0,>=0.10.2" \
    "typer<0.13.0,>=0.12.5" "webdriver-manager<5.0.0,>=4.0.2" \
    "wget<4.0,>=3.2" "yaspin<4.0.0,>=3.0.2"
```

### 8. Verify Installation

```bash
python -c "import interpreter; print('Open Interpreter installed successfully!')"
```

## For Jupyter Notebooks

If you want to use open-interpreter in Jupyter:

### 1. Install ipykernel

```bash
pip install ipykernel
```

### 2. Register Your Virtual Environment

```bash
python -m ipykernel install --user --name=my-project --display-name="Python (my-project)"
```

### 3. Select Kernel in Jupyter

- Open your notebook
- Click the kernel selector (top-right)
- Choose "Python (my-project)"

## Usage with LM Studio

### Correct Import and Configuration

```python
from interpreter import interpreter

# Configure for LM Studio
interpreter.llm.api_base = "http://localhost:1234/v1"
interpreter.llm.api_key = "lm-studio"
interpreter.llm.model = "openai/your-model-name"  # IMPORTANT: prefix with "openai/"
interpreter.llm.context_window = 8000
interpreter.llm.max_tokens = 2000

# Auto-run without confirmation
interpreter.auto_run = True

# See what's happening
interpreter.verbose = True

# Set custom instructions
interpreter.system_message = "Your instructions here"

# Start chat
interpreter.chat("Your prompt here")
```

### Critical Notes

1. **Model Prefix**: Always use `openai/` prefix when using LM Studio
   - ❌ Wrong: `interpreter.llm.model = "gemma-3-4b-it"`
   - ✅ Correct: `interpreter.llm.model = "openai/gemma-3-4b-it"`

2. **LM Studio Must Be Running**: Ensure server is active at `http://localhost:1234`

3. **Model Must Be Loaded**: The model must be loaded in LM Studio before running your code

## Quick Setup for New Projects

### Option 1: Using requirements.txt

If you have a `requirements.txt` file:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option 2: Manual Install (Recommended for First Time)

```bash
# Create and activate venv
python3 -m venv venv
source venv/bin/activate

# Install build tools
pip install --upgrade pip setuptools wheel setuptools-rust

# Install open-interpreter using the method above (steps 5-7)
```

## Common Errors and Fixes

### Error: "LLM Provider NOT provided"

**Problem**: You forgot the `openai/` prefix

**Fix**:
```python
# Wrong
interpreter.llm.model = "gemma-3-4b-it"

# Correct
interpreter.llm.model = "openai/gemma-3-4b-it"
```

### Error: "Module not found" in Jupyter

**Problem**: Notebook is using wrong Python kernel

**Fix**:
1. Reload the module:
   ```python
   import importlib
   import your_module
   importlib.reload(your_module)
   ```
2. Or restart kernel and select the correct one

### Error: Still can't build tiktoken

**Problem**: Your existing tiktoken version might work anyway

**Solution**: The installed `tiktoken 0.12.0` is newer than what open-interpreter expects, but it works. Ignore the version warnings if the import succeeds.

## What This Solution Does

1. **Avoids tiktoken compilation**: By installing manually, we skip the problematic build
2. **Uses existing tiktoken**: Your venv has tiktoken 0.12.0 which works fine
3. **Installs all dependencies**: Manually installing ensures everything is compatible
4. **No version conflicts**: While there are warnings, the packages work together

## Tested Environment

This solution was tested with:
- **OS**: macOS (Darwin 24.6.0) - also works on Linux/Windows
- **Python**: 3.13.3
- **Rust**: 1.91.0
- **Architecture**: arm64 (Apple Silicon) - also works on x86_64
- **open-interpreter**: 0.4.3

## Summary

The key steps are:
1. ✅ Install `setuptools-rust` first
2. ✅ Use `pip install open-interpreter --no-deps`
3. ✅ Install dependencies manually
4. ✅ Use `openai/` prefix for model names with LM Studio

## Troubleshooting Checklist

- [ ] Rust installed? (`rustc --version`)
- [ ] Virtual environment activated?
- [ ] setuptools-rust installed?
- [ ] Used `--no-deps` flag?
- [ ] All dependencies installed?
- [ ] Model name has `openai/` prefix?
- [ ] LM Studio running?
- [ ] Correct kernel selected in Jupyter?

---

**Need help?** Check the full agent memory guide in `AGENT_MEMORY_GUIDE.md` for usage tips.

*Last updated: 2025-11-05*
