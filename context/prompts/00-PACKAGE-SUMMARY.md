# ✅ PROMPTS PACKAGE - COMPLETE

## Created: November 6, 2025

---

## 📦 Package Summary

**Location**: `C:\CCB\sources\portal\context\prompts\`

**Purpose**: Analyze applications in banking monolith to identify data dependencies and suggest REST API alternatives

**Total Files**: 9

**Ready to Use**: ✅ Yes

---

## 📁 All Files Created

| # | File | Size | Purpose | Read First |
|---|------|------|---------|-----------|
| 1 | **00-START-HERE.md** | Summary | Complete package overview | ⭐ YES |
| 2 | **MASTER-PROMPT.md** | Compact | All-in-one prompt for AI | ⭐⭐ Use This |
| 3 | **QUICK-START.md** | Quick | 3-minute getting started | ✅ If new |
| 4 | **SYSTEM-PROMPT.md** | Full | Detailed methodology | 📖 If thorough |
| 5 | **USER-PROMPT.md** | Template | Task definition | 📝 Customize |
| 6 | **CODE-PATTERNS.md** | Reference | Pattern identification | 🔍 Keep open |
| 7 | **API-REQUIREMENT-TEMPLATE.md** | Template | Documentation format | 📋 Per source |
| 8 | **README.md** | Guide | Full instructions | 📚 Overview |
| 9 | **INDEX.md** | Navigation | File index | 📑 Find stuff |

---

## 🚀 Three Ways to Use

### 1️⃣ FASTEST (5 minutes)
```
File: MASTER-PROMPT.md
Steps:
1. Replace [INSERT APP NAME] with your app
2. Copy entire file
3. Paste to ChatGPT/Claude
4. Get analysis
```

### 2️⃣ STRUCTURED (15 minutes)
```
Files: SYSTEM-PROMPT.md + USER-PROMPT.md + CODE-PATTERNS.md
Steps:
1. Copy SYSTEM-PROMPT to system/context
2. Customize USER-PROMPT with app name
3. Reference CODE-PATTERNS as needed
4. Get detailed analysis
```

### 3️⃣ MANUAL (2-3 hours)
```
Files: All files
Steps:
1. Read README.md
2. Follow USER-PROMPT steps manually
3. Use CODE-PATTERNS for identification
4. Fill API-REQUIREMENT-TEMPLATE per source
5. Create comprehensive report
```

---

## 🎯 What You Get

### Input
```
App name: "kwk" (or any app)
```

### Output (Example)
```markdown
# Dependency Analysis: KWK

## Mainframe Calls ⚠️
1. PKVD - Customer Accounts
   File: sc/productbase/host/.../PersonKundeVertragsDatenV2Hostaccess.java
   Data: iban, accountOwnerName, permissions
   API: GET /api/accounts/v1/accounts?customerId={id}
   Search: "accounts", "customer accounts", "iban"

## Database Tables ✅
1. CUSTOMER_REFER_CUSTOMER
   Can migrate to microservice

## SC Services 🔄
1. NaturalPersonAPIV3Service
   Ultimately calls mainframe

## REST APIs ✅
1. DatalakeRestClient
   Already using REST
