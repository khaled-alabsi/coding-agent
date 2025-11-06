# USER PROMPT: Analyze [App Name] Dependencies

## Your Task

Analyze the **[APP_NAME]** application in this banking monolith and identify all data dependencies, then suggest REST API alternatives to replace mainframe/database access.

## Application to Analyze

**Application Name**: `[INSERT APP NAME HERE]`

**Possible Locations** (check these in order):
1. `C:\CCB\sources\portal\ucc\[app-name]\` (UCC pattern - newer apps)
2. `C:\CCB\sources\portal\ccb\ui\pk-webui\[app-name]\` (Legacy pattern - Postbank)
3. `C:\CCB\sources\portal\ccb\ui\msb-webui\[app-name]\` (Legacy pattern - Mittelstand)
4. `C:\CCB\sources\portal\ccb\ui\wp-webui\[app-name]\` (Legacy pattern - Private)

## Context Files Provided

Read these files IN ORDER before starting analysis:

### 1. System Prompt (READ FIRST)
**File**: `SYSTEM-PROMPT.md`
**Purpose**: Understanding the methodology and expected output format

### 2. Code Patterns (READ SECOND)
**File**: `CODE-PATTERNS.md`
**Purpose**: Quick reference for identifying data source types in code

### 3. API Template (REFERENCE)
**File**: `API-REQUIREMENT-TEMPLATE.md`
**Purpose**: Template for documenting each API requirement

## Your Analysis Steps

### Step 1: Locate the Application (5 minutes)
Search for the app in the locations listed above. Report:
- ✅ Found location: `[path]`
- Pattern identified: [UCC / Legacy]
- Key folders: [list main folders]

### Step 2: Find Entry Points (10 minutes)
Locate REST controllers:
- **UCC**: Check `ucc/[app]/process/src/main/java/**/rest/`
- **Legacy**: Check `ccb/ui/[bank]-webui/[app]/rest/src/main/java/`

List all endpoints found:
```
POST /path1 - Description
GET /path2 - Description
```

### Step 3: Trace Data Flow (20 minutes)
For EACH endpoint:
1. Find the controller method
2. Identify which Process it calls
3. In the Process, find all `@Inject @Named` dependencies
4. For each dependency, determine its type:
   - Ends in "DAO" → Database
   - Ends in "Hostaccess" → Mainframe ⚠️
   - Ends in "RestClient" → External API ✅
   - Ends in "Service" → Trace further

### Step 4: Classify Data Sources (15 minutes)
Group findings into categories:

**Mainframe Calls** ⚠️ (CRITICAL - need REST API)
- List each mainframe service
- File path
- What data it retrieves

**Database Tables** ✅ (Can migrate)
- List each `@Entity` class
- Table name
- What data it stores

**SC Services** 🔄 (Check further)
- List each service
- Trace to ultimate source

**External APIs** ✅ (Already good)
- List each RestClient
- Endpoint called

### Step 5: Define API Requirements (20 minutes)
For EACH mainframe call or critical data source:
- Use the API-REQUIREMENT-TEMPLATE.md
- Define exact fields needed
- Suggest REST API endpoint pattern
- Provide Swagger search keywords

### Step 6: Summary & Recommendations (10 minutes)
Provide migration recommendations specific to this app.

## Expected Output Format

```markdown
# Dependency Analysis: [App Name]

## 1. Application Location
- **Pattern**: [UCC / Legacy]
- **Path**: `C:\CCB\sources\portal\[path]`
- **Main Modules**: [list]

## 2. REST Endpoints
| Method | Path | Controller | Description |
|--------|------|------------|-------------|
| POST | /path | ClassName | What it does |

## 3. Data Flow Map
[For main endpoint]
```
Controller → Process → Service → Data Source
[Full class path chain]
```

## 4. Data Sources Identified

### 4.1 Mainframe Calls ⚠️ (Need REST API)

#### Mainframe Source 1: [Name]
- **File**: `[path]/[ClassName].java`
- **Method**: `methodName()`
- **Transaction**: [e.g., PKVD, TVS90]
- **Data Retrieved**: [list fields]
- **Used For**: [business purpose]

[Repeat for each mainframe call]

### 4.2 Database Tables ✅ (Can Migrate)

#### Table 1: [TABLE_NAME]
- **Entity Class**: `[path]/[EntityClass].java`
- **Columns**: [list key columns]
- **Purpose**: [what data is stored]
- **Owner**: Application-owned

[Repeat for each table]

### 4.3 SC Service Dependencies 🔄

#### Service 1: [ServiceName]
- **Interface**: `[path]/[ServiceInterface].java`
- **Implementation**: `[path]/[ServiceImpl].java`
- **Ultimate Source**: [Mainframe / Database / External API]
- **Data Provided**: [list]

