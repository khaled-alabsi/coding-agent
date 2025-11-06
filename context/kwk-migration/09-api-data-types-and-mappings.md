# KWK Migration - API Data Types and Field Mappings

## Purpose
This document provides the exact data types, field names, and mapping requirements needed to evaluate REST APIs for KWK migration.

---

## 📋 Quick Reference: Required Data Types

### **Summary Table**

| Data Category | Priority | Source Today | Need from API | Critical? |
|--------------|----------|--------------|---------------|-----------|
| Account List | 🔴 P1 | PKVD Mainframe | Account[] with IBAN + permissions | YES |
| Customer Name | 🔴 P1 | Natural Person API V3 | firstName, lastName | YES |
| IBAN Format | 🟡 P2 | IBAN Converter | Formatted IBAN string | YES |
| Account Permissions | 🟡 P2 | Authorization Service | Boolean permissions | YES |
| Product Config | 🟢 P3 | Configuration | Product + Reward list | NO* |
| Audit Logging | 🟢 P3 | Juridical Logging | POST endpoint | NO* |

*Can be configured locally or loaded from files

---

## 🎯 Data Type Specifications

### 1. Account Data Type

#### **Complete TypeScript/JSON Schema:**
```typescript
interface Account {
  // Primary Identifiers
  accountId: string;           // REQUIRED: Internal account ID
  iban: string;                // REQUIRED: International Bank Account Number
  
  // Account Details
  accountNumber?: string;      // OPTIONAL: Internal account number
  bankCode?: string;          // OPTIONAL: Bank code (BLZ)
  accountOwnerName: string;   // REQUIRED: Full name of owner
  
  // Product Information
  productType: string;        // REQUIRED: e.g., "CURRENT_ACCOUNT", "SAVINGS"
  productName?: string;       // OPTIONAL: e.g., "Girokonto Plus"
  productCategory?: string;   // OPTIONAL: e.g., "100" (branch code)
  
  // Financial Details
  currency: string;           // REQUIRED: ISO currency code (e.g., "EUR")
  balance?: number;           // OPTIONAL: Current balance
  
  // Status
  status: string;             // REQUIRED: "ACTIVE", "CLOSED", "BLOCKED", etc.
  
  // Permissions (CRITICAL for KWK)
  permissions: {
    canReceiveRewards: boolean;     // REQUIRED: Can this account receive KWK rewards?
    rewardCredit?: boolean;         // OPTIONAL: Specific REWARDCREDIT permission
    readAccess: boolean;            // REQUIRED: User can view this account
    writeAccess?: boolean;          // OPTIONAL: User can modify this account
  };
  
  // Display Information
  displayName?: string;       // OPTIONAL: Formatted name for UI
  
  // Metadata
  createdDate?: string;       // OPTIONAL: When account was opened (ISO 8601)
  lastModified?: string;      // OPTIONAL: Last update timestamp
}
```

#### **Minimum Viable Schema (What KWK Absolutely Needs):**
```typescript
interface MinimumAccount {
  iban: string;                    // MUST HAVE
  accountOwnerName: string;        // MUST HAVE
  productType: string;             // MUST HAVE
  currency: string;                // MUST HAVE (always "EUR" for KWK)
  permissions: {
    canReceiveRewards: boolean;    // MUST HAVE
  };
  status: string;                  // MUST HAVE (to filter out closed accounts)
}
```

#### **Example API Response We're Looking For:**
```json
{
  "accounts": [
    {
      "accountId": "ACC-123456",
      "iban": "DE89370400440532013000",
      "accountOwnerName": "Max Mustermann",
      "productType": "CURRENT_ACCOUNT",
      "productName": "Girokonto Plus",
      "currency": "EUR",
      "status": "ACTIVE",
      "permissions": {
        "canReceiveRewards": true,
        "rewardCredit": true,
        "readAccess": true,
        "writeAccess": true
      },
      "displayName": "Girokonto Plus | Max Mustermann"
    }
  ]
}
```

