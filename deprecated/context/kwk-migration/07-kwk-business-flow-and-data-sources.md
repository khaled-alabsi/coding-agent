# KWK Business Flow and Data Sources - Complete Journey

## Business Name
**KWK (Kunden werben Kunden)** - Customer Referral Program  
Also known as: **CRC (Customer Refer Customer)**

---

## Business Purpose
The KWK program allows existing bank customers to refer new customers and receive rewards (bonuses/premiums) when the referred customer opens a new product (account, credit card, etc.). This is a customer acquisition and loyalty program.

---

## Complete User Journey - From Browser to Database

### 1. **User Opens Browser and Navigates to KWK Page**

```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTION                                                 │
│ Browser: https://banking.commerzbank.de/pk/kwk/            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ WEB SERVER                                                  │
│ Serves HTML page with React container                       │
│ Location: ccb/ui/pk-webui/kwk/ui/                          │
│ File: KWKOverviewPage.java                                 │
└─────────────────────────────────────────────────────────────┘
```

**What Happens:**
- User is authenticated (already logged into online banking)
- Java-based Wicket page is rendered
- Page contains a React container: `<div id="kwkReactContainer">`
- React bundle is loaded from: `/media/system/js/lib_kwk-page-bundle.js`

---

### 2. **React Frontend Loads and Fetches Initial Data**

```
┌─────────────────────────────────────────────────────────────┐
│ REACT COMPONENT INITIALIZATION                              │
│ File: ui-react/.../react/parent_comp/kwk/kwkpanel.js       │
│ Component: KwKPanel                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓
              componentDidMount() executes
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ DATA LOADED FROM SERVER                                     │
│ Method: window.getReactData()                               │
│ Source: Embedded in HTML by Java backend                   │
└─────────────────────────────────────────────────────────────┘
```

**Initial Data Fetched:**

The page loads with pre-populated data from backend process:

#### **API Call 1: retrieveSettlementAccounts()**
- **Purpose**: Get list of customer's accounts eligible for receiving rewards
- **Endpoint**: Called server-side before page render
- **Process**: `CustomerReferCustomerProcessImpl.retrieveSettlementAccounts()`

**Data Flow:**
```
Process Layer:
├── Calls: productService.retrieveProductList(ProductFilter.KWK_REWARDCREDIT_FILTER)
│   │
│   ├─→ Service: ProductServiceImpl.retrieveProductList()
│   │   └─→ Location: ccb/middletier/shared/service/common-service/
│   │
│   ├─→ Calls: productRetrieverService.retrieveAccounts() + retrieveCreditcards()
│   │   └─→ Service: RawTnvProductRetrieverService (SC Layer)
│   │       └─→ Location: sc/productbase/service/
│   │
│   ├─→ Two Different Retrieval Strategies:
│   │   │
│   │   ├─→ Strategy 1: TNV Product Retriever (for TNV participants)
│   │   │   └─→ Service: TnvProductIdentifierRetrieverService
│   │   │       └─→ Retrieves from: TNV system/database
│   │   │       └─→ Cached: MmLegitimationCache (30 minutes)
│   │   │
│   │   └─→ Strategy 2: PKVD Product Retriever (for PKVD participants)
│   │       └─→ Service: PkvdProductIdentifierRetrieverService
│   │           └─→ Calls: PersonKundeVertragsDatenV2Hostaccess
│   │               │
│   │               ├─→ **MAINFRAME CALL** (PRIMARY DATA SOURCE)
│   │               │   └─→ Host Service: PKVD (Person-Kunde-Vertragsdaten)
│   │               │   └─→ Transaction: TVS90 (CICS transaction)
│   │               │   └─→ Copybook: Tvs90c01/Tvs90c02
│   │               │   └─→ Returns: Customer's accounts, products, relationships
│   │               │   └─→ Data Origin: **MAINFRAME CORE BANKING SYSTEM**
│   │               │       ├─→ Customer master data
│   │               │       ├─→ Account master data  
│   │               │       ├─→ Product relationships
│   │               │       └─→ Authorization information
│   │               │
│   │               └─→ Cached: PersonKundeVertragsDatenCache (30 minutes)
│   │
│   ├─→ Filters: Applies ProductFilter.KWK_REWARDCREDIT_FILTER
│   │   └─→ Only accounts with 'REWARDCREDIT' permission
│   │
│   ├─→ Calls: checkPermissions.retrieveProductLimitInformation()
│   │   └─→ **Another MAINFRAME CALL** (Product limits and permissions)
│   │       └─→ Enriches product data with transaction limits
│   │
│   └─→ Calls: authorizationService.updatePermissionInformation()
│       └─→ Updates each account with specific permissions
│       └─→ Determines which accounts are eligible for KWK rewards
│
├── Calls: baseProductMatrixService.determineProductName()
│   └── Data Source: Product configuration (database/cache)
│       └── Gets display name for each product type
│       └── Maps internal product codes to customer-facing names
│
└── Calls: ibanConverterService.convertLocaleDEToIbanDE()
    └── Data Source: IBAN conversion service
        └── Converts technical account numbers to IBAN format
        └── Uses ccbNumberResolverService
            └─→ May call mainframe for bank code resolution
```

**⚠️ CRITICAL: Where Does Account Data REALLY Come From?**

The account/product data does **NOT** come from the local database initially. Here's the truth:

