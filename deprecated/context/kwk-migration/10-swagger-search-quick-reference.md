# KWK Migration - Swagger Search Query Sheet

## 🎯 Quick Reference: Copy-Paste These Searches

This is your practical "cheat sheet" for searching Swagger/OpenAPI documentation.

---

## 📋 Search Queries by Priority

### 🔴 PRIORITY 1: CRITICAL - Must Find These First

#### **1. Account List API**
```
Swagger Search Terms (try in order):
1. "accounts"
2. "customer accounts"
3. "participant accounts"  
4. "eligible accounts"
5. "settlement accounts"
6. "product accounts"
7. "/accounts"
8. "iban"
```

**What to Look For in Results:**
- Endpoint pattern: `GET /api/*/accounts`
- Query parameter: `customerId` or `participantId`
- Response contains: `iban`, `accountOwnerName`, `permissions`

**Expected Swagger Paths:**
```
GET /api/accounts-api/v1/accounts
GET /api/accounts-api/v2/customers/{customerId}/accounts
GET /api/product-api/v1/accounts
GET /api/customer-api/v1/customers/{id}/accounts
GET /api/participant-api/v1/participants/{id}/accounts
GET /api/banking-api/v1/accounts/list
```

---

#### **2. Customer Name API**
```
Swagger Search Terms:
1. "customer"
2. "person"
3. "natural person"
4. "participant"
5. "customer details"
6. "customer profile"
7. "/customers/{id}"
8. "/persons"
```

**What to Look For:**
- Endpoint pattern: `GET /api/*/customers/{id}` or `/persons/{id}`
- Response contains: `firstName`, `lastName`

**Expected Swagger Paths:**
```
GET /api/customer-api/v3/customers/{customerId}
GET /api/person-api/v3/persons/{personId}
GET /api/person-api/v3/natural-persons/{npKenn}
GET /api/participant-api/v1/participants/{participantId}
GET /api/party-api/v1/parties/{partyId}
```

---

### 🟡 PRIORITY 2: HIGH - Important Services

#### **3. IBAN Conversion/Validation API**
```
Swagger Search Terms:
1. "iban"
2. "iban convert"
3. "iban validate"
4. "validate"
5. "convert"
6. "bank code"
7. "/iban"
```

**Expected Swagger Paths:**
```
POST /api/iban-api/v1/convert
POST /api/iban-api/v1/validate
GET /api/validation-api/v1/iban
POST /api/shared-business/v1/iban/convert
POST /api/utils-api/v1/iban/validate
```

---

#### **4. Authorization/Permission API**
```
Swagger Search Terms:
1. "authorization"
2. "permission"
3. "entitlement"
4. "access"
5. "rights"
6. "check permission"
7. "/authorize"
8. "/permissions"
```

**Expected Swagger Paths:**
```
GET /api/authorization-api/v1/permissions
GET /api/auth-api/v2/users/{userId}/permissions
POST /api/entitlement-api/v1/check
GET /api/access-api/v1/accounts/{accountId}/permissions
POST /api/authorization-api/v1/verify
```

---

### 🟢 PRIORITY 3: MEDIUM - Nice to Have

#### **5. Product/Reward Configuration API**
```
Swagger Search Terms:
1. "product"
2. "reward"
3. "campaign"
4. "promotion"
5. "referral"
6. "catalog"
7. "marketing"
8. "/products"
```

**Expected Swagger Paths:**
```
GET /api/product-api/v1/products/referral
GET /api/campaign-api/v1/campaigns
GET /api/reward-api/v1/products/{productId}/rewards
GET /api/marketing-api/v1/referral-programs
GET /api/catalog-api/v1/products
```

---

#### **6. Audit/Logging API**
```
Swagger Search Terms:
1. "audit"
2. "log"
3. "juridical"
4. "activity"
5. "compliance"
6. "event"
7. "/audit"
8. "/logs"
```

**Expected Swagger Paths:**
```
POST /api/audit-api/v1/logs
POST /api/compliance-api/v1/juridical-logs
POST /api/activity-api/v1/activities
POST /api/logging-api/v1/events
POST /api/audit-api/v2/business-events
```

---

## 🔍 Advanced Search Combinations

