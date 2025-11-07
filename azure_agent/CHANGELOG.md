# Changelog

All notable changes to the Azure Coding Agent.

## [1.1.0] - 2025-11-07

### ✨ Added - Complete Project Generation

**The agent now creates COMPLETE, RUNNABLE projects automatically!**

#### What Changed:
- 🎯 **Enhanced System Instructions**: Agent now understands it must create ALL necessary files
- 📦 **Auto-generates Config Files**: Automatically creates package.json, vite.config.ts, tsconfig.json, etc.
- 📝 **Includes README**: Every project gets a README with clear "How to Run" instructions
- 🗂️ **Creates .gitignore**: Proper gitignore files for each project type
- ✅ **Production-Ready**: Projects work immediately after `npm install` or `pip install`

#### Before vs After:

**Before (v1.0.0):**
```
Agent creates:
✓ src/components/
✓ Source files
✗ NO package.json
✗ NO build configs
✗ NO README
❌ Project won't run without manual setup
```

**After (v1.1.0):**
```
Agent creates:
✓ src/components/
✓ Source files
✓ package.json with all dependencies
✓ vite.config.ts, tsconfig.json
✓ README.md with run instructions
✓ .gitignore
✅ Project runs immediately!
```

#### Example - Web Projects:
The agent now automatically creates:
- ✅ `package.json` - Dependencies and scripts
- ✅ `vite.config.ts` - Build tool configuration
- ✅ `tsconfig.json` - TypeScript settings
- ✅ `tsconfig.node.json` - Node TypeScript config
- ✅ `README.md` - Setup and run instructions
- ✅ `.gitignore` - Git ignore patterns
- ✅ All source files in proper structure

#### Example - Python Projects:
The agent now automatically creates:
- ✅ `requirements.txt` - Python dependencies
- ✅ `setup.py` or `pyproject.toml` - Package setup
- ✅ `README.md` - Installation instructions
- ✅ `.env.example` - Environment variables template
- ✅ `.gitignore` - Python-specific ignores
- ✅ All Python modules in proper structure

#### Instructions Provided:
Every README now includes:
1. **Installation steps** - How to install dependencies
2. **Run commands** - How to start the project
3. **Build commands** - How to build for production
4. **Test commands** - How to run tests
5. **Project structure** - Overview of files

### 🔧 Technical Details

**Updated Files:**
- `azure_agent.py` - Enhanced system instructions with detailed requirements

**New System Instructions Include:**
- Complete project structure requirements
- Build tool configuration requirements
- README requirements with specific sections
- Project-type-specific checklists
- Example workflows for common project types

### 📚 Documentation

- Updated README.md with new features
- Added CHANGELOG.md to track changes
- Enhanced feature list

### 🎯 Impact

**User Experience:**
- ⏱️ **Faster Setup**: No manual configuration needed
- ✅ **Works First Time**: Projects run immediately
- 📖 **Clear Instructions**: README tells you exactly what to do
- 🎓 **Learn Better**: See complete project structure examples

**Developer Experience:**
- 🚀 **Production-Ready**: Can deploy immediately
- 🔧 **Best Practices**: Follows modern project structure
- 📦 **Complete Setup**: Nothing missing
- 🎯 **Consistent**: All projects follow the same quality standard

---

## [1.0.0] - 2025-11-07

### ✨ Initial Release

#### Features:
- Local LLM support via LM Studio
- Azure OpenAI support
- Code execution (bash commands, file operations)
- Conversation history management
- Auto-save functionality
- Inactivity watchdog
- Jupyter notebook interface
- Example scripts and documentation

#### Supported LLMs:
- Local: Any model in LM Studio (DeepSeek, Qwen, CodeLlama, etc.)
- Cloud: Azure GPT-4, GPT-3.5-Turbo

#### Documentation:
- README.md - Quick start guide
- LOCAL_LLM_GUIDE.md - Complete local LLM setup
- AZURE_SETUP_GUIDE.md - Azure OpenAI setup
- Example notebooks and scripts

---

## Future Improvements

Ideas for future versions:
- [ ] Add support for more project types (Next.js, Django, Flask, etc.)
- [ ] Auto-detect project type from specification
- [ ] Generate tests automatically
- [ ] Add Docker configuration
- [ ] CI/CD pipeline generation
- [ ] Database schema generation
- [ ] API documentation generation
- [ ] Support for monorepos

---

**Maintained by**: Coding Agent Team
**License**: MIT