1. **PRIMARY SOURCE: MAINFRAME CORE BANKING SYSTEM**
   - All customer accounts live in the mainframe
   - The PKVD host service (PersonKundeVertragsDaten) is called
   - This is a **real-time mainframe transaction** (TVS90)
   - Returns: All accounts, products, balances, customer relationships
   - **This is the MASTER data** - the single source of truth

2. **WHO CREATES/UPDATES THIS DATA?**
   - **Account Opening System**: When customer opens new account → Mainframe
   - **Teller Systems**: Branch transactions → Mainframe
   - **Core Banking Operations**: Nightly batch jobs → Mainframe
   - **Product Management**: New product types → Mainframe configuration
   - **NOT this application**: This app only READS the data, never writes accounts

3. **CACHING LAYER**
   - Response is cached for 30 minutes (PersonKundeVertragsDatenCache)
   - Cache key: SessionId + ParticipantId + "PERSON_KUNDE_VERTRAGSDATEN_LESEN"
   - Purpose: Avoid excessive mainframe calls
   - Risk: Data may be up to 30 minutes stale

4. **PERMISSION ENRICHMENT**
   - After retrieving from mainframe, permissions are added
   - Product limits checked (another mainframe call)
   - Authorization rules applied (from database/configuration)
   - Filter: Only accounts with 'REWARDCREDIT' permission shown

5. **FOR MIGRATION: DATA DEPENDENCY**
   - You CANNOT simply copy data to a new database
   - You MUST either:
     - Option A: Keep calling the mainframe (PKVD service)
     - Option B: Replicate mainframe data to microservice database (complex sync)
     - Option C: Use existing API wrapper around PKVD
   - The mainframe is the **SYSTEM OF RECORD** for all accounts

**Returns:**
- List of `CrcAccountData` objects containing:
  - `accountDisplayName`: "Girokonto Plus | Max Mustermann"
  - `iban`: "DE89 3704 0044 0532 0130 00"

#### **Embedded Configuration Data:**
- Available products (e.g., Girokonto, Premium Konto, Credit Cards)
- Rewards for each product (e.g., "50 EUR", "100 EUR", "Amazon Gutschein")
- Product IDs and Bounty IDs
- Max availability time for rewards
- Translations and labels

---

### 3. **User Interacts with the Form**

```
┌─────────────────────────────────────────────────────────────┐
│ USER ACTIONS ON PAGE                                        │
│                                                              │
│ 1. Selects Recommended Product                              │
│    └─→ Dropdown: "Girokonto Plus"                          │
│    └─→ React State: selectedProduct updated                │
│                                                              │
│ 2. Selects Reward/Premium                                   │
│    └─→ Dropdown: "50 EUR Prämie"                           │
│    └─→ React State: selectedReward updated                 │
│                                                              │
│ 3. Selects Settlement Account                               │
│    └─→ Dropdown: "DE89 3704 0044 0532 0130 00"            │
│    └─→ React State: selectedAccount updated                │
│                                                              │
│ 4. (Optional) Enters Email Address                          │
│    └─→ Input field: "friend@example.com"                   │
│    └─→ Validated client-side                               │
│                                                              │
│ 5. Clicks "Send" Button                                     │
│    └─→ Triggers: sendReference() method                    │
└─────────────────────────────────────────────────────────────┘
```

**Business Logic:**
- Product selection determines available rewards
- Account selection determines where customer receives the bonus
- Email is optional (can also share via WhatsApp, SMS, QR code)

---

### 4. **User Submits the Referral Request**

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND JAVASCRIPT                                         │
│ File: kwkpanel.js                                           │
│ Method: sendReference(targetApp = 'email')                  │
└─────────────────────────────────────────────────────────────┘
                          ↓
              Builds Request Payload
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ REQUEST PAYLOAD (JSON)                                      │
│ {                                                            │
│   "chosenAccountOwnerName": "Max Mustermann",               │
│   "chosenBounty": "50 EUR",                                 │
│   "chosenBountyId": "1",                                    │
│   "chosenIban": "DE89370400440532013000",                   │
│   "chosenProductId": "2",                                   │
│   "chosenProductName": "Girokonto Plus",                    │
│   "crcEmailAddress": "friend@example.com"                   │
│ }                                                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
              HTTP POST Request
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ REST ENDPOINT                                               │
│ URL: /banking/rest/sendReference                            │
│ Method: POST                                                │
│ Content-Type: application/json                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 5. **Backend Processing Begins**

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: REST CONTROLLER                                    │
│ File: ccb/ui/pk-webui/kwk/rest/                            │
│       CrcJsonController.java                                │
│ Method: sendReference(@RequestBody SendReferenceRequest)    │
└─────────────────────────────────────────────────────────────┘
                          ↓
              @RequestMapping("/sendReference")
              Method: POST
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ VALIDATION                                                   │
│ - Check if request is null                                  │
│ - Check if email is blank (set to null if empty)           │
│ - Bean validation on SendReferenceRequest object            │
│   └─→ @IbanDE, @EmailAddress, @GenericDescription          │
└─────────────────────────────────────────────────────────────┘
                          ↓
              Validation passes
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ CALLS PROCESS LAYER                                         │
│ Injected: customerReferCustomerProcess                      │
│ Method: crcProcess.sendReference(request)                   │
└─────────────────────────────────────────────────────────────┘
```

---

### 6. **Process Layer - Business Logic Execution**

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 2: PROCESS IMPLEMENTATION                             │
│ File: ccb/middletier/process/kwk/                          │
│       CustomerReferCustomerProcessImpl.java                 │
│ Method: sendReference(SendReferenceRequest)                 │
│ Annotation: @CCBProcess, @CCBTransactionalProcess           │
└─────────────────────────────────────────────────────────────┘
```

