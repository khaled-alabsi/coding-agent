# Changelog

All notable changes to the Azure Coding Agent.

## [1.2.0] - 2025-11-07

### 🔧 Fixed - CSS Files and Import Consistency

**The agent now creates proper CSS files and matches imports correctly!**

#### What Changed:
- 🎨 **CSS Files with Content**: Agent now creates CSS files with ACTUAL styling, not empty files
- 🔗 **Import Consistency**: Ensures all imports match the actual file names created
- ✅ **Verification Step**: Added checklist to verify all imports before marking complete
- 📋 **CSS Template**: Provided minimum CSS structure example in instructions
- 🚫 **No More Empty Files**: Explicitly forbidden creating empty CSS/style files

#### The Problem We Fixed:
```
Before v1.2.0:
❌ Created src/styles/main.css (EMPTY FILE)
❌ Import says './styles/index.css' (WRONG NAME)
❌ Project crashes with "Failed to resolve import"
```

**After v1.2.0:**
```
✅ Creates src/styles/main.css with FULL STYLING
✅ Import says './styles/main.css' (MATCHES!)
✅ Project runs immediately without errors
```

#### New Instructions Added:

1. **File Consistency Rules**:
   - If you create `src/styles/main.css`, import `'./styles/main.css'`
   - Never import files that don't exist
   - All file names must match imports exactly

2. **CSS Content Requirements**:
   - Must include CSS reset
   - Must include CSS variables
   - Must include component styles
   - Must include responsive media queries
   - NEVER create empty CSS files

3. **Verification Checklist**:
   - ✅ All imports reference existing files
   - ✅ CSS files contain actual styling
   - ✅ All file names match imports
   - ✅ Project builds without errors

#### Impact:
- 🎯 **Zero Import Errors**: No more "Failed to resolve import" errors
- 🎨 **Styled Projects**: All projects come with professional styling
- ⚡ **Works First Time**: No manual fixing of imports needed
- 📚 **Better Learning**: Developers see proper CSS structure examples

---

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
