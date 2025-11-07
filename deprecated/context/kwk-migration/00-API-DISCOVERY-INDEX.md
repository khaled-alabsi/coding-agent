# API Discovery - Summary and Index

## 📚 Document Overview

This folder contains comprehensive guides to help you find REST APIs that can replace mainframe/database dependencies for KWK migration.

---

## 📖 Document Index

### **[08-api-discovery-guide.md](./08-api-discovery-guide.md)**
**Purpose:** Complete guide to discovering APIs in Swagger documentation

**Contains:**
- Detailed data requirements for each dependency
- Swagger search hints and keywords
- Expected endpoint patterns
- API evaluation checklist
- Documentation templates
- Priority search order

**Use When:** Starting API discovery, need comprehensive reference

---

### **[09-api-data-types-and-mappings.md](./09-api-data-types-and-mappings.md)**
**Purpose:** Exact data types and field mappings needed from APIs

**Contains:**
- Complete TypeScript/JSON schemas for all data types
- Minimum viable data requirements
- Field mapping from KWK to API responses
- Example request/response formats
- Alternative response format handlers
- API compatibility scoring system

**Use When:** Evaluating if an API response matches your needs

---

### **[10-swagger-search-quick-reference.md](./10-swagger-search-quick-reference.md)**
**Purpose:** Quick copy-paste search queries for Swagger

**Contains:**
- Ready-to-use search terms (copy-paste)
- Expected Swagger paths
- Field name variations
- 30-minute fast-track guide
- Discovery tracking sheet
- Red flags and green flags

**Use When:** Actively searching in Swagger UI, need quick reference

---

## 🎯 Quick Start Guide

### Step 1: Understand What You Need (15 min)
Read: **[08-api-discovery-guide.md](./08-api-discovery-guide.md)** → Section "Overview: What We Need to Find"

**Key Takeaway:**
- Account List API (replaces PKVD mainframe) - CRITICAL
- Customer Name API - CRITICAL  
- IBAN Converter API - Important
- Authorization API - Important
- Product/Reward API - Optional
- Audit API - Optional

---

### Step 2: Prepare Your Search (10 min)
Read: **[09-api-data-types-and-mappings.md](./09-api-data-types-and-mappings.md)** → Section "Required Data Types"

**Print/Bookmark:**
- Minimum viable schemas
- Field mapping table
- Swagger search checklist

---

### Step 3: Start Searching (30 min)
Use: **[10-swagger-search-quick-reference.md](./10-swagger-search-quick-reference.md)** → Section "Fast Track"

**Action Items:**
1. Open Swagger documentation
2. Search for "accounts" → Find account API
3. Search for "customer" → Find customer API
4. Search for "iban" → Find IBAN API
5. Document findings using template

---

### Step 4: Evaluate Results (20 min)
Use: **[09-api-data-types-and-mappings.md](./09-api-data-types-and-mappings.md)** → Section "API Compatibility Score"

**For each API:**
- Check response schema against minimum requirements
- Score using compatibility matrix
- Document pros/cons
- Decide: Use / Need workaround / Find alternative

---

### Step 5: Document and Plan (15 min)
Use: **[08-api-discovery-guide.md](./08-api-discovery-guide.md)** → Section "Documentation Template"