#### **Step 6.1: Security Authorization Check**

```java
@PreAuthorize("protect('REWARDCREDIT')")
```

**Data Source:** Spring Security Context + Authorization Service
- Checks if logged-in user has 'REWARDCREDIT' permission
- If denied: throws AccessDeniedException
- Authorization rules come from database/configuration

#### **Step 6.2: Verify Account Authorization**

```java
checkAuthorizationForSelectedIban(chosenIban)
```

**Business Logic:**
- Ensures the selected IBAN belongs to the logged-in customer
- Prevents users from using someone else's account

**Data Sources:**
```
1. productService.retrieveProductList(ProductFilter.KWK_REWARDCREDIT_FILTER)
   └─→ Database Query (via JPA)
   └─→ Table: Product tables (account information)
   └─→ Gets all customer's accounts with reward permission

2. For each product:
   └─→ ibanConverterService.getIban(technicalAccountNumber)
       └─→ ccbNumberResolverService.resolveExternalAccountNumberAndBankCodeFromTechnicalAccountNumber()
           └─→ Data Source: May call Mainframe (MNC) or database
           └─→ Converts: Technical Account Number → Bank Code + Account Number → IBAN

3. Compare selected IBAN with customer's authorized IBANs
   └─→ If not found: throw AccessDeniedException
```

#### **Step 6.3: Generate Unique Referral Code**

```java
String kwkCode = generateUniqueReferrallCode()
```

**Algorithm:**
1. **Generate random 6-character code**
   - Allowed characters: 1-9, A-Z (excluding I, O, 0 to avoid confusion)
   - Example: "A7K9M2"
   - Rule: No character can appear more than 2 times
   - Code is reversed after generation

2. **Check uniqueness in database**
   ```
   kwkService.retrieveKwkData(kwkCode)
   └─→ Service Layer
       └─→ DAO Layer: KwkDAOImpl.retrieveKwkData()
           └─→ Database Query:
               SELECT * FROM CUSTOMER_REFER_CUSTOMER WHERE CRC_CODE = ?
   ```

3. **Loop until unique code found**
   - If code exists: generate new one
   - If code doesn't exist: use it

**Data Source:** 
- Database: `CUSTOMER_REFER_CUSTOMER` table
- Query: Check if `CRC_CODE` already exists

#### **Step 6.4: Retrieve Customer Information**

```java
Participant participant = participantService.retrieveParticipantData(getUserIdForFo())
```

**Data Sources:**
```
1. participantService (SC Layer)
   └─→ Data Source: Database or Mainframe (MNC)
   └─→ Returns: Participant object with NpKenn (customer number)
   └─→ Table/System: PARTICIPANT table or mainframe customer system

2. naturalPersonAPIV3Service.retrieveNaturalPersons(npKenn)
   └─→ Data Source: External API or Database
   └─→ Returns: Customer's first name and last name
   └─→ Purpose: Used to personalize referral messages
```

**Retrieved Data:**
- `npKenn`: Customer's natural person identifier
- `firstName`: "Max"
- `lastName`: "Mustermann"

#### **Step 6.5: Build CrcData Object**

```java
CrcData kwkData = new CrcData();
kwkData.setAccountOwnerName(sendReferenceRequest.getChosenAccountOwnerName());
kwkData.setBounty(sendReferenceRequest.getChosenBounty());
kwkData.setBountyId(sendReferenceRequest.getChosenBountyId());
kwkData.setAccountOwnerIban(sendReferenceRequest.getChosenIban());
kwkData.setKwkCode(kwkCode);
kwkData.setKwkEmailAddress(sendReferenceRequest.getCrcEmailAddress());
kwkData.setProductName(sendReferenceRequest.getChosenProductName());
kwkData.setProductId(sendReferenceRequest.getChosenProductId());
kwkData.setDateOfCreation(new Date());
kwkData.setNpkenn(participant.getNpKenn());
kwkData.setProposerFirstname(firstName);
kwkData.setProposerLastname(lastName);
```

**Data Consolidation:**
- User input (from request)
- Generated referral code
- Customer information (from participant service)
- Current timestamp

#### **Step 6.6: Save Referral to Database**

```java
kwkService.saveCrcData(kwkData)
```

---

