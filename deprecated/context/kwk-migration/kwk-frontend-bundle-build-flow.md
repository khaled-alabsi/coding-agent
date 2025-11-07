# KWK Frontend Bundle Build Flow

**Date:** November 6, 2025  
**Purpose:** Complete explanation of how the KWK frontend bundle is created, from source files to final output

---

## Quick Reference: Complete KWK Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     KWK COMPLETE STACK                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: FRONTEND SOURCE (ui-react)                             │
│ Location: ui-react/src/.../media/react/parent_comp/kwk/         │
│ Files: kwkpanel.js, kwkselection.js, confpanel.js, etc.        │
│ Dependencies: child_comp/* (24+ shared React components)        │
│ Build: Maven → NPM → Webpack → Babel                            │
│ Output: lib_kwk-page-bundle.js (~500KB)                         │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (bundle consumed by)
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 2: CCB UI MODULE (ccb/ui/pk-webui/kwk)                   │
│ ├── ui/      → KWKOverviewPage.java (Wicket page)              │
│ │              - Serves HTML with React container               │
│ │              - Loads lib_kwk-page-bundle.js                   │
│ │              - Provides data via getDataForReact()            │
│ │              Depends on: ui-shared-*, react-base, ui-react    │
│ │                                                               │
│ ├── rest/    → CrcJsonController.java (Spring REST)            │
│ │              - Endpoint: POST /banking/rest/sendReference     │
│ │              - Called by React components                     │
│ │              Depends on: process-interface-kwk                │
│ │                                                               │
│ └── public/  → CrcDispatcher.java (Shared utilities)           │
│                Depends on: process-interface-kwk                │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (calls via @Inject)
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 3: PROCESS INTERFACE (ccb/process-interface/kwk)         │
│ File: CustomerReferCustomerProcess.java (interface)             │
│ DTOs: SendReferenceRequest, SendReferenceResponse              │
│ Purpose: Contract between UI and Process layers                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (implemented by)
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 4: PROCESS IMPLEMENTATION (ccb/middletier/process/kwk)   │
│ File: CustomerReferCustomerProcessImpl.java                     │
│ Responsibilities:                                               │
│ - Generate unique referral code                                 │
│ - Validate IBAN authorization                                   │
│ - Orchestrate SC service calls                                  │
│ - Juridical logging                                             │
│ Depends on: 6+ SC services (Participant, Person, Product, etc.) │
│ NOTE: In ccb/middletier NOT ucc/ (legacy architecture)         │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (calls)
┌──────────────────────▼──────────────────────────────────────────┐
│ LAYER 5: SERVICE CLUSTER (sc/*)                                │
│ Services used:                                                  │
│ - ParticipantService (customer data)                            │
│ - NaturalPersonAPIV3Service (customer name)                     │
│ - ProductService (account authorization)                        │
│ - CustomerReferCustomerService (persist CRC data)               │
│ - IbanConverterService, CCBNumberResolverService, etc.          │
│ These access: Database, Host Systems                            │
└─────────────────────────────────────────────────────────────────┘

KEY POINTS:
✓ Frontend built in ui-react, consumed by ccb/ui/pk-webui/kwk
✓ NO UCC module - KWK uses legacy ccb/middletier structure
✓ CCB UI Module bridges frontend and backend
✓ Process layer depends on 6+ SC services
✓ ~52 total files minimum for extraction
```

---

## Overview

This document explains the complete build process for the KWK (Kunden Werben Kunden) frontend React bundle, showing:
- **Source file locations** and structure
- **Build process flow** (Maven → NPM → Webpack)
- **Dependency tree** (what imports what)
- **CCB UI Module integration** (how frontend connects to backend)
- **Complete architecture** (frontend to database)
- **Final output** location and usage

---

## Visual File Structure with Dependencies

```
C:\CCB\sources\portal\

├── ui-react\                                    ← FRONTEND SOURCE
│   ├── pom.xml                                  (Maven: runs npm run all-prod)
│   └── src\main\webapp\WEB-INF\resources\media\
│       ├── react\
│       │   ├── package.json                     (NPM: build scripts)
│       │   ├── webpack.config.js                (Webpack: bundler config)
│       │   │
│       │   ├── parent_comp\                     ← ENTRY POINTS
│       │   │   ├── kwk-page.js                  ──→ imports kwkpanel.js
│       │   │   ├── kwkconfirmation-page.js      ──→ imports confpanel.js
│       │   │   ├── qrkwkconfirmation-page.js    ──→ imports qrconfpanel.js
│       │   │   │
│       │   │   └── kwk\                         ← KWK COMPONENTS
│       │   │       ├── kwkpanel.js              ──→ imports 11 child components
│       │   │       ├── kwkselection.js          ──→ imports 4 child components
│       │   │       ├── confpanel.js             ──→ imports 5 child components
│       │   │       ├── qrconfpanel.js           ──→ imports QRCode library
│       │   │       └── kwkemailpanel.js         ──→ imports 2 child components
│       │   │
│       │   ├── child_comp\                      ← SHARED COMPONENTS
│       │   │   ├── buttons\
│       │   │   │   ├── button.js                ──→ used by kwkpanel.js
│       │   │   │   ├── whatsappbutton.js        ──→ used by kwkpanel.js
│       │   │   │   └── mailtobutton.js          ──→ used by confpanel.js
│       │   │   ├── dropdown\
│       │   │   │   ├── singledropdown.js        ──→ used by kwkselection.js
│       │   │   │   └── multidropdown.js         ──→ used by kwkselection.js
│       │   │   ├── inputs\
│       │   │   │   └── emailinputfield.js       ──→ used by kwkselection.js
│       │   │   ├── text\
│       │   │   │   ├── pageheading.js           ──→ used by kwkpanel.js
│       │   │   │   └── labeltext.js             ──→ used by kwkselection.js
│       │   │   ├── utils\
│       │   │   │   ├── webapi.js                ──→ used by kwkpanel.js (AJAX)
│       │   │   │   ├── loadingindicator.js      ──→ used by kwkpanel.js
│       │   │   │   ├── urlqueryreader.js        ──→ used by kwkpanel.js
│       │   │   │   └── pageredirection.js       ──→ used by kwkpanel.js
│       │   │   └── validators\
│       │   │       └── emailvalidator.js        ──→ used by emailinputfield.js
│       │   │
│       │   ├── adapters\                        ← LIBRARY ADAPTERS
│       │   │   ├── react.js                     (exports window.React)
│       │   │   └── jquery.js                    (exports window.$)
│       │   │
│       │   └── pack\                            ← THIRD-PARTY LIBS
│       │       └── qrcode (NPM package)
│       │
│       └── system\js\                           ← BUILD OUTPUT
│           ├── lib_kwk-page-bundle.js           ★ FINAL BUNDLE ★
│           ├── lib_kwkconfirmation-page-bundle.js
│           └── lib_qrkwkconfirmation-page-bundle.js
│
├── ccb\                                         ← BACKEND
│   ├── ui\pk-webui\kwk\                         ← CCB UI MODULE
│   │   ├── pom.xml                              (aggregates ui/rest/public)
│   │   │
│   │   ├── ui\                                  ← JAVA UI PAGES
│   │   │   ├── pom.xml                          depends on: ui-react (bundle)
│   │   │   └── src\main\java\...\kwk\
│   │   │       ├── KWKOverviewPage.java         ──→ loads lib_kwk-page-bundle.js
│   │   │       │                                ──→ injects @SpringBean CrcDispatcher
│   │   │       │                                ──→ implements ReactPage interface
│   │   │       ├── KWKOverviewPageModel.java
│   │   │       ├── confirmationpage\
│   │   │       └── container\
│   │   │
│   │   ├── rest\                                ← REST API
│   │   │   ├── pom.xml                          depends on: process-interface-kwk
│   │   │   └── src\main\java\...\rest\delegate\
│   │   │       └── CrcJsonController.java       ──→ @Inject CustomerReferCustomerProcess
│   │   │                                        ──→ endpoint: POST /sendReference
│   │   │                                        ──→ called by kwkpanel.js (AJAX)
│   │   │
│   │   └── public\                              ← SHARED CODE
│   │       └── src\main\java\...\kwk\
│   │           ├── delegate\KwkDispatcher.java
│   │           └── transfer\CrcDispatcher.java  ──→ used by KWKOverviewPage.java
│   │
│   ├── process-interface\kwk\                   ← PROCESS CONTRACT
│   │   └── src\main\java\...\processinterface\
│   │       ├── CustomerReferCustomerProcess.java (interface)
│   │       ├── request\SendReferenceRequest.java
│   │       └── response\SendReferenceResponse.java
│   │
│   └── middletier\process\kwk\                  ← PROCESS IMPLEMENTATION
│       └── src\main\java\...\process\
│           └── CustomerReferCustomerProcessImpl.java
│                                                ──→ implements CustomerReferCustomerProcess
│                                                ──→ @Inject ParticipantService (SC)
│                                                ──→ @Inject NaturalPersonAPIV3Service (SC)
│                                                ──→ @Inject ProductService (SC)
│                                                ──→ @Inject CustomerReferCustomerService (SC)
│                                                ──→ @Inject 5+ more SC services
│
└── sc\                                          ← SERVICE CLUSTER
    ├── participant\api\service\
    │   └── ParticipantService.java              ──→ used by Process layer
    ├── person\api\service\
    │   └── NaturalPersonAPIV3Service.java       ──→ used by Process layer
    ├── sharedbusiness\api\service\
    │   ├── ProductService.java                  ──→ used by Process layer
    │   ├── IbanConverterService.java            ──→ used by Process layer
    │   └── [more services...]
    └── [kwk-module]\service\
        └── CustomerReferCustomerService.java    ──→ used by Process layer
                                                 ──→ persists to database

LEGEND:
──→  = "depends on" or "calls" or "imports"
★   = final build output
← = layer/folder description
```

---

## Build Process Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. MAVEN BUILD TRIGGER                                          │
│    Command: mvn clean install                                   │
│    File: ui-react/pom.xml                                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. MAVEN EXEC PLUGIN RUNS NPM                                   │
│    Phase: process-sources                                       │
│    Command: npm run all-prod                                    │
│    Working Dir: src/main/webapp/WEB-INF/resources/media/react/  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. NPM INSTALLS DEPENDENCIES                                    │
│    Command: npm install --production                            │
│    File: package.json                                           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. WEBPACK BUNDLES REACT CODE                                   │
│    Command: npm run bundle-dev                                  │
│    Config: webpack.config.js                                    │
│    Entry: parent_comp/kwk-page.js                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. BABEL TRANSPILES ES6 TO ES5                                  │
│    Loader: babel-loader                                         │
│    Processes all .js files (except node_modules, pack, adapters)│
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. WEBPACK RESOLVES DEPENDENCIES                                │
│    - Resolves 'ccb/*' → child_comp/*                            │
│    - Resolves 'parent/*' → parent_comp/*                        │
│    - Resolves 'react' → adapters/react.js → window.React       │
│    - Bundles all imports into single file                       │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. OUTPUT BUNDLE CREATED                                        │
│    Output: ../system/js/lib_kwk-page-bundle.js                  │
│    Size: ~500KB (minified in production builds)                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. BUNDLE PACKAGED IN JAR/WAR                                   │
│    Maven packages bundle into deployable artifact               │
│    Deployed to application server                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Frontend to Backend Integration

### Complete Dependency Chain

The KWK frontend bundle doesn't exist in isolation - it's part of a multi-layer architecture:

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: FRONTEND BUNDLE (ui-react)                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Location: ui-react/src/main/webapp/WEB-INF/resources/media/   │
│            react/parent_comp/kwk/                               │
│                                                                 │
│  Files:                                                         │
│  - kwkpanel.js (React component)                                │
│  - kwkselection.js                                              │
│  - confpanel.js                                                 │
│                                                                 │
│  Build Output:                                                  │
│  - lib_kwk-page-bundle.js                                       │
│                                                                 │
│  Dependencies:                                                  │
│  - child_comp/* (shared React components)                       │
│  - window.React, window.$                                       │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (bundled and served by)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: CCB UI MODULE (ccb/ui/pk-webui/kwk)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Location: ccb/ui/pk-webui/kwk/                                 │
│                                                                 │
│  Structure:                                                     │
│  ├── pom.xml                    (Maven module definition)       │
│  ├── ui/                        (Java UI layer)                 │
│  │   ├── pom.xml                                                │
│  │   └── src/main/java/                                         │
│  │       └── com/commerzbank/ccb/kwk/                           │
│  │           ├── KWKOverviewPage.java       ← Serves HTML page  │
│  │           ├── KWKOverviewPageModel.java  ← Page model        │
│  │           ├── confirmationpage/                              │
│  │           └── container/                                     │
│  │                                                               │
│  ├── rest/                      (REST API layer)                │
│  │   ├── pom.xml                                                │
│  │   └── src/main/java/                                         │
│  │       └── com/commerzbank/ccb/crc/rest/delegate/             │
│  │           └── CrcJsonController.java     ← REST endpoint     │
│  │                                                               │
│  └── public/                    (Public resources)              │
│      └── pom.xml                                                │
│                                                                 │
│  What it does:                                                  │
│  1. Serves HTML page with React container div                   │
│  2. Loads React bundle (lib_kwk-page-bundle.js)                 │
│  3. Provides initial data (getDataForReact())                   │
│  4. Exposes REST endpoints (/banking/rest/sendReference)        │
│                                                                 │
│  Dependencies:                                                  │
│  - ui-react (frontend bundle) ← CONSUMES                        │
│  - ccb/process-interface/kwk (process interface)                │
│  - ccb/ui/shared (shared UI utilities)                          │
│  - fw/ui/api (framework UI API)                                 │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (calls via Spring injection)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: PROCESS INTERFACE (ccb/process-interface/kwk)         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Location: ccb/process-interface/kwk/                           │
│            src/main/java/com/commerzbank/ccb/kwk/               │
│            processinterface/                                    │
│                                                                 │
│  Files:                                                         │
│  - CustomerReferCustomerProcess.java (interface)                │
│  - request/SendReferenceRequest.java                            │
│  - response/SendReferenceResponse.java                          │
│                                                                 │
│  Purpose:                                                       │
│  - Defines process contract (interface)                         │
│  - Request/Response DTOs                                        │
│  - No implementation (just API definition)                      │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (implemented by)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: PROCESS IMPLEMENTATION (ccb/middletier/process/kwk)   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Location: ccb/middletier/process/kwk/                          │
│            src/main/java/com/commerzbank/ccb/kwk/process/       │
│                                                                 │
│  Files:                                                         │
│  - CustomerReferCustomerProcessImpl.java                        │
│    (implements CustomerReferCustomerProcess)                    │
│                                                                 │
│  What it does:                                                  │
│  - Business logic orchestration                                 │
│  - Generate referral code                                       │
│  - Authorization checks                                         │
│  - Call SC services                                             │
│  - Juridical logging                                            │
│                                                                 │
│  Dependencies:                                                  │
│  - sc/participant (ParticipantService)                          │
│  - sc/person (NaturalPersonAPIV3Service)                        │
│  - sc/sharedbusiness (ProductService, IbanConverter, etc.)      │
│  - sc/[kwk-service] (CustomerReferCustomerService)             │
│                                                                 │
│  Annotations:                                                   │
│  - @CCBProcess                                                  │
│  - @CCBTransactionalProcess                                    │
│  - @PreAuthorize("protect('REWARDCREDIT')")                    │
│                                                                 │
└──────────────────────┬──────────────────────────────────────────┘
                       │ (calls SC services)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 5: SERVICE CLUSTER (sc/*) - Domain Services              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Multiple SC modules used:                                      │
│                                                                 │
│  1. sc/participant/api/service/ParticipantService               │
│     - Retrieves customer participant data                       │
│                                                                 │
│  2. sc/person/api/service/NaturalPersonAPIV3Service             │
│     - Gets customer first/last name                             │
│                                                                 │
│  3. sc/sharedbusiness/api/service/ProductService                │
│     - Validates authorized accounts                             │
│                                                                 │
│  4. sc/sharedbusiness/api/service/IbanConverterService          │
│     - Converts account numbers to IBAN                          │
│                                                                 │
│  5. sc/[kwk-module]/service/CustomerReferCustomerService        │
│     - Persists CRC data to database                             │
│     - Retrieves existing referral codes                         │
│                                                                 │
│  Note: No UCC module for KWK - Process lives in ccb/middletier │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Insight: KWK Has NO UCC Module

**Important:** Unlike most use cases, KWK does **NOT** have a dedicated module in `ucc/`. Instead:

- **Process Implementation** lives in: `ccb/middletier/process/kwk/`
- **Process Interface** lives in: `ccb/process-interface/kwk/`
- **UI Module** lives in: `ccb/ui/pk-webui/kwk/`

This is because KWK is a **legacy module** that predates the UCC architecture pattern. It follows the older CCB structure.

---

## Source File Locations

### Complete Directory Structure

```
C:\CCB\sources\portal\ui-react\
├── pom.xml                                    ← Maven build configuration
└── src\main\webapp\WEB-INF\resources\media\
    ├── react\                                 ← SOURCE CODE LOCATION
    │   ├── package.json                       ← NPM dependencies & scripts
    │   ├── webpack.config.js                  ← Webpack bundler config
    │   ├── webpack.minified.config.js         ← Production minified build
    │   ├── webpack.production.config.js       ← Production build
    │   │
    │   ├── parent_comp\                       ← ENTRY POINT COMPONENTS
    │   │   ├── kwk-page.js                    ← KWK main page entry (STARTS HERE)
    │   │   ├── kwkconfirmation-page.js        ← Confirmation page entry
    │   │   ├── qrkwkconfirmation-page.js      ← QR confirmation page entry
    │   │   │
    │   │   └── kwk\                           ← KWK-SPECIFIC COMPONENTS
    │   │       ├── kwkpanel.js                ← Main KWK panel (CORE COMPONENT)
    │   │       ├── kwkselection.js            ← Product/reward/account selection
    │   │       ├── confpanel.js               ← Email confirmation panel
    │   │       ├── qrconfpanel.js             ← QR code confirmation panel
    │   │       └── kwkemailpanel.js           ← Email input panel
    │   │
    │   ├── child_comp\                        ← SHARED REUSABLE COMPONENTS
    │   │   ├── buttons\
    │   │   │   ├── button.js                  ← Generic button component
    │   │   │   ├── activebutton.js            ← Clickable button
    │   │   │   ├── staticbutton.js            ← Link button
    │   │   │   ├── whatsappbutton.js          ← WhatsApp share button
    │   │   │   └── mailtobutton.js            ← Email button
    │   │   │
    │   │   ├── dropdown\
    │   │   │   ├── singledropdown.js          ← Single selection dropdown
    │   │   │   └── multidropdown.js           ← Multi-line dropdown
    │   │   │
    │   │   ├── inputs\
    │   │   │   ├── emailinputfield.js         ← Email input with validation
    │   │   │   └── decoratedinputfield.js     ← Styled input field
    │   │   │
    │   │   ├── text\
    │   │   │   ├── pageheading.js             ← Page title component
    │   │   │   ├── labeltext.js               ← Label text
    │   │   │   └── labelhtmltext.js           ← HTML label text
    │   │   │
    │   │   ├── utils\
    │   │   │   ├── webapi.js                  ← REST API wrapper (AJAX calls)
    │   │   │   ├── loadingindicator.js        ← Loading spinner
    │   │   │   ├── urlqueryreader.js          ← URL parameter parser
    │   │   │   └── pageredirection.js         ← Page redirect utility
    │   │   │
    │   │   ├── validators\
    │   │   │   └── emailvalidator.js          ← Email validation
    │   │   │
    │   │   └── includes\
    │   │       ├── contentinclude.js          ← CMS content include
    │   │       └── contentincludeold.js       ← Legacy content include
    │   │
    │   ├── shared_comp\                       ← SHARED UTILITIES
    │   │   ├── utils\
    │   │   ├── order_components\
    │   │   └── modernComponents\
    │   │
    │   ├── adapters\                          ← LIBRARY ADAPTERS
    │   │   ├── react.js                       ← React adapter (exports window.React)
    │   │   └── jquery.js                      ← jQuery adapter (exports window.$)
    │   │
    │   └── pack\                              ← THIRD-PARTY LIBRARIES
    │       ├── react-with-addons.js           ← React library
    │       ├── reactrouter@1.0.0.js           ← React Router v1
    │       ├── reactrouter@2.4.0.js           ← React Router v2
    │       ├── jquery.mCustomScrollbar.js     ← Custom scrollbar
    │       ├── jquery.mousewheel-3.0.6.js     ← Mouse wheel support
    │       ├── d3.min.js                      ← D3.js for charts
    │       ├── progressbar.min.js             ← Progress bar
    │       └── order-chart-d3.js              ← Chart component
    │
    └── system\                                ← BUILD OUTPUT LOCATION
        └── js\
            ├── lib_kwk-page-bundle.js         ← FINAL BUNDLE (OUTPUT)
            ├── lib_kwkconfirmation-page-bundle.js
            └── lib_qrkwkconfirmation-page-bundle.js
```

---

## KWK Dependency Tree

### Complete Import Chain

```
lib_kwk-page-bundle.js                 ← FINAL OUTPUT
    │
    └── parent_comp/kwk-page.js        ← ENTRY POINT
            │
            ├── react                  → adapters/react.js → window.React
            │
            └── parent/kwk/kwkpanel    → parent_comp/kwk/kwkpanel.js
                    │
                    ├── react
                    │
                    ├── ccb/utils/webapi               → child_comp/utils/webapi.js
                    │       └── jquery                 → adapters/jquery.js → window.$
                    │
                    ├── ccb/buttons/button             → child_comp/buttons/button.js
                    │       ├── ccb/buttons/activebutton    → child_comp/buttons/activebutton.js
                    │       └── ccb/buttons/staticbutton    → child_comp/buttons/staticbutton.js
                    │
                    ├── ccb/includes/contentincludeold → child_comp/includes/contentincludeold.js
                    │
                    ├── parent/kwk/kwkselection        → parent_comp/kwk/kwkselection.js
                    │       ├── ccb/dropdown/singledropdown → child_comp/dropdown/singledropdown.js
                    │       ├── ccb/dropdown/multidropdown  → child_comp/dropdown/multidropdown.js
                    │       ├── ccb/text/labeltext          → child_comp/text/labeltext.js
                    │       └── ccb/inputs/emailinputfield  → child_comp/inputs/emailinputfield.js
                    │               └── ccb/validators/emailvalidator → child_comp/validators/emailvalidator.js
                    │
                    ├── ccb/text/pageheading           → child_comp/text/pageheading.js
                    │
                    ├── ccb/utils/loadingindicator     → child_comp/utils/loadingindicator.js
                    │
                    ├── ccb/utils/urlqueryreader       → child_comp/utils/urlqueryreader.js
                    │
                    ├── ccb/utils/pageredirection      → child_comp/utils/pageredirection.js
                    │
                    └── ccb/buttons/whatsappbutton     → child_comp/buttons/whatsappbutton.js
```

---

## Build Configuration Files

### 1. Maven POM (ui-react/pom.xml)

**File:** `C:\CCB\sources\portal\ui-react\pom.xml`

**Key Section:**
```xml
<plugin>
    <groupId>org.codehaus.mojo</groupId>
    <artifactId>exec-maven-plugin</artifactId>
    <configuration>
        <skip>${skipReact}</skip>
    </configuration>
    <executions>
        <execution>
            <id>build-dev-bundle</id>
            <phase>process-sources</phase>
            <goals>
                <goal>exec</goal>
            </goals>
            <configuration>
                <executable>npm</executable>
                <arguments>
                    <argument>run</argument>
                    <argument>all-prod</argument>
                </arguments>
                <workingDirectory>src/main/webapp/WEB-INF/resources/media/react/</workingDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```

**What it does:**
- **Phase:** `process-sources` - Runs during Maven build
- **Command:** `npm run all-prod`
- **Working Directory:** `src/main/webapp/WEB-INF/resources/media/react/`
- **Skip Option:** Can be skipped with `-DskipReact=true`

---

### 2. NPM Package.json

**File:** `C:\CCB\sources\portal\ui-react\src\main\webapp\WEB-INF\resources\media\react\package.json`

**Build Scripts:**
```json
{
  "scripts": {
    "all": "npm install && npm run bundle-dev && npm run bundle-minify && npm run bundle-test",
    "all-prod": "npm install --production && npm run bundle-dev && npm run bundle-minify && npm run bundle-test",
    "bundle-dev": "node node_modules/webpack/bin/webpack.js",
    "bundle-minify": "node node_modules/webpack/bin/webpack.js --config webpack.minified.config.js",
    "bundle-prod": "node node_modules/webpack/bin/webpack.js --config webpack.production.config.js",
    "bundle-test": "node node_modules/webpack/bin/webpack.js --config webpack.test.config.js"
  },
  "dependencies": {
    "async": "^1.4.2",
    "babel-loader": "5.2.1",
    "webpack": "2.2.1",
    "qrcode": "^1.4.4",
    "react-docgen": "^2.0.0",
    // ... more dependencies
  },
  "devDependencies": {
    "eslint": "^1.9.0",
    "webpack-dev-server": "2.2.1",
    // ... more dev dependencies
  }
}
```

**Script Breakdown:**
1. **`all-prod`** - Full production build (called by Maven)
   - `npm install --production` - Install dependencies
   - `npm run bundle-dev` - Create development bundles
   - `npm run bundle-minify` - Create minified bundles
   - `npm run bundle-test` - Create test bundles

2. **`bundle-dev`** - Development bundle creation
   - Uses default `webpack.config.js`
   - No minification
   - Includes source maps for debugging

3. **`bundle-minify`** - Production minified bundle
   - Uses `webpack.minified.config.js`
   - Minified and optimized
   - Smaller file size

---

### 3. Webpack Configuration

**File:** `C:\CCB\sources\portal\ui-react\src\main\webapp\WEB-INF\resources\media\react\webpack.config.js`

**Complete Configuration:**
```javascript
const path = require('path');
const fs = require('fs');

// 1. ENTRY POINT DISCOVERY
// Scans parent_comp directory for all .js files
const entryDir = path.resolve(__dirname, './parent_comp');
const entries = fs.readdirSync(entryDir);
let entryMap = {};
let outputName = 'lib_[name]-bundle.js';

// Build entry map: { 'kwk-page': './parent_comp/kwk-page' }
entries.forEach(function(entry) {
  const stat = fs.statSync(entryDir + '/' + entry);
  if (stat && !stat.isDirectory()) {
    const name = entry.substr(0, entry.length - 3);  // Remove .js extension
    entryMap[name] = entryDir + '/' + path.basename(entry, '.js');
  }
});

module.exports = {
  // 2. ENTRY POINTS
  // All files in parent_comp/ become entry points
  entry: entryMap,
  // Example for KWK:
  // entry: {
  //   'kwk-page': './parent_comp/kwk-page',
  //   'kwkconfirmation-page': './parent_comp/kwkconfirmation-page',
  //   'qrkwkconfirmation-page': './parent_comp/qrkwkconfirmation-page'
  // }

  // 3. OUTPUT CONFIGURATION
  output: {
    path: '../system/js',               // Output directory (relative to webpack working dir)
    filename: outputName,                // Output filename pattern: lib_[name]-bundle.js
    publicPath: '/portal/media/react',  // Public path for loading resources
  },
  // Result for KWK:
  // - lib_kwk-page-bundle.js
  // - lib_kwkconfirmation-page-bundle.js
  // - lib_qrkwkconfirmation-page-bundle.js

  // 4. MODULE RESOLUTION
  resolve: {
    // Path aliases for cleaner imports
    alias: {
      ccb: path.resolve('child_comp'),              // 'ccb/*' → 'child_comp/*'
      ccb_shared: path.resolve('shared_comp'),      // 'ccb_shared/*' → 'shared_comp/*'
      parent: path.resolve('parent_comp'),          // 'parent/*' → 'parent_comp/*'
      pack: path.resolve('pack'),                   // 'pack/*' → 'pack/*'
      
      // Library aliases (point to pack/ or adapters/)
      'jquery-custom-scrollbar$': path.resolve('pack/jquery.mCustomScrollbar.js'),
      'react-router$': path.resolve('pack/reactrouter@1.0.0.js'),
      'react-router2$': path.resolve('pack/reactrouter@2.4.0.js'),
      'progressbar$': path.resolve('pack/progressbar.min.js'),
      'react-with-addons$': path.resolve('pack/react-with-addons.js'),
      'd3$': path.resolve('pack/d3.min.js'),
      'react$': path.resolve('adapters/react.js'),  // 'react' → window.React
      'jquery$': path.resolve('adapters/jquery.js'), // 'jquery' → window.$
    },
    
    // File extensions to resolve automatically
    extensions: ['.js', '.jsx'],
  },

  // 5. MODULE LOADERS
  module: {
    loaders: [
      {
        // Babel loader for transpiling ES6 → ES5
        test: /\.(es6|js)$/,
        exclude: [
          path.resolve(__dirname, 'node_modules'),
          path.resolve(__dirname, 'pack'),      // Skip third-party libs
          path.resolve(__dirname, 'adapters'),  // Skip adapters
          path.resolve(__dirname, 'doc'),
          path.resolve(__dirname, 'LESS'),
        ],
        loader: 'babel-loader?optional[]=runtime',
      },
    ],
  },
};
```

**Key Points:**
1. **Auto-discovery:** All `.js` files in `parent_comp/` become entry points
2. **Path Aliases:** `ccb/*`, `parent/*`, `react`, `jquery` are resolved via aliases
3. **Babel Transpilation:** ES6 code is converted to ES5 for browser compatibility
4. **Output Pattern:** `lib_[name]-bundle.js` where `[name]` is the entry file name

---

## Concrete Example: Building kwk-page Bundle

### Step-by-Step Build Process

#### Step 1: Maven Triggers NPM
```bash
# Maven command
mvn clean install

# Maven executes (during process-sources phase)
cd src/main/webapp/WEB-INF/resources/media/react/
npm run all-prod
```

#### Step 2: NPM Installs Dependencies
```bash
npm install --production

# Installs:
# - webpack@2.2.1
# - babel-loader@5.2.1
# - qrcode@1.4.4
# - async@1.4.2
# - etc.
```

#### Step 3: NPM Runs Bundle Scripts
```bash
npm run bundle-dev

# Which executes:
node node_modules/webpack/bin/webpack.js
```

#### Step 4: Webpack Reads Configuration
```javascript
// webpack.config.js is loaded
// Entry map is built:
{
  'kwk-page': './parent_comp/kwk-page',
  'kwkconfirmation-page': './parent_comp/kwkconfirmation-page',
  'qrkwkconfirmation-page': './parent_comp/qrkwkconfirmation-page',
  // ... 70+ other entries
}
```

#### Step 5: Webpack Processes kwk-page.js Entry
```javascript
// File: parent_comp/kwk-page.js
import React from 'react';                  // Resolves to: adapters/react.js
import KwKPanel from 'parent/kwk/kwkpanel'; // Resolves to: parent_comp/kwk/kwkpanel.js

React.render(
  <KwKPanel/>, 
  document.getElementById('kwkReactContainer')
);
```

#### Step 6: Webpack Resolves KwKPanel Dependencies
```javascript
// File: parent_comp/kwk/kwkpanel.js
import React from 'react';                        // → adapters/react.js
import api from 'ccb/utils/webapi';              // → child_comp/utils/webapi.js
import Button from 'ccb/buttons/button';         // → child_comp/buttons/button.js
import ContentIncludeOld from 'ccb/includes/contentincludeold';
import KwKSelection from 'parent/kwk/kwkselection';
import PageHeading from 'ccb/text/pageheading';
import LoadingIndicator from 'ccb/utils/loadingindicator';
import UrlQueryReader from 'ccb/utils/urlqueryreader';
import Redirector from 'ccb/utils/pageredirection';
import WhatsAppButton from 'ccb/buttons/whatsappbutton';
```

#### Step 7: Webpack Resolves Nested Dependencies
```javascript
// File: child_comp/buttons/button.js
import React from 'react';
import ActiveButton from 'ccb/buttons/activebutton';  // → child_comp/buttons/activebutton.js
import StaticButton from 'ccb/buttons/staticbutton';  // → child_comp/buttons/staticbutton.js
```

```javascript
// File: parent_comp/kwk/kwkselection.js
import React from 'react';
import SingleDropdown from 'ccb/dropdown/singledropdown';  // → child_comp/dropdown/singledropdown.js
import MultiDropdown from 'ccb/dropdown/multidropdown';    // → child_comp/dropdown/multidropdown.js
import LabelText from 'ccb/text/labeltext';                // → child_comp/text/labeltext.js
import EmailInputField from 'ccb/inputs/emailinputfield';  // → child_comp/inputs/emailinputfield.js
```

```javascript
// File: child_comp/inputs/emailinputfield.js
import React from 'react';
import EmailValidator from 'ccb/validators/emailvalidator'; // → child_comp/validators/emailvalidator.js
```

#### Step 8: Babel Transpiles ES6 to ES5
```javascript
// BEFORE (ES6):
import React from 'react';
class KwKPanel extends React.Component {
  constructor(props) {
    super(props);
    this.state = { selectedProduct: {} };
  }
}
export default KwKPanel;

// AFTER (ES5):
var React = require('react');
var KwKPanel = function() {
  function KwKPanel(props) {
    _classCallCheck(this, KwKPanel);
    this.state = { selectedProduct: {} };
  }
  return KwKPanel;
}();
module.exports = KwKPanel;
```

#### Step 9: Webpack Bundles All Files
```javascript
// All dependencies are combined into single file:
// - parent_comp/kwk-page.js
// - parent_comp/kwk/kwkpanel.js
// - parent_comp/kwk/kwkselection.js
// - child_comp/buttons/button.js
// - child_comp/buttons/activebutton.js
// - child_comp/buttons/staticbutton.js
// - child_comp/buttons/whatsappbutton.js
// - child_comp/dropdown/singledropdown.js
// - child_comp/dropdown/multidropdown.js
// - child_comp/text/pageheading.js
// - child_comp/text/labeltext.js
// - child_comp/inputs/emailinputfield.js
// - child_comp/validators/emailvalidator.js
// - child_comp/utils/webapi.js
// - child_comp/utils/loadingindicator.js
// - child_comp/utils/urlqueryreader.js
// - child_comp/utils/pageredirection.js
// - child_comp/includes/contentincludeold.js
// - adapters/react.js
// - adapters/jquery.js
```

#### Step 10: Output Created
```
Output file created:
../system/js/lib_kwk-page-bundle.js

Full path:
C:\CCB\sources\portal\ui-react\src\main\webapp\WEB-INF\resources\media\system\js\lib_kwk-page-bundle.js

File size: ~500KB (development) / ~200KB (minified)
```

---

## CCB UI Module Details (ccb/ui/pk-webui/kwk)

### Module Structure

The CCB UI Module acts as the **bridge between frontend and backend**. It has three sub-modules:

```
C:\CCB\sources\portal\ccb\ui\pk-webui\kwk\
│
├── pom.xml                           ← Parent POM (aggregates ui/rest/public)
│
├── ui\                               ← Java UI Layer (Wicket pages)
│   ├── pom.xml
│   └── src\main\
│       ├── java\
│       │   └── com\commerzbank\ccb\kwk\
│       │       ├── KWKOverviewPage.java           ← Main page controller
│       │       ├── KWKOverviewPageModel.java      ← Page data model
│       │       ├── confirmationpage\
│       │       │   ├── KWKConfirmationPage.java
│       │       │   └── KWKConfirmationPageModel.java
│       │       ├── confirmationsmspage\
│       │       ├── confirmationwhatsapppage\
│       │       ├── container\
│       │       │   ├── KWKOverviewContainerPanel.java
│       │       │   └── KWKOverviewContainerModel.java
│       │       ├── recommendation\
│       │       └── lsg\                           ← Landing page variants
│       │
│       ├── js\dist\                  ← Pre-built static resources
│       │   ├── overview\
│       │   ├── email\
│       │   └── instantmessages\
│       │
│       └── resources\                ← Properties, config files
│
├── rest\                             ← REST API Layer (Spring Controllers)
│   ├── pom.xml
│   └── src\main\java\
│       └── com\commerzbank\ccb\crc\rest\delegate\
│           ├── CrcJsonController.java             ← Main REST controller
│           └── dto\
│               └── CrcCodeDto.java
│
└── public\                           ← Public shared code
    ├── pom.xml
    └── src\main\java\
        └── com\commerzbank\ccb\kwk\
            ├── delegate\
            │   └── KwkDispatcher.java
            ├── transfer\
            │   ├── CrcDispatcher.java
            │   └── KwkDispatcher.java
            └── util\
```

### UI Sub-Module (kwk/ui)

**Purpose:** Serves HTML pages that load React bundles

**Key File:** `KWKOverviewPage.java`

**Dependencies in pom.xml:**
```xml
<dependencies>
    <!-- UI Framework -->
    <dependency>
        <groupId>coba.ccb.ui.shared</groupId>
        <artifactId>ui-shared-ui</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- JSON Support -->
    <dependency>
        <groupId>coba.ccb.ui.shared</groupId>
        <artifactId>ui-shared-json</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- DCRM (CMS Content) -->
    <dependency>
        <groupId>coba.ccb.ui.shared</groupId>
        <artifactId>ui-shared-dcrm</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- Process Interface -->
    <dependency>
        <groupId>coba.ccb.process-interface</groupId>
        <artifactId>process-interface-kwk</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- React Base (React integration utilities) -->
    <dependency>
        <groupId>coba.ccb.ui.shared</groupId>
        <artifactId>react-base</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- Public module (shared KWK code) -->
    <dependency>
        <groupId>coba.ccb.ui.pk-webui.kwk</groupId>
        <artifactId>crc-pk-public</artifactId>
        <version>${project.version}</version>
    </dependency>
</dependencies>
```

**What KWKOverviewPage.java does:**
1. Extends `BasePage<KWKOverviewPageModel>` (Wicket framework)
2. Implements `ReactPage` interface
3. Loads React bundle via `ReactjsLoaderBehavior("kwk-page")`
4. Provides data to React via `getDataForReact()` method
5. Provides translations via `getTranslationsForReact()` method
6. Includes CMS content slots (wi1, ci1, ci2, ci3, wi2)
7. Checks user authorization and eligibility

**React Integration:**
```java
public class KWKOverviewPage extends BasePage<KWKOverviewPageModel> 
    implements ReactPage {
    
    @SpringBean
    private CrcDispatcher kwkDispatcher;
    
    @Override
    protected void onInitialize() {
        super.onInitialize();
        
        // Add React bundle loader
        add(new ReactjsLoaderBehavior("kwk-page"));
        // This loads: lib_kwk-page-bundle.js
    }
    
    @Override
    public Serializable getDataForReact() {
        // Calls dispatcher to get products, accounts, rewards
        JsonResponse jsonResponse = this.kwkDispatcher.retrieveDropdownData(...);
        return jsonResponse; // Serialized to window.getReactData()
    }
    
    @Override
    public Map<String, String> getTranslationsForReact() {
        // Returns translations for React components
        return getTranslations(this.transactionKeys);
        // Serialized to window.getReactTranslations()
    }
}
```

### REST Sub-Module (kwk/rest)

**Purpose:** Provides REST API endpoints for React frontend

**Key File:** `CrcJsonController.java`

**Dependencies in pom.xml:**
```xml
<dependencies>
    <!-- Process Interface (contract) -->
    <dependency>
        <groupId>coba.ccb.process-interface</groupId>
        <artifactId>process-interface-kwk</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- UI Shared JSON utilities -->
    <dependency>
        <groupId>coba.ccb.ui.shared</groupId>
        <artifactId>ui-shared-json</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- Framework -->
    <dependency>
        <groupId>coba.ccb.fw.shared</groupId>
        <artifactId>fw-shared-api</artifactId>
        <version>${project.version}</version>
    </dependency>

    <!-- Spring Framework -->
    <dependency>
        <groupId>org.springframework</groupId>
        <artifactId>spring-web</artifactId>
    </dependency>
</dependencies>
```

**Endpoints:**
```java
@Controller
@RequestMapping()
public class CrcJsonController extends AbstractJsonController {
    
    @Inject
    @Named("customerReferCustomerProcess")
    private CustomerReferCustomerProcess crcProcess;
    
    // Endpoint called by React: api.post('/banking/rest/sendReference', ...)
    @RequestMapping(
        value = "/sendReference", 
        method = RequestMethod.POST,
        produces = "application/json;charset=utf-8"
    )
    @ResponseBody
    public JsonResponse sendReference(@RequestBody SendReferenceRequest request) {
        // 1. Call process layer
        SendReferenceResponse response = this.crcProcess.sendReference(request);
        
        // 2. Extract referral code
        String referalCode = response.getKwkCode();
        
        // 3. Build JSON response
        JsonResult result = new JsonResult();
        result.addItem(new CrcCodeDto(referalCode));
        return new JsonResponse(result);
    }
    
    @RequestMapping(value = "crcCheck", method = RequestMethod.GET)
    @ResponseBody
    public String init() {
        return "Customer Refer Customer Check!";
    }
}
```

### Public Sub-Module (kwk/public)

**Purpose:** Shared code used by both UI and REST modules

**Key Classes:**
- `CrcDispatcher.java` - Orchestrates data retrieval for UI
- `KwkDispatcher.java` - Legacy dispatcher
- Error enums, validation utilities

---

## Complete Dependency Graph

### Frontend Bundle Dependencies

**File:** `lib_kwk-page-bundle.js`

**Built from:**
- `ui-react/src/main/webapp/WEB-INF/resources/media/react/parent_comp/kwk-page.js`
- Plus 20+ child components

**Consumed by:**
- `ccb/ui/pk-webui/kwk/ui` - KWKOverviewPage.java loads this bundle

**No direct dependency on UCC** - The bundle is pure frontend code that runs in the browser.

### CCB UI Module Dependencies

**Module:** `ccb/ui/pk-webui/kwk/ui`

**Depends on:**
```
ccb/ui/pk-webui/kwk/ui/pom.xml
    │
    ├── ui-react (bundle output) ← Frontend bundle
    │   └── lib_kwk-page-bundle.js
    │
    ├── coba.ccb.ui.shared:ui-shared-ui ← Shared UI utilities
    ├── coba.ccb.ui.shared:ui-shared-json ← JSON utilities
    ├── coba.ccb.ui.shared:ui-shared-dcrm ← CMS integration
    ├── coba.ccb.ui.shared:react-base ← React integration
    │
    ├── coba.ccb.process-interface:process-interface-kwk ← Process contract
    │   └── CustomerReferCustomerProcess.java (interface)
    │
    └── coba.ccb.ui.pk-webui.kwk:crc-pk-public ← Shared KWK code
        └── CrcDispatcher.java
```

**Module:** `ccb/ui/pk-webui/kwk/rest`

**Depends on:**
```
ccb/ui/pk-webui/kwk/rest/pom.xml
    │
    ├── coba.ccb.process-interface:process-interface-kwk ← Process contract
    │   └── CustomerReferCustomerProcess.java (interface)
    │
    ├── coba.ccb.ui.shared:ui-shared-json ← JSON utilities
    │
    └── Spring Framework ← MVC, DI
```

### Process Layer Dependencies

**Module:** `ccb/middletier/process/kwk`

**Location:** `C:\CCB\sources\portal\ccb\middletier\process\kwk\`

**Depends on:**
```
ccb/middletier/process/kwk/pom.xml
    │
    ├── coba.ccb.process-interface:process-interface-kwk ← Implements interface
    │
    ├── coba.ccb.sc.participant:participant-api ← SC: ParticipantService
    ├── coba.ccb.sc.person:person-api ← SC: NaturalPersonAPIV3Service
    ├── coba.ccb.sc.sharedbusiness:sharedbusiness-api ← SC: Multiple services
    │   ├── ProductService
    │   ├── IbanConverterService
    │   ├── CCBNumberResolverService
    │   ├── BaseProductMatrixService
    │   └── JuristicalLoggingService
    │
    ├── coba.ccb.sc.[kwk-service]:kwk-service ← SC: CustomerReferCustomerService
    │   └── saveCrcData(), retrieveKwkData()
    │
    ├── coba.ccb.fw.mt.api:fw-mt-api ← Framework
    └── Spring Framework ← DI, Security
```

---

## Why No UCC Module?

### Historical Context

KWK (Kunden Werben Kunden) was developed **before the UCC architecture pattern** was established. Therefore:

1. **Process Implementation** → `ccb/middletier/process/kwk/`
   - Normally would be in `ucc/kwkrecommendation/process/`
   
2. **Process Interface** → `ccb/process-interface/kwk/`
   - Normally would be in `ucc/kwkrecommendation/process-interface/`

3. **UI Module** → `ccb/ui/pk-webui/kwk/`
   - This is correct even in UCC pattern

4. **Service Layer** → `sc/[kwk-module]/service/`
   - This is correct

### Migration Impact

When migrating KWK to a standalone microservice:

**Current Structure:**
```
ccb/
├── middletier/process/kwk/          ← Process implementation
├── process-interface/kwk/           ← Process interface
└── ui/pk-webui/kwk/                 ← UI + REST

ui-react/                            ← Frontend bundle source
└── parent_comp/kwk/

sc/                                  ← Services
└── [kwk-module]/service/
```

**Should migrate to:**
```
kwk-microservice/                    ← New standalone service
├── backend/
│   ├── api/                         ← REST controllers (from kwk/rest)
│   ├── service/                     ← Business logic (from middletier/process/kwk)
│   ├── domain/                      ← Domain models
│   └── repository/                  ← Data access (from SC service)
│
└── frontend/
    ├── src/
    │   ├── components/              ← React components (from ui-react/kwk)
    │   ├── pages/                   ← Page components
    │   └── services/                ← API clients
    └── package.json
```

---

## Complete File List for KWK Bundle

### Entry Point Files
| File | Type | Purpose |
|------|------|---------|
| `parent_comp/kwk-page.js` | Entry | Main page entry point |
| `parent_comp/kwkconfirmation-page.js` | Entry | Confirmation page entry |
| `parent_comp/qrkwkconfirmation-page.js` | Entry | QR confirmation entry |

### KWK-Specific Components
| File | Type | Depends On |
|------|------|------------|
| `parent_comp/kwk/kwkpanel.js` | Component | React, 11 child components |
| `parent_comp/kwk/kwkselection.js` | Component | React, 4 dropdown/input components |
| `parent_comp/kwk/confpanel.js` | Component | React, 5 components |
| `parent_comp/kwk/qrconfpanel.js` | Component | React, qrcode library |
| `parent_comp/kwk/kwkemailpanel.js` | Component | React, 2 input components |

### Shared Child Components (Used by KWK)
| Category | Files | Location |
|----------|-------|----------|
| **Buttons** | `button.js`, `activebutton.js`, `staticbutton.js`, `whatsappbutton.js`, `mailtobutton.js` | `child_comp/buttons/` |
| **Dropdowns** | `singledropdown.js`, `multidropdown.js` | `child_comp/dropdown/` |
| **Inputs** | `emailinputfield.js`, `decoratedinputfield.js` | `child_comp/inputs/` |
| **Text** | `pageheading.js`, `labeltext.js`, `labelhtmltext.js` | `child_comp/text/` |
| **Utils** | `webapi.js`, `loadingindicator.js`, `urlqueryreader.js`, `pageredirection.js` | `child_comp/utils/` |
| **Validators** | `emailvalidator.js` | `child_comp/validators/` |
| **Includes** | `contentinclude.js`, `contentincludeold.js` | `child_comp/includes/` |

### Adapters
| File | Purpose | Exports |
|------|---------|---------|
| `adapters/react.js` | React adapter | `module.exports = window.React` |
| `adapters/jquery.js` | jQuery adapter | `module.exports = window.$` |

### Third-Party Libraries (from pack/)
| Library | Usage in KWK |
|---------|--------------|
| `qrcode` | QR code generation (qrconfpanel.js) |
| React library | Loaded globally via `window.React` |
| jQuery library | Loaded globally via `window.$` |

---

## Dependency Analysis for Migration

### What KWK Depends On

#### Direct Dependencies (Import Statements)
```javascript
// From kwkpanel.js:
import api from 'ccb/utils/webapi';               // REST API calls
import Button from 'ccb/buttons/button';          // Button component
import KwKSelection from 'parent/kwk/kwkselection'; // Dropdown selection
import PageHeading from 'ccb/text/pageheading';   // Page title
import LoadingIndicator from 'ccb/utils/loadingindicator'; // Spinner
import UrlQueryReader from 'ccb/utils/urlqueryreader';     // URL params
import Redirector from 'ccb/utils/pageredirection';        // Redirects
import WhatsAppButton from 'ccb/buttons/whatsappbutton';   // WhatsApp share
import ContentIncludeOld from 'ccb/includes/contentincludeold'; // CMS includes

// From kwkselection.js:
import SingleDropdown from 'ccb/dropdown/singledropdown';
import MultiDropdown from 'ccb/dropdown/multidropdown';
import LabelText from 'ccb/text/labeltext';
import EmailInputField from 'ccb/inputs/emailinputfield';

// From confpanel.js:
import MailButton from 'ccb/buttons/mailtobutton';
import ContentInclude from 'ccb/includes/contentinclude';
import LabelHTMLText from 'ccb/text/labelhtmltext';

// From qrconfpanel.js:
import QRCode from 'qrcode'; // External NPM package
```

#### Transitive Dependencies (What child components import)
- **Button** → ActiveButton, StaticButton
- **EmailInputField** → EmailValidator
- **WebApi** → jQuery (for AJAX)
- All components → React

### Files to Extract for Standalone KWK Frontend

#### Minimum Required Files (21 files)
```
1. parent_comp/kwk-page.js
2. parent_comp/kwk/kwkpanel.js
3. parent_comp/kwk/kwkselection.js
4. parent_comp/kwk/confpanel.js
5. parent_comp/kwk/qrconfpanel.js
6. parent_comp/kwk/kwkemailpanel.js
7. child_comp/buttons/button.js
8. child_comp/buttons/activebutton.js
9. child_comp/buttons/staticbutton.js
10. child_comp/buttons/whatsappbutton.js
11. child_comp/buttons/mailtobutton.js
12. child_comp/dropdown/singledropdown.js
13. child_comp/dropdown/multidropdown.js
14. child_comp/inputs/emailinputfield.js
15. child_comp/text/pageheading.js
16. child_comp/text/labeltext.js
17. child_comp/text/labelhtmltext.js
18. child_comp/utils/webapi.js
19. child_comp/utils/loadingindicator.js
20. child_comp/utils/urlqueryreader.js
21. child_comp/utils/pageredirection.js
22. child_comp/validators/emailvalidator.js
23. child_comp/includes/contentinclude.js
24. child_comp/includes/contentincludeold.js
```

#### Plus Each Child Component's Dependencies
Each of the above child components may have additional dependencies that need to be traced.

---

## Build Output Analysis

### Bundle Contents

**File:** `lib_kwk-page-bundle.js`

**Structure:**
```javascript
(function(modules) {
  // Webpack bootstrap code
  function __webpack_require__(moduleId) { /* ... */ }
  
  // Module definitions
  __webpack_require__.m = modules;
  
  // Module 0: Entry point (kwk-page.js)
  modules[0] = function(module, exports, __webpack_require__) {
    var React = __webpack_require__(1);
    var KwKPanel = __webpack_require__(2);
    React.render(/* ... */);
  };
  
  // Module 1: React adapter
  modules[1] = function(module, exports) {
    module.exports = window.React;
  };
  
  // Module 2: kwkpanel.js
  modules[2] = function(module, exports, __webpack_require__) {
    var React = __webpack_require__(1);
    var api = __webpack_require__(3);
    var Button = __webpack_require__(4);
    // ... component code
  };
  
  // Module 3: webapi.js
  modules[3] = function(module, exports, __webpack_require__) {
    var $ = __webpack_require__(5);
    // ... API code
  };
  
  // ... 50+ more modules
  
})([/* module array */]);
```

### Bundle Characteristics

| Aspect | Details |
|--------|---------|
| **Format** | UMD (Universal Module Definition) |
| **Module System** | CommonJS (within bundle) |
| **Global Dependencies** | `window.React`, `window.$`, `window.jQuery` |
| **Bundle Size (dev)** | ~500KB |
| **Bundle Size (minified)** | ~200KB |
| **Number of Modules** | ~60-80 modules |
| **Browser Support** | IE9+ (after Babel transpilation) |

---

## Migration Strategy for Frontend

### Option 1: Extract and Reuse Components

**Approach:** Copy KWK components to new project

**Steps:**
1. Create new React project (Vite/Create React App)
2. Copy all KWK files (21+ components)
3. Copy all child_comp dependencies (~30+ components)
4. Update imports (remove webpack aliases)
5. Replace adapters with proper imports
6. Update build configuration

**Pros:**
- Preserves existing code
- Faster migration
- Existing functionality maintained

**Cons:**
- Carries over technical debt
- Old React version
- Messy codebase structure
- Many transitive dependencies

### Option 2: Rewrite with Modern React

**Approach:** Rebuild KWK UI from scratch

**Steps:**
1. Create new React project (TypeScript + React 18)
2. Design new component structure
3. Implement KWK functionality:
   - Product selection
   - Reward selection
   - Account selection
   - Email input
   - Referral code generation UI
4. Use modern libraries:
   - React Router v6
   - Axios (instead of custom webapi)
   - React Hook Form
   - Modern UI library (Material-UI, Ant Design, Chakra UI)

**Pros:**
- Clean codebase
- Modern React features (Hooks, Context)
- Better performance
- Easier to maintain
- TypeScript support

**Cons:**
- More development effort
- Need to recreate all functionality
- UI/UX may differ initially

### Option 3: Hybrid Approach

**Approach:** Extract core components, modernize gradually

**Steps:**
1. Extract KWK components to new project
2. Replace child_comp dependencies with modern alternatives:
   - `ccb/utils/webapi` → Axios
   - `ccb/buttons/button` → Material-UI Button
   - `ccb/dropdown/singledropdown` → Material-UI Select
   - `ccb/inputs/emailinputfield` → React Hook Form + validation
3. Convert to TypeScript gradually
4. Update to React Hooks
5. Improve component structure

**Pros:**
- Balanced approach
- Gradual modernization
- Reduces risk
- Improves code quality over time

**Cons:**
- Mixed old/new code initially
- Requires planning
- Intermediate complexity

---

## Complete Dependency Matrix

### All KWK Components and Their Dependencies

| Component | Type | Location | Depends On | Used By |
|-----------|------|----------|------------|---------|
| **FRONTEND LAYER** |
| `kwk-page.js` | Entry Point | `ui-react/parent_comp/` | `kwkpanel.js`, React | Webpack |
| `kwkpanel.js` | React Component | `ui-react/parent_comp/kwk/` | 11 child components, React | `kwk-page.js` |
| `kwkselection.js` | React Component | `ui-react/parent_comp/kwk/` | 4 child components, React | `kwkpanel.js` |
| `confpanel.js` | React Component | `ui-react/parent_comp/kwk/` | 5 child components, React | `kwkconfirmation-page.js` |
| `qrconfpanel.js` | React Component | `ui-react/parent_comp/kwk/` | QRCode lib, React | `qrkwkconfirmation-page.js` |
| `lib_kwk-page-bundle.js` | Bundle Output | `ui-react/.../system/js/` | All above components | `KWKOverviewPage.java` |
| **CCB UI LAYER** |
| `KWKOverviewPage.java` | Wicket Page | `ccb/ui/pk-webui/kwk/ui/` | `ui-react` bundle, `react-base`, `CrcDispatcher` | Browser requests |
| `KWKOverviewPageModel.java` | Page Model | `ccb/ui/pk-webui/kwk/ui/` | `BasePage`, Framework | `KWKOverviewPage.java` |
| `CrcJsonController.java` | REST Controller | `ccb/ui/pk-webui/kwk/rest/` | `CustomerReferCustomerProcess` (interface) | React `kwkpanel.js` (AJAX) |
| `CrcDispatcher.java` | Dispatcher | `ccb/ui/pk-webui/kwk/public/` | Process interface, Product services | `KWKOverviewPage.java` |
| **PROCESS LAYER** |
| `CustomerReferCustomerProcess.java` | Interface | `ccb/process-interface/kwk/` | Request/Response DTOs | `CrcJsonController.java`, Process impl |
| `CustomerReferCustomerProcessImpl.java` | Process Impl | `ccb/middletier/process/kwk/` | 6 SC services, Process interface | `CrcJsonController.java` (via Spring) |
| **SERVICE LAYER** |
| `ParticipantService` | SC Service | `sc/participant/api/service/` | Database, Host | Process impl |
| `NaturalPersonAPIV3Service` | SC Service | `sc/person/api/service/` | Database, Host | Process impl |
| `ProductService` | SC Service | `sc/sharedbusiness/api/service/` | Database, Host | Process impl |
| `CustomerReferCustomerService` | SC Service | `sc/[kwk-module]/service/` | Database | Process impl |

### Dependency Flow Visualization

```
Browser (User)
    ↓ HTTP GET /portal/kwk
    │
    ▼