```

---

## ✅ What Makes This Special

### Comprehensive
- ✅ All data source types covered
- ✅ Complete tracing methodology
- ✅ Proven on real KWK analysis

### Actionable
- ✅ Exact file paths (not vague)
- ✅ Specific field names
- ✅ Copy-paste Swagger keywords
- ✅ Real API endpoint patterns

### Flexible
- ✅ Quick option (MASTER-PROMPT)
- ✅ Detailed option (SYSTEM+USER)
- ✅ Manual option (CODE-PATTERNS)
- ✅ Any AI agent or human

### Compact
- ✅ Everything in one folder
- ✅ Clear file naming (00-*, MASTER-*, etc.)
- ✅ Multiple entry points
- ✅ Cross-referenced

---

## 🎓 What Problem This Solves

### Before
```
❌ "I need to migrate this app but don't know what it depends on"
❌ "Where does this data come from?"
❌ "What REST APIs should I look for?"
❌ "How do I search Swagger?"
❌ "This will take weeks to figure out"
```

### After
```
✅ "Here's every dependency with exact file paths"
✅ "Data comes from PKVD mainframe, here's the exact file"
✅ "Search for these specific APIs: GET /api/accounts/v1/..."
✅ "Use these keywords in Swagger: 'accounts', 'iban', etc."
✅ "Complete analysis in 15 minutes"
```

---

## 📊 Proven Results

**Based on KWK Analysis**:
- ✅ Identified mainframe PKVD as primary account source
- ✅ Suggested specific Account API endpoints
- ✅ Provided exact Swagger search keywords
- ✅ Mapped all fields (Java → REST API)
- ✅ Created migration recommendations

**Can be applied to ANY app** in the monolith.

---

## 💡 Best Practices

### ✅ DO
- Start with MASTER-PROMPT.md for quick wins
- Be specific with app names
- Trace dependencies completely
- Document exact file paths
- Use templates consistently

### ❌ DON'T
- Skip steps in the analysis
- Stop at first service call
- Use vague descriptions
- Forget Swagger search keywords
- Ignore ultimate data source

---

## 🎯 Success Criteria

You'll know it worked when you have:
- ✅ Complete list of mainframe calls (with files)
- ✅ Specific REST API endpoints suggested
- ✅ Swagger keywords that find APIs
- ✅ Field mappings (current → API)
- ✅ Clear migration path

---

## 📞 How to Get Started

### Step 1: Choose File
- Quick → MASTER-PROMPT.md
- Detailed → SYSTEM-PROMPT.md + USER-PROMPT.md
- Manual → CODE-PATTERNS.md

### Step 2: Customize
- Replace [INSERT APP NAME] with your app
- Example: "kwk", "accountoverview", "mobilepayment"

### Step 3: Run
- AI Agent → Copy/paste prompt
- Manual → Follow steps in USER-PROMPT.md

### Step 4: Use Results
- Search Swagger for suggested APIs
- Test APIs with sample data
- Plan migration

---

## 🌟 Special Features

### MASTER-PROMPT.md
- ⭐ All-in-one file
- ⭐ Compact but complete
- ⭐ Copy-paste ready
- ⭐ Works with any AI agent

### CODE-PATTERNS.md
- 🔍 Quick pattern lookup
- 🔍 Real code examples
- 🔍 Identification checklist
- 🔍 File location patterns

### API-REQUIREMENT-TEMPLATE.md
- 📋 Professional documentation
- 📋 Complete with examples
- 📋 Reusable template
- 📋 Swagger search included

---

## 📚 Additional Resources

### In This Folder
- All 9 prompt files (complete package)

### In Parent Folder
- `../kwk-migration/00-CRITICAL-FINDINGS.md`
- `../kwk-migration/07-kwk-business-flow-and-data-sources.md`
- `../kwk-migration/08-api-discovery-guide.md`
- `../kwk-migration/09-api-data-types-and-mappings.md`

---

## 🎉 You're All Set!

Everything needed for dependency analysis is ready:
- ✅ Comprehensive prompts
- ✅ Pattern references
- ✅ Documentation templates
- ✅ Multiple usage options
- ✅ Proven methodology

**Pick your method and start analyzing!**

---

## 📝 Quick Reference

| Need | Use This File | Time |
|------|--------------|------|
| Fastest analysis | MASTER-PROMPT.md | 5 min |
| Learn system | QUICK-START.md | 3 min |
| Detailed analysis | SYSTEM-PROMPT.md + USER-PROMPT.md | 15 min |
| Manual analysis | CODE-PATTERNS.md | 2-3 hours |
| Documentation | API-REQUIREMENT-TEMPLATE.md | Per source |
| Overview | README.md or 00-START-HERE.md | 10 min |

---

## 🚀 Next Action

**Recommended**: Start with `MASTER-PROMPT.md`
1. Open the file
2. Replace `[INSERT APP NAME]` with your app name
3. Copy entire file
4. Paste to AI agent
5. Get complete dependency analysis in minutes

**Good luck!** 🎯

---

*Created November 6, 2025 - Ready for immediate use*

