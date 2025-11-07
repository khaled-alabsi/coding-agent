# KWK Application Analysis

## Application Overview

**KWK (Kunden Werben Kunden / Customer Refer Customer)** is a customer referral program application that allows existing customers to refer new customers and receive rewards.

**Location:** `C:\CCB\sources\portal\ccb\ui\pk-webui\kwk`

---

## Application Structure

The KWK application is organized into **3 main modules**:

```
kwk/
├── ui/          - Web UI (Wicket-based pages and panels)
├── rest/        - REST API endpoints
├── public/      - Shared components (delegates, dispatchers, DTOs)
└── pom.xml
```

---

## Business Functionality

### Core Features

1. **Customer Referral Creation**
   - Customer selects a product to recommend
   - Customer selects reward type and settlement account
   - Customer enters referee's email address
   - System generates unique referral code
   - System stores referral data in database

2. **Referral Sharing**
   - Email sharing capability
   - SMS sharing capability  
   - WhatsApp sharing capability
   - Display referral code for manual sharing

3. **Account & Product Management**
   - Retrieve eligible settlement accounts (with REWARDCREDIT permission)
   - Display available products for referral
   - Display reward information per product
   - Validate account authorization

4. **Customer Type Checking**
   - Determine if customer is an employee (different rules may apply)

---

## Technical Architecture

### Module Breakdown

#### 1. UI Module (`kwk/ui`)
**Technology:** Apache Wicket + JavaScript/React hybrid

**Key Components:**

**Pages:**
- `KWKOverviewPage.java` - Main overview page
- `KWKOverviewLsgPage.java` - LSG variant overview
- `KWKConfirmationPage.java` - Email confirmation page
- `KWKConfirmationSmsPage.java` - SMS confirmation page
- `KWKConfirmationWhatsAppPage.java` - WhatsApp confirmation page
- LSG variants of all confirmation pages

**Panels:**
- `KWKOverviewContainerPanel.java` - Container for overview content
- `KWKRecommendationPanel.java` - Product recommendation display

**Models:**
- `KWKOverviewPageModel.java` - Page data model
- `KWKOverviewContainerModel.java` - Container data model
- `KWKRecommendationModel.java` - Recommendation data model
- `KWKModelProvider.java` - Model provider interface

**Mount Registration:**
- `KwkPageMountRegistrationImpl.java` - Registers page URLs

**JavaScript:**
- `src/main/js/dist/overview/` - React components for overview
- `src/main/js/dist/email/` - React components for email sharing
- `src/main/js/dist/instantmessages/` - React components for instant messaging

**Dependencies:**
- Wicket framework
- React components (hybrid approach)
- DCRM (Dynamic Content & Resource Management)
- CCB UI framework

#### 2. REST Module (`kwk/rest`)
**Technology:** Spring MVC REST

**Key Components:**

**Controllers:**
- `CrcJsonController.java` - REST API endpoint
  - `GET /crcCheck` - Health check
  - `POST /sendReference` - Send customer reference

**DTOs:**
- `CrcCodeDto.java` - Referral code response DTO

**Dependencies:**
- Spring Web MVC
- Spring Security
- Process Interface (kwk)
- UI Shared JSON utilities

#### 3. Public Module (`kwk/public`)
**Technology:** Java components shared across UI and REST

**Key Components:**

**Business Delegates:**
- `CrcDelegate.java` - Main business delegate
  - `retrieveSettlementAccounts()` - Get eligible accounts
  - `isEmployee()` - Check customer type

**Dispatchers:**
- `CrcDispatcher.java` - Data transformation and orchestration
  - `retrieveDropdownData()` - Build JSON for dropdowns
  - Handles product/account filtering
  - Error handling and validation

**DTOs (JSON):**
- `CrcAccount.java` - Account data
- `CrcProduct.java` - Product data
- `CrcReward.java` - Reward data
- `CrcDropdownData.java` - Combined dropdown data
- `CrcErrorEnum.java` - Error codes

**CSV Models:**
- `CrcProductModel.java` - Product CSV model
- `CrcRewardModel.java` - Reward CSV model
- `CrcProducts.java` - Product collection

**Utilities:**
- `CrcConfig.java` - Configuration
- `RewardType.java` - Reward type enum
- `CcbKwkDataError.java` - Data validation errors
- `CcbKwkCSVFileFormateError.java` - CSV format errors

**Dependencies:**
- CCB Framework Shared API
- Process Interface (kwk)
- UI Shared JSON
- UI Shared UI components
- OpenCSV library
- Joda-Time

---

## Backend Dependencies

### Process Layer (`ccb/process-interface/kwk`)
**Purpose:** Process contract definitions

