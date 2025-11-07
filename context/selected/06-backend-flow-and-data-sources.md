# Backend Flow and Data Sources - Legacy vs UCC Pattern

## Overview
This document explains what happens after the controller endpoints are called in both the Legacy and UCC patterns, showing the complete backend flow including where data comes from (databases, external APIs, mainframe, etc.).

---

## 1. Legacy Pattern Backend Flow (KWK Example)

### Flow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│ BROWSER                                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Request
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ UI LAYER (Controller)                                       │
│ ccb/ui/pk-webui/kwk/rest/                                   │
│ ├── CrcJsonController.java                                 │
│ │   @RequestMapping("/sendReference")                      │
│ │   - Validates request                                    │
│ │   - Calls Process layer                                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ @Inject CustomerReferCustomerProcess
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ PROCESS LAYER (Business Logic)                             │
│ ccb/middletier/process/kwk/                                 │
│ ├── CustomerReferCustomerProcessImpl.java                  │
│ │   @CCBProcess                                            │
│ │   @CCBTransactionalProcess                               │
│ │   - Business logic orchestration                         │
│ │   - Authorization checks                                 │
│ │   - Generates referral code                              │
│ │   - Calls multiple services                              │
│ │                                                           │
│ │   ┌─────────────────────────────────────┐               │
│ │   │ Injected Services:                   │               │
│ │   ├─────────────────────────────────────┤               │
│ │   │ • kwkService                         │               │
│ │   │ • participantService (SC Layer)      │               │
│ │   │ • personService (SC Layer)           │               │
│ │   │ • productService (SC Layer)          │               │
│ │   │ • ibanConverterService (SC Layer)    │               │
│ │   │ • authorizationService (SC Layer)    │               │
│ │   │ • customersAPIV3Service (SC Layer)   │               │
│ │   │ • naturalPersonAPIV3Service (SC)     │               │
│ │   │ • juristicalLoggingService (SC)      │               │
│ │   └─────────────────────────────────────┘               │
└─────────────────────┬───────────────────────────────────────┘
                      │ @Inject CustomerReferCustomerService
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ SERVICE LAYER (Data Access)                                 │
│ ccb/middletier/service/kwk/                                 │
│ ├── CustomerReferCustomerServiceImpl.java                  │
│ │   @CCBService                                            │
│ │   - Maps domain objects to entities                      │
│ │   - Calls DAO layer                                      │
│ │   - Handles transactions                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ @Inject KwkDAO
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ DAO LAYER (Database Access)                                │
│ ccb/middletier/service/kwk/dao/                             │
│ ├── KwkDAOImpl.java                                        │
│ │   @CCBComponent                                          │
│ │   extends AbstractJpaDAO                                 │
│ │   - JPA/Hibernate operations                             │
│ │   - EntityManager operations                             │
│ │   - Direct database queries                              │
│ │                                                           │
│ ├── CustomerReferCustomer.java (Entity)                    │
│ │   @Entity                                                │
│ │   @Table(name = "CUSTOMER_REFER_CUSTOMER")              │
│ │   - JPA entity mapping                                   │
│ │   - Database column mappings                             │
└─────────────────────┬───────────────────────────────────────┘
                      │ JDBC/JPA
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ DATABASE (Oracle/DB2)                                       │
│ ├── Table: CUSTOMER_REFER_CUSTOMER                         │
│ │   - CRC_ID (Primary Key)                                │
│ │   - CRC_CODE (Referral Code)                            │
│ │   - CRC_ACCOUNTOWNER_NAME                               │
│ │   - CRC_IBAN                                            │
│ │   - CRC_FIRST_NAME                                      │
│ │   - CRC_LAST_NAME                                       │
│ │   - CRC_EMAIL_ADDRESS                                   │
│ │   - CRC_NPKENN                                          │
│ │   - CRC_BOUNTY                                          │
│ │   - CRC_CREATION_TS                                     │
│ │   etc.                                                   │
└─────────────────────────────────────────────────────────────┘
```

### Additional Data Sources Called by Process Layer

The Process Layer also calls SC (Service Cluster) layer services which access:

```
┌─────────────────────────────────────────────────────────────┐
│ SERVICE CLUSTER (SC) APIs                                   │
│ sc/person/api/, sc/participant/api/, etc.                   │
│                                                              │
│ These services can access:                                   │
│ ├── Internal Database (via JPA/DAO)                         │
│ ├── Mainframe Systems (via MNC - Mainframe Connector)       │
│ ├── External REST APIs (via RestTemplate)                   │
│ ├── Message Queues (JMS)                                    │
│ └── Other microservices                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. UCC Pattern Backend Flow (Transaction Overview Example)

