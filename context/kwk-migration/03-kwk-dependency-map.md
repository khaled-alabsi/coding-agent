# KWK Application - Complete Dependency Map

**Generated:** November 5, 2025  
**Purpose:** Comprehensive mapping of all KWK-related code across the CCB monolith

---

## 1. UI Layer - Wicket Web UI

### Location: `ccb/ui/pk-webui/kwk/ui`

#### 1.1 Main Pages

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/KWKOverviewPage.java` | Wicket Page | Main customer referral overview page | - Extends `BasePage`<br>- Function ID: `ccb.kundenwerbenkunden`<br>- Uses React hybrid components<br>- Injects `CrcDispatcher` |
| `src/main/java/com/commerzbank/ccb/kwk/KWKOverviewPage.html` | HTML Template | Wicket markup for overview page | - Wicket panel placeholders<br>- React component containers |
| `src/main/java/com/commerzbank/ccb/kwk/KWKOverviewPage.properties` | Properties | German translation keys | - 20+ translation keys |
| `src/main/java/com/commerzbank/ccb/kwk/KWKOverviewPage_en.properties` | Properties | English translation keys | - English translations |
| `src/main/java/com/commerzbank/ccb/kwk/KWKOverviewPageModel.java` | Model | Page data model | - Wicket page model |

#### 1.2 Confirmation Pages

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/confirmationpage/KWKConfirmationPage.java` | Wicket Page | Email confirmation page | - Displays referral code<br>- Email sharing functionality |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationpage/KWKConfirmationPage.html` | HTML Template | Email confirmation markup | - Wicket template |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationpage/KWKConfirmationPageModel.java` | Model | Email confirmation model | - Contains referral code |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationsmspage/KWKConfirmationSmsPage.java` | Wicket Page | SMS confirmation page | - SMS sharing functionality |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationsmspage/KWKConfirmationSmsPage.html` | HTML Template | SMS confirmation markup | - Wicket template |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationsmspage/KWKConfirmationSmsPageModel.java` | Model | SMS confirmation model | - Contains referral code |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationwhatsapppage/KWKConfirmationWhatsAppPage.java` | Wicket Page | WhatsApp confirmation page | - WhatsApp sharing functionality |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationwhatsapppage/KWKConfirmationWhatsAppPage.html` | HTML Template | WhatsApp confirmation markup | - Wicket template |
| `src/main/java/com/commerzbank/ccb/kwk/confirmationwhatsapppage/KWKConfirmationWhatsAppPageModel.java` | Model | WhatsApp confirmation model | - Contains referral code |

#### 1.3 LSG Variant Pages (Special Customer Segment)

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/lsg/overview/KWKOverviewLsgPage.java` | Wicket Page | LSG segment overview page | - Variant for LSG customers |
| `src/main/java/com/commerzbank/ccb/kwk/lsg/overview/KWKOverviewLsgPageModel.java` | Model | LSG overview model | - LSG-specific model |
| `src/main/java/com/commerzbank/ccb/kwk/lsg/overview/KWKModelLsgProvider.java` | Interface | LSG model provider | - Model provider for LSG |
| `src/main/java/com/commerzbank/ccb/kwk/lsg/confirmation/email/KWKConfirmationEmailLsgPage.java` | Wicket Page | LSG email confirmation | - Email for LSG customers |
| `src/main/java/com/commerzbank/ccb/kwk/lsg/confirmation/sms/KWKConfirmationSmsLsgPage.java` | Wicket Page | LSG SMS confirmation | - SMS for LSG customers |
| `src/main/java/com/commerzbank/ccb/kwk/lsg/confirmation/whatsapp/KWKConfirmationWhatsAppLsgPage.java` | Wicket Page | LSG WhatsApp confirmation | - WhatsApp for LSG customers |

#### 1.4 Wicket Panels & Components

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/container/KWKOverviewContainerPanel.java` | Wicket Panel | Container panel for overview | - Wraps main content |
| `src/main/java/com/commerzbank/ccb/kwk/container/KWKOverviewContainerModel.java` | Model | Container model | - Panel model |
| `src/main/java/com/commerzbank/ccb/kwk/recommendation/KWKRecommendationPanel.java` | Wicket Panel | Product recommendation panel | - Shows product recommendations |
| `src/main/java/com/commerzbank/ccb/kwk/recommendation/KWKRecommendationModel.java` | Model | Recommendation model | - Product data model |

#### 1.5 Model Providers

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/KWKModelProvider.java` | Interface | Model provider interface | - Methods:<br>  - `getProductList()`<br>  - `getPremium()`<br>  - `getRecommendationProduct()` |

