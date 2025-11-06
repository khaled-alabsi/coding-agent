# KWK Migration - REST API Discovery Guide

## Purpose
This document provides specific search hints, queries, and data requirements to find existing REST APIs that can replace the current mainframe/database dependencies for KWK migration.

---

## 🎯 Overview: What We Need to Find

The KWK application currently depends on:
1. **Mainframe PKVD** - Customer accounts data
2. **Multiple SC Services** - Customer details, permissions, conversions
3. **Database queries** - Local application data

We need to find **REST APIs** that can provide the same data without direct mainframe/database access.

---

## 📊 Data Requirements Breakdown

### 1. Customer Accounts Data (CRITICAL - Replaces PKVD Mainframe)

#### **What KWK Needs:**
```json
{
  "accounts": [
    {
      "accountId": "string",
      "iban": "DE89370400440532013000",
      "accountNumber": "string",
      "bankCode": "string",
      "accountOwnerName": "Max Mustermann",
      "accountDisplayName": "Girokonto Plus | Max Mustermann",
      "productType": "CURRENT_ACCOUNT",
      "productCategory": "100",
      "currency": "EUR",
      "permissions": {
        "canReceiveRewards": true,
        "rewardCredit": true,
        "readAccess": true,
        "writeAccess": true
      },
      "status": "ACTIVE"
    }
  ]
}
```

#### **Swagger Search Hints:**

| Search Query | Where to Look | Expected Endpoint Pattern |
|--------------|---------------|--------------------------|
| `accounts` | Account service, Product service | `/api/v*/accounts` |
| `customer accounts` | Customer service | `/api/v*/customers/{id}/accounts` |
| `iban` | Account service | `/api/v*/accounts?iban={iban}` |
| `product list` | Product service | `/api/v*/products` |
| `settlement accounts` | Payment service | `/api/v*/accounts/settlement` |
| `eligible accounts` | Account service | `/api/v*/accounts?eligible=true` |

#### **Look for These Swagger Paths:**
```
GET /api/accounts-api/v1/accounts
GET /api/accounts-api/v2/customers/{customerId}/accounts
GET /api/product-api/v1/accounts
GET /api/customer-api/v1/customers/{id}/products
GET /api/participant-api/v1/participants/{id}/accounts
```

#### **Required Response Fields:**
- ✅ `iban` (REQUIRED) - Account IBAN
- ✅ `accountOwnerName` (REQUIRED) - Owner's name
- ✅ `productName` or `productType` (REQUIRED) - Type of account
- ✅ `currency` (REQUIRED) - EUR, USD, etc.
- ✅ `permissions` or `entitlements` (REQUIRED) - Check for "reward" or "premium" permission
- ⚠️ `accountNumber` (OPTIONAL) - Internal account number
- ⚠️ `bankCode` (OPTIONAL) - BLZ
- ⚠️ `status` (OPTIONAL) - ACTIVE, CLOSED, etc.

#### **Filtering Capabilities Needed:**
- Filter by customer/participant ID
- Filter by permission type (e.g., `?permission=REWARDCREDIT`)
- Filter by account status (e.g., `?status=ACTIVE`)
- Include IBAN in response

#### **Example API Calls to Test:**
```bash
# Search in Swagger for:
GET /api/accounts/v1/accounts?customerId={id}&permission=REWARD
GET /api/products/v2/eligible-accounts?feature=REWARDS
GET /api/participant/v1/{participantId}/accounts?includePermissions=true
```

---

### 2. Customer Personal Information

#### **What KWK Needs:**
```json
{
  "customerId": "12345678",
  "naturalPersonId": "NP123456",
  "firstName": "Max",
  "lastName": "Mustermann",
  "customerType": "PRIVATE" | "EMPLOYEE",
  "customerNumber": "12345678"
}
```

#### **Swagger Search Hints:**

| Search Query | Where to Look | Expected Endpoint Pattern |
|--------------|---------------|--------------------------|
| `customer` | Customer service | `/api/v*/customers/{id}` |
| `natural person` | Person service | `/api/v*/persons/{id}` |
| `participant` | Participant service | `/api/v*/participants/{id}` |
| `customer details` | Customer service | `/api/v*/customers/{id}/details` |
| `customer type` | Customer service | `/api/v*/customers/{id}/type` |

#### **Look for These Swagger Paths:**
```
GET /api/customer-api/v3/customers/{customerId}
GET /api/person-api/v3/persons/{personId}
GET /api/participant-api/v1/participants/{participantId}
GET /api/customer-api/v1/customers/{id}/profile
```