**Create:**
- API inventory spreadsheet
- Integration architecture diagram
- Gap analysis (what's missing)
- Workaround strategies

---

## 📊 Critical Data Dependencies

### 1. Account Data (HIGHEST PRIORITY) 🔴

**Current Source:** PKVD Mainframe via Host Access  
**Need from API:**
```json
{
  "iban": "DE89370400440532013000",
  "accountOwnerName": "Max Mustermann",
  "productType": "CURRENT_ACCOUNT",
  "currency": "EUR",
  "permissions": {
    "canReceiveRewards": true
  }
}
```

**Search For:**
- Keywords: `accounts`, `customer accounts`, `iban`, `settlement`
- Endpoints: `/api/*/accounts`, `/api/*/customers/{id}/accounts`
- Response: Must include IBAN + permissions

**Replacement Strategy:**
- Option A: Find single API with all fields ✅ Preferred
- Option B: Combine account API + permission API ⚠️ Acceptable
- Option C: Keep calling mainframe wrapper 🔄 Fallback

---

### 2. Customer Personal Data (HIGH PRIORITY) 🟡

**Current Source:** Natural Person API V3, Participant Service  
**Need from API:**
```json
{
  "customerId": "12345678",
  "firstName": "Max",
  "lastName": "Mustermann"
}
```

**Search For:**
- Keywords: `customer`, `person`, `participant`, `natural person`
- Endpoints: `/api/*/customers/{id}`, `/api/*/persons/{id}`
- Response: Must include firstName + lastName

**Replacement Strategy:**
- Option A: Customer API with personal data ✅ Preferred
- Option B: Person/Participant API 🔄 Acceptable

---

### 3. IBAN Conversion (MEDIUM PRIORITY) 🟢

**Current Source:** IBAN Converter Service  
**Need from API:**
```json
{
  "iban": "DE89370400440532013000",
  "formatted": "DE89 3704 0044 0532 0130 00",
  "isValid": true
}
```

**Search For:**
- Keywords: `iban`, `convert`, `validate`, `format`
- Endpoints: `/api/*/iban/convert`, `/api/*/iban/validate`

**Replacement Strategy:**
- Option A: IBAN utility API ✅ Preferred
- Option B: Format client-side using library 🔄 Workaround

---

### 4. Authorization/Permissions (MEDIUM PRIORITY) 🟢

**Current Source:** Authorization Service  
**Need from API:**
```json
{
  "resourceId": "DE89370400440532013000",
  "hasRewardPermission": true
}
```

**Search For:**
- Keywords: `authorization`, `permission`, `entitlement`
- Endpoints: `/api/*/permissions`, `/api/*/authorize`

**Replacement Strategy:**
- Option A: Include in account API response ✅ Preferred
- Option B: Separate permission check API ⚠️ Acceptable
- Option C: Business rule in microservice 🔄 Workaround

---

### 5. Product/Reward Configuration (LOW PRIORITY) 🟢

**Current Source:** Configuration embedded in code  
**Need from API:**
```json
{
  "products": [{
    "productId": "1",
    "productName": "Girokonto Plus",
    "rewards": [{"rewardId": "1", "rewardName": "50 EUR"}]
  }]
}
```

**Search For:**
- Keywords: `product`, `reward`, `campaign`, `catalog`
- Endpoints: `/api/*/products`, `/api/*/campaigns`

**Replacement Strategy:**
- Option A: Product/Campaign API ✅ Preferred
- Option B: Configuration file in microservice 🔄 Acceptable
- Option C: Database configuration table 🔄 Acceptable

---

### 6. Audit Logging (LOW PRIORITY) 🟢

**Current Source:** Juridical Logging Service  
**Need from API:**
```json
{
  "activityName": "Kunden werben Kunden",
  "userId": "user123",
  "payload": { "referralCode": "A7K9M2" }
}
```

**Search For:**
- Keywords: `audit`, `log`, `juridical`, `compliance`
- Endpoints: `/api/*/audit`, `/api/*/logs`

**Replacement Strategy:**
- Option A: Audit/Compliance API ✅ Preferred
- Option B: Event streaming (Kafka) 🔄 Acceptable
- Option C: Log to file/database 🔄 Temporary

---

## 🎯 Success Metrics

### Minimum Viable API Set:
- ✅ **1 Account API** that returns IBAN + owner name + permissions
- ✅ **1 Customer API** that returns first/last name
- ⚠️ IBAN converter (nice to have, can be client-side)
- ⚠️ Audit API (nice to have, can log locally)

### Ideal API Set:
- ✅ Account API with all fields (IBAN, name, product, permissions)
- ✅ Customer API with full profile
- ✅ IBAN converter/validator API
- ✅ Authorization/permission check API
- ✅ Product/reward configuration API
- ✅ Audit/compliance logging API

### What Failure Looks Like:
- ❌ No API returns IBAN for customer accounts
- ❌ Account API doesn't include permissions
- ❌ Can't filter accounts by customer/participant
- ❌ APIs require mainframe access (defeats purpose)

**If you encounter failures:**
1. Check if wrapper APIs exist around mainframe
2. Consider building aggregation layer
3. Discuss with architecture team
4. May need to keep some mainframe dependencies

---

## 📋 Discovery Checklist

### Before You Start:
- [ ] Get Swagger documentation URLs
- [ ] Get API gateway credentials
- [ ] Get test customer/participant IDs
- [ ] Print quick reference guide
- [ ] Set up Postman/curl for testing

### During Discovery:
- [ ] Search for account APIs
- [ ] Search for customer/person APIs
- [ ] Search for utility APIs (IBAN, validation)
- [ ] Search for authorization APIs
- [ ] Search for product/campaign APIs
- [ ] Search for audit/logging APIs
- [ ] Test each API with sample data
- [ ] Document response schemas
- [ ] Note performance (response time)
- [ ] Check authentication requirements

### After Discovery:
- [ ] Create API inventory spreadsheet
- [ ] Score each API (compatibility)
- [ ] Identify gaps (missing data/fields)
- [ ] Design combination strategy
- [ ] Document integration plan
- [ ] Get architecture approval
- [ ] Plan prototype integration

---

## 🚀 Expected Timeline

### Week 1: Discovery
- Day 1-2: Read documentation, understand requirements
- Day 3-4: Search Swagger, find candidate APIs
- Day 5: Test APIs, validate responses

### Week 2: Validation
- Day 1-2: Score and evaluate APIs
- Day 3-4: Prototype integration with top candidates
- Day 5: Document findings and recommendations

### Week 3: Planning
- Day 1-2: Create detailed integration architecture
- Day 3-4: Design error handling and fallbacks
- Day 5: Present to architecture team

---

## ⚠️ Risk Factors

### High Risk:
- 🔴 No account API exists → Must build wrapper around mainframe
- 🔴 Account API missing IBAN → Need IBAN from separate source
- 🔴 No permission data → Can't filter eligible accounts

### Medium Risk:
- 🟡 Account API slow (>1s) → May need caching layer
- 🟡 Multiple APIs needed → Increases complexity
- 🟡 Different authentication per API → Complex credential management

### Low Risk:
- 🟢 Missing product names → Can enrich client-side
- 🟢 No IBAN formatter → Use JavaScript library
- 🟢 No audit API → Log locally temporarily

---

## 📞 Escalation Path

**If you can't find APIs after 1 week:**
1. Email architecture team with specific questions
2. Schedule meeting with API platform team
3. Ask for API catalog or service registry
4. Check with teams that have migrated similar apps
5. Consider building wrapper APIs as intermediate step

**Questions to Ask:**
- "Is there a service registry or API catalog I should be using?"
- "Do we have REST APIs that expose customer account data?"
- "Has anyone else migrated from PKVD mainframe calls? What did they use?"
- "Are there wrapper APIs around mainframe services?"

---

## 📚 Additional Resources

### Internal Resources (Ask for These):
- API Catalog or Service Registry
- API Gateway Documentation
- Architecture Decision Records (ADRs)
- Previous migration case studies
- Integration Patterns Guide

### External Resources:
- OpenAPI Specification: https://swagger.io/specification/
- Postman for API Testing: https://www.postman.com/
- JSON Schema Validator: https://www.jsonschemavalidator.net/

---

## 🎓 Key Learnings

### ✅ Do:
- Start with account API (most critical)
- Test APIs early with real data
- Document everything you find
- Score APIs objectively
- Ask for help if stuck

### ❌ Don't:
- Assume APIs exist without checking
- Accept incomplete APIs without validation
- Skip performance testing
- Forget to check authentication
- Wait too long to escalate if blocked

---

## 📝 Quick Templates

### Email Template: Request Swagger Access
```
Subject: Request Swagger Documentation Access for KWK Migration

Hi [API Team],

I'm working on migrating the KWK (Customer Referral) application to a microservice
and need to find REST APIs to replace current mainframe dependencies.

Could you please provide:
1. Swagger/OpenAPI documentation URLs
2. API gateway credentials for testing
3. Any API catalog or service registry

Specifically looking for APIs that provide:
- Customer account lists (with IBAN)
- Customer personal information (names)
- IBAN conversion/validation
- Account permissions/authorization

Thanks,
[Your Name]
```

### Email Template: API Not Found
```
Subject: Looking for Account/Customer APIs

Hi [Architecture Team],

I've been searching for REST APIs to support KWK migration but haven't found
APIs that provide customer account data with IBANs and permissions.

Questions:
1. Do we have REST APIs exposing customer account data?
2. Is there a wrapper API around the PKVD mainframe service?
3. Which team owns account data services?

Current requirement: Retrieve list of customer accounts with IBAN, owner name,
and reward eligibility permission.

Can we schedule a call to discuss?

Thanks,
[Your Name]
```

---

## 🎯 Final Checklist Before Migration

Before starting actual migration code:
- [ ] Found suitable account API (✅ CRITICAL)
- [ ] Found suitable customer API (✅ CRITICAL)
- [ ] Tested both APIs with real data
- [ ] Verified response times acceptable (<500ms)
- [ ] Confirmed authentication method
- [ ] Documented all API endpoints
- [ ] Created integration architecture
- [ ] Identified and planned for gaps
- [ ] Got architecture team approval
- [ ] Verified API SLAs and support

---

*Keep this index handy as your roadmap through the API discovery process!*