**Interface:**
- `CustomerReferCustomerProcess.java` - Main process interface

**Methods:**
1. `sendReference(SendReferenceRequest)` → `SendReferenceResponse`
   - Creates referral and generates code
   - Protected by `@PreAuthorize("protect('REWARDCREDIT')")`

2. `retrieveSettlementAccounts()` → `RetrieveCrcAccountDataResponse`
   - Returns accounts eligible for rewards

3. `checkCustomerType(CheckCustomerTypeRequest)` → `CheckCustomerTypeResponse`
   - Checks if customer is employee

**Request/Response Objects:**
- `SendReferenceRequest.java`
- `SendReferenceResponse.java`
- `CheckCustomerTypeRequest.java`
- `CheckCustomerTypeResponse.java`
- `RetrieveCrcAccountDataResponse.java`
- `CrcAccountData.java`
- `CrcJuristicalLoggingErrorMessages.java`

### Process Implementation (`ccb/middletier/process/kwk`)
**Class:** `CustomerReferCustomerProcessImpl.java`

**Annotations:**
- `@CCBProcess`
- `@CCBTransactionalProcess`

**Key Dependencies (Injected Services):**
1. `CustomerReferCustomerService` - KWK data persistence
2. `ParticipantService` (SC) - Participant data
3. `PersonService` - Person data  
4. `ProductService` - Product information
5. `IbanConverterService` (SC) - IBAN conversion
6. `CCBNumberResolverService` (SC) - Product number resolution
7. `AuthorizationService` - Authorization checks
8. `BaseProductMatrixService` (SC) - Product matrix data
9. `JuristicalLoggingService` (SC) - Legal logging
10. `UserDataService` (SC) - User data
11. `CustomersAPIV3Service` (SC) - Customer API v3
12. `NaturalPersonAPIV3Service` (SC) - Natural person API v3

**Key Methods:**
1. `sendReference(SendReferenceRequest)` 
   - Validates authorization for selected IBAN
   - Retrieves participant and person data
   - Generates unique referral code (8-character alphanumeric)
   - Saves referral data via service
   - Logs transaction
   
2. `retrieveSettlementAccounts()`
   - Gets products with KWK_REWARDCREDIT_FILTER
   - Converts to IBAN format
   - Returns account list

3. `checkCustomerType(CheckCustomerTypeRequest)`
   - Retrieves participant data
   - Checks employee status

4. `generateUniqueReferrallCode()` - Private
   - Generates random 8-character code
   - Ensures uniqueness by checking database

5. `checkAuthorizationForSelectedIban(String)` - Private
   - Validates user has access to selected IBAN
   - Uses `@InCodePermissionCheck` annotation
   - Throws `AccessDeniedException` if unauthorized

**Service Cluster (SC) Dependencies:**
- `sc.participant` - Participant services
- `sc.person` - Person services (V3 API)
- `sc.sharedbusiness` - Shared business services (IBAN, logging, etc.)

### Service Layer (`ccb/middletier/service/kwk`)
**Interface:** `CustomerReferCustomerService.java`

**Implementation:** `CustomerReferCustomerServiceImpl.java`

**Annotations:**
- `@CCBService`

**Methods:**
1. `saveCrcData(CrcData)` - Persists referral data
2. `retrieveKwkData(String kwkCode)` - Retrieves referral by code

**Dependencies:**
- `KwkDAO` - Data access object

### Data Access Layer (`ccb/middletier/service/kwk`)
**Interface:** `KwkDAO.java`

**Implementation:** `KwkDAOImpl.java`

**Annotations:**
- `@CCBComponent`

**Entity:**
- `CustomerReferCustomer.java` - JPA entity

**Methods:**
1. `saveCrcData(CustomerReferCustomer)` - Inserts to database
2. `retrieveKwkData(String kwkCode)` - Queries by referral code

**Technology:**
- JPA/Hibernate
- EntityManager
- JPQL queries
- Extends `AbstractJpaDAO`

**Database Table:** `CustomerReferCustomer` (JPA entity name)

**Fields:**
- `crcCode` - Referral code (unique)
- `crcProductName` - Product name
- `crcProductId` - Product ID
- `crcBounty` - Reward amount/description
- `crcBountyId` - Reward ID
- `crcAccountOwnerName` - Account owner name (max 150 chars)
- `crcIban` - Settlement IBAN
- `crcEmailAddress` - Referee email
- `crcFirstName` - Proposer first name
- `crcLastName` - Proposer last name
- `crcNpkenn` - Natural person identifier
- `crcCreationTs` - Creation timestamp

---

## Data Flow

### Referral Creation Flow