### Flow Diagram
```
┌─────────────────────────────────────────────────────────────┐
│ BROWSER                                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP Request
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ CONTROLLER LAYER                                            │
│ ucc/transactionoverview/process/rest/                       │
│ ├── TransactionOverviewRestController.java                 │
│ │   @Controller                                            │
│ │   @RequestMapping("/api/accounts-api/v1/accounts/{ID}/  │
│ │                    transactions")                        │
│ │   - Validates request parameters                         │
│ │   - Maps REST request to Process request                 │
│ │   - Handles pseudonymization                             │
│ │   - Calls Process directly (no UI layer)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │ @Inject Psd2TransactionOverviewProcess
                      ↓
┌─────────────────────────────────────────────────────────────┐
│ PROCESS LAYER                                               │
│ ucc/transactionoverview/process/                            │
│ ├── Psd2TransactionOverviewProcessImpl.java                │
│ │   @CCBProcess                                            │
│ │   @CCBTransactionalProcess                               │
│ │   @ProcessDefinition                                     │
│ │   - Business logic orchestration                         │
│ │   - Authorization via @PreAuthorize                      │
│ │   - Aggregates data from multiple sources                │
│ │                                                           │
│ │   ┌──────────────────────────────────────┐              │
│ │   │ Injected Services:                    │              │
│ │   ├──────────────────────────────────────┤              │
│ │   │ • productIdentifierService (SC)       │              │
│ │   │ • currentAccountTransactionsService   │              │
│ │   │ • savingsAccountTransactionsService   │              │
│ │   │ • realtimeTransactionService          │              │
│ │   │ • rtbsService (external API)          │              │
│ │   │ • featureSwitchService                │              │
│ │   └──────────────────────────────────────┘              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ├─────────────────────────────┐
                      │                             │
                      ↓                             ↓
┌───────────────────────────────┐   ┌──────────────────────────────┐
│ SC SERVICE LAYER              │   │ EXTERNAL API LAYER           │
│ sc/transaction/service/       │   │ sc/transaction/remote/       │
│                               │   │                              │
│ TransactionSearchServiceImpl  │   │ DatalakeTransactionsSearch-  │
│ @CCBService                   │   │ RestClient.java              │
│ - Business service logic      │   │ - External REST client       │
│ - Calls remote clients        │   │ - ApiBankingRestTemplate     │
└───────────┬───────────────────┘   │ - OAuth2 token handling      │
            │                       └────────┬─────────────────────┘
            │                                │
            │                                │ HTTP REST Call
            ↓                                ↓
┌───────────────────────────────┐   ┌──────────────────────────────┐
│ REST CLIENT LAYER             │   │ EXTERNAL SYSTEM              │
│                               │   │                              │
│ DatalakeTransactionsSearch-   │   │ API Management Gateway       │
│ RestClient                    │   │ └─→ Datalake Service         │
│ - Builds HTTP request         │   │     └─→ Data Lake            │
│ - Calls external API          │   │                              │
│ - Maps response               │   │ Endpoint:                    │
└───────────┬───────────────────┘   │ /payments-api/7/v1/          │
            │                       │ bulktransactions/search       │
            │                       └──────────────────────────────┘
            │ HTTP Response
            ↓
┌─────────────────────────────────────────────────────────────┐
│ Response flows back up through layers                       │
│ RestClient → Service → Process → Controller → Browser       │
└─────────────────────────────────────────────────────────────┘
```

