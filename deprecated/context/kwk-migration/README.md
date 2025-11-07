# KWK (Customer Refer Customer) - Microservice Migration
## Overview
This folder contains the analysis and migration plan for extracting the **KWK (Kunden Werben Kunden / Customer Refer Customer)** application from the CCB monolith into an independent microservice.
---
## Documentation Structure
### ?? 01-kwk-application-analysis.md
**Purpose:** Comprehensive analysis of the current KWK application
**Contents:**
- Application structure and organization
- Business functionality overview
- Technical architecture breakdown
- Module dependencies
- Data flow diagrams
- External dependencies summary
- Security & authorization model
- Testing structure
**Use this document to:** Understand the current state of the KWK application
---
### ?? 02-migration-plan.md
**Purpose:** Detailed step-by-step migration plan
**Contents:**
- Migration strategy and approach
- Pre-migration assessment
- 6 detailed phases with concrete steps
- File-by-file implementation guidance
- Code examples for key components
- Timeline and effort estimates
- Risk mitigation strategies
- Success criteria
**Use this document to:** Execute the migration from monolith to microservice
---
## Quick Summary
### Application: KWK (Customer Refer Customer)
- **Location:** `C:\CCB\sources\portal\ccb\ui\pk-webui\kwk`
- **Purpose:** Customer referral program allowing existing customers to refer new customers
- **Current Tech:** Wicket UI + Spring + JPA
- **Target Tech:** Spring Boot + React
### Migration Complexity: **HIGH** ??
**Why:**
- 13+ external service dependencies
- Tight coupling to CCB framework
- Wicket ? React conversion needed
- Shared database
- Complex security integration
### Estimated Timeline: **14-20 weeks**
**Team Required:**
- 1 Backend Developer (Java/Spring Boot)
- 1 Frontend Developer (React/TypeScript)
- 1 DevOps Engineer (Part-time)
- 1 QA Engineer (Part-time)
---
## Migration Phases
### Phase 1: Analysis & Planning (2-3 weeks)
- Dependency analysis
- Data model analysis
- API contract design
- Security design
### Phase 2: Backend Microservice Setup (3-4 weeks)
- Spring Boot project setup
- Database layer
- Service layer implementation
- External service integration clients
- REST API controllers
- Security implementation
- Testing
### Phase 3: Frontend Development (4-5 weeks)
- React project setup
- API integration layer
- State management
- UI components
- Pages (Overview, Confirmations)
- Testing
### Phase 4: Integration & Testing (2-3 weeks)
- Backend-frontend integration
- External service integration testing
- Performance testing
- Security testing
### Phase 5: Deployment & Migration (2-3 weeks)
- Infrastructure setup
- Database migration
- Gradual rollout
- Monitoring & observability
### Phase 6: Decommission Legacy (1-2 weeks)
- Traffic validation
- Legacy code removal
- Post-migration validation
---
## Key Dependencies to Replace
### Service Cluster (SC) Dependencies
1. **ParticipantService** - User participant data
2. **UserDataService** - User data
3. **CustomersAPIV3Service** - Customer data
4. **NaturalPersonAPIV3Service** - Person data
5. **IbanConverterService** - IBAN conversion
6. **CCBNumberResolverService** - Product number resolution
7. **BaseProductMatrixService** - Product matrix
8. **JuristicalLoggingService** - Legal logging
9. **ProductService** - Product information
10. **PersonService** - Person data (legacy)
11. **AuthorizationService** - Authorization
12. **Product filtering** - Product catalog access
13. **Account services** - Account information
### Framework Dependencies
- CCB Process Framework
- CCB Service Framework
- CCB UI Framework (Wicket)
- CCB Security
- CCB Context Management
- CCB Logging
---
## Current Application Structure
```
kwk/
+-- ui/          - Web UI (Wicket pages and panels)
¦   +-- KWKOverviewPage.java
¦   +-- KWKConfirmationPage.java
¦   +-- KWKConfirmationSmsPage.java
¦   +-- KWKConfirmationWhatsAppPage.java
¦   +-- JavaScript/React hybrid components
+-- rest/        - REST API endpoints
¦   +-- CrcJsonController.java
+-- public/      - Shared components
    +-- CrcDelegate.java
    +-- CrcDispatcher.java
    +-- DTOs
```
### Backend Layers
```
Process Layer (ccb/process-interface/kwk)
    +-- CustomerReferCustomerProcess
         ?
Process Implementation (ccb/middletier/process/kwk)
    +-- CustomerReferCustomerProcessImpl
         ?
Service Layer (ccb/middletier/service/kwk)
    +-- CustomerReferCustomerServiceImpl
         ?
DAO Layer (ccb/middletier/service/kwk)
    +-- KwkDAOImpl ? Database
```
---
## Target Microservice Architecture
### Backend (Spring Boot)
```
kwk-microservice/
+-- controller/     - REST API endpoints
+-- service/        - Business logic
+-- repository/     - Data access (Spring Data JPA)
+-- domain/         - JPA entities
+-- dto/            - Request/Response objects
+-- mapper/         - Entity ? DTO mapping
+-- client/         - External service clients
+-- security/       - JWT authentication
+-- exception/      - Error handling
```
### Frontend (React)
```
kwk-frontend/
+-- api/            - API client
+-- pages/          - Page components
¦   +-- Overview.tsx
¦   +-- ConfirmationEmail.tsx
¦   +-- ConfirmationSMS.tsx
¦   +-- ConfirmationWhatsApp.tsx
+-- components/     - Reusable components
+-- hooks/          - Custom hooks
+-- types/          - TypeScript types
```
---
## Critical Files to Migrate
### Backend Core Files
1. `CustomerReferCustomerProcessImpl.java` ? Extract to service layer
2. `CustomerReferCustomerServiceImpl.java` ? Reuse/adapt
3. `KwkDAOImpl.java` ? Replace with Spring Data repository
4. `CustomerReferCustomer.java` ? JPA entity (minimal changes)
### Frontend Core Files
1. `KWKOverviewPage.java` ? `Overview.tsx` (React)
2. `KWKConfirmationPage.java` ? `ConfirmationEmail.tsx` (React)
3. `KWKConfirmationSmsPage.java` ? `ConfirmationSMS.tsx` (React)
4. `KWKConfirmationWhatsAppPage.java` ? `ConfirmationWhatsApp.tsx` (React)
### Business Logic to Preserve
1. Referral code generation algorithm (8-character alphanumeric)
2. Account authorization validation
3. Product/reward filtering logic
4. Data validation rules
---
## Next Steps
1. **Review** both analysis and migration plan documents
2. **Approve** the migration approach and timeline
3. **Allocate** team members
4. **Start** with Phase 1: Analysis & Planning
   - Begin with Step 1.1: Dependency Analysis
   - Create `dependency-mapping.md`
5. **Schedule** weekly progress reviews
6. **Set up** project repositories (backend and frontend)
---
## Risk Assessment
### High-Risk Areas
?? **External Service Dependencies** - May change or become unavailable  
?? **Database Migration** - Risk of data loss or corruption  
?? **Security Integration** - Unauthorized access or data breaches  
?? **Performance** - May be slower than monolith initially  
?? **UI Conversion** - Wicket to React conversion complexity
### Mitigation Strategies
? Circuit breakers and fallback mechanisms  
? Dual-write pattern for database migration  
? Thorough security testing and code reviews  
? Performance testing early and often  
? Incremental migration with rollback capability
---
## Success Criteria
### Technical
- ? All functional tests passing
- ? API response time < 500ms (p95)
- ? Code coverage > 80%
- ? Zero critical security vulnerabilities
- ? 99.9% uptime
### Business
- ? Feature parity with legacy system
- ? User acceptance > 90%
- ? Error rate < 1%
- ? Successfully handle peak load
---
**Last Updated:** November 5, 2025  
**Version:** 1.0  
**Status:** Planning Phase
