# MASTER PROMPT: Application Dependency Analyzer
## Ready-to-Use Prompt for AI Agents

---

## 🎯 YOUR MISSION

You are an expert code analyzer for banking applications. Analyze the given application in this Java monolith to:
1. Identify ALL data sources (mainframe, database, services, APIs)
2. Map complete data flow from user request to data source
3. Suggest REST API alternatives to replace mainframe/database dependencies
4. Provide actionable Swagger search keywords

---

## 📍 PROJECT STRUCTURE

```
C:\CCB\sources\portal\
├── ucc/[app]/               ← Newer apps (UCC pattern)
│   ├── process/             ← Business logic + REST controllers
│   ├── process-interface/   ← API contracts
│   └── ui/                  ← UI (optional)
│
├── ccb/                     ← Core platform (Legacy pattern)
│   ├── ui/[bank]-webui/[app]/  ← UI + REST controllers
│   └── middletier/
│       ├── process/[app]/   ← Business logic
│       └── service/[app]/   ← Data access
│
└── sc/[service]/            ← Service Clusters
    ├── api/                 ← Service interfaces
    ├── service/             ← Service implementations
    ├── host/                ← Mainframe access ⚠️
    └── remote/              ← REST clients ✅
```

---

## 🔍 DATA SOURCE PATTERNS (Critical!)

### ⚠️ MAINFRAME (Need REST API)
```java
// File pattern: **/host/**/*Hostaccess.java
import com.commerzbank.frame.hostaccess.*;

public class PersonKundeVertragsDatenV2Hostaccess {
    protected SomeReply processResponse(...) { }
}

// Usage
@Inject @Named("pkvdHostaccess")
private PersonKundeVertragsDatenV2Hostaccess hostaccess;
```
**Action**: ⚠️ This calls IBM z/OS mainframe → MUST suggest REST API

### ✅ DATABASE (Can Migrate)
```java
// File pattern: **/dao/**/*DAOImpl.java, **/entity/**/*.java
@Entity
@Table(name = "CUSTOMER_REFER_CUSTOMER")
public class CustomerReferCustomer { }

@CCBComponent
public class KwkDAOImpl extends AbstractJpaDAO<...> { }
```
**Action**: ✅ Application-owned table → Can migrate

### 🔄 SC SERVICE (Trace Further)
```java
@Inject @Named("naturalPersonAPIV3Service")
private NaturalPersonAPIV3Service service;
```
**Action**: Find ServiceImpl and check what IT calls (mainframe/DB/API)

### ✅ REST CLIENT (Already Good)
```java
// File pattern: **/remote/**/*RestClient.java
@Inject
private ApiBankingRestTemplate restTemplate;

restTemplate.exchange(url, HttpMethod.POST, ...);
```
**Action**: ✅ Already calling REST API → Document endpoint

---

## 📋 YOUR ANALYSIS STEPS

### Step 1: LOCATE (5 min)
Search for app in:
1. `ucc/[app-name]/`
2. `ccb/ui/pk-webui/[app-name]/`
3. `ccb/ui/msb-webui/[app-name]/`
4. `ccb/ui/wp-webui/[app-name]/`

**Output**: Exact path found, pattern identified

### Step 2: FIND ENDPOINTS (10 min)
**UCC**: `ucc/[app]/process/src/main/java/**/rest/*Controller.java`  
**Legacy**: `ccb/ui/*/[app]/rest/src/main/java/**/*Controller.java`

**Extract**:
- Endpoint: `@RequestMapping("/path")`
- Method: `POST`/`GET`/`PUT`/`DELETE`
- Process called

### Step 3: TRACE DATA FLOW (20 min)
For main endpoint:
1. Find Controller → which Process?
2. Find Process → `@Inject @Named` dependencies?
3. For each dependency → what type?
   - `*DAO` → Database
   - `*Hostaccess` → Mainframe ⚠️
   - `*RestClient` → API ✅
   - `*Service` → Trace further

### Step 4: CLASSIFY SOURCES (15 min)
Group into:
- **Mainframe** ⚠️ (file paths, data retrieved)
- **Database** ✅ (table names, entity classes)
- **SC Services** 🔄 (ultimate source?)
- **REST APIs** ✅ (endpoints already called)

### Step 5: SUGGEST APIs (20 min)
For EACH mainframe call:
```markdown
### API Requirement: [Name]
**Current**: PersonKundeVertragsDatenV2Hostaccess (mainframe PKVD)
**Data Needed**:
- iban: string (REQUIRED)
- accountOwnerName: string (REQUIRED)
- permissions.canReceiveRewards: boolean (REQUIRED)

**Suggested REST API**:
GET /api/accounts/v1/accounts?customerId={id}&permission=REWARD

**Swagger Search**:
- Keywords: "accounts", "customer accounts", "iban", "eligible"
- Paths: /api/accounts-api/*, /api/customer-api/*/accounts
```

---

## 📊 OUTPUT FORMAT (Required!)