### 7. **Service Layer - Data Persistence**

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 3: SERVICE IMPLEMENTATION                             │
│ File: ccb/middletier/service/kwk/                          │
│       CustomerReferCustomerServiceImpl.java                 │
│ Method: saveCrcData(CrcData kwkData)                        │
│ Annotation: @CCBService                                     │
└─────────────────────────────────────────────────────────────┘
```

**Data Mapping:**
```java
// Map domain object (CrcData) to JPA entity (CustomerReferCustomer)
CustomerReferCustomer customerReferCustomer = new CustomerReferCustomer();
customerReferCustomer.setCrcAccountOwnerName(kwkData.getAccountOwnerName());
customerReferCustomer.setCrcBounty(kwkData.getBounty());
customerReferCustomer.setCrcFirstName(kwkData.getProposerFirstname());
customerReferCustomer.setCrcIban(kwkData.getAccountOwnerIban());
customerReferCustomer.setCrcCode(kwkData.getKwkCode());
customerReferCustomer.setCrcEmailAddress(kwkData.getKwkEmailAddress());
customerReferCustomer.setCrcLastName(kwkData.getProposerLastname());
customerReferCustomer.setCrcNpkenn(kwkData.getNpkenn());
customerReferCustomer.setCrcProductName(kwkData.getProductName());
customerReferCustomer.setCrcBountyId(Integer.parseInt(kwkData.getBountyId()));
customerReferCustomer.setCrcProductId(Integer.parseInt(kwkData.getProductId()));
```

**Special Handling:**
- Account owner name truncated to 150 characters if too long
- BountyId and ProductId converted from String to Integer
- Error handling for number format exceptions

---

### 8. **DAO Layer - Database Insertion**

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 4: DAO IMPLEMENTATION                                 │
│ File: ccb/middletier/service/kwk/dao/impl/                 │
│       KwkDAOImpl.java                                       │
│ Method: saveCrcData(CustomerReferCustomer entity)           │
│ Annotation: @CCBComponent                                   │
│ Extends: AbstractJpaDAO<CustomerReferCustomer, Long>        │
└─────────────────────────────────────────────────────────────┘
                          ↓
              Gets EntityManager
                          ↓
              Sets module for logging
                          ↓
              super.insert(customerReferCustomer)
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ JPA/HIBERNATE LAYER                                         │
│ - Generates SQL INSERT statement                            │
│ - Uses sequence for primary key: SEQ_CRC_ID                 │
│ - Sets creation timestamp automatically                     │
└─────────────────────────────────────────────────────────────┘
```

---

### 9. **Database - Record Persisted**

```
┌─────────────────────────────────────────────────────────────┐
│ DATABASE: Oracle or DB2                                     │
│ Table: CUSTOMER_REFER_CUSTOMER                              │
└─────────────────────────────────────────────────────────────┘

SQL Generated (Conceptual):

INSERT INTO CUSTOMER_REFER_CUSTOMER (
    CRC_ID,                    -- Auto-generated from SEQ_CRC_ID
    CRC_CODE,                  -- "A7K9M2" (unique referral code)
    CRC_ACCOUNTOWNER_NAME,     -- "Max Mustermann"
    CRC_IBAN,                  -- "DE89370400440532013000"
    CRC_FIRST_NAME,            -- "Max"
    CRC_LAST_NAME,             -- "Mustermann"
    CRC_EMAIL_ADDRESS,         -- "friend@example.com" or NULL
    CRC_NPKENN,                -- "12345678" (customer number)
    CRC_BOUNTY,                -- "50 EUR"
    CRC_BOUNTYID,              -- 1
    CRC_PRODUCTID,             -- 2
    CRC_PRODUCT_NAME,          -- "Girokonto Plus"
    CRC_CREATION_TS,           -- 2025-11-06 14:23:45
    CRC_LASTUPDATE_TS          -- 2025-11-06 14:23:45
) VALUES (
    SEQ_CRC_ID.NEXTVAL,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);
```

**Data Stored:**
- **Referral Code**: Unique 6-character code
- **Proposer Information**: Customer who is referring (first/last name, npkenn, IBAN)
- **Product Information**: What product is being recommended
- **Reward Information**: What bonus the proposer will receive
- **Contact Method**: Email address or NULL (if using WhatsApp/SMS/QR)
- **Timestamps**: When referral was created

---

### 10. **Juridical Logging**

```
┌─────────────────────────────────────────────────────────────┐
│ COMPLIANCE LOGGING                                          │
│ Method: logSelectedInformation(crcData, errorText)          │
└─────────────────────────────────────────────────────────────┘
                          ↓
              Calls: juristicalLoggingService.sendStartLog()
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ DATA LOGGED FOR COMPLIANCE                                  │
│ - Activity: "Kunden werben Kunden"                         │
│ - Action: "Abschicken Kunden werben Kunden"                │
│ - Participant Number                                        │
│ - Selected Account (IBAN)                                   │
│ - Selected Reward                                           │
│ - Recommended Product                                       │
│ - Generated Referral Code                                   │
│ - Timestamp                                                 │
│ - Channel (Web, Mobile)                                     │
│ - Error Status (if any)                                     │
└─────────────────────────────────────────────────────────────┘
```

**Data Source:** juristicalLoggingService (SC Layer)
- Writes to audit log database
- Required for regulatory compliance
- Tracks all customer referral activities

---

### 11. **Response Back to Frontend**

```
┌─────────────────────────────────────────────────────────────┐
│ RESPONSE FLOWS BACK UP                                      │
│ DAO → Service → Process → Controller                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ CONTROLLER BUILDS JSON RESPONSE                             │
│ File: CrcJsonController.java                               │
└─────────────────────────────────────────────────────────────┘

Response JSON:
{
  "result": {
    "items": [
      {
        "crcCode": "A7K9M2"
      }
    ]
  }
}
```

---

### 12. **Frontend Receives Response and Redirects**

```
┌─────────────────────────────────────────────────────────────┐
│ JAVASCRIPT CALLBACK                                         │
│ File: kwkpanel.js                                           │
│ Method: sendReference() callback                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
              Extracts referral code from response
                          ↓
              this.kwkCode = "A7K9M2"
                          ↓
              Stores in sessionStorage
                          ↓
              Redirects to confirmation page
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ CONFIRMATION PAGE                                           │
│ URL: /banking/pk/kwk/confirmationpage                      │
│ Shows: Referral code and sharing options                   │
└─────────────────────────────────────────────────────────────┘
```