#### 1.6 Page Mounting

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/pkwebui/mounting/KwkPageMountRegistrationImpl.java` | Service | URL mapping registration | - Registers page URLs<br>- Implements page routing |

#### 1.7 JavaScript/React Components

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/js/dist/overview/lib_kwk-page-bundle.js` | JavaScript | Overview page React bundle | - Bundled React components |
| `src/main/js/dist/email/lib_kwk-email-page-bundle.js` | JavaScript | Email page React bundle | - Email sharing components |
| `src/main/js/dist/instantmessages/lib_kwk-instant-messages-page-bundle.js` | JavaScript | Instant messages bundle | - SMS/WhatsApp components |

#### 1.8 Spring Configuration

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/resources/spring/config-kwk-ui.xml` | Spring XML | UI module Spring config | - Bean definitions<br>- Component scanning |

#### 1.9 Test Files

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/test/java/com/commerzbank/ccb/kwk/KwkOverviewPageModelTest.java` | JUnit Test | Page model unit test | - Tests page model logic |
| `src/test/resources/logback-test.xml` | Config | Test logging configuration | - Logback config for tests |

#### 1.10 POM File

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `pom.xml` | Maven POM | UI module build configuration | - Artifact: `kwk-pk-ui`<br>- Packaging: `jar`<br>- Dependencies:<br>  - `crc-pk-public`<br>  - Wicket framework<br>  - React integration |

---

## 2. REST API Layer

### Location: `ccb/ui/pk-webui/kwk/rest`

#### 2.1 REST Controllers

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/crc/rest/delegate/CrcJsonController.java` | Spring Controller | Main REST API controller | - `@Controller`<br>- `@RequestMapping()`<br>- Endpoints:<br>  - `GET /crcCheck` (health check)<br>  - `POST /sendReference` (create referral)<br>- Injects `CustomerReferCustomerProcess` |

#### 2.2 DTOs

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/crc/rest/dto/CrcCodeDto.java` | DTO | Referral code response DTO | - Contains referral code string |

#### 2.3 Test Files

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/test/java/com/commerzbank/ccb/crc/rest/delegate/CrcJsonControllerTest.java` | JUnit Test | Controller unit test | - Tests REST endpoints |
| `src/test/java/com/commerzbank/ccb/crc/rest/dto/CrcCodeDtoTest.java` | JUnit Test | DTO unit test | - Tests DTO serialization |
| `src/test/java/com/commerzbank/ccb/crc/rest/mock/CustomerReferCustomerProcessMock.java` | Mock | Process mock for testing | - Mock implementation of process interface |

#### 2.4 Spring Configuration

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/resources/spring/config-crc-rest.xml` | Spring XML | REST module Spring config | - Controller bean definitions<br>- MVC configuration |
| `src/test/resources/spring/crc-rest-test.xml` | Spring XML | Test Spring config | - Test bean configurations |

#### 2.5 Properties

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/resources/CrcJsonController.properties` | Properties | Controller messages | - Error messages<br>- Response messages |

#### 2.6 Test Configuration

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/test/resources/stage/local.config` | Config | Local test environment config | - Environment settings |
| `src/test/resources/stage/ccb-cms.properties` | Properties | CMS properties for testing | - CMS configuration |
| `src/test/resources/logback-test.xml` | Config | Test logging configuration | - Logback settings |

#### 2.7 POM File

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `pom.xml` | Maven POM | REST module build configuration | - Artifact: `kwk-pk-rest`<br>- Packaging: `jar`<br>- Dependencies:<br>  - `process-interface-kwk`<br>  - `ui-shared-rest`<br>  - `ui-shared-json`<br>  - Spring Web<br>  - Spring Security |

---

## 3. Public/Shared Components Layer

### Location: `ccb/ui/pk-webui/kwk/public`

#### 3.1 Business Delegates

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/delegate/CrcDelegate.java` | Delegate | Main business delegate | - `@CCBBusinessDelegate`<br>- Methods:<br>  - `retrieveSettlementAccounts()`<br>  - `isEmployee()`<br>- Injects `CustomerReferCustomerProcess` |

#### 3.2 Dispatchers

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/transfer/CrcDispatcher.java` | Component | Data transformation dispatcher | - `@CCBComponent`<br>- `@Named("kwkDispatcher")`<br>- Method: `retrieveDropdownData()`<br>- Handles JSON transformation<br>- CSV file processing<br>- Error handling |