### Note: No DAO Layer in This Example
Unlike the legacy pattern, this UCC example **does not have a DAO layer** because it fetches data from external APIs (Datalake) rather than directly from the database.

---

## 3. Complete Backend Layer Structure

### Legacy Pattern Layers
```
┌────────────────────────────────────────────────────────────┐
│ Layer 1: UI/REST Controller                                │
│ Location: ccb/ui/pk-webui/kwk/rest/                        │
│ Role: HTTP endpoint, request validation, JSON mapping      │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 2: Process (Business Logic)                          │
│ Location: ccb/middletier/process/kwk/                      │
│ Role: Orchestration, business rules, authorization         │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 3: Service (Data Access Coordination)                │
│ Location: ccb/middletier/service/kwk/                      │
│ Role: Transaction management, domain-to-entity mapping     │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 4: DAO (Database Access)                             │
│ Location: ccb/middletier/service/kwk/dao/                  │
│ Role: JPA/Hibernate, SQL queries, entity management        │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 5: Database (Oracle/DB2)                             │
│ Tables: CUSTOMER_REFER_CUSTOMER, etc.                      │
└────────────────────────────────────────────────────────────┘
```

### UCC Pattern Layers
```
┌────────────────────────────────────────────────────────────┐
│ Layer 1: REST Controller (in Process module)               │
│ Location: ucc/transactionoverview/process/rest/            │
│ Role: HTTP endpoint, request validation, mapping           │
└────────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────────┐
│ Layer 2: Process (Business Logic)                          │
│ Location: ucc/transactionoverview/process/                 │
│ Role: Orchestration, business rules, authorization         │
└────────────────────────────────────────────────────────────┘
                          ↓
                    ┌─────┴─────┐
                    ↓           ↓
┌──────────────────────────┐  ┌────────────────────────────┐
│ Layer 3a: SC Services    │  │ Layer 3b: Remote Clients   │
│ Location: sc/.../service/│  │ Location: sc/.../remote/   │
│ Role: Business services  │  │ Role: External API calls   │
└──────────┬───────────────┘  └────────┬───────────────────┘
           │                           │
           ↓                           ↓
┌──────────────────────┐    ┌─────────────────────────────┐
│ Database (Optional)  │    │ External Systems            │
│ - JPA/DAO (if used)  │    │ - Datalake                  │
│                      │    │ - Mainframe (MNC)           │
│                      │    │ - Other Microservices       │
└──────────────────────┘    │ - Message Queues            │
                            └─────────────────────────────┘
```

---

## 4. Data Sources in the Monolith

### 4.1 Internal Database (JPA/Hibernate)
- **Technology**: JPA (Java Persistence API) with Hibernate
- **Location**: DAO layer uses EntityManager
- **Example**: 
  ```java
  // ccb/middletier/service/kwk/dao/impl/KwkDAOImpl.java
  @CCBComponent
  public class KwkDAOImpl extends AbstractJpaDAO<CustomerReferCustomer, Long> {
      @Override
      public void saveCrcData(CustomerReferCustomer customerReferCustomer) {
          EntityManager entityManager = getEntityManager();
          super.insert(customerReferCustomer);
      }
      
      @Override
      public CrcData retrieveKwkData(String kwkCode) {
          List<CustomerReferCustomer> list = entityManager
              .createQuery("select c from CustomerReferCustomer c where c.crcCode=:code")
              .setParameter("code", kwkCode)
              .getResultList();
          // ...
      }
  }
  ```
- **Entities**: Classes annotated with `@Entity` and `@Table`
- **Tables**: Direct table access in Oracle/DB2 database

### 4.2 Mainframe Systems (MNC - Mainframe Connector)
- **Technology**: MNC (Mainframe Network Connector)
- **Purpose**: Access legacy mainframe systems (COBOL, CICS, etc.)
- **Pattern**: Service classes call MNC adapters which communicate via TCP/IP or MQ
- **Example services that might use MNC**:
  - Account balance queries
  - Customer master data
  - Transaction posting
  - Product information

