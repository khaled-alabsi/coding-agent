
**Don't understand pattern?**  
→ See CODE-PATTERNS.md examples

**Output format unclear?**  
→ Check API-REQUIREMENT-TEMPLATE.md

**General questions?**  
→ Read README.md troubleshooting section

---

## 📞 Quick Links

| Need | File | Section |
|------|------|---------|
| Get started | QUICK-START.md | Top |
| Understand system | README.md | "How to Use" |
| Set up AI agent | SYSTEM-PROMPT.md | Full file |
| Define task | USER-PROMPT.md | "Your Task" |
| Identify pattern | CODE-PATTERNS.md | Pattern sections |
| Document finding | API-REQUIREMENT-TEMPLATE.md | Full template |

---

*Use this index to quickly find what you need!*
# Prompts Folder - Complete Index

## 📚 All Files in This Folder

| File | Purpose | Size | Use When |
|------|---------|------|----------|
| **QUICK-START.md** | How to use these prompts | Quick | Starting fresh |
| **README.md** | Overview and guide | Full | Understanding system |
| **SYSTEM-PROMPT.md** | Main AI agent instructions | Full | Setting up agent |
| **USER-PROMPT.md** | Task definition template | Full | Defining analysis task |
| **CODE-PATTERNS.md** | Code pattern reference | Quick | Analyzing code |
| **API-REQUIREMENT-TEMPLATE.md** | Documentation template | Template | Documenting findings |
| **INDEX.md** | This file | Quick | Finding what you need |

---

## 🚀 Start Here

### Never Used Before?
→ Read **QUICK-START.md** (3 minutes)

### Want Full Understanding?
→ Read **README.md** (10 minutes)

### Ready to Analyze?
→ Use **USER-PROMPT.md** with your app name

### Analyzing Code Manually?
→ Keep **CODE-PATTERNS.md** open as reference

### Documenting Findings?
→ Use **API-REQUIREMENT-TEMPLATE.md** for each data source

---

## 🎯 Quick Reference

### To Analyze App with AI Agent:
1. Copy **SYSTEM-PROMPT.md** → System context
2. Customize **USER-PROMPT.md** → User task
3. Reference **CODE-PATTERNS.md** → Patterns guide
4. Get analysis output

### To Analyze App Manually:
1. Follow steps in **USER-PROMPT.md**
2. Use **CODE-PATTERNS.md** to identify sources
3. Fill **API-REQUIREMENT-TEMPLATE.md** for each source
4. Create summary report

---

## 📂 File Descriptions

### QUICK-START.md
**What**: 3-minute guide to get started  
**Contains**:
- Setup instructions (AI agent or manual)
- Example prompts (copy-paste ready)
- Expected output preview
- Success criteria

**Read First**: Yes, if new to this system

---

### README.md
**What**: Complete overview of prompts system  
**Contains**:
- File purposes
- How to use workflow
- Example scenario
- What agent will find
- Troubleshooting guide

**Read First**: After QUICK-START if you want details

---

### SYSTEM-PROMPT.md
**What**: Main instructions for AI agent  
**Contains**:
- Agent's mission
- Monolith structure overview
- Data source identification patterns
- Analysis methodology
- Output format specification

**Use**: Copy entire file into AI agent's system/context prompt

**Size**: ~8,000 words (comprehensive)

---

### USER-PROMPT.md
**What**: Task definition for specific app  
**Contains**:
- Application name placeholder [APP_NAME]
- Step-by-step analysis process
- Expected output format
- File location references
- Success criteria

**Use**: Customize app name, then give to AI agent as task

**Size**: ~3,000 words

**Customize**: Replace `[APP_NAME]` with actual app name

---

### CODE-PATTERNS.md
**What**: Quick reference for code patterns  
**Contains**:
- Mainframe access patterns
- Database (JPA/DAO) patterns
- SC service patterns
- REST client patterns
- Quick identification checklist

**Use**: Keep open while analyzing code

**Size**: ~4,000 words (reference guide)