[Repeat for each service]

### 4.4 External APIs ✅ (Already Using REST)

#### API 1: [API Name]
- **Client**: `[path]/[RestClient].java`
- **Endpoint**: `[URL pattern]`
- **Purpose**: [what data]
- **Status**: ✅ Already REST API

## 5. REST API Requirements

[Use API-REQUIREMENT-TEMPLATE for each]

### API Requirement 1: [Name]
**Current Source**: Mainframe PKVD
**Data Needed**:
```typescript
{
  field1: string;    // REQUIRED
  field2: number;    // REQUIRED
  field3?: boolean;  // OPTIONAL
}
```

**Suggested Endpoint**:
```
GET /api/[service]/v1/[resource]?param={value}
```

**Swagger Search**:
- Keywords: "keyword1", "keyword2"
- Expected paths: `/api/path1`, `/api/path2`

**Field Mapping**:
| Java Field | API Field | Type | Required |
|------------|-----------|------|----------|
| javaName | apiName | string | Yes |

[Repeat for each requirement]

## 6. Migration Recommendations

### Critical Dependencies
1. **[Dependency Name]** - Mainframe PKVD
   - Impact: HIGH
   - Recommendation: Find Account API with permissions
   - Fallback: Wrapper API around PKVD

### Low Risk Items
1. **[Item Name]** - Database table
   - Can migrate directly
   - No external dependency

### Timeline Estimate
- **Discovery**: [X] days
- **API Integration**: [X] days
- **Testing**: [X] days
- **Total**: [X] days

## 7. Next Steps
1. [ ] Search Swagger for suggested APIs
2. [ ] Test found APIs with sample data
3. [ ] Validate response schemas
4. [ ] Create integration plan
5. [ ] Estimate effort for implementation
```

## Key Reminders

1. **Be Specific**: Always provide EXACT file paths, not just folder names
2. **Trace Completely**: Don't stop at first service call - find the ultimate source
3. **Group Logically**: Combine related data into single API requirements
4. **Real Examples**: Use actual field names from the code
5. **Actionable**: Provide concrete Swagger search terms that can be copy-pasted

## Common Mistakes to Avoid

❌ **DON'T**: Say "calls a service" without specifying which service
✅ **DO**: Say "calls PersonKundeVertragsDatenV2Hostaccess.callService() in file sc/productbase/host/.../PersonKundeVertragsDatenV2Hostaccess.java"

❌ **DON'T**: Say "needs account data"
✅ **DO**: List exact fields: "iban (string), accountOwnerName (string), permissions.canReceiveRewards (boolean)"

❌ **DON'T**: Stop at "calls ProductService"
✅ **DO**: Trace further: "ProductService → PkvdRetriever → PersonKundeVertragsDatenV2Hostaccess → MAINFRAME"

## Files and Paths Reference

### Project Root
```
C:\CCB\sources\portal\
```

### Common File Locations

**Controllers:**
```
ucc/[app]/process/src/main/java/**/*Controller.java
ccb/ui/[bank]-webui/[app]/rest/src/main/java/**/*Controller.java
```

**Processes:**
```
ucc/[app]/process/src/main/java/**/*ProcessImpl.java
ccb/middletier/process/[app]/src/main/java/**/*ProcessImpl.java
```

**Services:**
```
ccb/middletier/service/[app]/src/main/java/**/*ServiceImpl.java
sc/[service]/service/src/main/java/**/*ServiceImpl.java
```

**DAOs:**
```
ccb/middletier/service/[app]/src/main/java/**/dao/**/*DAOImpl.java
```

**Entities:**
```
ccb/middletier/service/[app]/src/main/java/**/dao/**/*Entity.java
ccb/middletier/service/[app]/src/main/java/**/entity/**/*.java
```

**Mainframe:**
```
sc/[service]/host/src/main/java/**/*Hostaccess.java
```

**REST Clients:**
```
sc/[service]/remote/src/main/java/**/*RestClient.java
```

## Success Criteria

Your analysis is complete when you have:
- ✅ Identified ALL data sources (mainframe, database, services, APIs)
- ✅ Provided exact file paths for each dependency
- ✅ Listed exact fields needed from each source
- ✅ Suggested specific REST API endpoint patterns
- ✅ Provided actionable Swagger search keywords
- ✅ Grouped data into logical API requirements
- ✅ Given migration recommendations

## Start Your Analysis

Begin by reading the SYSTEM-PROMPT.md file, then search for the application in the locations listed above.

**Application to analyze**: [INSERT APP NAME HERE]

Good luck! 🚀