### 4.3 External REST APIs
- **Technology**: Spring RestTemplate, ApiBankingRestTemplate
- **Location**: `sc/.../remote/` packages
- **Example**:
  ```java
  // sc/transaction/remote/DatalakeTransactionsSearchRestClient.java
  public class DatalakeTransactionsSearchRestClient {
      @Inject
      @Named("paymentsApiBankingRestTemplate")
      private ApiBankingRestTemplate apiBankingRestTemplate;
      
      @Value("${apiManagement.baseUrl}")
      private String apiBaseURL;
      
      public TransactionSearchRemoteResponse retrieveTransaction(
              BulkTransactionRequest request) {
          ResponseEntity<BulkTransactionResponse> responseEntity = 
              apiBankingRestTemplate.exchange(
                  apiBaseURL + "/payments-api/7/v1/bulktransactions/search",
                  HttpMethod.POST, request, httpHeaders,
                  BulkTransactionResponse.class, null, null);
          // ...
      }
  }
  ```
- **External systems called**:
  - Datalake (transaction search)
  - API Management Gateway
  - PSD2 APIs
  - Payment services
  - Third-party services

### 4.4 Message Queues (JMS)
- **Technology**: JMS (Java Message Service)
- **Purpose**: Asynchronous communication
- **Use cases**:
  - Event publishing
  - Background processing
  - System integration

### 4.5 Caching Layer
- **Technology**: Spring Cache, Redis
- **Annotation**: `@Cacheable`
- **Example**:
  ```java
  @Cacheable(value = "transactions")
  public TransactionResponse getTransactions(...) {
      // ...
  }
  ```

---

## 5. Key Differences Between Patterns

### Legacy Pattern
| Aspect | Details |
|--------|---------|
| **Controller Location** | Separate UI module: `ccb/ui/pk-webui/kwk/rest/` |
| **Process Location** | Separate middletier: `ccb/middletier/process/kwk/` |
| **Service Location** | Separate middletier: `ccb/middletier/service/kwk/` |
| **DAO Layer** | Always present for database access |
| **Data Sources** | Primarily internal database via JPA |
| **Dependency** | Controllers → Process → Service → DAO → DB |
| **Modularity** | Lower - spread across ccb/ui and ccb/middletier |

### UCC Pattern
| Aspect | Details |
|--------|---------|
| **Controller Location** | Inside UCC: `ucc/transactionoverview/process/rest/` |
| **Process Location** | Inside UCC: `ucc/transactionoverview/process/` |
| **Service Location** | Calls SC layer: `sc/.../service/` |
| **DAO Layer** | Optional - may not exist if using external APIs |
| **Data Sources** | Mixed: databases, external APIs, SC services |
| **Dependency** | Controllers → Process → SC Services → External/DB |
| **Modularity** | Higher - self-contained within UCC folder |

---

## 6. Where Data Comes From - Summary

### Data Source Types

1. **Local Database (JPA/DAO)**
   - Customer data
   - Referral codes (KWK example)
   - User preferences
   - Configuration data
   - Path: Process → Service → DAO → Database

2. **Mainframe (MNC)**
   - Core banking data
   - Account information
   - Legacy customer data
   - Transaction history
   - Path: Process → SC Service → MNC Adapter → Mainframe

3. **External REST APIs**
   - Datalake (transaction search)
   - PSD2 services
   - Payment gateways
   - Third-party integrations
   - Path: Process → SC Service → RestClient → External API

4. **Message Queues (JMS)**
   - Asynchronous events
   - Background jobs
   - System notifications
   - Path: Process → JMS Producer → Queue

5. **Cache (Redis/Spring Cache)**
   - Frequently accessed data
   - Session data
   - Performance optimization
   - Path: Process → Cache (if miss) → Source

---

## 7. Technology Stack

