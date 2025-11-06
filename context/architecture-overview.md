# CCB Portal - High-Level Architecture Overview

## Table of Contents
1. [Project Overview](#project-overview)
2. [Main Architecture Layers](#main-architecture-layers)
3. [Detailed Module Breakdown](#detailed-module-breakdown)
4. [Technology Stack](#technology-stack)
5. [Module Relationships](#module-relationships)

---

## Project Overview

**CCB (Cross-Channel Banking)** is a large-scale enterprise banking monolith built using Maven and Java. The system is organized as a multi-module Maven project with clear separation of concerns across different architectural layers.

**Version:** 48.250.3-SNAPSHOT  
**Build Tool:** Maven (Multi-module project)  
**Primary Language:** Java  
**UI Technologies:** React (modern), Legacy Web UI

---

## Main Architecture Layers

The codebase is organized into **7 major top-level modules**, each serving a distinct architectural purpose:

### 1. **`parents/`** - Build & Dependency Management
- Contains parent POMs that define common build configurations
- Manages dependency versions across all modules
- Contains: `ccb-parent` for standardization

### 2. **`fw/`** - Framework Layer
**Purpose:** Core technical framework components shared across the entire application

**Sub-modules:**
- `mt/` - Middle Tier framework components
- `shared/` - Shared framework utilities and base classes
- `ui/` - UI framework components

**Description:** Provides foundational technical capabilities like base services, process engines, annotations, context management, and logging infrastructure.

### 3. **`ccb/`** - Core Cross-Channel Banking Platform
**Purpose:** The core banking platform infrastructure

**Sub-modules:**
- `shared/` - Shared domain models and utilities
  - `functional-domain/` - Business domain objects
  - `functionality/` - Common business logic
  - `technical-domain/` - Technical infrastructure
  - `servlet-forward/` - Request routing
  - `shared-armouring/` - Security layer
- `process-interface/` - Process orchestration interfaces
- `middletier/` - Middle tier implementation
  - `backend/` - Backend services
  - `composition/` - Service composition layer
  - `coreservice/` - Core business services
  - `process/` - Business process implementations
  - `service/` - Service layer
- `ui/` - Legacy UI modules
  - `approval-webui/`
  - `msb-webui/`
  - `pk-webui/`
  - `wp-webui/`
  - `fil-webui/`
- `batch/` - Batch processing jobs
- `ccbis-is/` - Integration services

**Description:** Core banking platform providing the technical and business infrastructure that all use cases build upon.

### 4. **`sc/`** - Service Clusters (Business Services)
**Purpose:** Reusable business service components organized by domain

**Description:** Contains **60+ service modules**, each representing a specific business domain. These are the building blocks used by use cases.

**Key Service Examples:**
- `customer/` - Customer management services
  - Sub-structure: `api/`, `bom/`, `host/`, `remote/`, `service/`, `soap/`
- `debitcard/` - Debit card services
- `authentication/` - Authentication services
- `authority/` - Authority/authorization services
- `balance/` - Balance inquiry services
- `transaction/` - Transaction services
- `payment/` - Payment processing
- `loan/` - Loan management
- `account/` (various types) - Account management
- `person/` - Person/entity data services
- `product*/` - Product catalog and management
- `creditcard/`, `creditdecision/` - Credit services
- `communication/` - Communication services
- `document/` - Document management
- `knowyourcustomer/` - KYC services
- `legitimation/` - Identity verification
- And many more...

**Typical Service Module Structure:**
```
sc/{domain}/
  ├── api/          - Service interfaces and DTOs
  ├── service/      - Service implementation
  ├── host/         - Host system integration
  ├── remote/       - Remote service clients
  ├── soap/         - SOAP web services
  ├── bom/          - Bill of Materials (dependencies)
  └── pom.xml
```

### 5. **`ucc/`** - Use Case Clusters (Business Applications)
**Purpose:** End-to-end business use cases that compose services into complete user-facing applications

**Description:** Contains **70+ use case modules**. Each use case can be considered as a mini-application within the monolith, orchestrating multiple services to deliver specific business functionality.

**Key Use Case Examples:**
- `accountoverview/` - Account overview functionality
- `accountcardandcreditmanagement/` - Card and credit management
- `approval/` - Approval workflows
- `balance/` - Balance management
- `creditoverview/` - Credit overview
- `creditoffercreation/` - Credit offer creation
- `currentaccountmanagement/` - Current account management
- `customerauthentication/` - Customer authentication flows
- `debitcard/` - Debit card management
- `document/` - Document management UI
- `insurance/` - Insurance products
- `investmentadvice/` - Investment advisory
- `mobilepayment/` - Mobile payment flows
- `partymanagement/` - Party/customer management
- `privatecustomeronboarding/` - Customer onboarding
- `transactionoverview/` - Transaction viewing
- `transactionsearch/` - Transaction search
- And many more...

**Typical Use Case Module Structure:**
```
ucc/{usecase}/
  ├── process/           - Business process orchestration
  │   └── src/main/java/ - Process implementation (Java)
  ├── process-interface/ - Process API definitions
  ├── bom/              - Bill of Materials
  └── pom.xml
```

**Use Case Characteristics:**
- Orchestrates multiple SC (Service Cluster) services
- Implements business workflows and processes
- Contains process logic annotated with `@CCBProcess`, `@CCBProcessStep`
- Provides the end-to-end user experience for specific banking operations

### 6. **`sb/`** - Shared Business Components
**Purpose:** Cross-cutting business components used by multiple use cases

**Sub-modules:**
- `dc/` - Domain components
- `fragmentorchestration/` - UI fragment orchestration

**Description:** Provides shared business logic and domain objects that don't fit into specific services but are needed across multiple use cases.

### 7. **`ui-react/`** - Modern React UI
**Purpose:** Modern React-based user interface

**Structure:**
- `src/main/webapp/WEB-INF/resources/media/react/` - React components
- Contains React components, parent components, utilities
- LESS stylesheets compiled to CSS
- Modern front-end architecture replacing legacy UIs

### 8. **`layout-react/`** - React Layout Framework
**Purpose:** Layout and theming infrastructure for React UI

**Contains:**
- `src/` - Layout components and themes
- `fe-tests/` - Frontend tests

### 9. **`runtime-artifacts/`** - Runtime Resources
**Purpose:** Runtime configuration and resources

**Sub-modules:**
- `ui/` - UI runtime artifacts

### 10. **`builds/runtimes/`** - Deployment Artifacts
**Purpose:** Build outputs and deployable artifacts

**Contains:**
- `webui-war/` - Web UI WAR package
- `middletier-war/` - Middle tier WAR package

---

## Detailed Module Breakdown

### Framework Layer (`fw/`)

The framework provides:
- **Base classes** for services and processes
- **Process engine** annotations and runtime
- **Context management** (user context, technical context, channel context)
- **Logging infrastructure** (`CcbLogger`)
- **Exception handling** (`CCBTechnicalException`, `CCBBusinessException`)
- **Annotations** (`@CCBService`, `@CCBProcess`, `@CCBTransactionalProcess`)
- **Hystrix integration** for resilience (`@CcbHystrix`)
- **Async processing** support (`CcbFuture`, `CcbAsyncResult`)

### Service Clusters (`sc/`)

**Purpose:** Domain-driven business services

**Design Pattern:** Each service cluster follows a consistent structure:
- **API module** - Interfaces, request/response DTOs, domain objects
- **Service module** - Business logic implementation extending `BaseService`
- **Host module** - Integration with legacy host systems
- **Remote module** - Remote service adapters
- **SOAP module** - SOAP web service endpoints

**Example Service Flow:**
```
Use Case (UCC) → SC API → SC Service → SC Host → Legacy System
```

Services are:
- Annotated with `@CCBService`
- Protected with `@CcbHystrix` for fault tolerance
- Designed to be reusable across multiple use cases
- Focused on single business domains (customer, account, card, etc.)

### Use Case Clusters (`ucc/`)

**Purpose:** Complete business workflows

**Design Pattern:** Use cases orchestrate multiple services:
- **Process module** - Main business process orchestration
  - Implements multi-step processes using `BaseMultistepProcess`
  - Annotated with `@CCBProcess`, `@ProcessDefinition`
  - Uses `@CCBProcessStep`, `@CCBInitProcessStep` for workflow steps
- **Process-Interface module** - Process contracts and DTOs

**Example Use Case Flow:**
```
User Request → UCC Process → Multiple SC Services → Response
```

Use cases typically:
1. Receive user input
2. Validate and transform data
3. Call multiple SC services to retrieve/update data
4. Orchestrate workflow steps
5. Return consolidated response
6. Handle errors and business rules

---

## Technology Stack

### Backend
- **Java** (Enterprise Java)
- **Maven** (Build & Dependency Management)
- **Spring Framework** (Dependency Injection via `@Inject`, `@Named`)
- **Hystrix** (Circuit breaker for resilience)
- **SOAP** Web Services (Legacy integration)
- **REST** APIs (Modern integration)

### Frontend
- **React** (Modern UI)
- **LESS** (Stylesheets, compiled to CSS)
- **Legacy Web UI** (JSP/Servlets)

### Integration
- **Host Systems** (Legacy mainframe integration)
- **SOAP** Services
- **REST** Services

### Architecture Patterns
- **Multi-tier architecture** (UI → Middle Tier → Services → Host)
- **Service-Oriented Architecture (SOA)**
- **Process Orchestration** (BPM-style workflows)
- **Domain-Driven Design** (Service clusters organized by domain)
- **Microservices-within-monolith** (Use cases as bounded contexts)

---

## Module Relationships

### Dependency Flow (Bottom-Up)

**Backend Dependencies:**
```
┌─────────────────────────────────────────┐
│  Use Case Clusters (UCC)                │  ← End-user applications
│  - accountoverview                       │
│  - creditmanagement                      │
│  - mobilepayment                         │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│  Service Clusters (SC)                   │  ← Business services
│  - customer, account, card               │
│  - authentication, authorization         │
│  - transaction, payment                  │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│  Shared Business (SB)                    │  ← Cross-cutting business
│  - dc, fragmentorchestration             │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│  Core Platform (CCB)                     │  ← Core infrastructure
│  - middletier, shared, ui                │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│  Framework (FW)                          │  ← Technical foundation
│  - mt, shared, ui                        │
└──────────────────────────────────────────┘
```

**Frontend Dependencies:**
```
┌─────────────────────────────────────────────────────────────┐
│  UI-React (React Components Library)                        │  ← Shared React UI
│  - parent_comp/kwk-page.js                                  │     Components
│  - parent_comp/depot-page.js                                │
│  - child_comp/* (reusable components)                       │
│  - shared_comp/* (utilities)                                │
│  Build Output: lib_[name]-bundle.js                         │
└──────────────┬──────────────────────────────────────────────┘
               │ consumed by (via bundles)
               │
┌──────────────▼──────────────────────────────────────────────┐
│  CCB UI Modules (pk-webui, msb-webui, etc.)                 │  ← UI Page
│  Example: ccb/ui/pk-webui/kwk/                              │     Containers
│  - ui/ (Java Pages: KWKOverviewPage.java)                   │
│  - rest/ (REST Controllers: CrcJsonController.java)         │
│  - Serves React bundles + provides backend                  │
└──────────────┬──────────────────────────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────────────────────────┐
│  UCC Process Layer                                          │  ← Business Logic
│  - Handles business workflows                               │
│  - Called by REST controllers from UI modules               │
└─────────────────────────────────────────────────────────────┘
```

**Complete Full-Stack Flow:**
```
Browser
    ↓
┌───────────────────────────────────────────┐
│ Static HTML Page                          │ (e.g., KWKOverviewPage.java)
│ <div id="kwkReactContainer"></div>        │
│ <script src="lib_kwk-page-bundle.js">     │
└───────────────┬───────────────────────────┘
                │ loads React bundle from ui-react
┌───────────────▼───────────────────────────┐
│ UI-React Bundle (lib_kwk-page-bundle.js)  │ (built from ui-react/parent_comp/)
│ - Renders React components                │
│ - Makes REST API calls                    │
└───────────────┬───────────────────────────┘
                │ REST API calls
┌───────────────▼───────────────────────────┐
│ CCB UI REST Controllers                   │ (e.g., kwk/rest/CrcJsonController.java)
│ @RequestMapping("/api/kwk")                │
└───────────────┬───────────────────────────┘
                │ calls
┌───────────────▼───────────────────────────┐
│ UCC Process Layer                         │ (Business orchestration)
└───────────────┬───────────────────────────┘
                │ uses
┌───────────────▼───────────────────────────┐
│ SC Service Layer                          │ (Domain services)
└───────────────────────────────────────────┘
```

### Module Communication Pattern

**Typical Request Flow:**
```
Browser/Mobile App
    ↓
[1] HTML Page served by CCB UI Module
    (e.g., ccb/ui/pk-webui/kwk/ui → KWKOverviewPage.java)
    Includes: <script src="lib_kwk-page-bundle.js">
    ↓
[2] React Bundle from ui-react (loaded in browser)
    (Built from: ui-react/parent_comp/kwk-page.js)
    Renders: React components (kwkpanel.js, etc.)
    ↓
[3] REST API Call (from React component)
    Calls: /api/kwk/* endpoints
    ↓
[4] CCB UI REST Controller
    (e.g., kwk/rest/CrcJsonController.java)
    ↓
[5] UCC Process (Business Orchestration)
    Process annotations: @CCBProcess
    ↓
[6] SC Services (Domain Services)
    Service annotations: @CCBService
    ↓
[7] SC Host Adapters (Legacy Integration)
    ↓
[8] Host Systems (Mainframe/Core Banking)
```

**Key Insight:**
- **ui-react** is a **shared React component library**, NOT a use case layer
- It provides **reusable React UI components** consumed by multiple CCB UI modules
- Each UI module (like `kwk/ui`) is a Java-based page container that:
  1. Serves an HTML page (Java class extending `BasePage`)
  2. Loads React bundles built from `ui-react`
  3. Provides REST endpoints for React components to call
  4. Integrates with UCC/SC backend layers

### Key Design Principles

1. **Separation of Concerns**
   - Framework (FW) = Technical infrastructure
   - Core (CCB) = Platform capabilities
   - Services (SC) = Reusable business logic
   - Use Cases (UCC) = Application-specific workflows

2. **Reusability**
   - SC services are shared across multiple UCC use cases
   - Common functionality in SB (Shared Business)
   - Technical capabilities in FW (Framework)

3. **Modularity**
   - Each use case is relatively independent
   - Services are domain-focused and loosely coupled
   - Clear APIs and contracts between layers

4. **Scalability Considerations**
   - Each UCC can theoretically be extracted as a microservice
   - Services (SC) already have well-defined APIs
   - Process orchestration is encapsulated in UCC modules

---

## Summary

The CCB Portal is a well-structured banking monolith with:

- **~70 Use Cases** (UCC) - Each representing a complete business application
- **~60 Service Clusters** (SC) - Reusable domain services
- **Layered Architecture** - Clear separation between framework, platform, services, and applications
- **Modern & Legacy UI** - React-based modern UI alongside legacy web components
- **Enterprise Patterns** - Service orchestration, circuit breakers, multi-step processes
- **Maven Multi-Module** - Organized build with dependency management

**Key Insight:** While this is a monolith, it's organized internally like microservices - each UCC (use case) is a bounded context that could potentially be extracted into its own service. The SC (service clusters) already provide well-defined service boundaries with clear APIs.

This architecture suggests a path toward **modular monolith** or eventual **microservices migration**, as the domain boundaries are already well-established.

