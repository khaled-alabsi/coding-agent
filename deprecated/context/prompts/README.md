# Prompts Folder - Application Dependency Analyzer

## Purpose
This folder contains prompts and templates to help an AI agent (or human) analyze applications in this banking monolith to identify data dependencies and suggest REST API alternatives.

---

## 📁 Files in This Folder

### 1. **SYSTEM-PROMPT.md** (Main Instructions)
The complete system prompt that defines:
- Agent's mission and role
- Monolith structure overview
- Data source identification patterns
- Analysis methodology
- Expected output format

**Use**: Give this to an AI agent as the system/context prompt

---

### 2. **CODE-PATTERNS.md** (Quick Reference)
Code patterns for identifying different data sources:
- Mainframe access patterns
- Database (JPA/DAO) patterns
- SC service patterns
- REST client patterns
- Process and controller patterns

**Use**: Quick lookup when analyzing code

---

### 3. **API-REQUIREMENT-TEMPLATE.md** (Documentation Template)
Template for documenting each REST API requirement identified:
- Current implementation details
- Data structure needed
- Suggested REST API specification
- Swagger search hints
- Field mappings

**Use**: Copy and fill out for each data source

---

### 4. **USER-PROMPT.md** (Task Definition)
The user-facing prompt that defines:
- Specific application to analyze
- Step-by-step analysis process
- Expected output format
- File location references

**Use**: Customize with app name and give to AI agent

---

### 5. **README.md** (This File)
Overview of the prompts folder

---

## 🚀 How to Use These Prompts

### For AI Agents (e.g., ChatGPT, Claude, etc.)

**Step 1**: Load System Context
```
Read and understand these files in order:
1. SYSTEM-PROMPT.md (full context)
2. CODE-PATTERNS.md (reference guide)
3. API-REQUIREMENT-TEMPLATE.md (output format)
```

**Step 2**: Provide Task
```
Customize USER-PROMPT.md with the application name:
- Replace [APP_NAME] with actual app name (e.g., "kwk", "accountoverview")
- Provide this as the user task
```

**Step 3**: Provide Code Access
- Give agent access to the C:\CCB\sources\portal folder structure
- Or provide relevant code files on request

**Step 4**: Review Output
- Agent will analyze the app
- Output will follow the format in USER-PROMPT.md
- Use API-REQUIREMENT-TEMPLATE for each data source

### For Humans

**Step 1**: Read SYSTEM-PROMPT.md to understand the methodology

**Step 2**: Use CODE-PATTERNS.md as a cheat sheet while analyzing code

**Step 3**: For each data source found, fill out API-REQUIREMENT-TEMPLATE.md

**Step 4**: Follow the structure in USER-PROMPT.md for your final report

---

## 📊 Example Workflow

### Scenario: Analyze the "accountoverview" application

1. **Prepare the prompt**:
   - Open USER-PROMPT.md
   - Replace `[APP_NAME]` with "accountoverview"
   
2. **Give to AI Agent**:
   ```
   System Prompt: [Contents of SYSTEM-PROMPT.md]
   User Task: [Customized USER-PROMPT.md]
   Reference: [CODE-PATTERNS.md]
   ```