#### **Alternative Response Formats to Accept:**
```json
// Option 1: Permissions as array of strings
{
  "iban": "DE89370400440532013000",
  "permissions": ["READ", "WRITE", "REWARD_CREDIT"]
}

// Option 2: Nested entitlements
{
  "iban": "DE89370400440532013000",
  "entitlements": {
    "features": ["REWARDS_ELIGIBLE"]
  }
}

// Option 3: Flat boolean flags
{
  "iban": "DE89370400440532013000",
  "isRewardEligible": true,
  "isActive": true
}
```

---

### 2. Customer/Person Data Type

#### **Complete TypeScript/JSON Schema:**
```typescript
interface CustomerPerson {
  // Primary Identifiers
  customerId: string;          // REQUIRED: Customer number
  naturalPersonId?: string;    // OPTIONAL: Natural person identifier (npKenn)
  participantId?: string;      // OPTIONAL: Participant ID
  
  // Personal Information
  firstName: string;           // REQUIRED: Given name
  lastName: string;            // REQUIRED: Family name
  middleName?: string;         // OPTIONAL: Middle name
  title?: string;              // OPTIONAL: Dr., Prof., etc.
  
  // Customer Classification
  customerType?: string;       // OPTIONAL: "PRIVATE", "EMPLOYEE", "BUSINESS"
  customerSegment?: string;    // OPTIONAL: "PREMIUM", "STANDARD", etc.
  
  // Contact Information (if needed)
  email?: string;              // OPTIONAL: Email address
  phone?: string;              // OPTIONAL: Phone number
  
  // Metadata
  createdDate?: string;        // OPTIONAL: Customer since
  lastLogin?: string;          // OPTIONAL: Last activity
}
```

#### **Minimum Viable Schema:**
```typescript
interface MinimumCustomer {
  customerId: string;          // MUST HAVE
  firstName: string;           // MUST HAVE
  lastName: string;            // MUST HAVE
}
```

#### **Example API Response:**
```json
{
  "customerId": "12345678",
  "naturalPersonId": "NP123456",
  "firstName": "Max",
  "lastName": "Mustermann",
  "customerType": "PRIVATE"
}
```

---

### 3. IBAN Conversion Data Type

#### **Complete TypeScript/JSON Schema:**
```typescript
interface IbanConversion {
  // Input
  bankCode?: string;           // Input: Bank code (BLZ)
  accountNumber?: string;      // Input: Account number
  country?: string;            // Input: Country code (default "DE")
  
  // Output
  iban: string;                // REQUIRED: Generated IBAN
  formatted?: string;          // OPTIONAL: IBAN with spaces "DE89 3704 0044..."
  
  // Validation
  isValid: boolean;            // REQUIRED: Is the IBAN valid?
  
  // Additional Info
  bankName?: string;           // OPTIONAL: Name of the bank
  bic?: string;                // OPTIONAL: Bank Identifier Code (SWIFT)
  
  // Error Handling
  errorCode?: string;          // OPTIONAL: If validation fails
  errorMessage?: string;       // OPTIONAL: Error description
}
```

#### **Example API Request/Response:**
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
  "isValid": true,
  "bankName": "Commerzbank AG",
  "bic": "COBADEFFXXX"
}
```

---

### 4. Authorization/Permission Data Type

#### **Complete TypeScript/JSON Schema:**
```typescript
interface Permission {
  // Resource Identification
  resourceType: string;        // REQUIRED: "ACCOUNT", "PRODUCT", "FEATURE"
  resourceId: string;          // REQUIRED: IBAN or account ID
  
  // Permission Details
  permissionName: string;      // REQUIRED: e.g., "REWARDCREDIT", "READ", "WRITE"
  isGranted: boolean;          // REQUIRED: True if permission exists
  accessLevel?: string;        // OPTIONAL: "FULL", "READ_ONLY", "NONE"
  