#### **Required Response Fields:**
- ✅ `firstName` (REQUIRED)
- ✅ `lastName` (REQUIRED)
- ✅ `customerId` or `customerNumber` (REQUIRED)
- ⚠️ `customerType` (OPTIONAL) - To check if employee
- ⚠️ `npKenn` or `naturalPersonId` (OPTIONAL)

#### **Example API Calls to Test:**
```bash
GET /api/customers/v3/customers/{customerId}
GET /api/persons/v3/natural-persons/{npKenn}
```

---

### 3. IBAN Validation and Conversion

#### **What KWK Needs:**
```json
{
  "iban": "DE89370400440532013000",
  "isValid": true,
  "bankCode": "37040044",
  "accountNumber": "0532013000",
  "bankName": "Commerzbank AG",
  "country": "DE"
}
```

#### **Swagger Search Hints:**

| Search Query | Where to Look | Expected Endpoint Pattern |
|--------------|---------------|--------------------------|
| `iban` | IBAN service, Validation service | `/api/v*/iban` |
| `validate iban` | Validation service | `/api/v*/iban/validate` |
| `convert iban` | IBAN service | `/api/v*/iban/convert` |
| `account number` | Account service | `/api/v*/accounts/convert` |

#### **Look for These Swagger Paths:**
```
POST /api/iban-api/v1/validate
POST /api/iban-api/v1/convert
GET /api/validation-api/v1/iban?iban={iban}
POST /api/shared-business/v1/iban/convert
```

#### **Required Request/Response:**
```json
// Request
{
  "bankCode": "37040044",
  "accountNumber": "0532013000",
  "country": "DE"
}

// Response
{
  "iban": "DE89370400440532013000",
  "formatted": "DE89 3704 0044 0532 0130 00",
  "isValid": true
}
```

---

### 4. Authorization and Permissions

#### **What KWK Needs:**
```json
{
  "userId": "user123",
  "permissions": [
    "REWARDCREDIT",
    "READ_ACCOUNTS",
    "WRITE_ACCOUNTS"
  ],
  "accountPermissions": [
    {
      "iban": "DE89370400440532013000",
      "canReceiveReward": true,
      "accessLevel": "FULL"
    }
  ]
}
```

#### **Swagger Search Hints:**

| Search Query | Where to Look | Expected Endpoint Pattern |
|--------------|---------------|--------------------------|
| `authorization` | Auth service | `/api/v*/authorization` |
| `permissions` | Auth service | `/api/v*/users/{id}/permissions` |
| `entitlements` | Entitlement service | `/api/v*/entitlements` |
| `access rights` | Authorization service | `/api/v*/access` |

#### **Look for These Swagger Paths:**
```
GET /api/auth/v1/users/{userId}/permissions
GET /api/authorization/v2/accounts/{accountId}/permissions
GET /api/entitlements/v1/check?resource=REWARDCREDIT
POST /api/authorization/v1/verify
```

---

### 5. Product Configuration and Rewards

#### **What KWK Needs:**
```json
{
  "products": [
    {
      "productId": "1",
      "productName": "Girokonto Plus",
      "productCode": "GKP",
      "category": "CURRENT_ACCOUNT",
      "rewards": [
        {
          "rewardId": "1",
          "rewardName": "50 EUR Prämie",
          "rewardAmount": 50.00,
          "currency": "EUR",
          "validUntil": "2025-12-31",
          "maxAvailabilityTime": "90 days"
        }
      ]
    }
  ]
}
```

#### **Swagger Search Hints:**

| Search Query | Where to Look | Expected Endpoint Pattern |
|--------------|---------------|--------------------------|
| `products` | Product service | `/api/v*/products` |
| `rewards` | Reward service, Campaign service | `/api/v*/rewards` |
| `promotions` | Marketing service | `/api/v*/promotions` |
| `campaigns` | Campaign service | `/api/v*/campaigns` |
| `product catalog` | Catalog service | `/api/v*/catalog/products` |

#### **Look for These Swagger Paths:**
```
GET /api/product-api/v1/products/referral
GET /api/campaign-api/v1/campaigns/kwk
GET /api/rewards-api/v1/products/{productId}/rewards
GET /api/marketing-api/v1/referral-rewards
```

---

### 6. Compliance Logging (Juridical Logging)

