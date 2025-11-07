# Prompts Folder - Complete Package

## ✅ Created Successfully

All prompt files have been created in: `C:\CCB\sources\portal\context\prompts\`

---

## 📦 Package Contents (8 Files)

### 1. **MASTER-PROMPT.md** ⭐ (All-in-One)
**What**: Complete ready-to-use prompt for AI agents  
**Size**: Compact (~3,000 words)  
**Use**: Copy entire file → paste to AI agent → get analysis  
**Best For**: Quick analysis without reading other docs

### 2. **QUICK-START.md** (3-Minute Guide)
**What**: How to use the prompts  
**Size**: Short guide  
**Use**: First-time users  
**Best For**: Getting started fast

### 3. **SYSTEM-PROMPT.md** (Comprehensive Instructions)
**What**: Full system prompt with complete methodology  
**Size**: Full (~8,000 words)  
**Use**: When you need detailed instructions  
**Best For**: Thorough analysis, training

### 4. **USER-PROMPT.md** (Task Template)
**What**: Task definition with app name placeholder  
**Size**: Medium (~3,000 words)  
**Use**: Customize with app name  
**Best For**: Structured analysis workflow

### 5. **CODE-PATTERNS.md** (Pattern Reference)
**What**: Quick lookup for code patterns  
**Size**: Reference guide (~4,000 words)  
**Use**: Keep open while analyzing  
**Best For**: Pattern identification

### 6. **API-REQUIREMENT-TEMPLATE.md** (Documentation)
**What**: Template for each API requirement  
**Size**: Template (~2,000 words)  
**Use**: Copy and fill for each data source  
**Best For**: Documenting findings

### 7. **README.md** (Full Guide)
**What**: Complete overview and instructions  
**Size**: Full documentation  
**Use**: Understanding the system  
**Best For**: Learning methodology

### 8. **INDEX.md** (Quick Reference)
**What**: File index and navigation  
**Size**: Quick reference  
**Use**: Finding what you need  
**Best For**: Navigation

---

## 🚀 Quick Start Options

### Option 1: Fastest (5 minutes)
```
1. Open: MASTER-PROMPT.md
2. Replace: [INSERT APP NAME] with your app
3. Copy entire file
4. Paste to AI agent (ChatGPT, Claude, etc.)
5. Get complete dependency analysis
```

### Option 2: Structured (15 minutes)
```
1. Read: QUICK-START.md
2. Use: SYSTEM-PROMPT.md + USER-PROMPT.md
3. Reference: CODE-PATTERNS.md
4. Get detailed analysis
```

### Option 3: Manual (2-3 hours)
```
1. Read: README.md
2. Follow: USER-PROMPT.md steps manually
3. Use: CODE-PATTERNS.md for identification
4. Document: API-REQUIREMENT-TEMPLATE.md for each source
5. Create comprehensive report
```

---

## 🎯 What These Prompts Do

### Input
```
Application name: "kwk" (or any app in the monolith)
```

### Output
```markdown
1. Application location and structure
2. All REST endpoints with paths
3. Complete data flow trace
4. Data sources classified:
   - Mainframe calls (need REST API) ⚠️
   - Database tables (can migrate) ✅
   - SC services (check further) 🔄
   - REST clients (already good) ✅
5. For EACH mainframe call:
   - Exact file paths
   - Specific fields needed
   - Suggested REST API endpoint
   - Swagger search keywords
   - Field mapping tables