  // Scope
  scope?: string[];            // OPTIONAL: ["ACCOUNTS", "TRANSACTIONS"]
  
  // Validity
  validFrom?: string;          // OPTIONAL: Permission valid from (ISO 8601)
  validUntil?: string;         // OPTIONAL: Permission expires (ISO 8601)
  
  // Metadata
  grantedBy?: string;          // OPTIONAL: Who granted this permission
  grantedAt?: string;          // OPTIONAL: When permission was granted
}
```

#### **Minimum Viable Schema:**
```typescript
interface MinimumPermission {
  resourceId: string;          // MUST HAVE: IBAN or account ID
  hasRewardPermission: boolean; // MUST HAVE: Can receive rewards?
}
```

#### **Example API Response:**
```json
{
  "permissions": [
    {
      "resourceType": "ACCOUNT",
      "resourceId": "DE89370400440532013000",
      "permissionName": "REWARDCREDIT",
      "isGranted": true,
      "accessLevel": "FULL"
    }
  ]
}
```

---

### 5. Product/Reward Configuration Data Type

#### **Complete TypeScript/JSON Schema:**
```typescript
interface ProductReward {
  // Product Information
  productId: string;           // REQUIRED: Unique product identifier
  productName: string;         // REQUIRED: Display name
  productCode?: string;        // OPTIONAL: Internal code
  productType: string;         // REQUIRED: "CURRENT_ACCOUNT", "CREDIT_CARD"
  category?: string;           // OPTIONAL: Product category
  
  // Rewards
  rewards: Reward[];           // REQUIRED: List of available rewards
  
  // Availability
  isActive: boolean;           // REQUIRED: Is this product/reward active?
  validFrom?: string;          // OPTIONAL: Campaign start date
  validUntil?: string;         // OPTIONAL: Campaign end date
  
  // Display
  description?: string;        // OPTIONAL: Product description
  displayOrder?: number;       // OPTIONAL: Sort order in UI
}

interface Reward {
  rewardId: string;            // REQUIRED: Unique reward identifier
  rewardName: string;          // REQUIRED: Display name (e.g., "50 EUR Prämie")
  rewardType: string;          // REQUIRED: "CASH", "VOUCHER", "POINTS"
  
  // Reward Details
  amount?: number;             // OPTIONAL: Reward amount
  currency?: string;           // OPTIONAL: Currency code
  voucherCode?: string;        // OPTIONAL: For voucher rewards
  
  // Conditions
  maxAvailabilityTime?: string; // OPTIONAL: "90 days", "unlimited"
  minimumAmount?: number;      // OPTIONAL: Minimum transaction for reward
  
  // Display
  description?: string;        // OPTIONAL: Reward description
  termsAndConditions?: string; // OPTIONAL: Legal text
}
```

#### **Example API Response:**
```json
{
  "products": [
    {
      "productId": "1",
      "productName": "Girokonto Plus",
      "productType": "CURRENT_ACCOUNT",
      "isActive": true,
      "rewards": [
        {
          "rewardId": "1",
          "rewardName": "50 EUR Prämie",
          "rewardType": "CASH",
          "amount": 50.00,
          "currency": "EUR",
          "maxAvailabilityTime": "90 days"
        },
        {
          "rewardId": "2",
          "rewardName": "100 EUR Prämie",
          "rewardType": "CASH",
          "amount": 100.00,
          "currency": "EUR",
          "maxAvailabilityTime": "180 days"
        }
      ]
    }
  ]
}
```

---

### 6. Audit/Logging Data Type

#### **Complete TypeScript/JSON Schema:**
```typescript
interface AuditLog {
  // Activity Identification
  activityId?: string;         // OPTIONAL: Generated by system
  activityName: string;        // REQUIRED: "Kunden werben Kunden"
  actionName: string;          // REQUIRED: "Abschicken Kunden werben Kunden"
  