#### 3.3 JSON DTOs

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/json/dto/CrcAccount.java` | DTO | Account data DTO | - IBAN, owner name |
| `src/main/java/com/commerzbank/ccb/kwk/json/dto/CrcProduct.java` | DTO | Product data DTO | - Product ID, name, description |
| `src/main/java/com/commerzbank/ccb/kwk/json/dto/CrcReward.java` | DTO | Reward data DTO | - Reward type, amount |
| `src/main/java/com/commerzbank/ccb/kwk/json/dto/CrcDropdownData.java` | DTO | Combined dropdown data | - Products + Accounts |
| `src/main/java/com/commerzbank/ccb/kwk/json/dto/CrcErrorEnum.java` | Enum | Error codes enumeration | - Error code definitions |

#### 3.4 CSV Models

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/csv/CrcProductModel.java` | Model | CSV product model | - Maps CSV product data |
| `src/main/java/com/commerzbank/ccb/kwk/csv/CrcRewardModel.java` | Model | CSV reward model | - Maps CSV reward data |
| `src/main/java/com/commerzbank/ccb/kwk/csv/CrcProducts.java` | Model | Product collection | - Collection of products from CSV |

#### 3.5 Utilities

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/util/CrcConfig.java` | Config | Configuration utility | - CSV file paths<br>- Configuration constants |
| `src/main/java/com/commerzbank/ccb/kwk/util/RewardType.java` | Enum | Reward type enumeration | - Cash, voucher, etc. |
| `src/main/java/com/commerzbank/ccb/kwk/util/CcbKwkDataError.java` | Exception | Data validation error | - Custom exception class |
| `src/main/java/com/commerzbank/ccb/kwk/util/CcbKwkCSVFileFormateError.java` | Exception | CSV format error | - CSV parsing exception |

#### 3.6 Test Files

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/test/java/com/commerzbank/ccb/kwk/delegate/KwkDelegateTest.java` | JUnit Test | Delegate unit test | - Tests delegate methods |
| `src/test/java/com/commerzbank/ccb/kwk/transfer/CrcDispatcherTest.java` | JUnit Test | Dispatcher unit test | - Tests data transformation |
| `src/test/java/com/commerzbank/ccb/kwk/transfer/KwkDispatcherTest.java` | JUnit Test | Legacy dispatcher test | - Legacy test file |
| `src/test/java/com/commerzbank/ccb/kwk/json/dto/KwkRewardMapperTest.java` | JUnit Test | Reward mapper test | - Tests DTO mapping |

#### 3.7 Spring Configuration

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/resources/spring/config-kwk-pk-ui.xml` | Spring XML | Public module Spring config | - Bean definitions<br>- Component scanning |

#### 3.8 POM File

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `pom.xml` | Maven POM | Public module build configuration | - Artifact: `crc-pk-public`<br>- Packaging: `jar`<br>- Dependencies:<br>  - `fw-shared-api`<br>  - `ui-shared-json`<br>  - `process-interface-kwk`<br>  - OpenCSV<br>  - Joda-Time |

---

## 4. Process Interface Layer

### Location: `ccb/process-interface/kwk`

#### 4.1 Process Interface

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/CustomerReferCustomerProcess.java` | Interface | Main process interface | - Methods:<br>  - `sendReference(SendReferenceRequest)`<br>  - `retrieveSettlementAccounts()`<br>  - `checkCustomerType(CheckCustomerTypeRequest)` |

#### 4.2 Request Objects

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/request/SendReferenceRequest.java` | DTO | Create referral request | - Product ID/name<br>- Bounty ID/description<br>- IBAN<br>- Account owner name<br>- Email address<br>- `@Valid` annotations |
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/request/CheckCustomerTypeRequest.java` | DTO | Check customer type request | - Simple request object |

#### 4.3 Response Objects

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/response/SendReferenceResponse.java` | DTO | Create referral response | - Contains referral code |
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/response/RetrieveCrcAccountDataResponse.java` | DTO | Account list response | - List of `CrcAccountData` |
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/response/CrcAccountData.java` | DTO | Single account data | - Account number, IBAN, owner |
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/response/CheckCustomerTypeResponse.java` | DTO | Customer type response | - Boolean: `isEmployee` |
| `src/main/java/com/commerzbank/ccb/kwk/processinterface/response/CrcJuristicalLoggingErrorMessages.java` | Enum | Legal logging errors | - Error message constants |