### Database Access
- **JPA 2.x** (Java Persistence API)
- **Hibernate** (ORM implementation)
- **Oracle Database** or **DB2**
- **JDBC** (underlying connectivity)
- **HikariCP** (connection pooling)

### External Communication
- **Spring RestTemplate** (HTTP client)
- **ApiBankingRestTemplate** (OAuth2-enabled REST client)
- **HttpClient** (Apache)
- **Hystrix** (circuit breaker, fault tolerance)
- **Feign** (declarative REST client - possibly)

### Mainframe Integration
- **MNC** (Mainframe Network Connector)
- **CICS** (Customer Information Control System)
- **MQ Series** (IBM message queuing)

### Caching
- **Spring Cache Abstraction**
- **Redis** (distributed cache)
- **EhCache** (local cache)

### Security & Auth
- **Spring Security**
- **OAuth2** (for external APIs)
- **JWT** (token-based auth)
- **Token Manager** (custom implementation)

---

## 9. Example: Complete Flow for KWK sendReference

```
1. Browser → HTTP POST /sendReference
             └─→ Headers: Authorization, Content-Type
             └─→ Body: {chosenIban, bounty, email, ...}

2. CrcJsonController.sendReference()
   └─→ Validates request is not null
   └─→ Validates email address
   └─→ Calls: crcProcess.sendReference(request)

3. CustomerReferCustomerProcessImpl.sendReference()
   └─→ @PreAuthorize("protect('REWARDCREDIT')") ← Security check
   └─→ checkAuthorizationForSelectedIban() 
       └─→ productService.retrieveProductList() → Database query
       └─→ ibanConverterService.getIban() → Convert account number
   └─→ participantService.retrieveParticipantData() → SC Service
       └─→ May call database or mainframe
   └─→ naturalPersonAPIV3Service.retrieveNaturalPersons() → SC Service
       └─→ Calls external API or database
   └─→ generateUniqueReferrallCode()
       └─→ Loop until unique code found
           └─→ kwkService.retrieveKwkData() → Check uniqueness in DB
   └─→ kwkService.saveCrcData() → Save to database

4. CustomerReferCustomerServiceImpl.saveCrcData()
   └─→ Maps CrcData → CustomerReferCustomer entity
   └─→ Calls: kwkDAO.saveCrcData(entity)

5. KwkDAOImpl.saveCrcData()
   └─→ Gets EntityManager
   └─→ Calls: super.insert(customerReferCustomer)
   └─→ JPA/Hibernate executes:
       INSERT INTO CUSTOMER_REFER_CUSTOMER (
           CRC_ID, CRC_CODE, CRC_ACCOUNTOWNER_NAME,
           CRC_IBAN, CRC_FIRST_NAME, CRC_LAST_NAME,
           CRC_EMAIL_ADDRESS, CRC_NPKENN, CRC_BOUNTY,
           CRC_BOUNTYID, CRC_PRODUCTID, CRC_PRODUCT_NAME,
           CRC_CREATION_TS
       ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

6. Database (Oracle/DB2)
   └─→ Stores record in CUSTOMER_REFER_CUSTOMER table
   └─→ Returns success

7. Response bubbles back up:
   DAO → Service → Process → Controller → Browser
   └─→ JsonResponse with referral code
```

---

## 10. Summary

### Legacy Pattern Flow
**Browser → UI Controller → Process → Service → DAO → Database**

- Clear separation between UI and business logic
- Always uses DAO layer for database
- Process layer orchestrates multiple services
- Primarily database-centric

### UCC Pattern Flow
**Browser → Controller (in Process) → Process → SC Services → External APIs / Database**

- Controller embedded in process module
- More direct external API integration
- May skip DAO layer entirely
- Uses RestClients for external systems
- More service-oriented architecture

### Common Data Sources
1. **Internal Database** (via JPA/DAO)
2. **Mainframe Systems** (via MNC)
3. **External REST APIs** (via RestTemplate)
4. **Message Queues** (via JMS)
5. **Cache** (via Spring Cache)

This layered architecture allows the monolith to integrate multiple data sources while maintaining separation of concerns.