---

### API-REQUIREMENT-TEMPLATE.md
**What**: Template for each API requirement  
**Contains**:
- Current implementation section
- Data structure specification
- REST API suggestion format
- Swagger search hints
- Field mapping tables

**Use**: Copy and fill out for each data source identified

**Size**: ~2,000 words (template with example)

---

## 🎨 Usage Patterns

### Pattern 1: Quick AI Analysis
```
Time: 15 minutes
Files: SYSTEM-PROMPT.md + USER-PROMPT.md
Output: Complete dependency analysis
```

### Pattern 2: Detailed Manual Analysis
```
Time: 2-3 hours
Files: All files in order
Output: Comprehensive documentation
```

### Pattern 3: Focused Investigation
```
Time: 30 minutes
Files: CODE-PATTERNS.md + API-REQUIREMENT-TEMPLATE.md
Output: Specific data source documentation
```

---

## 📊 File Dependency Map

```
QUICK-START.md
    ↓ (references)
README.md
    ↓ (references)
SYSTEM-PROMPT.md ──→ CODE-PATTERNS.md ──→ API-REQUIREMENT-TEMPLATE.md
    ↑                     ↑                        ↑
    │                     │                        │
    └─────────────── USER-PROMPT.md ───────────────┘
```

---

## ✅ Checklist: Do I Have Everything?

Before starting analysis:
- [ ] QUICK-START.md - Read for overview
- [ ] SYSTEM-PROMPT.md - Ready to copy to AI
- [ ] USER-PROMPT.md - Customized with app name
- [ ] CODE-PATTERNS.md - Open as reference
- [ ] API-REQUIREMENT-TEMPLATE.md - Ready to duplicate
- [ ] Access to C:\CCB\sources\portal\ folder

---

## 🎯 Common Use Cases

### Use Case 1: "Analyze new app for migration"
**Files Needed**: SYSTEM-PROMPT.md, USER-PROMPT.md  
**Method**: AI agent  
**Time**: 15 minutes  
**Output**: Full dependency analysis

### Use Case 2: "Document specific mainframe call"
**Files Needed**: CODE-PATTERNS.md, API-REQUIREMENT-TEMPLATE.md  
**Method**: Manual  
**Time**: 20 minutes  
**Output**: Single API requirement doc

### Use Case 3: "Verify existing analysis"
**Files Needed**: CODE-PATTERNS.md  
**Method**: Manual verification  
**Time**: 30 minutes  
**Output**: Validated findings

### Use Case 4: "Train team on methodology"
**Files Needed**: README.md, CODE-PATTERNS.md  
**Method**: Training session  
**Time**: 1 hour  
**Output**: Team knowledge

---

## 📈 Maturity Levels

### Level 1: Beginner
**Read**: QUICK-START.md, README.md  
**Use**: Pre-built prompts as-is  
**Customize**: Minimal (just app name)

### Level 2: Intermediate
**Read**: All files  
**Use**: Templates with modifications  
**Customize**: Adjust for specific needs

### Level 3: Advanced
**Read**: Use as reference  
**Use**: Create custom variations  
**Customize**: Adapt methodology

---

## 🔗 Related Resources

### In Parent Folder (../kwk-migration/)
- `00-CRITICAL-FINDINGS.md` - Example analysis results
- `07-kwk-business-flow-and-data-sources.md` - Complete flow example
- `08-api-discovery-guide.md` - How to find APIs in Swagger
- `09-api-data-types-and-mappings.md` - API data types
- `10-swagger-search-quick-reference.md` - Swagger search guide

### In This Folder
- All prompt files described above

---

## 💡 Tips

1. **Start Small**: Analyze simple app first (e.g., KWK)
2. **Be Thorough**: Don't skip steps
3. **Document Well**: Use templates consistently
4. **Iterate**: Refine prompts based on results
5. **Share**: Use for team training

---

## 🆘 Need Help?

**Can't find app?**  
→ Check locations in USER-PROMPT.md