#### 4.4 POM File

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `pom.xml` | Maven POM | Process interface build config | - Artifact: `process-interface-kwk`<br>- Description: "CCB kwk process layer API"<br>- Dependencies:<br>  - Validation API<br>  - `shared-functional-domain-base` |

---

## 5. Process Implementation Layer

### Location: `ccb/middletier/process/kwk`

#### 5.1 Process Implementation

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/process/CustomerReferCustomerProcessImpl.java` | Process | Main business process | - `@CCBProcess`<br>- `@CCBTransactionalProcess`<br>- Extends `BaseProcess`<br>- Implements `CustomerReferCustomerProcess`<br>- Key methods:<br>  - `sendReference()` - `@PreAuthorize("protect('REWARDCREDIT')")`<br>  - `retrieveSettlementAccounts()`<br>  - `checkCustomerType()`<br>  - `generateUniqueReferrallCode()` (private)<br>  - `checkAuthorizationForSelectedIban()` (private)<br>- **13+ injected dependencies** (see section 8) |

#### 5.2 Test Files

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/test/java/com/commerzbank/ccb/kwk/process/CustomerReferCustomerProcessImplTest.java` | JUnit Test | Process unit test | - Tests process logic<br>- Mock dependencies |

#### 5.3 POM File

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `pom.xml` | Maven POM | Process module build config | - Artifact: `kwk-process`<br>- Dependencies:<br>  - `sc-sharedbusiness-api`<br>  - `process-interface-dcrm`<br>  - `account-service-public`<br>  - `common-service`<br>  - `middletier-shared-functionality-process` |

---

## 6. Service Layer

### Location: `ccb/middletier/service/kwk`

#### 6.1 Service Interface

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/service/CustomerReferCustomerService.java` | Interface | Service interface | - Methods:<br>  - `saveCrcData(CrcData)`<br>  - `retrieveKwkData(String kwkCode)` |

#### 6.2 Service Implementation

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/kwk/service/impl/CustomerReferCustomerServiceImpl.java` | Service | Service implementation | - `@CCBService`<br>- Extends `BaseService`<br>- Injects `KwkDAO`<br>- Implements data persistence |

#### 6.3 DAO Layer

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/common/kwk/dao/KwkDAO.java` | Interface | DAO interface | - Methods:<br>  - `saveCrcData(CustomerReferCustomer)`<br>  - `retrieveKwkData(String kwkCode)` |
| `src/main/java/com/commerzbank/ccb/common/kwk/dao/impl/KwkDAOImpl.java` | DAO | DAO implementation | - `@CCBComponent`<br>- Extends `AbstractJpaDAO`<br>- Uses `EntityManager`<br>- JPQL queries |
| `src/main/java/com/commerzbank/ccb/common/kwk/dao/impl/CustomerReferCustomer.java` | Entity | JPA entity | - `@Entity`<br>- Table: `CustomerReferCustomer`<br>- Fields:<br>  - `crcCode` (unique)<br>  - `crcProductName/Id`<br>  - `crcBounty/BountyId`<br>  - `crcAccountOwnerName`<br>  - `crcIban`<br>  - `crcEmailAddress`<br>  - `crcFirstName/LastName`<br>  - `crcNpkenn`<br>  - `crcCreationTs` |

#### 6.4 Test Files

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/test/java/com/commerzbank/ccb/kwk/service/impl/CustomerReferCustomerServiceImplTest.java` | JUnit Test | Service unit test | - Tests service methods |
| `src/test/java/com/commerzbank/ccb/common/kwk/dao/impl/KwkDAOImplTest.java` | JUnit Test | DAO unit test | - Tests database operations |

#### 6.5 POM File

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `pom.xml` | Maven POM | Service module build config | - Artifact: `kwk-service`<br>- Dependencies:<br>  - `fw-shared-api`<br>  - `shared-functional-domain-base`<br>  - `account-service-public`<br>  - `backend-host-depot`<br>  - `backend-host-cowias` |

---

## 7. Shared Domain Layer

### Location: `ccb/shared/functional-domain/base`