6. Migration recommendations
```

---

## 📊 Use Case Examples

### Use Case 1: "I need to migrate KWK to microservice"
**File**: MASTER-PROMPT.md  
**Customize**: Replace [INSERT APP NAME] with "kwk"  
**Result**: Complete list of dependencies + REST API suggestions

### Use Case 2: "I need to understand app dependencies for project planning"
**Files**: SYSTEM-PROMPT.md + USER-PROMPT.md  
**Result**: Detailed analysis with effort estimates

### Use Case 3: "I'm manually analyzing code"
**File**: CODE-PATTERNS.md  
**Result**: Quick pattern matching reference

### Use Case 4: "I need to document findings for architecture review"
**File**: API-REQUIREMENT-TEMPLATE.md  
**Result**: Professional documentation template

---

## ✅ Quality Guarantees

Analysis will include:
- ✅ Exact file paths (not vague descriptions)
- ✅ Specific field names and types
- ✅ Complete tracing to ultimate source
- ✅ Concrete API endpoint suggestions
- ✅ Actionable Swagger search terms
- ✅ Field mapping tables
- ✅ Migration recommendations

---

## 🎓 What You'll Learn

By using these prompts, you'll understand:
1. **Where data comes from** (mainframe vs database vs service)
2. **How to trace dependencies** (following the chain)
3. **How to suggest APIs** (grouping data logically)
4. **How to search Swagger** (effective keywords)
5. **How to plan migration** (what can/cannot migrate)

---

## 📁 File Organization

```
context/prompts/
├── MASTER-PROMPT.md          ⭐ Start here (all-in-one)
├── QUICK-START.md            📖 How to use
├── SYSTEM-PROMPT.md          🎯 Full methodology
├── USER-PROMPT.md            📝 Task template
├── CODE-PATTERNS.md          🔍 Pattern reference
├── API-REQUIREMENT-TEMPLATE.md 📋 Documentation template
├── README.md                 📚 Full guide
└── INDEX.md                  📑 Navigation
```

---

## 💡 Pro Tips

1. **For Quick Results**: Use MASTER-PROMPT.md (all-in-one)
2. **For Training**: Use SYSTEM-PROMPT.md (detailed)
3. **For Manual Work**: Use CODE-PATTERNS.md (reference)
4. **For Documentation**: Use API-REQUIREMENT-TEMPLATE.md (template)
5. **For Understanding**: Read README.md (overview)

---

## 🎯 Success Metrics

You'll know it worked when you have:
- ✅ List of all mainframe calls with exact files
- ✅ Specific REST API endpoints suggested for each
- ✅ Swagger keywords that actually find relevant APIs
- ✅ Exact fields mapped from current → API format
- ✅ Clear migration path identified

---

## 📞 Next Steps

1. **Choose your method**: Quick (MASTER-PROMPT), Structured (SYSTEM+USER), or Manual (CODE-PATTERNS)
2. **Pick an app**: Start with a small app (e.g., KWK)
3. **Run analysis**: Follow chosen method
4. **Use results**: Search Swagger, test APIs, plan migration
5. **Iterate**: Refine prompts based on results

---

## 🌟 Key Features

### Comprehensive
- Covers all data source types (mainframe, DB, services, APIs)
- Complete tracing methodology
- Detailed output format

### Actionable
- Concrete file paths
- Specific field names
- Copy-paste Swagger keywords
- Real API endpoint patterns

### Flexible
- All-in-one option (MASTER-PROMPT)
- Detailed option (SYSTEM + USER)
- Manual option (CODE-PATTERNS)
- Documentation option (TEMPLATE)

### Proven
- Based on actual KWK analysis
- Real patterns from the monolith
- Tested output format

---

## 📚 Related Resources

In parent folder (`../kwk-migration/`):
- `00-CRITICAL-FINDINGS.md` - KWK analysis example
- `07-kwk-business-flow-and-data-sources.md` - Complete flow
- `08-api-discovery-guide.md` - Swagger search guide
- `09-api-data-types-and-mappings.md` - Data types
- `10-swagger-search-quick-reference.md` - Quick reference

---

## 🎉 You're Ready!

Everything you need is in this folder. Pick your approach and start analyzing!

**Quickest Path**:
1. Open `MASTER-PROMPT.md`
2. Replace `[INSERT APP NAME]` with your app name
3. Copy → Paste to AI agent
4. Get results in 5-10 minutes

**Good luck!** 🚀

---

*All prompts are designed to work with any AI agent (ChatGPT, Claude, Copilot, etc.) or can be followed manually.*