  // User Context
  userId: string;              // REQUIRED: Who performed the action
  participantId?: string;      // OPTIONAL: Participant identifier
  sessionId?: string;          // OPTIONAL: Session identifier
  
  // Timestamp
  timestamp: string;           // REQUIRED: ISO 8601 format
  
  // Payload
  payload: {                   // REQUIRED: Activity-specific data
    account?: string;
    reward?: string;
    product?: string;
    referralCode?: string;
    emailAddress?: string;
    [key: string]: any;        // Flexible for other fields
  };
  
  // System Context
  channel?: string;            // OPTIONAL: "WEB", "MOBILE", "API"
  ipAddress?: string;          // OPTIONAL: User's IP
  userAgent?: string;          // OPTIONAL: Browser/app info
  
  // Result
  status?: string;             // OPTIONAL: "SUCCESS", "ERROR"
  errorCode?: string;          // OPTIONAL: If error occurred
  errorMessage?: string;       // OPTIONAL: Error details
}
```

#### **Example API Request:**
```json
{
  "activityName": "Kunden werben Kunden",
  "actionName": "Abschicken Kunden werben Kunden",
  "userId": "user123",
  "timestamp": "2025-11-06T14:23:45Z",
  "payload": {
    "account": "DE89370400440532013000",
    "reward": "50 EUR",
    "product": "Girokonto Plus",
    "referralCode": "A7K9M2",
    "emailAddress": "friend@example.com"
  },
  "channel": "WEB",
  "status": "SUCCESS"
}
```

---

## 🔄 Field Mapping Guide

### Current KWK Code → API Response Field Mapping

| KWK Java Field | Java Type | API JSON Field | JSON Type | Notes |
|----------------|-----------|----------------|-----------|-------|
| `chosenIban` | String | `iban` | string | IBAN format |
| `chosenAccountOwnerName` | String | `accountOwnerName` | string | Full name |
| `chosenBounty` | String | `rewards[].rewardName` | string | Reward description |
| `chosenBountyId` | String | `rewards[].rewardId` | string | Reward ID |
| `chosenProductId` | String | `productId` | string | Product ID |
| `chosenProductName` | String | `productName` | string | Product name |
| `npkenn` | String | `naturalPersonId` or `customerId` | string | Customer ID |
| `firstName` | String | `firstName` | string | First name |
| `lastName` | String | `lastName` | string | Last name |
| `permissions.canReceiveRewards` | Boolean | `permissions.canReceiveRewards` | boolean | Permission flag |

---

## 📊 Swagger Search Checklist

### ✅ When Evaluating an Account API:

#### **Must Have (Deal Breakers):**
- [ ] Returns `iban` field as string
- [ ] Returns `accountOwnerName` or similar name field
- [ ] Returns `currency` field
- [ ] Has some form of permission/entitlement indicator
- [ ] Can filter by customer/participant ID
- [ ] Returns active accounts (or can filter by status)

#### **Should Have (Important):**
- [ ] Returns `productType` or `productName`
- [ ] Has `status` field to identify active accounts
- [ ] Includes formatted IBAN (with spaces)
- [ ] Has pagination for large result sets
- [ ] Documented response schema in Swagger

#### **Nice to Have (Bonus):**
- [ ] Returns `balance` information
- [ ] Includes `displayName` formatted for UI
- [ ] Has `createdDate` for account age
- [ ] Supports batch requests
- [ ] Has caching headers for performance

---

### ✅ When Evaluating a Customer API:

#### **Must Have:**
- [ ] Returns `firstName` as string
- [ ] Returns `lastName` as string
- [ ] Accepts customer ID or participant ID as input
- [ ] Returns JSON format

#### **Should Have:**
- [ ] Returns `customerId` or `customerNumber`
- [ ] Has `customerType` field (to distinguish employees)
- [ ] Documented in Swagger

#### **Nice to Have:**
- [ ] Returns `email` (if available)
- [ ] Has `title` field (Dr., Prof., etc.)
- [ ] Includes `middleName`

---

### ✅ When Evaluating an IBAN API:

#### **Must Have:**
- [ ] Can convert account number + bank code → IBAN
- [ ] Returns valid IBAN string
- [ ] Has validation endpoint

#### **Should Have:**
- [ ] Returns formatted IBAN (with spaces)
- [ ] Validates IBAN format
- [ ] Returns bank name

#### **Nice to Have:**
- [ ] Returns BIC/SWIFT code
- [ ] Has error codes for invalid IBANs
- [ ] Supports batch conversion

---

## 🎯 API Compatibility Score

Score each API you find:

| Criteria | Weight | Score (0-5) | Weighted |
|----------|--------|-------------|----------|
| Has all MUST HAVE fields | 40% | ___ / 5 | ___ |
| Performance < 500ms | 20% | ___ / 5 | ___ |
| Has good documentation | 15% | ___ / 5 | ___ |
| Easy to integrate | 10% | ___ / 5 | ___ |
| Has SHOULD HAVE fields | 10% | ___ / 5 | ___ |
| Has NICE TO HAVE fields | 5% | ___ / 5 | ___ |
| **TOTAL** | **100%** | | **___ / 5** |

**Scoring Guide:**
- 5 = Excellent, exceeds requirements
- 4 = Good, meets all requirements
- 3 = Acceptable, meets most requirements
- 2 = Poor, missing some requirements
- 1 = Bad, missing many requirements
- 0 = Unusable, doesn't meet requirements

**Decision:**
- Score ≥ 4.0: ✅ Use this API
- Score 3.0-3.9: ⚠️ Use with caution, may need workarounds
- Score < 3.0: ❌ Find alternative or combine multiple APIs

---

## 📝 API Documentation Template

When documenting a found API:

```markdown
# [API Name]