#### 7.1 Domain Objects

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `src/main/java/com/commerzbank/ccb/framework/domain/kwk/CrcData.java` | Domain Object | Referral data domain model | - Shared across layers<br>- Fields:<br>  - `kwkCode`<br>  - `productName/productId`<br>  - `bounty/bountyId`<br>  - `accountOwnerName`<br>  - `accountOwnerIban`<br>  - `kwkEmailAddress`<br>  - `proposerFirstname/Lastname`<br>  - `npkenn`<br>  - `dateOfCreation` |

---

## 8. React UI Components (Modern)

### Location: `ui-react/src/main/webapp/WEB-INF/resources/media`

#### 8.1 React LSG5 Components (TypeScript)

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `react-lsg5/src/parent/kwk/main-page/KwkMainPage.tsx` | React Component | Main page component | - TypeScript<br>- Modern React |
| `react-lsg5/src/parent/kwk/main-page/KwkMainPage.css` | CSS | Main page styles | - Component styles |
| `react-lsg5/src/parent/kwk/email_page/EmailPage.tsx` | React Component | Email sharing page | - TypeScript |
| `react-lsg5/src/parent/kwk/email_page/EmailPage.css` | CSS | Email page styles | - Component styles |
| `react-lsg5/src/parent/kwk/instant-messages-page/InstantMessagesPage.tsx` | React Component | SMS/WhatsApp page | - TypeScript |
| `react-lsg5/src/parent/kwk/qr-code/KwkQRCode.tsx` | React Component | QR code component | - TypeScript<br>- QR code generation |
| `react-lsg5/src/parent/kwk/helper/AdditionalInformationRow.tsx` | React Component | Helper component | - Reusable UI component |
| `react-lsg5/src/parent/kwk/GA/AnalyticsPixel.js` | JavaScript | Google Analytics tracking | - Analytics integration |

#### 8.2 React Storybook Stories

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `react-lsg5/src/stories/kwk/main-page/Kwk.stories.tsx` | Storybook Story | Main page stories | - Component documentation |
| `react-lsg5/src/stories/kwk/emailPage/emailPage.stories.tsx` | Storybook Story | Email page stories | - Component documentation |
| `react-lsg5/src/stories/kwk/instant-messages-page/InstantMessages.stories.tsx` | Storybook Story | IM page stories | - Component documentation |
| `react-lsg5/src/stories/kwk/qr-code/KwkQRCode.stories.tsx` | Storybook Story | QR code stories | - Component documentation |

#### 8.3 Legacy React Components (JavaScript)

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `react/parent_comp/kwk/kwkpanel.js` | React Component | Main KWK panel | - Legacy JavaScript |
| `react/parent_comp/kwk/kwkselection.js` | React Component | Selection component | - Product/account selection |
| `react/parent_comp/kwk/kwkemailpanel.js` | React Component | Email panel | - Email sharing UI |
| `react/parent_comp/kwk/confpanel.js` | React Component | Confirmation panel | - General confirmation |
| `react/parent_comp/kwk/qrconfpanel.js` | React Component | QR confirmation panel | - QR code display |

---

## 9. Cross-References & Integration Points

### 9.1 FormsProcess Integration

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `ccb/middletier/process/formsprocess/src/test/resources/spring/kwkData-restController-test.xml` | Spring Test Config | Test configuration for KWK | - Beans:<br>  - `crcRestController`<br>  - `crcFormsProcess` (mock) |

### 9.2 Module Parent POM

| File Path | Type | Description | Technical Details |
|-----------|------|-------------|-------------------|
| `ccb/ui/pk-webui/kwk/pom.xml` | Maven POM | Parent POM for all KWK modules | - Group: `coba.ccb.ui.pk-webui.kwk`<br>- Artifact: `kwk-pk-parent`<br>- Modules:<br>  - `ui`<br>  - `rest`<br>  - `public` |

---

## 10. External Dependencies (Service Clusters)

### From Process Implementation Analysis

| Dependency | Package | Purpose |
|-----------|---------|---------|
| `CustomerReferCustomerService` | `ccb.kwk.service` | Persist/retrieve referral data |
| `ParticipantService` | `sc.participant.api.service` | Get participant data |
| `UserDataService` | `sc.participant.api.service` | Get user data |
| `CustomersAPIV3Service` | `sc.person.api.service` | Get customer information |
| `NaturalPersonAPIV3Service` | `sc.person.api.service` | Get person details (name) |
| `ProductService` | `common.service` | Product filtering (KWK_REWARDCREDIT_FILTER) |
| `PersonService` | `common.service.person` | Legacy person service |
| `IbanConverterService` | `sc.sharedbusiness.api.service` | Convert account numbers to IBAN |
| `CCBNumberResolverService` | `sc.sharedbusiness.api.service` | Resolve product numbers |
| `AuthorizationService` | `framework.security.services` | Authorization checks |
| `BaseProductMatrixService` | `sc.sharedbusiness.api.service` | Product matrix data |
| `JuristicalLoggingService` | `sc.sharedbusiness.api.service` | Legal/compliance logging |