### Combination 1: Find Account APIs with Permissions
```
Search: "accounts" AND "permissions"
Or: "accounts" AND "entitlements"
Or: "accounts" AND "eligible"
```

### Combination 2: Find Customer APIs with Personal Data
```
Search: "customer" AND "name"
Or: "person" AND "first name"
Or: "participant" AND "details"
```

### Combination 3: Find IBAN Services
```
Search: "iban" AND "convert"
Or: "iban" AND "format"
Or: "account number" AND "iban"
```

---

## 📱 Swagger UI Search Tips

### If Swagger has a Search Box:
1. Type one keyword at a time
2. Try singular and plural: "account" vs "accounts"
3. Try abbreviations: "acc", "cust", "auth"
4. Try with/without hyphens: "iban" vs "i-ban"

### If Swagger has Tag Groups:
Look for these tag names:
- `Accounts`
- `Customers`
- `Products`
- `Authorization`
- `IBAN`
- `Validation`
- `Utilities`
- `Shared Business`

### If Swagger has Expandable Sections:
Expand these sections:
1. Customer Management
2. Account Services
3. Product Services
4. Authorization
5. Shared Services
6. Utilities
7. Compliance

---

## 🎯 Quick Validation Checklist

When you find a potential API, check these in order:

### ✅ Step 1: Check the Endpoint (10 seconds)
- [ ] Is it `GET` (for retrieving data) or `POST` (for operations)?
- [ ] Does the path make sense? (e.g., `/accounts` for accounts)
- [ ] Does it have path parameters? (e.g., `{customerId}`)

### ✅ Step 2: Check Request Parameters (20 seconds)
- [ ] Can you filter by customer/participant?
- [ ] Are there optional parameters for permissions?
- [ ] Does it accept the IDs you have?

### ✅ Step 3: Check Response Schema (30 seconds)
- [ ] Click "Schema" or "Model" tab in Swagger
- [ ] Look for required fields (marked with *)
- [ ] Check if field names match what you need

### ✅ Step 4: Check Example Response (30 seconds)
- [ ] Is there an example response?
- [ ] Does it show actual field names?
- [ ] Does the data structure make sense?

**Total Time: ~90 seconds per API**

---

## 📊 Field Name Variations

Different APIs might use different names for the same data:

### Account Identifier:
```
iban ✓
IBAN ✓
accountIBAN ✓
accountNumber (might be IBAN or not - check!)
accountId (usually internal ID, not IBAN)
```

### Account Owner Name:
```
accountOwnerName ✓
accountHolder ✓
holderName ✓
ownerName ✓
customerName ✓
name ✓
```

### Product Type:
```
productType ✓
productCategory ✓
accountType ✓
type ✓
category ✓
productCode ✓
```

### Permissions:
```
permissions ✓
entitlements ✓
accessRights ✓
authorizations ✓
capabilities ✓
features ✓
```

### Customer ID:
```
customerId ✓
customerNumber ✓
participantId ✓
userId ✓
personId ✓
naturalPersonId ✓
npKenn ✓
```

### First/Last Name:
```
firstName ✓
first_name ✓
givenName ✓
forename ✓

lastName ✓
last_name ✓
surname ✓
familyName ✓
```

---

## 🚀 Fast Track: API Discovery in 30 Minutes

### Minutes 1-10: Find Account API
1. Search: "accounts"
2. Look for: `GET /api/*/accounts`
3. Check: Returns IBAN + permissions
4. Test: Try "Try it out" in Swagger
5. Document: Copy response schema

### Minutes 11-15: Find Customer API
1. Search: "customer" or "person"
2. Look for: `GET /api/*/customers/{id}`
3. Check: Returns firstName + lastName
4. Test: Try with a customer ID
5. Document: Copy response

### Minutes 16-20: Find IBAN API
1. Search: "iban"
2. Look for: `POST /api/*/iban/convert` or `/validate`
3. Check: Request/response format
4. Test: Try with sample account number
5. Document: Copy request/response

### Minutes 21-25: Find Authorization API
1. Search: "permission" or "authorization"
2. Look for: Permission check endpoints
3. Check: Can check account permissions
4. Test: Try with account ID
5. Document: Permission structure