## Basic Info
- **Service:** [Service Name]
- **Base URL:** https://api.example.com
- **Version:** v1
- **Documentation:** [Swagger URL]

## Endpoints Used

### GET /api/v1/accounts
**Purpose:** Retrieve customer accounts
**KWK Use Case:** Get settlement accounts for reward

**Request:**
```http
GET /api/v1/accounts?customerId={id}&includePermissions=true
Authorization: Bearer {token}
```

**Response Schema:**
```json
{
  "accounts": [
    {
      "iban": "string",
      "accountOwnerName": "string",
      "permissions": {
        "canReceiveRewards": boolean
      }
    }
  ]
}
```

**Field Mapping:**
| API Field | Maps to KWK | Type | Required |
|-----------|-------------|------|----------|
| `iban` | `chosenIban` | string | YES |
| `accountOwnerName` | `chosenAccountOwnerName` | string | YES |

**Compatibility Score:** 4.2 / 5.0

**Pros:**
- ✅ Fast response (~200ms)
- ✅ Includes permissions
- ✅ Well documented

**Cons:**
- ❌ Doesn't include product name (need separate call)
- ⚠️ No formatted IBAN (need to format ourselves)

**Decision:** ✅ Use (with minor adjustments)
```

---

## 🚀 Quick Start: Testing an API

### Step 1: Get API Access
```bash
# Get Bearer token (example)
curl -X POST "https://auth.example.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=YOUR_ID&client_secret=YOUR_SECRET"
```

### Step 2: Test Account Endpoint
```bash
curl -X GET "https://api.example.com/api/v1/accounts?customerId=123" \
  -H "Authorization: Bearer {TOKEN}" \
  -H "Accept: application/json"
```

### Step 3: Validate Response
- Check if all required fields are present
- Verify data types match expectations
- Test with multiple customers
- Check error responses

### Step 4: Performance Test
```bash
# Measure response time
time curl -X GET "..." -H "..." -o /dev/null -s -w "Time: %{time_total}s\n"
```

---

*Use this guide to evaluate API responses and ensure they provide the exact data types KWK needs for migration.*