---

## 11. Database Schema

### Table: `CustomerReferCustomer`

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `id` | Long | PRIMARY KEY, AUTO_INCREMENT | Primary key |
| `crc_code` | String(8) | UNIQUE, NOT NULL | Referral code |
| `crc_product_name` | String(255) | | Product name |
| `crc_product_id` | Integer | | Product ID |
| `crc_bounty` | String(255) | | Reward description |
| `crc_bounty_id` | Integer | | Reward ID |
| `crc_account_owner_name` | String(150) | | Account owner name |
| `crc_iban` | String(34) | | Settlement IBAN |
| `crc_email_address` | String(255) | | Referee email |
| `crc_first_name` | String(100) | | Proposer first name |
| `crc_last_name` | String(100) | | Proposer last name |
| `crc_npkenn` | String(50) | | Natural person identifier |
| `crc_creation_ts` | Timestamp | NOT NULL | Creation timestamp |

---

## 12. Build & Deployment

### Maven Module Hierarchy

```
portal/
└── ccb/
    ├── process-interface/
    │   └── kwk/                      [process-interface-kwk]
    ├── middletier/
    │   ├── process/
    │   │   └── kwk/                  [kwk-process]
    │   └── service/
    │       └── kwk/                  [kwk-service]
    ├── shared/
    │   └── functional-domain/
    │       └── base/                 [shared-functional-domain-base]
    │           └── (contains CrcData.java)
    └── ui/
        └── pk-webui/
            └── kwk/                  [kwk-pk-parent]
                ├── ui/               [kwk-pk-ui]
                ├── rest/             [kwk-pk-rest]
                └── public/           [crc-pk-public]
```

### Dependency Flow

```
kwk-pk-ui
  └─> crc-pk-public
      └─> process-interface-kwk

kwk-pk-rest
  └─> process-interface-kwk
  └─> ui-shared-json

crc-pk-public
  └─> process-interface-kwk
  └─> fw-shared-api

kwk-process (implementation)
  └─> process-interface-kwk
  └─> kwk-service
  └─> sc-sharedbusiness-api
  └─> common-service

kwk-service
  └─> shared-functional-domain-base
  └─> fw-shared-api
```

---

## 13. Security & Permissions

| Aspect | Details |
|--------|---------|
| Function ID | `ccb.kundenwerbenkunden` |
| Permission | `REWARDCREDIT` |
| Security Annotation | `@PreAuthorize("protect('REWARDCREDIT')")` |
| Authorization Check | In-code check for IBAN access via `@InCodePermissionCheck` |
| Product Filter | `KWK_REWARDCREDIT_FILTER` |

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total Java Files** | ~60+ |
| **Wicket Pages** | 12 (6 standard + 6 LSG variants) |
| **REST Controllers** | 1 |
| **Service Classes** | 2 (Service + DAO) |
| **Process Classes** | 1 |
| **Domain Objects** | 1 (CrcData) |
| **JPA Entities** | 1 (CustomerReferCustomer) |
| **React Components (Modern)** | 8 TypeScript + 5 JavaScript |
| **DTOs** | 15+ |
| **Test Files** | 10+ |
| **Maven Modules** | 5 (ui, rest, public, process, service) |
| **External SC Dependencies** | 13+ |
| **Database Tables** | 1 |

---

## Migration Impact Analysis

### High Coupling Points
1. ✅ **Process Layer** → 13+ SC service dependencies
2. ✅ **DAO Layer** → Shared database
3. ✅ **UI Layer** → CCB Wicket framework
4. ✅ **Security** → CCB authorization framework
5. ✅ **Domain Objects** → Shared functional domain module

### Independence Level: **LOW** ⚠️

The KWK application is deeply integrated into the CCB monolith and cannot be easily extracted without significant refactoring.

---

**Document Version:** 1.0  
**Last Updated:** November 5, 2025

