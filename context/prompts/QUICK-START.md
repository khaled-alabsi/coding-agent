# QUICK START: How to Use These Prompts

## 🎯 Goal
Analyze any application in this monolith to identify data dependencies and find REST API alternatives.

---

## ⚡ 3-Minute Setup

### Option A: Using AI Agent (ChatGPT, Claude, etc.)

**1. Copy System Prompt**
```
File: SYSTEM-PROMPT.md
Action: Copy entire contents
Paste into: AI agent's system/context section
```

**2. Customize User Prompt**
```
File: USER-PROMPT.md
Action: 
- Replace [APP_NAME] with your app (e.g., "kwk", "accountoverview")
- Copy entire contents
Paste into: AI agent's user message
```

**3. Provide Code Access**
```
Option 1: Upload specific files agent requests
Option 2: Give agent folder structure overview
Option 3: Paste relevant code snippets
```

**4. Run Analysis**
```
Agent will:
1. Locate the app
2. Find controllers and endpoints
3. Trace to data sources
4. Suggest REST APIs
5. Provide Swagger search terms
```

---

### Option B: Manual Analysis

**1. Print Reference**
```
File: CODE-PATTERNS.md
Action: Print or keep open as reference
```

**2. Follow USER-PROMPT Steps**
```
File: USER-PROMPT.md
Follow: Step 1-6 manually
Use: CODE-PATTERNS.md to identify patterns
```

**3. Document Findings**
```
File: API-REQUIREMENT-TEMPLATE.md
For each data source: Fill out template
```

---

## 📋 Example: Analyze "KWK" App

### Setup (30 seconds)
```
1. Open: SYSTEM-PROMPT.md
2. Open: USER-PROMPT.md
3. Replace [APP_NAME] with "kwk"
```

### AI Agent Prompt (Copy-Paste)
```
SYSTEM CONTEXT:
[Paste entire SYSTEM-PROMPT.md here]

USER TASK:
Analyze the "kwk" (Kunden werben Kunden) application.
[Paste customized USER-PROMPT.md here]

REFERENCE:
[Paste CODE-PATTERNS.md here]

Please start your analysis.
```

### Expected Output (5-10 minutes from agent)
```markdown
# Dependency Analysis: KWK

## 1. Application Location
- Pattern: Legacy
- Path: `C:\CCB\sources\portal\ccb\ui\pk-webui\kwk\`

## 2. REST Endpoints
| Method | Path | Controller |
|--------|------|------------|
| POST | /sendReference | CrcJsonController |

## 3. Data Sources Identified

### Mainframe: PKVD ⚠️
- File: `sc/productbase/host/.../PersonKundeVertragsDatenV2Hostaccess.java`
- Data: Customer accounts
- Need API: GET /api/accounts/v1/accounts
- Search: "accounts", "customer accounts", "iban"

### Database: CUSTOMER_REFER_CUSTOMER ✅
- Entity: CustomerReferCustomer.java
- Can migrate table

## 4. REST API Requirements
[Detailed requirements for each data source]
```

---

## 🎨 Prompt Variations

### Minimal Prompt (Fast)
```
Analyze [APP_NAME] in C:\CCB\sources\portal.
Find:
1. Location (ucc or ccb/ui)
2. All mainframe calls (files ending in Hostaccess.java)
3. All database tables (@Entity classes)
4. Suggest REST APIs to replace mainframe
Use patterns from CODE-PATTERNS.md
```

### Detailed Prompt (Thorough)
```
[Full SYSTEM-PROMPT.md + USER-PROMPT.md]
```

### Focused Prompt (Specific Need)
```
For [APP_NAME], identify only:
- Mainframe PKVD calls
- What account data is needed
- Suggest Account API endpoint pattern
```

---

## 📊 What You'll Get

### Input
```
App name: "accountoverview"
```

### Output
```markdown
1. App location and structure
2. All REST endpoints
3. Data sources:
   - Mainframe calls → Need REST API
   - Database tables → Can migrate
   - SC services → Check further
   - REST clients → Already good
4. For each mainframe call:
   - Exact fields needed
   - Suggested REST API endpoint
   - Swagger search keywords
5. Migration recommendations
```

---

## ✅ Quality Check

Good output has:
- [x] Exact file paths (not "somewhere in sc folder")
- [x] Specific field names (not "account data")
- [x] Complete class names (not "some service")
- [x] Actionable API suggestions (not "find an API")
- [x] Copy-paste Swagger keywords

Bad output:
- [ ] Vague descriptions
- [ ] Missing file paths
- [ ] Stopped at first service call
- [ ] No specific field names

---

## 🚀 Start Now

### To Analyze an App:

**Step 1**: Choose app name
```
Example: "kwk", "accountoverview", "mobilepayment"
```

**Step 2**: Pick method
```
AI Agent → Use SYSTEM-PROMPT.md + USER-PROMPT.md
Manual → Use CODE-PATTERNS.md + API-REQUIREMENT-TEMPLATE.md
```

**Step 3**: Run analysis
```
AI: Paste prompts and wait
Manual: Follow USER-PROMPT steps
```

**Step 4**: Use results
```
- Search Swagger for suggested APIs
- Test APIs with sample data
- Plan migration
```

---

## 📁 File Checklist

Before starting, have these ready:
- [x] SYSTEM-PROMPT.md (system context)
- [x] USER-PROMPT.md (task definition)
- [x] CODE-PATTERNS.md (reference)
- [x] API-REQUIREMENT-TEMPLATE.md (output format)
- [x] Access to C:\CCB\sources\portal\ folder

---

## 💡 Pro Tips

1. **Start with USER-PROMPT.md** - It has the complete workflow
2. **Use CODE-PATTERNS.md** - Quick pattern matching saves time
3. **Be specific** - "PersonKundeVertragsDatenV2Hostaccess.java" not "some host service"
4. **Trace completely** - Don't stop at first service call
5. **Group logically** - Combine related data into one API requirement

---

## 🎯 Success in 3 Steps

1. **Locate**: Find the app folder
2. **Trace**: Follow dependencies to ultimate sources
3. **Suggest**: Provide REST API alternatives

---

*Ready? Start with USER-PROMPT.md and customize with your app name!*

