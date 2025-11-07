# Legacy Pattern vs UCC Pattern - Architecture Comparison

## Quick Summary

The CCB monolith has **TWO architectural patterns** for organizing business applications:

| Aspect | **Legacy Pattern** | **UCC Pattern** |
|--------|-------------------|-----------------|
| **Used For** | Older applications (pre-UCC era) | Modern applications (post-UCC era) |
| **Location** | `ccb/` folder structure | `ucc/` folder structure |
| **Count** | ~50+ applications | ~70+ applications |
| **Process Location** | `ccb/middletier/process/{app}/` | `ucc/{app}/process/` |
| **Interface Location** | `ccb/process-interface/{app}/` | `ucc/{app}/process-interface/` |
| **UI Location** | `ccb/ui/{channel}-webui/{app}/` | `ccb/ui/{channel}-webui/{app}/` (same) |
| **Example** | KWK, Login, Depot, Payments | KnowYourCustomer, AccountOverview, MobilePayment |

---

## Table of Contents
1. [Visual Comparison](#visual-comparison)
2. [Legacy Pattern (Pre-UCC)](#legacy-pattern-pre-ucc)
3. [UCC Pattern (Modern)](#ucc-pattern-modern)
4. [Flow & Dependency Differences](#flow--dependency-differences)
5. [Complete Application Lists](#complete-application-lists)
6. [Migration Implications](#migration-implications)

---

## Visual Comparison

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CCB MONOLITH STRUCTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ FRONTEND LAYER (Shared for both patterns)                 │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ ui-react/                                                  │ │
│  │  - Shared React components                                │ │
│  │  - Build output: lib_*-bundle.js                          │ │
│  └───────────────────────────────────────────────────────────┘ │
│                             ↓                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ UI LAYER (Shared for both patterns)                       │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ ccb/ui/pk-webui/{app}/  ← Pages, REST controllers         │ │
│  │ ccb/ui/msb-webui/{app}/ ← (Same structure for both)       │ │
│  │ ccb/ui/wp-webui/{app}/                                     │ │
│  └────────────┬──────────────────────────┬───────────────────┘ │
│               │                          │                      │
│               │                          │                      │
│  ┌────────────▼───────────────┐  ┌──────▼──────────────────┐  │
│  │ LEGACY PATTERN             │  │ UCC PATTERN             │  │
│  │ (ccb/ structure)           │  │ (ucc/ structure)        │  │
│  ├────────────────────────────┤  ├─────────────────────────┤  │
│  │ ccb/process-interface/     │  │ ucc/{app}/              │  │
│  │    {app}/                  │  │   process-interface/    │  │
│  │      - Interfaces          │  │     - Interfaces        │  │
│  │      - DTOs                │  │     - DTOs              │  │
│  │                            │  │                         │  │
│  │ ccb/middletier/process/    │  │   process/              │  │
│  │    {app}/                  │  │     - Implementation    │  │
│  │      - Implementation      │  │                         │  │
│  │                            │  │   bom/                  │  │
│  │ Examples:                  │  │     - Dependencies      │  │
│  │ - kwk                      │  │                         │  │
│  │ - login                    │  │ Examples:               │  │
│  │ - depot                    │  │ - knowyourcustomer      │  │
│  │ - payments                 │  │ - accountoverview       │  │
│  │ - kreditkarten             │  │ - mobilepayment         │  │
│  └────────────┬───────────────┘  └──────┬──────────────────┘  │
│               │                          │                      │
│               └──────────┬───────────────┘                      │
│                          ↓                                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ SERVICE LAYER (Shared for both patterns)                  │ │
│  ├───────────────────────────────────────────────────────────┤ │
│  │ sc/ - Service Clusters (60+ services)                     │ │
│  │ sb/ - Shared Business                                     │ │
│  │ fw/ - Framework                                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Legacy Pattern (Pre-UCC)

### Structure

```
LEGACY PATTERN STRUCTURE
========================

ccb/
├── process-interface/           ← Process API definitions
│   ├── kwk/                     ← KWK interfaces
│   │   ├── pom.xml
│   │   └── src/main/java/
│   │       └── com/commerzbank/ccb/kwk/processinterface/
│   │           ├── CustomerReferCustomerProcess.java (interface)
│   │           ├── request/
│   │           │   └── SendReferenceRequest.java
│   │           └── response/
│   │               └── SendReferenceResponse.java
│   │
│   ├── login/                   ← Login interfaces
│   ├── payments/                ← Payment interfaces
│   ├── depot/                   ← Depot interfaces
│   └── ... (50+ more apps)
│
├── middletier/process/          ← Process implementations
│   ├── kwk/                     ← KWK implementation
│   │   ├── pom.xml
│   │   └── src/main/java/
│   │       └── com/commerzbank/ccb/kwk/process/
│   │           ├── CustomerReferCustomerProcessImpl.java
│   │           │   @CCBProcess
│   │           │   @CCBTransactionalProcess
│   │           │   implements CustomerReferCustomerProcess
│   │           │
│   │           ├── mapper/
│   │           └── ... (business logic)
│   │
│   ├── login/                   ← Login implementation
│   ├── payments/                ← Payment implementation
│   ├── depot/                   ← Depot implementation
│   └── ... (50+ more apps)
│
└── ui/                          ← UI layer (shared with UCC pattern)
    ├── pk-webui/                ← Private banking UI
    │   ├── kwk/
    │   │   ├── ui/              ← Pages (Wicket)
    │   │   ├── rest/            ← REST controllers
    │   │   └── public/          ← Shared utilities
    │   ├── login/
    │   ├── payments/
    │   └── ...
    │
    ├── msb-webui/               ← Middle-sized business UI
    └── wp-webui/                ← Wealth management UI
```

### Key Characteristics

**Pros:**
- ✅ All process code lives in `ccb/` - single location
- ✅ Clear separation: interfaces vs implementations
- ✅ Simpler to navigate (fewer folders)

**Cons:**
- ❌ No module aggregation (process & interface separate)
- ❌ No BOM (Bill of Materials) - dependencies scattered
- ❌ Mixed with CCB core infrastructure code
- ❌ Harder to identify what's an "app" vs infrastructure

**File Locations:**
```
Process Interface:    ccb/process-interface/{app}/
Process Implementation: ccb/middletier/process/{app}/
UI Pages:            ccb/ui/{channel}-webui/{app}/ui/
REST API:            ccb/ui/{channel}-webui/{app}/rest/
```

---

## UCC Pattern (Modern)

### Structure

```
UCC PATTERN STRUCTURE
=====================

ucc/
├── knowyourcustomer/            ← Complete app module
│   ├── pom.xml                  ← Aggregator (builds all sub-modules)
│   │   <modules>
│   │     <module>process-interface</module>
│   │     <module>process</module>
│   │     <module>ui</module>
│   │     <module>bom</module>
│   │   </modules>
│   │
│   ├── process-interface/       ← Process API
│   │   ├── pom.xml
│   │   └── src/main/java/
│   │       └── com/commerzbank/ccb/ucc/knowyourcustomer/processinterface/
│   │           ├── CddCheckWithBpkennProcess.java (interface)
│   │           ├── request/
│   │           └── response/
│   │
│   ├── process/                 ← Process implementation
│   │   ├── pom.xml
│   │   └── src/main/java/
│   │       └── com/commerzbank/ccb/ucc/knowyourcustomer/process/
│   │           ├── CddCheckWithBpkennProcessImpl.java
│   │           │   @CCBProcess
│   │           │   @CCBTransactionalProcess
│   │           │
│   │           ├── mapper/
│   │           └── ... (business logic)
│   │
│   ├── ui/                      ← UI module (usually empty)
│   │   └── pom.xml
│   │
│   └── bom/                     ← Bill of Materials
│       └── pom.xml              ← All runtime dependencies
│
├── accountoverview/             ← Another complete app
│   ├── pom.xml
│   ├── process-interface/
│   ├── process/
│   ├── ui/
│   └── bom/
│
├── mobilepayment/
├── privatecustomeronboarding/
└── ... (70+ more apps)

ccb/ui/                          ← UI still lives here (shared with legacy)
└── pk-webui/
    └── accountoverview/         ← UI for UCC apps
        ├── ui/
        ├── rest/
        └── public/
```

### Key Characteristics

**Pros:**
- ✅ Self-contained module - everything for one app in one folder
- ✅ Aggregator POM - build all parts together
- ✅ BOM module - clear runtime dependencies
- ✅ Easy to identify apps (just look at `ucc/` folders)
- ✅ Better isolation - each app is independent
- ✅ Maven reactor build - can build single app

**Cons:**
- ❌ More folders/structure overhead
- ❌ UI still separated in `ccb/ui/` (not truly self-contained)

**File Locations:**
```
Process Interface:    ucc/{app}/process-interface/
Process Implementation: ucc/{app}/process/
UI Pages:            ccb/ui/{channel}-webui/{app}/ui/
REST API:            ccb/ui/{channel}-webui/{app}/rest/
BOM:                 ucc/{app}/bom/
Aggregator:          ucc/{app}/pom.xml
```

---

## Flow & Dependency Differences

### Request Flow: Legacy Pattern

```
LEGACY PATTERN FLOW (Example: KWK)
===================================

1. User in Browser
   └── Loads page: http://banking/kwk

2. CCB UI Layer (pk-webui)
   File: ccb/ui/pk-webui/kwk/ui/src/.../KWKOverviewPage.java
   ├── Loads React bundle (lib_kwk-page-bundle.js)
   ├── Provides initial data via getDataForReact()
   └── User submits form → triggers REST call

3. REST Controller (pk-webui)
   File: ccb/ui/pk-webui/kwk/rest/src/.../CrcJsonController.java
   │
   │   @Controller
   │   public class CrcJsonController {
   │       @Inject
   │       @Named("customerReferCustomerProcess")
   │       private CustomerReferCustomerProcess process; ← LEGACY INTERFACE
   │                                                        from ccb/process-interface/kwk/
   │       @RequestMapping("/sendReference")
   │       public JsonResponse sendReference(...) {
   │           return process.sendReference(request); ─┐
   │       }                                            │
   │   }                                                │
   │                                                    │
4. Process Interface (Separate Location)               │
   File: ccb/process-interface/kwk/src/.../           │
         CustomerReferCustomerProcess.java             │
   │                                                    │
   │   public interface CustomerReferCustomerProcess { │ (interface)
   │       SendReferenceResponse sendReference(...);   │
   │   }                                                │
   │                                                    │
5. Process Implementation (Another Separate Location)  │
   File: ccb/middletier/process/kwk/src/.../          │
         CustomerReferCustomerProcessImpl.java    <────┘
   │                                                (implementation)
   │   @CCBProcess
   │   @CCBTransactionalProcess
   │   public class CustomerReferCustomerProcessImpl
   │           implements CustomerReferCustomerProcess {
   │
   │       @Inject private ParticipantService participantService; ← SC service
   │       @Inject private NaturalPersonService personService;     ← SC service
   │       @Inject private ProductService productService;          ← SC service
   │       @Inject private CustomerReferCustomerService crcService;← SC service
   │
   │       public SendReferenceResponse sendReference(SendReferenceRequest req) {
   │           // 1. Get participant data
   │           Participant p = participantService.get(req.getUserId()).get();
   │           
   │           // 2. Get customer name
   │           Person person = personService.get(p.getPersonId()).get();
   │           
   │           // 3. Validate product
   │           Product product = productService.get(req.getProductCode()).get();
   │           
   │           // 4. Generate referral code
   │           String code = crcService.generateCode(...).get();
   │           
   │           // 5. Save to database
   │           crcService.saveReferral(...);
   │           
   │           return new SendReferenceResponse(code);
   │       }
   │   }

6. Service Cluster Layer
   Files: sc/participant/, sc/person/, sc/sharedbusiness/
   └── SC services execute business logic
       ├── Query database
       ├── Call host systems
       └── Return data

7. Response flows back up the chain
   Process → REST Controller → Browser (JSON)
```

**Dependency Path (Legacy):**
```
ccb/ui/pk-webui/kwk/rest
    │ (depends on)
    ├── ccb/process-interface/kwk        ← Interface (separate location)
    │
    └── (Spring wires to implementation)
            ↓
        ccb/middletier/process/kwk       ← Implementation (separate location)
            │ (depends on)
            ├── sc/participant
            ├── sc/person
            ├── sc/sharedbusiness
            └── sc/kwk-service (if exists)
```

### Request Flow: UCC Pattern

```
UCC PATTERN FLOW (Example: Know Your Customer)
===============================================

1. User in Browser
   └── Calls API: http://banking/api/cddCheck

2. REST Controller (UI layer - still in ccb/ui)
   File: ccb/ui/pk-webui/kyc/rest/src/.../KycJsonController.java
   │
   │   @Controller
   │   public class KycJsonController {
   │       @Inject
   │       @Named("cddCheckWithBpkennProcess")
   │       private CddCheckWithBpkennProcess process; ← UCC INTERFACE
   │                                                     from ucc/knowyourcustomer/
   │       @RequestMapping("/cddCheck")                      process-interface/
   │       public JsonResponse cddCheck(...) {
   │           return process.cddCheckWithBpkenn(req); ─┐
   │       }                                             │
   │   }                                                 │
   │                                                     │
3. Process Interface (Inside UCC Module)                │
   File: ucc/knowyourcustomer/process-interface/src/...│
         CddCheckWithBpkennProcess.java                 │
   │                                                     │ (interface)
   │   public interface CddCheckWithBpkennProcess {     │
   │       CddCheckWithBpkennResponse                   │
   │           cddCheckWithBpkenn(...);                 │
   │   }                                                 │
   │                                                     │
4. Process Implementation (Same UCC Module)             │
   File: ucc/knowyourcustomer/process/src/.../         │
         CddCheckWithBpkennProcessImpl.java        <────┘
   │                                                (implementation)
   │   @CCBProcess
   │   @CCBTransactionalProcess
   │   public class CddCheckWithBpkennProcessImpl
   │           implements CddCheckWithBpkennProcess {
   │
   │       @Inject
   │       @Named("customerDueDiligenceService")
   │       private CustomerDueDiligenceService cddService; ← SC service
   │
   │       public CddCheckWithBpkennResponse
   │               cddCheckWithBpkenn(CddCheckWithBpkennRequest req) {
   │           
   │           // 1. Map UCC request → SC request
   │           CheckCustomerRiskRatingServiceRequest svcReq =
   │               Mapper.toServiceRequest(req);
   │           
   │           // 2. Call SC service
   │           CheckCustomerRiskRatingServiceResponse svcResp =
   │               cddService.checkCustomerRiskRating(svcReq).get();
   │           
   │           // 3. Map SC response → UCC response
   │           return Mapper.toProcessResponse(svcResp);
   │       }
   │   }

5. Service Cluster Layer
   Files: sc/knowyourcustomer/
   └── SC services execute business logic

6. Response flows back
   Process → REST Controller → Browser
```

**Dependency Path (UCC):**
```
ccb/ui/pk-webui/kyc/rest
    │ (depends on)
    └── ucc/knowyourcustomer/process-interface  ← Interface
            │
            └── (Spring wires to implementation)
                    ↓
                ucc/knowyourcustomer/process     ← Implementation (SAME MODULE!)
                    │ (depends on)
                    ├── sc/knowyourcustomer
                    ├── sc/customer
                    └── ... (other SC services)
                    
                    │ (runtime dependencies listed in)
                    └── ucc/knowyourcustomer/bom  ← BOM module
```

### Key Differences

| Aspect | Legacy Pattern | UCC Pattern |
|--------|---------------|-------------|
| **Interface Location** | `ccb/process-interface/{app}/` | `ucc/{app}/process-interface/` |
| **Implementation Location** | `ccb/middletier/process/{app}/` | `ucc/{app}/process/` |
| **Module Cohesion** | Interface & impl separated | Interface & impl in same module |
| **Build Unit** | Build interface + impl separately | Build entire app with one command |
| **Dependency Management** | Scattered in multiple POMs | Centralized in BOM module |
| **Discoverability** | Hard to find (mixed with CCB core) | Easy (one folder = one app) |

---

## Complete Application Lists

### Legacy Pattern Applications

**How to Identify:** Look for matching folders in both:
- `ccb/process-interface/{name}/` AND
- `ccb/middletier/process/{name}/`

**Complete List (60 applications):**

```
LEGACY PATTERN APPS (in ccb/)
==============================

Account & Banking:
  1. account                      - Account management
  2. depot                        - Securities depot
  3. cfd                          - CFD (Contract for Difference) trading
  4. savings-plan                 - Savings plan management
  5. sepaupload                   - SEPA payment upload
  6. guarantees                   - Bank guarantees
  7. loan                         - Loan processing
  8. kreditkarten                 - Credit cards

Payment & Transactions:
  9. payments                     - Payment processing
  10. epay                        - Electronic payment
  11. swiftresearch               - SWIFT payment research

Investment & Trading:
  12. investmentadvice            - Investment advisory
  13. ipo                         - IPO (Initial Public Offering)
  14. fund-mgmt                   - Fund management
  15. asset-mgmt                  - Asset management
  16. financeoverview             - Finance overview

Customer Acquisition & Referral:
  17. kwk                         - Kunden Werben Kunden (Customer Referral)
  
Authentication & Security:
  18. login                       - User login
  19. application-login           - Application login
  20. appauthentication           - App authentication
  21. appprofile                  - App profile management
  22. cmappprofile                - CM app profile
  23. phototan-authorisation      - PhotoTAN authorization
  24. tan                         - TAN (Transaction Number) management
  25. bicauthorization            - BIC authorization
  26. frauddetection              - Fraud detection

Digital Processes (DiPro):
  27. dipro-advisersearch         - Adviser search
  28. dipro-adviserselection      - Adviser selection
  29. dipro-affiliatetracking     - Affiliate tracking
  30. dipro-callmoney             - Call money
  31. dipro-checkeligibility      - Eligibility check
  32. dipro-createparticipant     - Create participant
  33. dipro-creditcardconfiguration - Credit card config
  34. dipro-crs                   - CRS (Common Reporting Standard)
  35. dipro-currentaccountopening - Current account opening
  36. dipro-deletedocument        - Delete document
  37. dipro-generateletter        - Generate letter
  38. dipro-googleanalyticsreporting - Google Analytics
  39. dipro-juristicallogging     - Legal logging
  40. dipro-onlinebankingaccess   - Online banking access
  41. dipro-piahandover           - PIA handover
  42. dipro-schufaacceptance      - SCHUFA acceptance
  43. dipro-sendemail             - Send email
  44. dipro-sendsms               - Send SMS
  45. dipro-tnv                   - TNV process
  46. dipro-tnvprofiletostandard  - TNV profile to standard

DIVOLE (Digital Vollmacht - Digital Power of Attorney):
  47. divole-pia                  - PIA (digital power of attorney)
  48. divole-shared               - DIVOLE shared

Content & Document:
  49. document                    - Document management
  50. dcrm                        - DCRM (Digital Content & Rights Management)
  51. formsprocess                - Forms processing

Landing Pages & Portals:
  52. landingpage                 - Landing page
  53. accessdigitalexploration    - Access digital exploration
  54. accessleasingportal         - Access leasing portal

Mobile & Alerts:
  55. mobile2.0-reporting         - Mobile 2.0 reporting
  56. mobileaccountalert          - Mobile account alerts
  57. kontoalarmprofile           - Account alert profile

Misc/Technical:
  58. smartapp                    - Smart app
  59. gppdata                     - GPP data
  60. productdetails              - Product details
  61. zvue-creation               - ZVUE creation
  62. technical-processes         - Technical processes
  63. common                      - Common processes
  64. shared                      - Shared processes
  65. shared-divole               - Shared DIVOLE
  66. legacy                      - Legacy processes
```

**UI Locations for Legacy Apps:**

```
PK-WEBUI (Private Banking):
  ccb/ui/pk-webui/
    - account, administration, cfd, comdirect, crs, dcrm, depot
    - epay, financeoverview, formsprocess, fund-mgmt
    - investmentadvice, ipo, kreditkarten, kwk
    - landingpage, login, payments, pib, productdetail
    - react, savings-plan, securitytransactions, sepaupload
    - zvue-creation

MSB-WEBUI (Middle-Sized Business):
  ccb/ui/msb-webui/
    - administration, cb-accessdigitalexploration
    - cb-accessleasingportal, cb-creditcard
    - cb-financeoverview, cb-smartapp
    - cmappprofile, document, login, moneycollect
    - msb-guarantees, swiftresearch

WP-WEBUI (Wealth Management):
  ccb/ui/wp-webui/
    - cb-securitiesaccounts, cb-securitytransactions
    - ipo
```

### UCC Pattern Applications

**How to Identify:** Just list folders under `ucc/` (excludes utilities, each folder = one app)

**Complete List (79 applications):**

```
UCC PATTERN APPS (in ucc/)
==========================

Account Management:
  1. accountcardandcreditmanagement    - Account, card & credit mgmt
  2. accountoverview                   - Account overview
  3. accountproductchangemanagement    - Account product changes
  4. currentaccountmanagement          - Current account management
  5. savingsaccountmanagement          - Savings account management
  6. balanceoverview                   - Balance overview
  7. balance                           - Balance services

Activity & Tasks:
  8. activitymanagement                - Activity management

Advisory & Sales:
  9. adviser                           - Adviser functions

Approval & Workflow:
  10. approval                         - Approval workflows
  11. approvalapproaches               - Approval approaches
  12. approvalmanagement               - Approval management

Asset & Investment:
  13. assetmanagement                  - Asset management
  14. investmentadvice                 - Investment advice
  15. ebase                            - eBase integration
  16. depotorderbook                   - Depot order book

Authentication & Security:
  17. appownershiptoken                - App ownership token
  18. customerauthentication           - Customer authentication
  19. authenticationmanagement         - Authentication management
  20. authoritymanagement              - Authority management
  21. personalauthoritymanagement      - Personal authority mgmt

Cards & Credit:
  22. creditcardmanagement             - Credit card management
  23. creditdecisionmanagment          - Credit decision management
  24. creditoffercreation              - Credit offer creation
  25. creditoverview                   - Credit overview
  26. debitcard                        - Debit card

Consent & Compliance:
  27. appuserconsentmanagement         - App user consent
  28. dataaccessconsentmanagement      - Data access consent
  29. customerschufaclause             - Customer SCHUFA clause
  30. regulatorymodule                 - Regulatory module

Customer Management:
  31. customeroffboarding              - Customer offboarding
  32. hybridcustomer                   - Hybrid customer
  33. fasttrackparticipantcreation     - Fast participant creation
  34. participantcreation              - Participant creation
  35. privatecustomeronboarding        - Private customer onboarding
  36. participantprofilemanagement     - Participant profile mgmt
  37. partymanagement                  - Party management
  38. partyprofilemanagement           - Party profile management
  39. profilemanagement                - Profile management

Documents & Archive:
  40. document                         - Document management
  41. archive                          - Archive

Finance & Products:
  42. financeoverview                  - Finance overview
  43. specialproductmanagement         - Special product management
  44. productbase                      - Product base
  45. homeloan                         - Home loan
  46. leasing                          - Leasing
  47. moneymarketloans                 - Money market loans

KYC & Compliance:
  48. knowyourcustomer                 - Know Your Customer (KYC)
  49. legitimationmanagement           - Legitimation management
  50. watchlistcheck                   - Watchlist check

Overdraft & Limits:
  51. overdraftmanagement              - Overdraft management

Payments & Transfers:
  52. mobilepayment                    - Mobile payment
  53. instantpayment                   - Instant payment
  54. psd2paymentmanagement            - PSD2 payment management
  55. transactionoverview              - Transaction overview
  56. transactionsearch                - Transaction search
  57. msborderoverview                 - MSB order overview

Risk & Fraud:
  58. riskinformation                  - Risk information
  59. productorderfraud                - Product order fraud

Search & Discovery:
  60. ordersearch                      - Order search

Security & Recommendations:
  61. securityrecommendations          - Security recommendations

Service Orders:
  62. serviceorder                     - Service orders

PIA & PSD2:
  63. pia                              - PIA (Payment Initiation API)
  64. psd2productfilter                - PSD2 product filter

Push & Notifications:
  65. pushgatewaymt                    - Push gateway (middle tier)
  66. pushgatewaynotifications         - Push notifications
  67. pushtanapp                       - Push TAN app

Chat & Communication:
  68. mobilechat                       - Mobile chat

Insurance:
  69. insurance                        - Insurance

Blocker & Limits:
  70. blocker                          - Blocker functionality

Shared & Utilities:
  71. sharedbusiness                   - Shared business logic
  72. sharedprocesses                  - Shared processes
  73. processmanagementutils           - Process management utilities
  74. utilities                        - Utilities

Banking Solutions:
  75. cbv                              - CBV (Commerzbank Vermögen)
  76. comfinanz                        - Comfinanz
  77. comfortlogin                     - Comfort login
  78. clientidentifier                 - Client identifier

Examples & POC:
  79. reactexample                     - React example
  80. zvuepoc                          - ZVUE POC
  81. tushakedowneft                   - TU Shakedown EFT
```

**Note:** UCC apps typically do NOT have UI folders in `ucc/{app}/ui/` - their UI still lives in `ccb/ui/{channel}-webui/{app}/`

---

## Migration Implications

### For KWK Migration to Microservice

Since **KWK uses the Legacy Pattern**, here's what needs to be extracted:

```
LEGACY PATTERN (Current KWK)
============================

Backend to Extract:
  ✓ ccb/process-interface/kwk/          → Move to microservice
      └── CustomerReferCustomerProcess.java
      └── request/response DTOs
  
  ✓ ccb/middletier/process/kwk/         → Move to microservice
      └── CustomerReferCustomerProcessImpl.java
      └── Mappers, business logic
  
  Dependencies to Extract:
  ✓ SC services used by KWK:
      - sc/participant (ParticipantService)
      - sc/person (NaturalPersonAPIV3Service)
      - sc/sharedbusiness (ProductService, IbanConverter, etc.)
      - sc/kwk-service (if exists - CustomerReferCustomerService)

Frontend to Extract:
  ✓ ccb/ui/pk-webui/kwk/                → Move to microservice
      ├── ui/ (KWKOverviewPage.java, models)
      ├── rest/ (CrcJsonController.java)
      └── public/ (dispatchers, utilities)
  
  ✓ ui-react React components:          → Move to microservice
      └── parent_comp/kwk/
          ├── kwk-page.js
          ├── kwkpanel.js
          ├── kwkselection.js
          ├── confpanel.js
          ├── qrconfpanel.js
          └── kwkemailpanel.js
      
      └── child_comp/*                   → Shared components
          (buttons, dropdowns, inputs, utils, validators)
```

### Migration Complexity Comparison

| Aspect | Legacy Pattern | UCC Pattern |
|--------|---------------|-------------|
| **Module Identification** | Hard - scattered across ccb/ | Easy - one folder in ucc/ |
| **Dependency Extraction** | Hard - no BOM, dependencies in multiple POMs | Easier - BOM lists all deps |
| **Build Isolation** | Hard - tied to CCB build | Easier - can build module independently |
| **Testing Isolation** | Hard - shared test infrastructure | Easier - module has own tests |
| **Interface Stability** | Same for both | Same for both |
| **SC Service Dependencies** | Same for both | Same for both |

**Verdict:** UCC pattern is **slightly easier** to migrate, but both require similar effort for:
- Extracting SC service dependencies
- Migrating UI code
- Setting up new microservice infrastructure

---

## Quick Reference Tables

### Pattern Identification

**How to identify which pattern an app uses:**

```bash
# Check if app exists in UCC folder
ls ucc/ | grep {app-name}
  → If found: UCC Pattern
  → If not found: Check legacy

# Check if app exists in legacy folders
ls ccb/process-interface/ | grep {app-name}
ls ccb/middletier/process/ | grep {app-name}
  → If found in BOTH: Legacy Pattern
```

### File Path Quick Reference

| Component | Legacy Pattern | UCC Pattern |
|-----------|---------------|-------------|
| Process Interface | `ccb/process-interface/{app}/` | `ucc/{app}/process-interface/` |
| Process Implementation | `ccb/middletier/process/{app}/` | `ucc/{app}/process/` |
| Process BOM | N/A | `ucc/{app}/bom/` |
| Aggregator POM | N/A | `ucc/{app}/pom.xml` |
| UI Pages | `ccb/ui/{channel}-webui/{app}/ui/` | `ccb/ui/{channel}-webui/{app}/ui/` (same) |
| REST Controllers | `ccb/ui/{channel}-webui/{app}/rest/` | `ccb/ui/{channel}-webui/{app}/rest/` (same) |
| React Components | `ui-react/src/.../parent_comp/{app}/` | `ui-react/src/.../parent_comp/{app}/` (same) |

### Dependency Patterns

**Legacy Pattern:**
```xml
<!-- In ccb/ui/pk-webui/kwk/rest/pom.xml -->
<dependency>
    <groupId>coba.ccb.process-interface</groupId>
    <artifactId>process-interface-kwk</artifactId>  ← Separate module
</dependency>
```

**UCC Pattern:**
```xml
<!-- In ccb/ui/pk-webui/kyc/rest/pom.xml -->
<dependency>
    <groupId>coba.ccb.ucc.knowyourcustomer</groupId>
    <artifactId>ucc-knowyourcustomer-process-interface</artifactId>  ← Part of UCC module
</dependency>
```

---

## Summary

### Key Differences

1. **Structure:**
   - **Legacy:** Interfaces and implementations in separate top-level folders
   - **UCC:** All parts of an app in one self-contained module

2. **Organization:**
   - **Legacy:** Mixed with CCB core infrastructure in `ccb/`
   - **UCC:** Isolated in dedicated `ucc/` folder

3. **Discoverability:**
   - **Legacy:** Hard to identify apps (need to cross-reference multiple folders)
   - **UCC:** Easy - one folder = one app

4. **Build:**
   - **Legacy:** Build interface + implementation separately
   - **UCC:** Build entire app with single aggregator POM

5. **Dependencies:**
   - **Legacy:** No BOM - dependencies scattered
   - **UCC:** Centralized BOM module

### Both Patterns Share

- ✓ UI layer location (`ccb/ui/`)
- ✓ React components location (`ui-react/`)
- ✓ SC service dependencies
- ✓ Framework dependencies (fw/)
- ✓ Same runtime environment
- ✓ Same Spring configuration approach
- ✓ Same process annotations (@CCBProcess, etc.)

### Migration Recommendation

For migrating **any app** (legacy or UCC) to microservice:
1. **Identify pattern** (check folders)
2. **Map dependencies** (SC services used)
3. **Extract process layer** (interface + implementation)
4. **Extract UI layer** (pages + REST + React)
5. **Recreate SC service contracts** (REST APIs)
6. **Set up new infrastructure** (database, deployment, etc.)

**Complexity is similar** - the hard part is extracting SC service dependencies, not the pattern itself.

---

**Created:** 2025-11-06  
**Author:** GitHub Copilot  
**Purpose:** Compare Legacy vs UCC architectural patterns in CCB monolith