#### **What KWK Needs:**
```json
{
  "activityName": "Kunden werben Kunden",
  "actionName": "Abschicken Kunden werben Kunden",
  "participantId": "user123",
  "timestamp": "2025-11-06T14:23:45Z",
  "payload": {
    "account": "DE89370400440532013000",
    "reward": "50 EUR",
    "product": "Girokonto Plus",
    "referralCode": "A7K9M2"
  }
}
```

#### **Swagger Search Hints:**

| Search Query | Where to Look | Expected Endpoint Pattern |
|--------------|---------------|--------------------------|
| `audit` | Audit service | `/api/v*/audit` |
| `logging` | Logging service | `/api/v*/logs` |
| `juridical` | Compliance service | `/api/v*/juridical-logs` |
| `activity log` | Activity service | `/api/v*/activities` |
| `compliance` | Compliance service | `/api/v*/compliance/logs` |

#### **Look for These Swagger Paths:**
```
POST /api/audit-api/v1/logs
POST /api/compliance-api/v1/juridical-logs
POST /api/activity-api/v1/activities
POST /api/logging-api/v1/business-activities
```

---

## 🔍 Swagger Search Strategy

### Step 1: Identify Available Services
Look for Swagger documentation at these typical URLs:
```
https://{domain}/swagger-ui.html
https://{domain}/api-docs
https://{domain}/swagger
https://{domain}/v2/api-docs
https://{domain}/v3/api-docs
https://{domain}/openapi.json
```

### Step 2: Search by Category

#### **Category 1: Account/Product Services**
Search for: `account`, `product`, `iban`, `settlement`

**What to check:**
- Does it return account lists?
- Can it filter by customer ID?
- Does it include IBAN?
- Does it include permissions/entitlements?

#### **Category 2: Customer/Person Services**
Search for: `customer`, `person`, `participant`, `natural-person`

**What to check:**
- Does it return first/last name?
- Does it accept customer number or participant ID?
- Does it include customer type (employee vs. private)?

#### **Category 3: Utility Services**
Search for: `iban`, `validate`, `convert`, `resolver`

**What to check:**
- Can it convert account number → IBAN?
- Can it validate IBAN format?
- Does it return bank name?

#### **Category 4: Authorization Services**
Search for: `auth`, `permission`, `entitlement`, `authorization`

**What to check:**
- Can it check specific permissions (e.g., REWARDCREDIT)?
- Does it work per account or per user?
- Does it return boolean/access level?

#### **Category 5: Configuration Services**
Search for: `product`, `reward`, `campaign`, `promotion`, `catalog`

**What to check:**
- Does it list available products for referral?
- Does it include reward amounts?
- Can it filter by campaign type?

---

## 📝 API Evaluation Checklist

For each API you find, check:

### ✅ Functional Requirements
- [ ] Returns all required fields
- [ ] Supports filtering by customer/participant
- [ ] Handles authentication/authorization
- [ ] Returns data in JSON format
- [ ] Has clear error responses

### ✅ Technical Requirements
- [ ] Has Swagger/OpenAPI documentation
- [ ] Uses standard HTTP methods (GET, POST)
- [ ] Supports API versioning (v1, v2, v3)
- [ ] Has examples in documentation
- [ ] Includes schema definitions

### ✅ Performance Requirements
- [ ] Response time < 500ms (check SLA)
- [ ] Supports pagination (for large result sets)
- [ ] Has caching headers
- [ ] Supports batch requests (if needed)

### ✅ Security Requirements
- [ ] Requires authentication (OAuth2, JWT, etc.)
- [ ] Has rate limiting
- [ ] Supports scopes/permissions
- [ ] Uses HTTPS

---

## 🎯 Priority Search Order

### **Priority 1: CRITICAL (Must Have)**
1. **Account List API** - Replaces PKVD mainframe call
   - Search: `accounts`, `products`, `eligible accounts`
   - Must return: IBAN, owner name, product type, permissions

2. **Customer Details API** - For customer name
   - Search: `customer`, `person`, `natural-person`
   - Must return: firstName, lastName

### **Priority 2: HIGH (Very Important)**
3. **IBAN Converter API** - Format conversion
   - Search: `iban`, `convert`, `validate`
   - Must return: formatted IBAN

4. **Authorization API** - Permission checks
   - Search: `permission`, `entitlement`, `authorization`
   - Must return: account permissions

### **Priority 3: MEDIUM (Important)**
5. **Product/Reward API** - Configuration data
   - Search: `product`, `reward`, `campaign`
   - Must return: products and associated rewards

