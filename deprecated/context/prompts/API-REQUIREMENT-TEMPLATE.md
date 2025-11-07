# API REQUIREMENTS TEMPLATE

Use this template to document REST API requirements for each data source identified.

---

## API Requirement: [Name of Data/Feature]

### Current Implementation
- **Source Type**: [Mainframe / Database / SC Service / External API]
- **File Path**: `[exact path to file]`
- **Class Name**: `[ClassName.java]`
- **Method Called**: `methodName(parameters)`

### Data Retrieved
```typescript
interface DataStructure {
  field1: string;        // REQUIRED - Description
  field2: number;        // REQUIRED - Description
  field3?: boolean;      // OPTIONAL - Description
  nested?: {
    subField1: string;
    subField2: number;
  };
}
```

### Current Data Flow
```
[Controller] → [Process] → [Service] → [DAO/Hostaccess/RestClient] → [Data Source]
Exact path: [Full class path chain]
```

### REST API Specification

#### Suggested Endpoint
```http
GET /api/[service]/v[version]/[resource]?[params]
```

**Example:**
```http
GET /api/accounts/v1/accounts?customerId=12345&includePermissions=true
```

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| customerId | string | Yes | Customer identifier |
| includePermissions | boolean | No | Include permission data |

#### Response Schema
```json
{
  "field1": "value",
  "field2": 123,
  "field3": true,
  "nested": {
    "subField1": "value",
    "subField2": 456
  }
}
```

#### Minimum Viable Response
**Must Have Fields:**
- `field1` - Critical for feature X
- `field2` - Used for calculation Y

**Should Have Fields:**
- `field3` - Nice to have for feature Z

**Can Be Derived:**
- `derived1` - Can calculate from field1 + field2

### Swagger Search Hints

**Keywords to Search:**
```
"[primary keyword]"
"[secondary keyword]"
"[alternative term]"
```

**Expected Path Patterns:**
```
/api/[service-name]/v*/[resource]
/api/[resource]/v*/[action]
```

**Tag Names to Check:**
```
- [Service Category]
- [Resource Type]
```

### Field Mapping

| Current Field (Java) | Type | API Field (JSON) | Type | Notes |
|---------------------|------|------------------|------|-------|
| `javaFieldName` | String | `apiFieldName` | string | Exact match |
| `oldName` | Integer | `newName` | number | Renamed |
| `calculated` | Boolean | N/A | N/A | Derive locally |

### Alternative APIs

If primary API not available:

**Option 1: [API Name]**
- Endpoint: `[path]`
- Pros: [advantages]
- Cons: [disadvantages]

**Option 2: [API Name]**
- Endpoint: `[path]`
- Pros: [advantages]
- Cons: [disadvantages]

**Option 3: Workaround**
- Description: [how to work around missing API]
- Feasibility: [High/Medium/Low]

### Migration Strategy

**Preferred Approach:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Fallback Approach:**
1. [Alternative step 1]
2. [Alternative step 2]

### Dependencies

**This API requirement depends on:**
- [ ] API Requirement: [Other requirement]
- [ ] Configuration: [Config needed]
- [ ] Authentication: [Auth method]

**Other features depend on this:**
- [ ] Feature: [Feature name]
- [ ] Use Case: [Use case]

### Validation Checklist

- [ ] Found API in Swagger documentation
- [ ] API returns all required fields
- [ ] Response time < 500ms
- [ ] Authentication method identified
- [ ] Error handling documented
- [ ] Tested with sample data
- [ ] Compatible with our data model

### Status

- **Status**: [Not Started / In Progress / Found / Verified / Approved]
- **API Found**: [Yes / No / Partial]
- **Compatibility Score**: [X.X / 5.0]
- **Last Updated**: [YYYY-MM-DD]

### Notes

[Additional notes, concerns, or observations]

---

## Example: Customer Account List

### Current Implementation
- **Source Type**: Mainframe (PKVD)
- **File Path**: `sc/productbase/service/src/main/java/com/commerzbank/ccb/sc/productbase/service/retriever/PkvdProductIdentifierRetrieverService.java`
- **Class Name**: `PkvdProductIdentifierRetrieverService.java`
- **Method Called**: `retrievePersonKundeVertragsDaten(technicalCtx, userId)`

### Data Retrieved
```typescript
interface Account {
  iban: string;                    // REQUIRED - Account IBAN
  accountOwnerName: string;        // REQUIRED - Full name
  productType: string;             // REQUIRED - Account type
  currency: string;                // REQUIRED - EUR, USD, etc.
  permissions: {
    canReceiveRewards: boolean;    // REQUIRED - Reward eligibility
  };
  status: string;                  // REQUIRED - ACTIVE/CLOSED
}
```

### Current Data Flow
```
CrcJsonController → CustomerReferCustomerProcessImpl → ProductServiceImpl → 
PkvdProductIdentifierRetrieverService → PersonKundeVertragsDatenV2Hostaccess → 
MAINFRAME (PKVD/TVS90)
```

### REST API Specification

#### Suggested Endpoint
```http
GET /api/accounts/v1/accounts?customerId={id}&permission=REWARD&status=ACTIVE
```

#### Request Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| customerId | string | Yes | Customer/participant ID |
| permission | string | No | Filter by permission (e.g., "REWARD") |
| status | string | No | Filter by status (default: "ACTIVE") |
| includePermissions | boolean | No | Include detailed permissions |

#### Response Schema
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
        "rewardCredit": true
      }
    }
  ]
}
```

### Swagger Search Hints

**Keywords:**
```
"accounts"
"customer accounts"
"participant accounts"
"iban"
"eligible accounts"
"settlement accounts"
```

**Expected Paths:**
```
/api/accounts-api/v1/accounts
/api/accounts/v2/customers/{customerId}/accounts
/api/product-api/v1/accounts
```

**Tags:**
```
- Accounts
- Customer Management
- Products
```

### Field Mapping

| Current (Java) | Type | API (JSON) | Type | Notes |
|----------------|------|------------|------|-------|
| `chosenIban` | String | `iban` | string | Direct map |
| `chosenAccountOwnerName` | String | `accountOwnerName` | string | Direct map |
| `productType` | String | `productType` | string | Direct map |
| `currency` | String | `currency` | string | Always "EUR" for KWK |
| `permissions.canReceiveRewards` | Boolean | `permissions.canReceiveRewards` | boolean | Critical field |

### Migration Strategy

**Preferred:**
1. Find Account API with permission filtering
2. Test with real customer ID
3. Verify all required fields present
4. Implement in microservice with caching

**Fallback:**
1. Use Account API + separate Permission API
2. Combine responses in application layer
3. Cache combined result

### Status
- **Status**: In Progress
- **API Found**: Partial (need to verify permissions)
- **Compatibility Score**: 4.0 / 5.0
- **Last Updated**: 2025-11-06

---

*Use this template for each data source/API requirement you identify.*