### Minutes 26-30: Document Findings
1. Create summary table
2. Note missing fields
3. Identify gaps (what's not available)
4. Plan combination strategy if needed

---

## 📋 Discovery Tracking Sheet

Use this to track your findings:

| Data Need | Found API? | Endpoint | Has Required Fields? | Notes |
|-----------|------------|----------|---------------------|-------|
| Account List | ☐ Yes ☐ No | | ☐ IBAN ☐ Name ☐ Permissions | |
| Customer Name | ☐ Yes ☐ No | | ☐ First ☐ Last | |
| IBAN Convert | ☐ Yes ☐ No | | ☐ Convert ☐ Validate | |
| Authorization | ☐ Yes ☐ No | | ☐ Check permission | |
| Product Config | ☐ Yes ☐ No | | ☐ Products ☐ Rewards | |
| Audit Logging | ☐ Yes ☐ No | | ☐ POST logs | |

---

## 🎓 Common Patterns in Banking APIs

### Pattern 1: Resource-Based
```
GET /api/v1/accounts
GET /api/v1/accounts/{id}
GET /api/v1/customers/{id}/accounts
```

### Pattern 2: Service-Based
```
GET /api/account-service/v1/list
GET /api/customer-service/v1/details/{id}
```

### Pattern 3: Domain-Based
```
GET /api/banking/v1/accounts
GET /api/retail/v1/customers/{id}
```

### Pattern 4: PSD2 Style
```
GET /api/accounts-api/v1/accounts
GET /api/payment-api/v1/payments
```

---

## ⚠️ Red Flags: APIs to Avoid

❌ **Skip if you see:**
- No Swagger documentation
- Marked as "deprecated"
- Version 0.x (unstable)
- "Internal use only" note
- No examples in Swagger
- Response type is XML only (need JSON)
- No authentication method specified
- Response time > 2 seconds (in docs)

---

## ✅ Green Flags: Good APIs

✅ **Prefer if you see:**
- Version 1.0+ (stable)
- OpenAPI 3.0 specification
- Complete examples
- Clear schema definitions
- Active maintenance (recent updates)
- SLA documented
- Rate limits specified
- OAuth2 authentication
- Supports JSON
- Has "Try it out" functionality

---

## 🔗 Common Swagger URL Patterns

Try these URLs if you don't know where Swagger is:

```
https://api.{domain}/swagger-ui.html
https://api.{domain}/swagger
https://api.{domain}/api-docs
https://api.{domain}/v2/api-docs
https://api.{domain}/v3/api-docs
https://api.{domain}/swagger-ui/
https://api.{domain}/docs
https://api.{domain}/openapi.json
https://{domain}/swagger
https://{domain}/api/swagger
```

---

## 📞 What to Ask If You Can't Find APIs

**Ask Architecture Team:**
> "Do we have a REST API for retrieving customer accounts with IBANs?"

**Ask API Platform Team:**
> "Is there an API catalog or portal where I can search for account services?"

**Ask Integration Team:**
> "Has anyone integrated with account data APIs before? Which service did you use?"

**Ask Product Owner:**
> "Which teams own the account data? Do they expose REST APIs?"

---

## 💾 Save Your Results Template

```markdown
# API Discovery Results - [Date]

## Found APIs

### 1. Account API
- **Service:** Account Service
- **Endpoint:** GET /api/accounts/v1/list
- **Swagger URL:** https://...
- **Status:** ✅ Suitable
- **Score:** 4.2/5
- **Notes:** Missing product name, need separate call

### 2. Customer API
- **Service:** Customer Service  
- **Endpoint:** GET /api/customers/v3/{id}
- **Swagger URL:** https://...
- **Status:** ✅ Suitable
- **Score:** 4.5/5
- **Notes:** Perfect match

## Missing APIs
- [ ] IBAN converter (workaround: format ourselves)
- [ ] Product rewards (workaround: configure locally)

## Next Steps
1. Test Account API with real credentials
2. Prototype integration
3. Performance test
```

---

## 🎯 Success Criteria

You're done when you have:
- ✅ Found account API with IBAN + permissions
- ✅ Found customer API with first/last name
- ✅ Documented each API's endpoint
- ✅ Tested with sample requests
- ✅ Identified any gaps
- ✅ Created integration plan

---

*Print this sheet and keep it handy while searching Swagger documentation!*