6. **Audit/Logging API** - Compliance
   - Search: `audit`, `log`, `juridical`
   - Must accept: activity logs

---

## 📋 Documentation Template for Found APIs

When you find a relevant API, document it using this template:

```markdown
### API Name: [Service Name]

**Base URL:** `https://api.example.com`

**Endpoint:** `GET /api/v1/accounts`

**Purpose:** Retrieves customer accounts

**Authentication:** OAuth2 Bearer Token

**Request Parameters:**
- `customerId` (required): Customer identifier
- `includePermissions` (optional): Include permission details

**Request Example:**
```bash
curl -X GET "https://api.example.com/api/v1/accounts?customerId=123&includePermissions=true" \
  -H "Authorization: Bearer {token}"
```

**Response Example:**
```json
{
  "accounts": [...]
}
```

**Maps to KWK Need:** Account List (replaces PKVD)

**Pros:**
- ✅ Returns IBAN
- ✅ Includes permissions
- ✅ Fast response time

**Cons:**
- ❌ Doesn't include product name (need separate call)
- ⚠️ Requires additional permission check

**Status:** ✅ Suitable / ⚠️ Needs Verification / ❌ Not Suitable
```

---

## 🔎 Specific Search Queries for Swagger UI

Copy-paste these into Swagger search boxes:

### For Account Data:
```
account
accounts
iban
settlement
eligible
product
customer/accounts
participant/accounts
```

### For Customer Data:
```
customer
person
natural-person
participant
customer/details
customer/profile
```

### For Utilities:
```
iban/validate
iban/convert
convert
validate
resolver
bank-code
```

### For Authorization:
```
permission
authorization
entitlement
access
rights
check
verify
```

### For Configuration:
```
product
reward
campaign
promotion
referral
catalog
marketing
```

---

## 📊 Data Mapping Matrix

| KWK Current Source | Data Needed | Potential API Service | Search Keyword |
|--------------------|-------------|----------------------|----------------|
| PKVD Mainframe | Account list with IBAN | Account API, Product API | `accounts`, `iban` |
| PKVD Mainframe | Account permissions | Authorization API | `permissions`, `entitlement` |
| Natural Person API V3 | First name, Last name | Customer API, Person API | `customer`, `person` |
| Customers API V3 | Customer type | Customer API | `customer/type` |
| IBAN Converter | IBAN format | IBAN API, Validation API | `iban/convert` |
| Number Resolver | Bank code | IBAN API | `bank-code` |
| Product Matrix | Product names | Product API, Catalog API | `product`, `catalog` |
| Juridical Logging | Audit logs | Audit API, Logging API | `audit`, `log` |

---

## 🚀 Next Steps

1. **Access Swagger Documentation**
   - Ask for Swagger URLs from architecture team
   - Get API gateway documentation
   - Check internal API portal

2. **Test Each API**
   - Use Postman or curl
   - Verify response structure
   - Check performance
   - Validate data accuracy

3. **Document Findings**
   - Use template above
   - Note any gaps
   - Identify combination strategies (if single API doesn't provide all)

4. **Create API Integration Plan**
   - Map each KWK need to specific API
   - Design fallback strategies
   - Plan error handling

---

## ⚠️ Common Pitfalls to Avoid

1. **Assuming API exists** - Verify in Swagger before planning
2. **Not checking permissions** - API may exist but your service may not have access
3. **Ignoring SLAs** - API may be too slow for user-facing features
4. **Missing fields** - API returns account but not IBAN → need additional call
5. **Different data models** - API uses different terminology (map it)
6. **Stale documentation** - Swagger may be outdated, test actual endpoints

---

## 📞 Who to Ask

If you can't find the right API in Swagger:

1. **API Platform Team** - Ask for API catalog
2. **Architecture Team** - Ask about account/customer APIs
3. **Integration Team** - May have used similar APIs
4. **Product Owners** - Know which services are available
5. **Mainframe Team** - May know if PKVD wrapper exists

---

## 🎓 Success Criteria

You've found the right APIs when:
- ✅ Can retrieve accounts with IBAN for a customer
- ✅ Can get customer first/last name
- ✅ Can validate/convert IBAN
- ✅ Can check account permissions
- ✅ Can log compliance activities
- ✅ All APIs have acceptable performance (<500ms)
- ✅ All APIs are documented and supported
- ✅ Your microservice has permission to call them

---

*Use this guide to systematically search through Swagger documentation and identify the right APIs for KWK migration.*