┌─────────────────────────────────────────────┐
│ KWKOverviewPage.java                        │ ← ccb/ui/pk-webui/kwk/ui
│ (Wicket Page Container)                     │
│                                             │
│ Dependencies:                                │
│ - ui-shared-ui                              │
│ - ui-shared-json                            │
│ - ui-shared-dcrm                            │
│ - react-base                                │
│ - process-interface-kwk                     │
│ - crc-pk-public (CrcDispatcher)             │
└──┬──────────────────────────────────────────┘
   │
   │ Loads React bundle
   │ Calls getDataForReact()
   │
   ▼
┌─────────────────────────────────────────────┐
│ lib_kwk-page-bundle.js                      │ ← Built from ui-react
│ (React Application)                         │
│                                             │
│ Built from:                                 │
│ - parent_comp/kwk-page.js                   │
│ - parent_comp/kwk/kwkpanel.js               │
│ - parent_comp/kwk/kwkselection.js           │
│ - child_comp/buttons/*                      │
│ - child_comp/dropdown/*                     │
│ - child_comp/inputs/*                       │
│ - child_comp/utils/*                        │
│ - child_comp/validators/*                   │
│ - (20+ more files)                          │
│                                             │
│ No direct backend dependencies              │
│ (Communicates via REST API)                 │
└──┬──────────────────────────────────────────┘
   │
   │ User fills form and clicks Send
   │ POST /banking/rest/sendReference
   │
   ▼
┌─────────────────────────────────────────────┐
│ CrcJsonController.java                      │ ← ccb/ui/pk-webui/kwk/rest
│ (REST API Controller)                       │
│                                             │
│ Dependencies:                                │
│ - process-interface-kwk                     │
│ - ui-shared-json                            │
│ - Spring MVC                                │
│                                             │
│ Injected:                                   │
│ @Inject CustomerReferCustomerProcess        │
└──┬──────────────────────────────────────────┘
   │
   │ Calls process.sendReference(request)
   │
   ▼
┌─────────────────────────────────────────────┐
│ CustomerReferCustomerProcessImpl.java       │ ← ccb/middletier/process/kwk
│ (Business Logic Orchestration)              │
│                                             │
│ Dependencies:                                │
│ - process-interface-kwk (implements)        │
│ - fw-mt-api (BaseProcess)                   │
│ - fw-shared-api (annotations)               │
│                                             │
│ Service Layer Dependencies:                 │
│ @Inject ParticipantService                  │ ← sc/participant
│ @Inject NaturalPersonAPIV3Service           │ ← sc/person
│ @Inject ProductService                      │ ← sc/sharedbusiness
│ @Inject IbanConverterService                │ ← sc/sharedbusiness
│ @Inject CCBNumberResolverService            │ ← sc/sharedbusiness
│ @Inject BaseProductMatrixService            │ ← sc/sharedbusiness
│ @Inject JuristicalLoggingService            │ ← sc/sharedbusiness
│ @Inject CustomerReferCustomerService        │ ← sc/[kwk-module]
│ @Inject CustomersAPIV3Service               │ ← sc/person
└──┬──────────────────────────────────────────┘
   │
   │ Calls multiple SC services
   │
   ▼
┌─────────────────────────────────────────────┐
│ SC Services (Service Cluster)               │ ← sc/*
│                                             │
│ - ParticipantService                        │
│ - NaturalPersonAPIV3Service                 │
│ - ProductService                            │
│ - CustomerReferCustomerService              │
│   └── saveCrcData(kwkData)                  │
│   └── retrieveKwkData(kwkCode)              │
│                                             │
│ These call:                                 │
│ - Database (JPA repositories)               │
│ - Host systems (mainframe)                  │
└─────────────────────────────────────────────┘
```

### Maven Build Dependencies

**Build Order (Reactor):**
```
1. parents/                           ← Base parent POMs
2. fw/                                ← Framework
3. ccb/shared/                        ← Shared utilities
4. ccb/process-interface/kwk/         ← Process contract
5. ccb/middletier/process/kwk/        ← Process implementation
6. sc/                                ← Service clusters
7. ui-react/                          ← Frontend bundle build
8. ccb/ui/shared/                     ← Shared UI utilities
9. ccb/ui/pk-webui/kwk/public/        ← Shared KWK code
10. ccb/ui/pk-webui/kwk/ui/           ← UI pages (depends on ui-react output)
11. ccb/ui/pk-webui/kwk/rest/         ← REST controllers
12. ccb/ui/pk-webui/kwk/              ← Parent aggregator
13. runtime-artifacts/                ← WAR packaging
```

**Key Point:** `ui-react` must build BEFORE `ccb/ui/pk-webui/kwk/ui/` because the UI module needs the built bundle.

---

## Summary

### Key Findings

1. **Frontend Code Location:** 
   - Source: `ui-react/src/main/webapp/WEB-INF/resources/media/react/parent_comp/kwk/`
   - Built bundle: `ui-react/.../system/js/lib_kwk-page-bundle.js`

2. **CCB UI Module Location:**
   - Java pages: `ccb/ui/pk-webui/kwk/ui/` (KWKOverviewPage.java)
   - REST API: `ccb/ui/pk-webui/kwk/rest/` (CrcJsonController.java)
   - Shared code: `ccb/ui/pk-webui/kwk/public/` (CrcDispatcher.java)

3. **Process Layer Location:**
   - Interface: `ccb/process-interface/kwk/` (CustomerReferCustomerProcess.java)
   - Implementation: `ccb/middletier/process/kwk/` (CustomerReferCustomerProcessImpl.java)
   - **NOT in ucc/** - This is a legacy module that predates UCC architecture

4. **Frontend Components:**
   - Entry Points: 3 files in `parent_comp/`
   - KWK Components: 5 files in `parent_comp/kwk/`
   - Shared Components: 20+ files from `child_comp/`

5. **Build Process:** Maven → NPM → Webpack → Babel → Bundle
   - Output: `lib_kwk-page-bundle.js` (~500KB dev, ~200KB minified)

6. **Dependencies:**
   - **Frontend:** React (window.React), jQuery (window.$), QRCode library
   - **CCB UI Module:** ui-shared-*, react-base, process-interface-kwk
   - **Process Layer:** 6+ SC services (Participant, Person, Product, etc.)

7. **No UCC Module:**
   - KWK follows old CCB architecture, not UCC pattern
   - Process implementation in `ccb/middletier/` instead of `ucc/`

### Complete Component Inventory

#### Frontend (ui-react)
- **Entry Points:** 3 files
- **KWK Components:** 5 files
- **Shared Components:** 24+ files
- **Total Frontend Files:** 30+ files

#### CCB UI Module (ccb/ui/pk-webui/kwk)
- **UI Sub-module:** 10+ Java files
- **REST Sub-module:** 2+ Java files
- **Public Sub-module:** 5+ Java files
- **Total Java Files:** 17+ files

#### Process Layer (ccb/middletier & ccb/process-interface)
- **Interface:** 1 interface + 3 DTOs
- **Implementation:** 1 implementation class
- **Total Process Files:** 5 files

#### Total KWK Codebase
- **Frontend:** ~30 files
- **Backend:** ~22 files
- **Total:** ~52 files minimum for extraction

### Dependency Summary

**Frontend → Backend Flow:**
```
React Component (kwkpanel.js)
    ↓ (AJAX POST)
REST Controller (CrcJsonController.java)
    ↓ (Spring @Inject)
Process Implementation (CustomerReferCustomerProcessImpl.java)
    ↓ (Spring @Inject)
SC Services (ParticipantService, ProductService, etc.)
    ↓
Database & Host Systems
```

**Frontend Dependencies:**
- **Direct:** 24 child components, React, jQuery
- **Build:** Webpack, Babel, NPM
- **Runtime:** window.React, window.$

**Backend Dependencies:**
- **UI Module:** ui-shared-*, react-base, process-interface-kwk
- **Process Layer:** 6 SC services, Framework APIs
- **Build:** Maven, Spring Framework

### For Migration

**Minimum Scope:**
- **Frontend:** 30+ React component files
- **Backend:** 22+ Java files
- **Dependencies:** 6 SC services (need REST clients or copy)
- **Database:** CRC_DATA table schema + data access layer

**Migration Approaches Refined:**

1. **Extract As-Is (2-3 weeks)**
   - Copy all 52+ files
   - Preserve dependencies
   - Quick but carries technical debt

2. **Modernize Frontend Only (4-6 weeks)**
   - Keep backend as-is
   - Rewrite React components with modern stack
   - Replace child_comp with modern UI library

3. **Full Modernization (8-12 weeks)**
   - Backend: Spring Boot microservice
   - Frontend: React 18 + TypeScript + Vite
   - Services: REST clients for SC services
   - Database: Separate database instance

**Critical Dependencies to Address:**

| Dependency | Current | Migration Option |
|------------|---------|------------------|
| **ui-react bundle** | Shared monolith | Extract to standalone React project |
| **CCB UI Module** | Wicket pages | Replace with React SPA or Next.js |
| **Process Interface** | Internal API | Keep contract, implement independently |
| **SC Services** | Direct injection | Create REST clients or GraphQL |
| **CMS Content** | DCRM integration | Replace with headless CMS |
| **Security** | Spring Security | OAuth2/JWT |
| **Database** | Shared DB | Separate schema or microservice DB |

### Architecture Clarification

**Why No UCC Module?**
- KWK was developed before UCC architecture pattern
- Follows older CCB monolith structure
- Process lives in `ccb/middletier/` not `ucc/`
- This is **intentional**, not an error

**Modern vs Legacy:**
- **Modern Use Cases:** Have `ucc/{usecase}/` modules
- **Legacy Use Cases (like KWK):** Have `ccb/middletier/process/{usecase}/` modules
- Both patterns coexist in the monolith

**Impact on Migration:**
- No difference in functionality
- Same migration complexity
- Need to extract from different locations
- Final microservice structure should be the same

---

## Migration Readiness Checklist

### Frontend Migration Checklist
- [ ] Identify all 30+ frontend component files
- [ ] Map dependencies (child_comp imports)
- [ ] Choose migration approach (extract vs rewrite)
- [ ] Set up new React project structure
- [ ] Migrate or replace shared components
- [ ] Update API client (webapi.js → Axios/Fetch)
- [ ] Replace adapters (window.React → proper imports)
- [ ] Test all UI functionality

### Backend Migration Checklist
- [ ] Extract Java files from ccb/ui/pk-webui/kwk
- [ ] Extract process from ccb/middletier/process/kwk
- [ ] Extract process interface from ccb/process-interface/kwk
- [ ] Identify all 6 SC service dependencies
- [ ] Create REST clients for SC services (or copy service code)
- [ ] Extract database schema (CRC_DATA table)
- [ ] Implement authentication/authorization
- [ ] Set up Spring Boot microservice project
- [ ] Migrate REST endpoints
- [ ] Test all API functionality

### Infrastructure Checklist
- [ ] Set up CI/CD pipeline
- [ ] Configure database (separate instance)
- [ ] Set up API gateway routing
- [ ] Configure security (OAuth2/JWT)
- [ ] Set up monitoring/logging
- [ ] Plan deployment strategy (blue/green, canary)
- [ ] Document API contracts (OpenAPI/Swagger)
- [ ] Performance testing
- [ ] Load testing
- [ ] Security testing

### Risk Mitigation
- [ ] Document all dependencies
- [ ] Create integration tests
- [ ] Plan rollback strategy
- [ ] Identify breaking changes
- [ ] Communicate with stakeholders
- [ ] Plan feature flag strategy
- [ ] Schedule phased rollout