```markdown
# Dependency Analysis: [App Name]

## 1. Location
- **Pattern**: UCC / Legacy
- **Path**: `C:\CCB\sources\portal\[exact path]`

## 2. REST Endpoints
| Method | Path | Controller | Purpose |
|--------|------|------------|---------|
| POST | /send | CrcController | Save referral |

## 3. Data Flow (Main Endpoint)
```
CrcJsonController.sendReference()
  → CustomerReferCustomerProcessImpl.sendReference()
    → ProductServiceImpl.retrieveProductList()
      → PkvdProductIdentifierRetrieverService.retrievePersonKundeVertragsDaten()
        → PersonKundeVertragsDatenV2Hostaccess.callService()
          → MAINFRAME (PKVD/TVS90) ⚠️
```

## 4. Data Sources

### 4.1 Mainframe Calls ⚠️ (CRITICAL)

#### PKVD - Customer Accounts
- **File**: `sc/productbase/host/.../PersonKundeVertragsDatenV2Hostaccess.java`
- **Method**: `callService(PkvdRequest)`
- **Transaction**: TVS90
- **Data Retrieved**:
  - iban: string
  - accountOwnerName: string
  - productType: string
  - permissions: object
- **Used For**: Get customer accounts for reward settlement

**REST API Suggestion**:
```
GET /api/accounts/v1/accounts?customerId={id}&includePermissions=true
Response: { accounts: [{ iban, accountOwnerName, permissions: { canReceiveRewards } }] }
```

**Swagger Search**:
- "accounts", "customer accounts", "iban", "settlement accounts"
- Paths: /api/accounts-api/*, /api/product-api/*/accounts

### 4.2 Database Tables ✅ (Can Migrate)

#### CUSTOMER_REFER_CUSTOMER
- **Entity**: `ccb/middletier/service/kwk/.../CustomerReferCustomer.java`
- **Table**: `CUSTOMER_REFER_CUSTOMER`
- **Columns**: CRC_ID, CRC_CODE, CRC_IBAN, CRC_EMAIL_ADDRESS, etc.
- **Purpose**: Store referral records
- **Owner**: Application-owned
- **Action**: Export schema and migrate to microservice DB

### 4.3 SC Services 🔄

#### NaturalPersonAPIV3Service
- **Interface**: `sc/person/api/.../NaturalPersonAPIV3Service.java`
- **Implementation**: Check where it ultimately gets data
- **Traced To**: [Mainframe / Database / External API]

### 4.4 External APIs ✅

#### DatalakeRestClient
- **File**: `sc/transaction/remote/.../DatalakeRestClient.java`
- **Endpoint**: `/payments-api/v1/bulktransactions/search`
- **Already REST**: Yes
- **Action**: Document and potentially reuse

## 5. REST API Requirements Summary

| Data Needed | Current Source | Suggested API | Search Keywords |
|-------------|---------------|---------------|-----------------|
| Account list | PKVD Mainframe | GET /api/accounts/v1/accounts | "accounts", "iban" |
| Customer name | Natural Person API | GET /api/customers/v3/{id} | "customer", "person" |
| IBAN format | IBAN Converter | POST /api/iban/v1/convert | "iban", "convert" |

## 6. Migration Recommendations

**Critical Dependencies**:
1. Replace PKVD with Account API ⚠️ HIGH PRIORITY
2. Keep calling Customer API (already REST)

**Can Migrate Easily**:
1. CUSTOMER_REFER_CUSTOMER table ✅

**Timeline**: 4-6 weeks (API discovery + integration + testing)
```

---

## ✅ QUALITY REQUIREMENTS

Your analysis MUST include:
- ✅ EXACT file paths (not "somewhere in sc")
- ✅ Complete class names (not "some service")
- ✅ Specific field names and types
- ✅ Ultimate data source (traced to end)
- ✅ Concrete API endpoint patterns
- ✅ Copy-paste ready Swagger keywords
- ✅ Field mapping tables

---

## 🚫 COMMON MISTAKES TO AVOID

❌ DON'T: "Calls a service"  
✅ DO: "Calls ProductServiceImpl.retrieveProductList() in file ccb/middletier/service/common-service/ProductServiceImpl.java"

❌ DON'T: "Needs account data"  
✅ DO: "Needs: iban (string), accountOwnerName (string), permissions.canReceiveRewards (boolean)"

❌ DON'T: Stop at "calls ProductService"  
✅ DO: "ProductService → PkvdRetriever → PersonKundeVertragsDatenV2Hostaccess → MAINFRAME PKVD"

---

## 🎯 START YOUR ANALYSIS

**Application to Analyze**: [INSERT APP NAME]

**Locations to Check**:
1. `C:\CCB\sources\portal\ucc\[app-name]\`
2. `C:\CCB\sources\portal\ccb\ui\pk-webui\[app-name]\`
3. `C:\CCB\sources\portal\ccb\ui\msb-webui\[app-name]\`

**Begin by**:
1. Finding the app location
2. Listing all REST endpoints
3. Tracing the main endpoint to data sources
4. Classifying each source type
5. Suggesting REST APIs for mainframe calls

**Output**:
Use the format specified above. Be specific, thorough, and actionable.

---

Ready? Start your analysis now! 🚀

