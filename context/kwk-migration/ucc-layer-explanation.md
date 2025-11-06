# UCC (Use Case Clusters) Layer - Complete Explanation

## Table of Contents
1. [What is UCC?](#what-is-ucc)
2. [UCC Role in CCB Architecture](#ucc-role-in-ccb-architecture)
3. [UCC Structure & Organization](#ucc-structure--organization)
4. [Backend vs Frontend in UCC](#backend-vs-frontend-in-ucc)
5. [How UCC Works with Other Layers](#how-ucc-works-with-other-layers)
6. [UCC in KWK Use Case Context](#ucc-in-kwk-use-case-context)
7. [Concrete Examples](#concrete-examples)
8. [UCC Best Practices & Patterns](#ucc-best-practices--patterns)

---

## What is UCC?

**UCC (Use Case Clusters)** is the **application layer** in the CCB (Cross-Channel Banking) architecture. It represents complete, end-to-end business applications that orchestrate multiple services to deliver specific banking functionality to end users.

### Key Characteristics

- **Location:** `C:\CCB\sources\portal\ucc\`
- **Module Count:** 70+ use case modules
- **Purpose:** Business workflow orchestration and application logic
- **Pattern:** Each UCC module = One complete business application
- **Naming Convention:** `ucc/{usecase-name}/`

### What Makes a Use Case Cluster?

A UCC module is:
- ✅ **Business-oriented:** Represents a user-facing business capability
- ✅ **Orchestrator:** Composes multiple SC (Service Cluster) services
- ✅ **Self-contained:** Has its own process logic, interfaces, and BOMs
- ✅ **Deployable:** Can be independently built and deployed
- ❌ **NOT a technical framework:** Uses the framework, doesn't provide it
- ❌ **NOT reusable services:** Consumes services, doesn't provide them

---

## UCC Role in CCB Architecture

### The Complete Architecture Stack

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 7: Frontend (Browser)                                     │
│  - React components (ui-react)                                  │
│  - JavaScript bundles                                           │
│  - HTML pages                                                   │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 6: CCB UI Layer (ccb/ui/*)                                │
│  - Java UI pages (Wicket/Spring)                                │
│  - REST controllers                                             │
│  - Serves HTML + React bundles                                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Spring @Inject
┌──────────────────────▼──────────────────────────────────────────┐
│ ★ LAYER 5: UCC - Use Case Clusters (THIS LAYER) ★              │
│                                                                 │
│  Purpose: Business Application Orchestration                   │
│                                                                 │
│  Examples:                                                      │
│  - ucc/knowyourcustomer/         (KYC processes)                │
│  - ucc/accountoverview/           (Account overview)            │
│  - ucc/mobilepayment/             (Mobile payments)             │
│  - ucc/privatecustomeronboarding/ (Customer onboarding)         │
│  - ucc/creditoffercreation/       (Credit offers)               │
│                                                                 │
│  What it does:                                                  │
│  1. Implements business workflows (multi-step processes)        │
│  2. Orchestrates multiple SC services                           │
│  3. Enforces business rules and validation                      │
│  4. Manages process state and transactions                      │
│  5. Provides process interfaces (APIs) for UI layer             │
│                                                                 │
│  Code Type: BACKEND ONLY (Java)                                 │
│  - No UI code (HTML, JavaScript, React)                         │
│  - No direct user interaction                                   │
│  - Pure business logic orchestration                            │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Spring @Inject
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 4: SC - Service Clusters (Domain Services)               │
│  - 60+ business domain services                                 │
│  - Examples: customer, account, transaction, payment, etc.      │
│  - Provides: ParticipantService, CustomerService, etc.          │
└──────────────────────┬──────────────────────────────────────────┘
                       │ depends on
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 3: SB - Shared Business (Cross-cutting business)         │
│  - Shared domain components                                     │
│  - Fragment orchestration                                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │ depends on
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 2: CCB - Core Platform (Banking infrastructure)          │
│  - Middle tier implementation                                   │
│  - Core services                                                │
│  - Process engine                                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │ depends on
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 1: FW - Framework (Technical foundation)                 │
│  - Base classes, annotations, utilities                         │
│  - Logging, context management, async processing               │
└─────────────────────────────────────────────────────────────────┘
```

### UCC's Position: The Application Orchestration Layer

**UCC sits between UI and Services:**
- **Above:** Consumed by CCB UI modules (ccb/ui/*)
- **Below:** Consumes SC (Service Cluster) services

**UCC is the "Glue" Layer:**
- Takes user requests from UI layer
- Orchestrates multiple services to fulfill request
- Returns consolidated response to UI layer

---

## UCC Structure & Organization

### Typical UCC Module Structure

Every UCC module follows a standard structure:

```
ucc/{usecase-name}/
├── pom.xml                           ← Parent POM (aggregator)
│
├── process-interface/                ← Process API Definition
│   ├── pom.xml
│   └── src/main/java/
│       └── com/commerzbank/ccb/ucc/{usecase}/processinterface/
│           ├── {ProcessName}Process.java           (interface)
│           ├── request/
│           │   └── {ProcessName}Request.java      (DTOs)
│           ├── response/
│           │   └── {ProcessName}Response.java     (DTOs)
│           ├── domain/
│           │   └── {DomainObject}.java            (domain models)
│           └── soap/                               (SOAP contracts - optional)
│               ├── {ProcessName}Delegate.java
│               ├── request/
│               └── response/
│
├── process/                          ← Process Implementation
│   ├── pom.xml
│   └── src/
│       ├── main/
│       │   ├── java/
│       │   │   └── com/commerzbank/ccb/ucc/{usecase}/process/
│       │   │       ├── {ProcessName}ProcessImpl.java   (implementation)
│       │   │       ├── mapper/
│       │   │       │   └── {ProcessName}Mapper.java    (data transformations)
│       │   │       └── soap/                           (SOAP delegates)
│       │   │           └── {ProcessName}DelegateImpl.java
│       │   │
│       │   └── resources/
│       │       ├── spring/
│       │       │   └── config-{usecase}-process.xml    (Spring config)
│       │       └── WEB-INF/
│       │           ├── sun-jaxws.xml                   (SOAP config)
│       │           └── wsdl/
│       │               └── {ProcessName}Service.wsdl
│       │
│       └── test/java/                                  (unit tests)
│
├── ui/                               ← UI Module (OPTIONAL - RARE)
│   ├── pom.xml
│   └── src/main/
│       └── (usually empty or test files only)
│
└── bom/                              ← Bill of Materials
    ├── pom.xml
    └── (dependency management for runtime)
```

### Real Example: ucc/knowyourcustomer/

```
ucc/knowyourcustomer/
├── pom.xml                           ← Aggregates all sub-modules
│   <groupId>coba.ccb.ucc.knowyourcustomer</groupId>
│   <artifactId>ucc-knowyourcustomer-aggregator</artifactId>
│   <modules>
│       <module>process-interface</module>
│       <module>ui</module>
│       <module>process</module>
│       <module>bom</module>
│   </modules>
│
├── process-interface/
│   └── src/main/java/.../processinterface/
│       ├── CddCheckWithBpkennProcess.java           ← Interface
│       ├── request/
│       │   └── CddCheckWithBpkennRequest.java
│       ├── response/
│       │   ├── CddCheckWithBpkennResponse.java
│       │   └── CddCheckProcessResponseCode.java
│       ├── domain/
│       │   └── CustomerRiskRatingData.java
│       └── soap/
│           ├── CddCheckWithBpkennDelegate.java
│           ├── CddCheckWithBpkennSoapFault.java
│           └── request/response/...
│
├── process/
│   ├── pom.xml
│   │   <dependencies>
│   │       <!-- Own interface -->
│   │       <dependency>
│   │           <groupId>coba.ccb.ucc.knowyourcustomer</groupId>
│   │           <artifactId>ucc-knowyourcustomer-process-interface</artifactId>
│   │       </dependency>
│   │       <!-- SC Services it uses -->
│   │       <dependency>
│   │           <groupId>coba.ccb.sc.knowyourcustomer</groupId>
│   │           <artifactId>sc-knowyourcustomer-api</artifactId>
│   │       </dependency>
│   │   </dependencies>
│   │
│   └── src/main/java/.../process/
│       ├── CddCheckWithBpkennProcessImpl.java       ← Implementation
│       │   @CCBProcess
│       │   @CCBTransactionalProcess
│       │   @ProcessDefinition
│       │   implements CddCheckWithBpkennProcess
│       │
│       │   @Inject
│       │   private CustomerDueDiligenceService customerDueDiligenceService;
│       │
│       │   @PreAuthorize("protect('DIGIOPS_CHECK_CUSTOMER_RISK_RATING')")
│       │   public CddCheckWithBpkennResponse cddCheckWithBpkenn(
│       │       CddCheckWithBpkennRequest request) {
│       │       // 1. Map UCC request → SC service request
│       │       // 2. Call SC service
│       │       // 3. Map SC response → UCC response
│       │       // 4. Handle errors
│       │   }
│       │
│       ├── mapper/
│       │   ├── CddCheckWithBpkennMapper.java        ← Maps between layers
│       │   └── CddCheckWithBpkennSoapMapper.java
│       │
│       └── soap/
│           └── CddCheckWithBpkennDelegateImpl.java  ← SOAP endpoint
│               @WebService(endpointInterface = "...")
│
├── ui/                               ← Usually empty for UCC
│   └── src/test/                     (only test files, if any)
│
└── bom/
    └── pom.xml                       ← Lists all runtime dependencies
        <dependencies>
            <dependency>
                <groupId>coba.ccb.ucc.knowyourcustomer</groupId>
                <artifactId>ucc-knowyourcustomer-process</artifactId>
            </dependency>
        </dependencies>
```

---

## Backend vs Frontend in UCC

### ❌ UCC Has NO Frontend Code

**Important:** UCC modules are **BACKEND ONLY**. They contain:

✅ **What UCC Contains (Backend):**
- Java classes
- Process implementations
- Business logic
- Service orchestration
- Data mapping/transformation
- SOAP/REST service endpoints (for external systems)
- Spring configuration
- Unit tests

❌ **What UCC Does NOT Contain (Frontend):**
- ❌ React components
- ❌ JavaScript/TypeScript
- ❌ HTML templates
- ❌ CSS/LESS styles
- ❌ Webpack configurations
- ❌ Frontend bundles
- ❌ UI pages

### Why UCC Has a `ui/` Folder

**Confusing:** Some UCC modules have a `ucc/{usecase}/ui/` folder

**Explanation:**
- This folder is usually **EMPTY** or contains only **test files**
- It exists for **structural consistency** (Maven module pattern)
- It was planned for future use but rarely used
- **Real UI code** lives in `ccb/ui/*` instead

**Example:**
```
ucc/knowyourcustomer/ui/
├── pom.xml           ← Exists but minimal dependencies
└── src/
    └── test/         ← Only test files (if any)
        └── (empty or test resources)
```

### Where Frontend Actually Lives

Frontend code for use cases lives in **separate UI modules:**

```
ccb/ui/pk-webui/{usecase}/
├── ui/                    ← Java UI pages (Wicket)
│   └── src/main/java/
│       └── {UseCase}Page.java
│
├── rest/                  ← REST endpoints for frontend
│   └── src/main/java/
│       └── {UseCase}JsonController.java
│
└── public/                ← Shared UI utilities
```

**Separation of Concerns:**
- **UCC** = Business logic (process orchestration)
- **ccb/ui** = User interface (pages, REST APIs, UI logic)
- **ui-react** = Shared frontend components (React)

---

## How UCC Works with Other Layers

### Complete Request Flow Example

Let's trace a user action from browser to database:

```
USER ACTION: Submit "Know Your Customer" (KYC) check for a business partner
```

**Step-by-Step Flow:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. BROWSER (User Interface)                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  User fills form and clicks "Submit KYC Check"                  │
│                                                                 │
│  JavaScript (React component) calls:                            │
│  POST /banking/rest/cddCheck                                    │
│  Body: { businessPartnerNumber: "12345678" }                    │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ HTTP POST
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. CCB UI LAYER - REST Controller                              │
│    Location: ccb/ui/pk-webui/kyc/rest/                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  File: KycJsonController.java                                  │
│                                                                 │
│  @Controller                                                    │
│  @RequestMapping("/cddCheck")                                   │
│  public class KycJsonController {                               │
│                                                                 │
│      @Inject                                                    │
│      @Named("cddCheckWithBpkennProcess")                        │
│      private CddCheckWithBpkennProcess process;                 │
│                                                                 │
│      @RequestMapping(method = POST)                             │
│      @ResponseBody                                              │
│      public JsonResponse cddCheck(@RequestBody CddCheckDto dto) {│
│          // 1. Map DTO → Process Request                        │
│          CddCheckWithBpkennRequest request =                    │
│              mapper.toProcessRequest(dto);                      │
│                                                                 │
│          // 2. Call UCC Process ← CALLS UCC LAYER               │
│          CddCheckWithBpkennResponse response =                  │
│              process.cddCheckWithBpkenn(request);               │
│                                                                 │
│          // 3. Map Process Response → JSON Response             │
│          return mapper.toJsonResponse(response);                │
│      }                                                           │
│  }                                                               │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Spring DI injection
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ ★ 3. UCC LAYER - Process Implementation ★                      │
│    Location: ucc/knowyourcustomer/process/                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  File: CddCheckWithBpkennProcessImpl.java                       │
│                                                                 │
│  @CCBProcess                                                    │
│  @CCBTransactionalProcess                                       │
│  @ProcessDefinition                                             │
│  public class CddCheckWithBpkennProcessImpl                     │
│         extends BaseProcess                                     │
│         implements CddCheckWithBpkennProcess {                  │
│                                                                 │
│      @Inject                                                    │
│      @Named("customerDueDiligenceService")                      │
│      private CustomerDueDiligenceService cddService; ← SC Service│
│                                                                 │
│      @PreAuthorize("protect('DIGIOPS_CHECK_CUSTOMER_RISK_RATING')")│
│      @Override                                                  │
│      public CddCheckWithBpkennResponse cddCheckWithBpkenn(      │
│              CddCheckWithBpkennRequest request) {               │
│                                                                 │
│          LOG.info("Starting CDD check for BP: {}",              │
│              request.getBusinessPartnerNumber());               │
│                                                                 │
│          try {                                                  │
│              // 1. Validate request                             │
│              validateRequest(request);                          │
│                                                                 │
│              // 2. Map UCC request → SC service request         │
│              CheckCustomerRiskRatingServiceRequest svcReq =     │
│                  CddCheckMapper.mapToServiceRequest(request);   │
│                                                                 │
│              // 3. Call SC Service ← CALLS SC LAYER             │
│              CheckCustomerRiskRatingServiceResponse svcResp =   │
│                  cddService.checkCustomerRiskRating(svcReq)     │
│                             .get(); // Async call               │
│                                                                 │
│              // 4. Map SC service response → UCC response       │
│              CddCheckWithBpkennResponse response =              │
│                  CddCheckMapper.mapToProcessResponse(svcResp);  │
│                                                                 │
│              // 5. Additional business logic                    │
│              if (response.getRiskRating() == HIGH_RISK) {       │
│                  LOG.warn("High risk customer detected!");      │
│                  // Trigger additional workflows...             │
│              }                                                  │
│                                                                 │
│              LOG.info("CDD check completed successfully");      │
│              return response;                                   │
│                                                                 │
│          } catch (Exception e) {                                │
│              LOG.error("CDD check failed", e);                  │
│              return new CddCheckWithBpkennResponse(             │
│                  CddCheckProcessResponseCode.UNDEFINED_ERROR);  │
│          }                                                      │
│      }                                                           │
│  }                                                               │
│                                                                 │
│  ★ THIS IS WHERE UCC ADDS VALUE: ★                             │
│  - Orchestrates multiple SC services (could call 5+ services)   │
│  - Enforces business rules and authorization                    │
│  - Manages transactions (@CCBTransactionalProcess)              │
│  - Handles errors and logging                                   │
│  - Maps data between layers                                     │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ Spring DI injection
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. SC LAYER - Service Implementation                           │
│    Location: sc/knowyourcustomer/service/                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  File: CustomerDueDiligenceServiceImpl.java                     │
│                                                                 │
│  @CCBService                                                    │
│  public class CustomerDueDiligenceServiceImpl                   │
│         extends BaseService                                     │
│         implements CustomerDueDiligenceService {                │
│                                                                 │
│      @Inject                                                    │
│      private CustomerRepository repository;                     │
│                                                                 │
│      @Inject                                                    │
│      private HostSystemAdapter hostAdapter;                     │
│                                                                 │
│      @Override                                                  │
│      @CcbHystrix(fallbackMethod = "fallback")                   │
│      public CcbFuture<CheckCustomerRiskRatingServiceResponse>   │
│         checkCustomerRiskRating(                                │
│              CheckCustomerRiskRatingServiceRequest request) {   │
│                                                                 │
│          // 1. Retrieve customer data from database             │
│          Customer customer = repository.findByBpNumber(         │
│              request.getBusinessPartnerNumber());               │
│                                                                 │
│          // 2. Call legacy host system for risk rating          │
│          HostRiskRatingResponse hostResp =                      │
│              hostAdapter.getRiskRating(customer.getId());       │
│                                                                 │
│          // 3. Persist CDD check to database                    │
│          CddCheckRecord record = new CddCheckRecord(            │
│              customer.getId(),                                  │
│              hostResp.getRiskRating(),                          │
│              LocalDateTime.now());                              │
│          repository.saveCddCheck(record);                       │
│                                                                 │
│          // 4. Build response                                   │
│          CheckCustomerRiskRatingServiceResponse response =      │
│              new CheckCustomerRiskRatingServiceResponse(        │
│                  hostResp.getRiskRating(),                      │
│                  hostResp.getRiskReasonCodes());                │
│                                                                 │
│          return CcbAsyncResult.forValue(response);              │
│      }                                                           │
│  }                                                               │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ JPA/Hibernate
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. DATABASE / HOST SYSTEM                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  - Database: Save CDD check record                              │
│  - Host System: Query legacy mainframe for risk rating          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### UCC Orchestration: Multi-Service Example

UCC processes typically orchestrate **multiple SC services**:

```java
@CCBProcess
@CCBTransactionalProcess
public class CorporateCreditOfferProcessImpl 
        extends BaseMultistepProcess 
        implements CorporateCreditOfferProcess {
    
    // UCC Process injects MULTIPLE SC services
    
    @Inject
    @Named("participantService")
    private ParticipantService participantService;
    
    @Inject
    @Named("customerService")
    private CustomerService customerService;
    
    @Inject
    @Named("creditDecisionService")
    private CreditDecisionService creditDecisionService;
    
    @Inject
    @Named("productCatalogService")
    private ProductCatalogService productCatalogService;
    
    @Inject
    @Named("documentService")
    private DocumentService documentService;
    
    @Inject
    @Named("communicationService")
    private CommunicationService communicationService;
    
    @Override
    public CreditOfferResponse createCreditOffer(CreditOfferRequest request) {
        
        // Step 1: Get customer information
        Customer customer = customerService
            .getCustomerById(request.getCustomerId())
            .get();
        
        // Step 2: Get participant details
        Participant participant = participantService
            .getParticipantByCustomer(customer.getId())
            .get();
        
        // Step 3: Get product details
        ProductDetails product = productCatalogService
            .getProductByCode(request.getProductCode())
            .get();
        
        // Step 4: Perform credit decision
        CreditDecisionResponse creditDecision = creditDecisionService
            .evaluateCredit(customer, request.getRequestedAmount())
            .get();
        
        if (!creditDecision.isApproved()) {
            // Step 5a: Send rejection notification
            communicationService.sendEmail(
                customer.getEmail(),
                "CREDIT_REJECTED",
                Map.of("reason", creditDecision.getRejectionReason())
            );
            
            return CreditOfferResponse.rejected(
                creditDecision.getRejectionReason()
            );
        }
        
        // Step 5b: Generate offer document
        Document offerDoc = documentService
            .generateDocument(
                "CREDIT_OFFER_TEMPLATE",
                Map.of(
                    "customer", customer,
                    "product", product,
                    "amount", creditDecision.getApprovedAmount(),
                    "interestRate", creditDecision.getInterestRate()
                )
            )
            .get();
        
        // Step 6: Send offer to customer
        communicationService.sendEmail(
            customer.getEmail(),
            "CREDIT_OFFER",
            Map.of("documentId", offerDoc.getId())
        );
        
        // Step 7: Return response
        return CreditOfferResponse.approved(
            creditDecision.getApprovedAmount(),
            creditDecision.getInterestRate(),
            offerDoc.getId()
        );
    }
}
```

**What UCC Adds:**
1. **Orchestration:** Coordinates 6 different SC services
2. **Business Logic:** Conditional flows based on credit decision
3. **Transaction Management:** All operations in one transaction
4. **Error Handling:** Centralized exception management
5. **Workflow:** Multi-step process (credit check → document → notification)

---

## UCC in KWK Use Case Context

### Why KWK Has NO UCC Module

**Important Discovery:** KWK (Kunden Werben Kunden - Customer Referral) does **NOT** have a UCC module.

**Actual Structure:**
```
❌ ucc/kwk/                           ← DOES NOT EXIST
❌ ucc/customerreferral/              ← DOES NOT EXIST

✅ ccb/process-interface/kwk/         ← Process interface
✅ ccb/middletier/process/kwk/        ← Process implementation
✅ ccb/ui/pk-webui/kwk/               ← UI module
```

**Reason:** KWK is a **legacy module** that predates the UCC architecture pattern.

### Legacy Pattern vs Modern UCC Pattern

**Legacy Pattern (KWK):**
```
ccb/
├── process-interface/kwk/            ← Process contract
├── middletier/process/kwk/           ← Process implementation
└── ui/pk-webui/kwk/                  ← UI + REST
```

**Modern UCC Pattern (Most new use cases):**
```
ucc/{usecase}/
├── process-interface/                ← Process contract
├── process/                          ← Process implementation
├── ui/                               ← (usually empty)
└── bom/                              ← Dependencies

ccb/ui/pk-webui/{usecase}/            ← Separate UI module
├── ui/                               ← Pages
├── rest/                             ← REST controllers
└── public/                           ← Shared code
```

### UCC Modules Related to KWK

While KWK itself has no UCC, these UCC modules handle similar customer-related workflows:

```
ucc/
├── privatecustomeronboarding/        ← Customer onboarding
│   ├── process-interface/
│   └── process/
│       └── CustomerOnboardingProcessImpl.java
│
├── participantcreation/              ← Create participant records
│   ├── process-interface/
│   └── process/
│       └── ParticipantCreationProcessImpl.java
│
├── customerauthentication/           ← Customer authentication
│   ├── process-interface/
│   └── process/
│       └── CustomerAuthenticationProcessImpl.java
│
├── partymanagement/                  ← Party/customer management
│   ├── process-interface/
│   └── process/
│       └── PartyManagementProcessImpl.java
│
└── profilemanagement/                ← Customer profile management
    ├── process-interface/
    └── process/
        └── ProfileManagementProcessImpl.java
```

These UCC modules **might consume KWK's SC services** if KWK had SC modules in `sc/`.

---

## Concrete Examples

### Example 1: ucc/knowyourcustomer

**Business Purpose:** Perform KYC (Know Your Customer) due diligence checks

**Module Structure:**
```
ucc/knowyourcustomer/
├── process-interface/
│   └── src/main/java/.../processinterface/
│       ├── CddCheckWithBpkennProcess.java
│       ├── request/CddCheckWithBpkennRequest.java
│       ├── response/CddCheckWithBpkennResponse.java
│       └── domain/CustomerRiskRatingData.java
│
└── process/
    ├── pom.xml
    │   <dependencies>
    │       <!-- Own interface -->
    │       <dependency>
    │           <groupId>coba.ccb.ucc.knowyourcustomer</groupId>
    │           <artifactId>ucc-knowyourcustomer-process-interface</artifactId>
    │       </dependency>
    │       <!-- SC Services -->
    │       <dependency>
    │           <groupId>coba.ccb.sc.knowyourcustomer</groupId>
    │           <artifactId>sc-knowyourcustomer-api</artifactId>
    │       </dependency>
    │   </dependencies>
    │
    └── src/main/java/.../process/
        ├── CddCheckWithBpkennProcessImpl.java
        ├── mapper/CddCheckWithBpkennMapper.java
        └── soap/CddCheckWithBpkennDelegateImpl.java
```

**Process Implementation:**
```java
@ProcessDefinition
@CCBProcess
@CCBTransactionalProcess
public class CddCheckWithBpkennProcessImpl 
        extends BaseProcess 
        implements CddCheckWithBpkennProcess {
    
    @Inject
    @Named("customerDueDiligenceService")
    private CustomerDueDiligenceService customerDueDiligenceService;
    
    @PreAuthorize("protect('DIGIOPS_CHECK_CUSTOMER_RISK_RATING')")
    @Override
    public CddCheckWithBpkennResponse cddCheckWithBpkenn(
            CddCheckWithBpkennRequest request) {
        
        LOG.info("Starting CDD check");
        
        try {
            // Map UCC request → SC service request
            CheckCustomerRiskRatingServiceRequest serviceRequest = 
                CddCheckWithBpkennMapper.mapProcessRequestToServiceRequest(request);
            
            // Call SC service
            CheckCustomerRiskRatingServiceResponse serviceResponse = 
                this.customerDueDiligenceService
                    .checkCustomerRiskRating(serviceRequest)
                    .get();
            
            // Map SC service response → UCC response
            CddCheckWithBpkennResponse response = 
                CddCheckWithBpkennMapper.mapServiceResponseToProcessResponse(serviceResponse);
            
            return response;
            
        } catch (Exception e) {
            LOG.error("CDD check failed", e);
            return new CddCheckWithBpkennResponse(
                CddCheckProcessResponseCode.UNDEFINED_ERROR
            );
        }
    }
}
```

**Who Calls This UCC Process:**
- External systems via SOAP web service
- CCB UI modules via Spring injection
- Other UCC processes (composition)

### Example 2: ucc/accountoverview

**Business Purpose:** Retrieve and display account information overview

**Module Structure:**
```
ucc/accountoverview/
├── process-interface/
│   └── src/main/java/.../processinterface/
│       ├── request/RetrieveAccountInfoListsRestRequest.java
│       ├── response/
│       │   ├── RetrieveAccountInfoRestResponse.java
│       │   └── RetrieveAccountInfoListsRestResponse.java
│       └── dto/
│           ├── CurrentAccountInfo.java
│           ├── SavingsAccountInfo.java
│           └── Currency.java
│
└── process/
    ├── pom.xml
    │   <dependencies>
    │       <!-- Process contract -->
    │       <dependency>
    │           <groupId>coba.ccb.ucc.accountoverview</groupId>
    │           <artifactId>ucc-accountoverview-process-interface</artifactId>
    │       </dependency>
    │       <!-- Framework -->
    │       <dependency>
    │           <groupId>coba.ccb.fw.mt</groupId>
    │           <artifactId>fw-mt-api</artifactId>
    │       </dependency>
    │       <!-- Likely dependencies (not in partial view) -->
    │       <!-- SC account services, balance services, etc. -->
    │   </dependencies>
    │
    └── src/main/java/.../process/
        └── (Process implementations would be here)
```

**What This UCC Does:**
1. Calls multiple SC services:
   - `sc/currentaccount` - Get current account details
   - `sc/savingsaccount` - Get savings account details
   - `sc/balance` - Get account balances
   - `sc/transaction` - Get recent transactions
2. Aggregates data from multiple services
3. Transforms data into DTOs for UI
4. Applies business rules (e.g., hide accounts based on status)
5. Returns consolidated account overview

### Example 3: ucc/creditoffercreation

**Business Purpose:** Create and manage corporate credit offers

**Module Structure:**
```
ucc/creditoffercreation/
├── process-interface/
│   └── src/main/java/.../processinterface/
│       └── (Offer creation process interfaces)
│
└── process/
    └── src/
        ├── main/java/.../process/
        │   ├── CorporateCreditOrderProcessImpl.java
        │   ├── CorporateCreditOfferDecisionProcessImpl.java
        │   ├── CorporateCreditOfferConditionsProcessImpl.java
        │   └── soap/
        │       ├── GenerateCorporateCreditContractSOAPDelegateImpl.java
        │       └── CorporateCreditOfferDecisionSOAPDelegateImpl.java
        │
        └── test/java/.../process/
            ├── CorporateCreditOrderProcessImplTest.java
            ├── CorporateCreditOfferDecisionProcessImplTest.java
            └── CorporateCreditOfferConditionsProcessImplTest.java
```

**What This UCC Does:**
1. **CorporateCreditOrderProcessImpl:**
   - Receives credit order request
   - Validates business partner data
   - Creates order record
   
2. **CorporateCreditOfferDecisionProcessImpl:**
   - Evaluates credit worthiness
   - Calls SC credit decision service
   - Generates offer decision
   
3. **CorporateCreditOfferConditionsProcessImpl:**
   - Calculates offer conditions (rates, terms)
   - Calls SC product catalog service
   - Builds offer details

**Multi-Step Workflow:**
```
User submits credit request
    ↓
CorporateCreditOrderProcessImpl.createOrder()
    ↓ (calls)
SC: CustomerService.getCustomer()
SC: ParticipantService.getParticipant()
SC: ProductCatalogService.getProduct()
    ↓ (then calls)
CorporateCreditOfferDecisionProcessImpl.evaluateCredit()
    ↓ (calls)
SC: CreditDecisionService.evaluateCredit()
    ↓ (if approved, calls)
CorporateCreditOfferConditionsProcessImpl.calculateConditions()
    ↓ (calls)
SC: ProductService.getProductConditions()
SC: DocumentService.generateOffer()
    ↓ (returns)
CreditOfferResponse (back to UI)
```

---

## UCC Best Practices & Patterns

### 1. Single Responsibility

**Each UCC Module = One Business Use Case**

✅ **Good:**
```
ucc/mobilepayment/          ← Handles mobile payment workflows
ucc/accountoverview/        ← Handles account overview
ucc/creditoffercreation/    ← Handles credit offer creation
```

❌ **Bad:**
```
ucc/banking/                ← Too broad, not specific
ucc/utils/                  ← Not a use case, utilities belong in shared
```

### 2. Process Interface Pattern

**Always separate interface from implementation:**

```
ucc/{usecase}/
├── process-interface/      ← API contract (what)
│   └── {Process}Process.java (interface)
│
└── process/                ← Implementation (how)
    └── {Process}ProcessImpl.java (concrete class)
```

**Benefits:**
- UI layer depends only on interface (loose coupling)
- Implementation can be swapped
- Easier testing (mock interface)
- Clear API definition

### 3. Process Annotations

**Use framework annotations correctly:**

```java
@ProcessDefinition              // ← Marks as CCB process
@CCBProcess                     // ← Enables process features
@CCBTransactionalProcess        // ← Manages transactions
public class MyProcessImpl extends BaseProcess {
    
    @PreAuthorize("protect('MY_AUTHORITY')")  // ← Security
    @Override
    public MyResponse myProcess(MyRequest request) {
        // Implementation
    }
}
```

### 4. Service Orchestration Pattern

**UCC orchestrates, doesn't implement:**

✅ **Good UCC Process:**
```java
@CCBProcess
public class CreditOfferProcessImpl {
    
    @Inject private CustomerService customerService;
    @Inject private CreditDecisionService creditService;
    @Inject private DocumentService documentService;
    
    public CreditOfferResponse createOffer(CreditOfferRequest req) {
        // Orchestrate multiple services
        Customer customer = customerService.getCustomer(req.getId()).get();
        Decision decision = creditService.evaluate(customer).get();
        Document doc = documentService.generate(decision).get();
        
        return new CreditOfferResponse(decision, doc);
    }
}
```

❌ **Bad UCC Process (too much logic):**
```java
@CCBProcess
public class CreditOfferProcessImpl {
    
    @Inject private JdbcTemplate jdbc;
    
    public CreditOfferResponse createOffer(CreditOfferRequest req) {
        // DON'T: Direct database access
        Customer customer = jdbc.queryForObject(
            "SELECT * FROM customers WHERE id = ?",
            new Object[]{req.getId()},
            new CustomerRowMapper()
        );
        
        // DON'T: Complex business logic in UCC
        BigDecimal score = calculateCreditScore(customer);
        if (score.compareTo(new BigDecimal("700")) > 0) {
            // Complex scoring logic...
        }
        
        // This should be in SC services!
    }
}
```

### 5. Data Mapping Pattern

**Map data between layers:**

```java
@CCBProcess
public class MyProcessImpl {
    
    public MyProcessResponse execute(MyProcessRequest uccRequest) {
        
        // 1. Map UCC request → SC service request
        MyServiceRequest serviceRequest = 
            MyMapper.toServiceRequest(uccRequest);
        
        // 2. Call SC service
        MyServiceResponse serviceResponse = 
            myService.execute(serviceRequest).get();
        
        // 3. Map SC service response → UCC response
        MyProcessResponse uccResponse = 
            MyMapper.toProcessResponse(serviceResponse);
        
        return uccResponse;
    }
}
```

**Mapper Class:**
```java
public class MyMapper {
    
    public static MyServiceRequest toServiceRequest(MyProcessRequest uccReq) {
        MyServiceRequest serviceReq = new MyServiceRequest();
        serviceReq.setCustomerId(uccReq.getBusinessPartnerId());
        serviceReq.setProductCode(uccReq.getProductIdentifier());
        // Map fields...
        return serviceReq;
    }
    
    public static MyProcessResponse toProcessResponse(MyServiceResponse svcResp) {
        MyProcessResponse uccResp = new MyProcessResponse();
        uccResp.setResultCode(svcResp.getStatusCode());
        uccResp.setResultMessage(svcResp.getMessage());
        // Map fields...
        return uccResp;
    }
}
```

### 6. Error Handling Pattern

**Centralized error handling in UCC:**

```java
@CCBProcess
public class MyProcessImpl {
    
    private static final CcbLogger LOG = CcbLogger.getLogger(MyProcessImpl.class);
    
    public MyResponse execute(MyRequest request) {
        
        LOG.info("Starting process for request: {}", request);
        
        try {
            // Validate input
            validateRequest(request);
            
            // Call services
            MyServiceResponse response = myService.execute(request).get();
            
            // Map response
            return mapToProcessResponse(response);
            
        } catch (ValidationException e) {
            LOG.error("Validation failed: {}", e.getMessage());
            return MyResponse.validationError(e.getMessage());
            
        } catch (ServiceException e) {
            LOG.error("Service call failed", e);
            return MyResponse.serviceError(e.getErrorCode());
            
        } catch (Exception e) {
            LOG.error("Unexpected error in process", e);
            return MyResponse.systemError();
        }
    }
}
```

### 7. Async Service Calls Pattern

**Use CcbFuture for async operations:**

```java
@CCBProcess
public class MyProcessImpl {
    
    @Inject private ServiceA serviceA;
    @Inject private ServiceB serviceB;
    @Inject private ServiceC serviceC;
    
    public MyResponse execute(MyRequest request) {
        
        // Call services in parallel (all return CcbFuture)
        CcbFuture<ResponseA> futureA = serviceA.callA(request);
        CcbFuture<ResponseB> futureB = serviceB.callB(request);
        CcbFuture<ResponseC> futureC = serviceC.callC(request);
        
        // Wait for all to complete (blocks here)
        ResponseA respA = futureA.get();
        ResponseB respB = futureB.get();
        ResponseC respC = futureC.get();
        
        // Combine results
        return combineResponses(respA, respB, respC);
    }
}
```

---

## Summary: UCC Layer Key Points

### What is UCC?

✅ **UCC IS:**
- Application/Use Case orchestration layer
- Backend business logic only (Java)
- Orchestrates multiple SC services
- Implements workflows and business processes
- Provides process interfaces (APIs) for UI layer
- Manages transactions and security
- 70+ modules, each representing one business use case

❌ **UCC IS NOT:**
- Frontend/UI layer (no React, HTML, JavaScript)
- Reusable services layer (that's SC)
- Technical framework (that's FW)
- UI page container (that's ccb/ui)

### UCC's Role in Architecture

**Position:** Layer 5 (between UI and Services)

**Responsibilities:**
1. **Orchestration:** Coordinate multiple SC services
2. **Workflow:** Implement multi-step business processes
3. **Business Rules:** Enforce business logic and validation
4. **Transaction Management:** Handle ACID transactions
5. **Security:** Authorization and authentication
6. **Data Transformation:** Map between UI and service layers
7. **Error Handling:** Centralized exception management

### UCC Module Structure

```
ucc/{usecase}/
├── process-interface/     ← API contract (interfaces, DTOs)
├── process/               ← Implementation (business logic)
├── ui/                    ← Usually empty
└── bom/                   ← Runtime dependencies
```

### How UCC Works with Other Layers

```
Browser (User)
    ↓ HTTP/REST
ccb/ui/* (UI Pages + REST Controllers)
    ↓ Spring @Inject
★ ucc/* (Process Orchestration) ★ ← THIS LAYER
    ↓ Spring @Inject
sc/* (Domain Services)
    ↓ depends on
sb/* (Shared Business)
    ↓ depends on
ccb/* (Core Platform)
    ↓ depends on
fw/* (Framework)
```

### KWK Special Case

**KWK does NOT use UCC pattern** - it follows legacy structure:
- Process: `ccb/middletier/process/kwk/`
- Interface: `ccb/process-interface/kwk/`
- UI: `ccb/ui/pk-webui/kwk/`

This is because KWK predates the UCC architecture.

### Key Takeaways

1. **UCC = Application Layer** - Complete business use cases
2. **Backend Only** - No frontend code in UCC
3. **Orchestrator** - Composes SC services, doesn't implement them
4. **Process-Oriented** - Workflows, not CRUD operations
5. **Transaction Boundary** - Manages consistency across services
6. **Security Enforcement** - @PreAuthorize annotations
7. **Layer Isolation** - UI depends on UCC interface, not implementation

---

## Related Documentation

- [Architecture Overview](./architecture-overview.md) - Complete CCB architecture
- [KWK Frontend Bundle Build Flow](./kwk-frontend-bundle-build-flow.md) - KWK build process
- [UI React Layer Explanation](./ui-react-layer-explanation.md) - Frontend layer details

---

**Created:** 2025-11-06  
**Author:** GitHub Copilot  
**Purpose:** Explain UCC layer structure and role in KWK use case context