**User Sees:**
- Success message
- Referral code: "A7K9M2"
- Options to share:
  - Email (compose email with code)
  - WhatsApp (share via WhatsApp)
  - SMS (share via SMS)
  - QR Code (generate QR code with link)

---

## Complete Data Source Summary

### ⚠️ CRITICAL UNDERSTANDING: The Account Data Origin Chain

Before diving into technical data sources, it's crucial to understand **where account data comes from originally**:

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: CUSTOMER OPENS ACCOUNT                              │
│ - Branch teller system OR                                   │
│ - Online account opening application OR                     │
│ - Mobile app account opening                                │
└──────────────────────┬──────────────────────────────────────┘
                       │ Creates account
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: ACCOUNT CREATED IN CORE BANKING SYSTEM             │
│ **MAINFRAME** (IBM z/OS, COBOL/CICS)                       │
│ - Account master record created                             │
│ - Customer relationship established                         │
│ - Account number assigned                                   │
│ - Product type set (checking, savings, etc.)               │
│ - Initial permissions/limits set                            │
└──────────────────────┬──────────────────────────────────────┘
                       │ Account now exists
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: NIGHTLY BATCH PROCESSES                             │
│ - Mainframe batch jobs run (e.g., every night at 2 AM)     │
│ - Synchronize account states                                │
│ - Update balances, limits, permissions                      │
│ - Generate reports and data feeds                           │
└──────────────────────┬──────────────────────────────────────┘
                       │ Data is now queryable
                       ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: KWK APPLICATION QUERIES DATA                        │