```
User (Browser)
    ↓
KWKOverviewPage (Wicket)
    ↓
CrcDispatcher.retrieveDropdownData()
    ↓
CrcDelegate.retrieveSettlementAccounts()
    ↓
CustomerReferCustomerProcess.retrieveSettlementAccounts()
    ↓
ProductService (retrieves products with KWK_REWARDCREDIT_FILTER)
    ↓
IbanConverterService (converts to IBAN)
    ↓
Return accounts to UI
```

### Send Reference Flow

```
User submits referral
    ↓
CrcJsonController.sendReference(@RequestBody SendReferenceRequest)
    ↓
CustomerReferCustomerProcess.sendReference(request)
    ↓
├─ checkAuthorizationForSelectedIban() - Validates IBAN permission
├─ ParticipantService.retrieveParticipantData() - Get participant
├─ NaturalPersonAPIV3Service.retrieveNaturalPersons() - Get person name
├─ generateUniqueReferrallCode() - Generate code
│   └─ CustomerReferCustomerService.retrieveKwkData() - Check uniqueness
└─ CustomerReferCustomerService.saveCrcData(kwkData)
    ↓
KwkDAO.saveCrcData(customerReferCustomer)
    ↓
EntityManager.persist() - Database insert
    ↓
Return referral code to user
```

---

## External Dependencies Summary

### Service Cluster (SC) Dependencies
1. **sc.participant**
   - `ParticipantService`
   - `UserDataService`

2. **sc.person**
   - `CustomersAPIV3Service`
   - `NaturalPersonAPIV3Service`

3. **sc.sharedbusiness**
   - `IbanConverterService`
   - `CCBNumberResolverService`
   - `BaseProductMatrixService`
   - `JuristicalLoggingService`

4. **sc.productbase** (via ProductService)
   - Product filtering and retrieval

5. **sc.authorization** (via AuthorizationService)
   - Permission checks

### CCB Core Dependencies
1. **Framework (fw)**
   - `fw.shared.api` - Annotations, logging, exceptions
   - `fw.mt.api` - BaseService, BaseProcess
   - `fw.ui.api` - BasePage, Wicket components

2. **CCB Shared**
   - `shared-functional-domain-base` - Domain objects
   - `shared-functional-domain-bankingproducts` - Product models

3. **CCB Middletier**
   - `account-service-public` - Account services
   - `common-service` - Common services
   - Product services

### Third-Party Libraries
- **Apache Wicket** - UI framework
- **Spring Framework** - DI, MVC, Security
- **JPA/Hibernate** - Persistence
- **OpenCSV** - CSV processing
- **Joda-Time** - Date/time handling
- **Jackson** - JSON processing
- **Commons Lang3** - Utilities
- **Commons Collections** - Collection utilities

---

## Security & Authorization

### Permission Model
- **Function ID:** `ccb.kundenwerbenkunden`
- **Permission:** `REWARDCREDIT`
- **Security Annotation:** `@PreAuthorize("protect('REWARDCREDIT')")`

### Authorization Checks
1. **Page Access** - User must have function access
2. **IBAN Selection** - User must have permission for selected account
3. **Product Filter** - Only products with `KWK_REWARDCREDIT_FILTER` shown

### In-Code Permission Checks
- `@InCodePermissionCheck` - Used in `checkAuthorizationForSelectedIban()`
- `@PermissionsCheckedInternal` - Applied to process methods

---

## Configuration

### Properties/Configuration Files
- Located in `src/main/resources/`
- Message bundles for i18n
- CSV files for product/reward configuration
- Application properties

### CSV Configuration
- Product definitions
- Reward definitions  
- Mapping between products and rewards

---

## Testing

### Test Structure
- Unit tests in `src/test/java/`
- Mock implementations for external dependencies
- Test coverage for:
  - Process layer
  - Service layer
  - DAO layer
  - REST controllers
  - Delegates

### Key Test Files
- `CustomerReferCustomerProcessImplTest.java`
- `CustomerReferCustomerServiceImplTest.java`
- `KwkDAOImplTest.java`
- `CustomerReferCustomerProcessMock.java` (for REST testing)
- `KwkDelegateTest.java`

---

## Summary

The KWK application is a **3-tier application** with:
- **Presentation Layer** - Wicket UI + REST API
- **Business Logic Layer** - Process + Service
- **Data Access Layer** - DAO + JPA

It has **strong dependencies** on:
- CCB Framework infrastructure
- Service Cluster (SC) services for customer, account, and product data
- CCB shared domain models
- Apache Wicket for UI rendering
- Spring for REST and security

**Key Challenge for Migration:** The application is tightly coupled to the CCB monolith's service layer and would require significant refactoring to operate independently.