3. **Agent analyzes**:
   - Searches for app in ucc/accountoverview or ccb/ui/*/accountoverview
   - Finds controllers and endpoints
   - Traces process layer
   - Identifies data sources (mainframe/database/services)
   - Groups data into API requirements

4. **Agent outputs**:
   - Complete dependency analysis
   - List of mainframe calls → Need REST APIs
   - List of database tables → Can migrate
   - Suggested REST API endpoints
   - Swagger search keywords

5. **You use the output**:
   - Search Swagger for suggested APIs
   - Test APIs with sample data
   - Plan migration based on findings

---

## 🎯 What the Agent Will Find

### For Each Application, Agent Identifies:

#### 🔴 Critical: Mainframe Dependencies
```
Source: PersonKundeVertragsDatenV2Hostaccess
File: sc/productbase/host/.../PersonKundeVertragsDatenV2Hostaccess.java
Data: Customer accounts with IBAN, permissions
Suggested API: GET /api/accounts/v1/accounts?customerId={id}
Search: "accounts", "customer accounts", "iban"
```

#### ✅ Can Migrate: Database Tables
```
Table: CUSTOMER_REFER_CUSTOMER
Entity: CustomerReferCustomer.java
Columns: CRC_ID, CRC_CODE, CRC_IBAN, etc.
Owner: Application-owned
Action: Export schema and migrate
```

#### 🔄 Check Further: SC Services
```
Service: NaturalPersonAPIV3Service
Implementation: sc/person/service/.../NaturalPersonAPIV3ServiceImpl.java
Ultimate Source: [Traced to mainframe/database/API]
Action: Check if REST API exists
```

#### ✅ Already Good: REST Clients
```
Client: DatalakeTransactionsSearchRestClient
Endpoint: /payments-api/v1/bulktransactions/search
Status: Already calling REST API
Action: Document and potentially reuse
```

---

## 🎓 Key Concepts

### Data Source Types

| Type | Pattern | Action for Migration |
|------|---------|---------------------|
| **Mainframe** | `*Hostaccess.java` | ⚠️ Find REST API or create wrapper |
| **Database** | `@Entity`, `*DAO.java` | ✅ Can migrate table schema |
| **SC Service** | `*Service.java` | 🔄 Trace to ultimate source |
| **REST API** | `*RestClient.java` | ✅ Already good, document endpoint |

### Analysis Goals

1. **Identify Dependencies**: What does this app need to function?
2. **Classify Sources**: Where does each piece of data come from?
3. **Group by API**: What REST APIs could provide this data?
4. **Provide Search Hints**: How to find these APIs in Swagger?

---

## 📝 Output Example

After analysis, you'll have:

```markdown
# App: accountoverview

## Mainframe Dependencies (Need REST APIs)
1. Account List - PKVD Mainframe
   - Suggested API: GET /api/accounts/v1/accounts
   - Search: "accounts", "customer accounts"
   
2. Transaction History - Mainframe
   - Suggested API: GET /api/transactions/v1/transactions
   - Search: "transactions", "account transactions"

## Database Tables (Can Migrate)
1. USER_PREFERENCES
   - Entity: UserPreference.java
   - Can export and migrate

## SC Services (Check for APIs)
1. CustomerService
   - Ultimately calls mainframe
   - Check if Customer API exists
   
## REST APIs (Already Using)
1. DatalakeClient
   - Endpoint: /datalake/api/v1/search
   - Already good
```

---

## 🔧 Customization

### To Analyze Different App
Edit USER-PROMPT.md:
- Change `[APP_NAME]` to your app name
- Adjust file locations if different pattern

### To Focus on Specific Aspect
Edit SYSTEM-PROMPT.md:
- Emphasize specific data sources
- Add custom output sections
- Adjust analysis depth

### To Add New Patterns
Edit CODE-PATTERNS.md:
- Add new code signature
- Add new file location pattern
- Add identification rules

---

## 📚 Related Documentation

In parent folder (../kwk-migration/):
- `07-kwk-business-flow-and-data-sources.md` - Example analysis for KWK
- `08-api-discovery-guide.md` - How to find APIs in Swagger
- `09-api-data-types-and-mappings.md` - Data type specifications
- `10-swagger-search-quick-reference.md` - Quick search guide
- `00-CRITICAL-FINDINGS.md` - Example findings from KWK analysis

---

## ✅ Quality Checklist

Good analysis includes:
- [ ] Exact file paths (not just folder names)
- [ ] Complete class/method names
- [ ] Specific field names and types
- [ ] Ultimate data source (traced to end)
- [ ] Concrete API endpoint suggestions
- [ ] Copy-paste ready Swagger search terms
- [ ] Field mapping tables
- [ ] Migration recommendations

---

## 💡 Tips for Best Results

1. **Be Patient**: Tracing dependencies takes time
2. **Be Thorough**: Don't stop at first service call
3. **Be Specific**: Exact paths > vague descriptions
4. **Be Practical**: Focus on actionable findings
5. **Use Templates**: Consistency helps comparison

---

## 🆘 Troubleshooting

**Problem**: Agent can't find the app
- **Solution**: Check all 4 possible locations (ucc, pk-webui, msb-webui, wp-webui)
- **Try**: Search for app name in folder names

**Problem**: Too many dependencies
- **Solution**: Focus on main endpoints first
- **Prioritize**: Mainframe calls are most critical

**Problem**: Can't trace service to source
- **Solution**: Check *ServiceImpl.java for the service
- **Look for**: What methods it calls, what it injects

**Problem**: Unclear data requirements
- **Solution**: Check request/response DTOs
- **Files**: *Request.java, *Response.java in processinterface/

---

## 🎯 Success Metrics

You've succeeded when you can:
- ✅ List all mainframe calls with exact files
- ✅ Suggest specific REST API endpoints for each
- ✅ Provide Swagger keywords that find relevant APIs
- ✅ Map exact fields from current → API format
- ✅ Estimate migration effort

---

## 📞 Support

For questions about:
- **Methodology**: See SYSTEM-PROMPT.md
- **Code patterns**: See CODE-PATTERNS.md
- **Output format**: See API-REQUIREMENT-TEMPLATE.md
- **Examples**: See ../kwk-migration/ folder

---

*These prompts are designed to make dependency analysis fast, thorough, and actionable.*