│ - User logs into online banking                             │
│ - Opens KWK page                                            │
│ - App calls PKVD mainframe transaction                      │
│ - Retrieves list of customer's accounts                     │
│ - **APP NEVER WRITES ACCOUNTS** - only reads!              │
└─────────────────────────────────────────────────────────────┘
```

**Key Insights:**
1. ✅ **Account data is NOT created by this application**
2. ✅ **Mainframe is the SYSTEM OF RECORD** (single source of truth)
3. ✅ **This app is READ-ONLY** for account data
4. ✅ **Accounts are created by**: Branch systems, online banking, mobile apps
5. ✅ **For migration**: You MUST keep accessing mainframe OR replicate the data

---

## Complete Data Source Summary

### Database Tables Used

#### **1. CUSTOMER_REFER_CUSTOMER (Main Table)**
- **Purpose**: Stores all customer referral records
- **Access**: Via KwkDAO → JPA/Hibernate
- **Operations**: INSERT (create referral), SELECT (check code uniqueness)
- **Data**:
  ```
  CRC_ID              (Primary Key, auto-generated)
  CRC_CODE            (Unique referral code)
  CRC_ACCOUNTOWNER_NAME
  CRC_IBAN            (Settlement account)
  CRC_FIRST_NAME      (Proposer's first name)
  CRC_LAST_NAME       (Proposer's last name)
  CRC_EMAIL_ADDRESS   (Optional email)
  CRC_NPKENN          (Customer number)
  CRC_BOUNTY          (Reward description)
  CRC_BOUNTYID        (Reward ID)
  CRC_PRODUCTID       (Product ID)
  CRC_PRODUCT_NAME    (Product name)
  CRC_CREATION_TS     (Creation timestamp)
  CRC_LASTUPDATE_TS   (Last update timestamp)
  ```

#### **2. Product/Account Data from MAINFRAME (PKVD)**
- **⚠️ CRITICAL**: This data does NOT come from local database tables!
- **Primary Source**: Mainframe Core Banking System
- **Access**: Via ProductService → RawTnvProductRetrieverService → PKVD Host Access
- **Mainframe Transaction**: TVS90 (PersonKundeVertragsDaten)
- **Operations**: Real-time mainframe query
- **What's Retrieved**:
  - All customer accounts (checking, savings, loans, credit cards)
  - Account ownership and relationships
  - Product types and categories
  - Authorization levels (read/write permissions)
  - Account status and limits
- **Who Populates**: Core banking systems, account opening applications, not this app
- **Caching**: 30 minutes in PersonKundeVertragsDatenCache
- **For KWK**: Filtered to show only accounts with 'REWARDCREDIT' permission

#### **3. Participant/Customer Tables**
- **Purpose**: Store customer master data
- **Access**: Via ParticipantService → Database or Mainframe
- **Operations**: SELECT (retrieve customer details)

#### **4. Audit/Log Tables**
- **Purpose**: Compliance and audit logging
- **Access**: Via JuristicalLoggingService → Log database
- **Operations**: INSERT (log all KWK activities)

---

### External Systems Called

#### **1. Natural Person API V3 Service**
- **Purpose**: Retrieve customer's first and last name
- **Type**: Internal API (SC Layer)
- **Data Source**: Database or external system
- **Called by**: naturalPersonAPIV3Service.retrieveNaturalPersons()

#### **2. Customers API V3 Service**
- **Purpose**: Check customer type (employee vs regular customer)
- **Type**: Internal API (SC Layer)
- **Data Source**: Database or CRM system
- **Called by**: customersAPIV3Service.retrieveCustomerAgreement()

#### **3. IBAN Converter Service**
- **Purpose**: Convert account numbers to IBAN format
- **Type**: Internal service (SC Layer)
- **Data Source**: May call mainframe for bank code resolution
- **Called by**: ibanConverterService.convertLocaleDEToIbanDE()

#### **4. CCB Number Resolver Service**
- **Purpose**: Resolve technical account numbers to external formats
- **Type**: Internal service (SC Layer)
- **Data Source**: May call mainframe (MNC)
- **Called by**: ccbNumberResolverService.resolveExternalAccountNumberAndBankCodeFromTechnicalAccountNumber()

#### **5. Mainframe PKVD Service (PersonKundeVertragsDaten)** ⭐ **MOST IMPORTANT**
- **Purpose**: THE primary source for all customer account data
- **Type**: Mainframe host service (CICS transaction)
- **Transaction Code**: TVS90
- **Technology**: 
  - Host Access Framework (com.commerzbank.frame.hostaccess)
  - COBOL copybooks (Tvs90c01 for request, Tvs90c02 for response)
  - MNC (Mainframe Network Connector) for communication
- **Called by**: PkvdProductIdentifierRetrieverService.retrievePersonKundeVertragsDaten()
- **Request Structure**:
  ```
  PkvdRequest:
  - Mandant: "CB" (Commerzbank)
  - PersonId: User/Customer identifier
  - FilterFlag: "F" (filter flag)
  - Offset: For pagination (multi-page results)
  ```
- **Response Structure**:
  ```
  PkvdReply:
  - ReturnCode: "0000" = success
  - Products[]: List of all customer accounts
    └─→ For each product:
        ├─→ CustomerNumber
        ├─→ InternalAccountNumber
        ├─→ Branch (product category code)
        ├─→ Currency
        ├─→ TnvCategory
        ├─→ DepotNumber (for securities)
        ├─→ GeschäftsvereinbarungsKennung (product number)
        └─→ etc.
  - CustomerRelations[]: Customer relationships
    └─→ For each relation:
        ├─→ CustomerNumber
        ├─→ Role (account holder, authorized signer, etc.)
        └─→ AuthorizationType (read/write permissions)
  - Offset: For pagination (if more data available)
  ```
- **Pagination**: 
  - Mainframe may return data in chunks
  - App automatically reloads with offset until complete
  - Handled by: PersonKundeVertragsDatenV2Hostaccess.isReloadingComplete()
- **Caching**:
  - Cache: PersonKundeVertragsDatenCache
  - TTL: 30 minutes
  - Key: SessionId + PersonId + "PERSON_KUNDE_VERTRAGSDATEN_LESEN"
  - Annotation: @Cacheable
  - **Risk**: User sees stale data if account opened/closed in last 30 min
- **Hystrix Circuit Breaker**:
  - Annotation: @CcbHystrix(groupKey = "PersonKundeVertragsDaten")
  - Purpose: If mainframe is down, prevent cascading failures
  - Fallback: Application cannot show accounts if mainframe unavailable
- **Data Returned**: EVERYTHING the customer owns
  - Current accounts (Girokonto)
  - Savings accounts (Sparkonto)
  - Fixed-term deposits (Festgeld)
  - Credit cards (Kreditkarten)
  - Loans (Kredite)
  - Securities accounts (Depot)
  - And more...

#### **6. Permission Check Services**
#### **6. Permission Check Services**
- **Purpose**: Determine which accounts have 'REWARDCREDIT' permission
- **Called by**: 
  - authorizationService.updatePermissionInformation()
  - checkPermissions.retrieveProductLimitInformation()
- **Data Source**: 
  - May call mainframe for product limits
  - Local authorization rules (database/configuration)
  - Combines mainframe data + local rules
- **Result**: Each account flagged with allowed actions/permissions

#### **7. Additional Mainframe Services**
- **Purpose**: Various account operations and data enrichment
- **Type**: Legacy mainframe system (COBOL/CICS)
- **Protocol**: MNC (Mainframe Network Connector)
- **Usage**: 
  - Account balance queries (if not in PKVD response)
  - Transaction history
  - Product limit checks
  - Customer master data lookups
- **Note**: PKVD returns most data, but additional calls may be needed

---

### Where Does Data Come From? - The Complete Picture

```
┌────────────────────────────────────────────────────────────┐
│ QUESTION: Where does account data in KWK come from?       │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ ANSWER: It's a CHAIN of data sources                       │
└────────────────────────────────────────────────────────────┘

Level 1: ORIGIN (Who creates accounts?)
├─→ Branch systems (teller creates account for customer)
├─→ Online banking (customer self-service account opening)
├─→ Mobile apps (account opening via smartphone)
└─→ Partner systems (e.g., comdirect transfers)
       ↓ All write to...

Level 2: SYSTEM OF RECORD (Where is the master data?)
└─→ **MAINFRAME CORE BANKING SYSTEM**
    ├─→ IBM z/OS operating system
    ├─→ COBOL/CICS applications
    ├─→ DB2 or IMS databases
    ├─→ This is THE authoritative source
    └─→ All other systems must sync from here
       ↓ Accessed via...

Level 3: ACCESS LAYER (How does KWK read it?)
└─→ **PKVD Host Service** (PersonKundeVertragsDaten)
    ├─→ Transaction: TVS90
    ├─→ Copybooks: Tvs90c01/Tvs90c02
    ├─→ Returns: Complete list of customer accounts
    └─→ Called by: PkvdProductIdentifierRetrieverService
       ↓ Then...

Level 4: SERVICE LAYER (Who calls PKVD?)
└─→ ProductServiceImpl.retrieveProductList()
    ├─→ Location: ccb/middletier/shared/service/common-service/
    ├─→ Calls: RawTnvProductRetrieverService
    └─→ Applies filters: KWK_REWARDCREDIT_FILTER
       ↓ Then...

Level 5: CACHING LAYER (Avoid repeated mainframe calls)
└─→ PersonKundeVertragsDatenCache
    ├─→ TTL: 30 minutes
    ├─→ Reduces mainframe load
    └─→ Risk: Slightly stale data
       ↓ Finally...

Level 6: APPLICATION LAYER (What does KWK do?)
└─→ KWK Process: retrieveSettlementAccounts()
    ├─→ Gets accounts from cache/mainframe
    ├─→ Filters to accounts with REWARDCREDIT permission
    ├─→ Formats IBANs for display
    ├─→ Adds product display names
    └─→ Returns to frontend for user selection

┌────────────────────────────────────────────────────────────┐
│ CRITICAL POINT: KWK NEVER CREATES OR MODIFIES ACCOUNTS    │
│ It only READS them from mainframe!                         │
└────────────────────────────────────────────────────────────┘
```

---

## Business Rules and Logic

### **1. Security and Authorization**
- ✅ User must be authenticated (logged into online banking)
- ✅ User must have 'REWARDCREDIT' permission
- ✅ Selected IBAN must belong to the logged-in customer
- ✅ All actions are logged for compliance

### **2. Referral Code Generation**
- ✅ 6 characters long
- ✅ Alphanumeric: 1-9, A-Z (excluding I, O, 0)
- ✅ No character appears more than 2 times
- ✅ Code is reversed after generation
- ✅ Must be unique in database
- ✅ Generated on server-side (security)

### **3. Data Validation**
- ✅ IBAN format validated (@IbanDE)
- ✅ Email format validated (@EmailAddress) - optional
- ✅ Account owner name max 150 characters
- ✅ Generic descriptions max 256 characters

### **4. Settlement Account**
- ✅ Must have KWK_REWARDCREDIT_FILTER permission
- ✅ Customer can choose which account receives the reward
- ✅ IBAN is displayed to user
- ✅ Authorization check ensures customer owns the account

### **5. Product and Reward Configuration**
- Products and rewards are pre-configured
- Each product has associated rewards (bounties)
- Reward amounts and types vary by product
- Max availability time may apply to rewards

### **6. Sharing Methods**
- Email: Send referral code via email
- WhatsApp: Share on WhatsApp (mobile only)
- SMS: Share via SMS
- QR Code: Generate QR code for scanning

---

## Data Flow Diagram - Summary

```
┌──────────────┐
│   BROWSER    │ User opens /banking/pk/kwk/
└──────┬───────┘
       │
       ↓ (1) HTTP GET
┌──────────────────────────────────────────────────────────┐
│  JAVA PAGE (KWKOverviewPage.java)                        │
│  - Calls retrieveSettlementAccounts()                    │
│  - Embeds data in HTML                                   │
│  - Loads React bundle                                    │
└──────┬───────────────────────────────────────────────────┘
       │
       │ Data Sources for Page Load:
       ├──→ **MAINFRAME (PKVD)** - PRIMARY SOURCE for account data
       │    └─→ Transaction: TVS90 (PersonKundeVertragsDaten)
       │    └─→ Returns: All customer accounts and products
       ├──→ IBAN Converter Service (format IBANs)
       ├──→ Product Matrix Service (product names)
       └──→ Cache (30 min) to avoid repeated mainframe calls
       │
       ↓ (2) HTML + React rendered
┌──────────────────────────────────────────────────────────┐
│  REACT FRONTEND (kwkpanel.js)                            │
│  - User fills form                                       │
│  - Clicks "Send"                                         │
└──────┬───────────────────────────────────────────────────┘
       │
       ↓ (3) HTTP POST /banking/rest/sendReference
┌──────────────────────────────────────────────────────────┐
│  REST CONTROLLER (CrcJsonController)                     │
│  - Validates input                                       │
│  - Calls process layer                                   │
└──────┬───────────────────────────────────────────────────┘
       │
       ↓ (4) Process call
┌──────────────────────────────────────────────────────────┐
│  PROCESS LAYER (CustomerReferCustomerProcessImpl)        │
│  - Authorization check (@PreAuthorize)                   │
│  - Verify IBAN ownership                                 │
│  - Generate referral code                                │
│  - Retrieve customer info                                │
│  - Build CrcData                                         │
│  - Save to database                                      │
│  - Log for compliance                                    │
└──────┬───────────────────────────────────────────────────┘
       │
       │ Data Sources:
       ├──→ (5) Authorization Service (permissions)
       ├──→ (6) Product Service → Database (accounts)
       ├──→ (7) IBAN Converter → Database/Mainframe
       ├──→ (8) Database: SELECT (check code uniqueness)
       ├──→ (9) Participant Service → Database/Mainframe (customer data)
       ├──→ (10) Natural Person API → Database (name)
       ├──→ (11) Service Layer → DAO Layer
       ├──→ (12) Database: INSERT (save referral)
       └──→ (13) Juridical Logging → Audit Database
       │
       ↓ (14) Response
┌──────────────────────────────────────────────────────────┐
│  REST RESPONSE                                           │
│  { "result": { "items": [{ "crcCode": "A7K9M2" }] } }   │
└──────┬───────────────────────────────────────────────────┘
       │
       ↓ (15) Redirect
┌──────────────────────────────────────────────────────────┐
│  CONFIRMATION PAGE                                       │
│  - Shows referral code                                   │
│  - Provides sharing options                              │
└──────────────────────────────────────────────────────────┘
```

---

## Data Dependencies for Migration

When migrating KWK to a microservice, you need to handle:

### **Database Dependencies**
1. ✅ **CUSTOMER_REFER_CUSTOMER table**
   - Primary data storage
   - Needs to be migrated or replicated
   - Sequence: SEQ_CRC_ID

2. ✅ **Product/Account data**
   - Currently accessed via ProductService
   - Option 1: Replicate data
   - Option 2: Call via API gateway

3. ✅ **Customer master data**
   - Currently accessed via ParticipantService, Natural Person API
   - Option 1: Call existing APIs
   - Option 2: Replicate needed data

### **Service Dependencies**
1. ✅ **ProductService** (SC Layer)
2. ✅ **IbanConverterService** (SC Layer)
3. ✅ **CCBNumberResolverService** (SC Layer)
4. ✅ **ParticipantService** (SC Layer)
5. ✅ **NaturalPersonAPIV3Service** (SC Layer)
6. ✅ **CustomersAPIV3Service** (SC Layer)
7. ✅ **AuthorizationService** (Security)
8. ✅ **JuristicalLoggingService** (Compliance)
9. ✅ **BaseProductMatrixService** (SC Layer)

### **Configuration Dependencies**
1. ✅ Product and reward configuration
2. ✅ Authorization rules
3. ✅ IBAN conversion rules
4. ✅ Email templates
5. ✅ Translations and labels

### **Frontend Dependencies**
1. ✅ React components (kwkpanel.js)
2. ✅ Shared UI components (buttons, dropdowns)
3. ✅ Styling and theming
4. ✅ Translations

---

---

## Migration Considerations - CRITICAL DECISIONS

### ⚠️ THE MAINFRAME DEPENDENCY CHALLENGE

**The biggest challenge for migration is NOT the code - it's the mainframe dependency for account data.**

**Option A: Keep Calling Mainframe via API Wrapper** ✅ **RECOMMENDED**
- Create REST API wrapper around PKVD service
- Microservice calls wrapper instead of direct host access
- Pros: Always current data, lowest risk, mainframe stays system of record
- Cons: Still dependent on mainframe availability

**Option B: Data Replication** ⚠️ **VERY COMPLEX**
- Set up Change Data Capture (CDC) from mainframe
- Sync account data to microservice database
- Pros: Local data copy, faster queries
- Cons: Complex sync logic, eventual consistency, requires mainframe team

**Option C: Hybrid with Aggressive Caching**
- Use Redis for caching account data (5-10 min TTL)
- Call mainframe on cache miss
- Pros: Reduced mainframe calls, better performance
- Cons: Still depends on mainframe

**Recommendation**: Start with Option A or C, avoid Option B unless you have CDC infrastructure.

### What Can Be Migrated Easily
1. ✅ CUSTOMER_REFER_CUSTOMER table (owned by KWK)
2. ✅ KWK business logic (code)
3. ✅ Frontend React components
4. ✅ Referral code generation logic
5. ✅ REST endpoints

### What Cannot Be Migrated (Must Call External Services)
1. ❌ Account data (lives in mainframe)
2. ❌ Customer master data (mainframe)
3. ❌ Product configurations (may be in mainframe)
4. ❌ Authorization rules (complex, multi-system)
5. ❌ Juridical logging (compliance system)

### Service Dependencies to Handle
- Natural Person API V3 → Call via API gateway
- Customers API V3 → Call via API gateway
- IBAN Converter → Call via API gateway
- Authorization Service → Call via API gateway
- Juridical Logging → Call via API gateway
- **PKVD Mainframe** → Create wrapper or use existing account API

---

## Conclusion

The KWK business flow is a complete customer referral system that:
1. **Authenticates and authorizes** the customer
2. **⚠️ Fetches customer's eligible accounts from MAINFRAME** (PKVD host service)
3. **Allows selection** of product, reward, and settlement account
4. **Generates unique referral code** with server-side validation
5. **Retrieves customer information** from multiple services
6. **Persists referral** to local database (CUSTOMER_REFER_CUSTOMER table)
7. **Logs activity** for compliance
8. **Returns referral code** to customer
9. **Provides sharing options** (email, WhatsApp, SMS, QR code)

**CRITICAL UNDERSTANDING**:
- **Account Data Source**: ⭐ **MAINFRAME** (PKVD - PersonKundeVertragsDaten service)
- **Referral Data Storage**: Oracle/DB2 database (CUSTOMER_REFER_CUSTOMER table)
- **System of Record for Accounts**: Mainframe core banking system (NOT this application)
- **KWK's Role**: READ account data, WRITE referral data
- **External Dependencies**: Mainframe, SC layer services, APIs
- **Compliance**: All activities logged for regulatory purposes

**For Migration**:
- **Biggest Challenge**: Mainframe dependency for account data
- **Cannot Migrate**: Account master data (must keep calling mainframe or create wrapper)
- **Can Migrate**: Referral database, business logic, frontend
- **Strategy**: Microservice architecture with external service calls via API gateway

