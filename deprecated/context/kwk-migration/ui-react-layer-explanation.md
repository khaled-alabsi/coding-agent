# UI-React Layer Explanation

**Date:** November 6, 2025  
**Purpose:** Clarifying the role of `ui-react` in the CCB architecture

---

## The Confusion: Where Does ui-react Fit?

You noticed that `ui-react` doesn't appear in the backend dependency diagram:
```
UCC → SC → SB → CCB → FW
```

**Why?** Because `ui-react` is **NOT a backend layer** - it's a **frontend shared component library**.

---

## What is ui-react?

### Definition
`ui-react` is a **centralized React component library** that provides reusable UI components for multiple CCB web UI modules.

### Think of it as:
- **NPM Package** (but built internally via Maven)
- **Shared Component Library** (like Material-UI or Ant Design)
- **Frontend SDK** used by multiple apps

### What it Contains
```
ui-react/
└── src/main/webapp/WEB-INF/resources/media/react/
    ├── parent_comp/          ← Entry point components (pages)
    │   ├── kwk-page.js       ← KWK main page
    │   ├── depot-page.js     ← Depot page
    │   ├── payments-page.js  ← Payments page
    │   └── [70+ other page entries]
    │
    ├── child_comp/           ← Reusable child components
    │   ├── buttons/
    │   ├── forms/
    │   ├── modals/
    │   └── [shared widgets]
    │
    ├── shared_comp/          ← Utilities and helpers
    │   ├── utils/
    │   ├── validators/
    │   └── [common logic]
    │
    ├── adapters/             ← Library adapters
    │   ├── react.js
    │   └── jquery.js
    │
    └── pack/                 ← Third-party libraries
```

---

## ui-react vs UCC: The Key Difference

| Aspect | ui-react | UCC |
|--------|----------|-----|
| **Type** | Frontend component library | Backend use case logic |
| **Language** | JavaScript (React) | Java |
| **Provides** | UI components | Business processes |
| **Shared?** | Yes - used by many UI modules | No - each UCC is independent |
| **Location** | `ui-react/` (top-level) | `ucc/{usecase}/` |
| **Build Output** | JavaScript bundles | JAR files |
| **Used By** | CCB UI modules (pk-webui, msb-webui, etc.) | CCB UI REST controllers |

---

## The Actual Architecture (Frontend + Backend)

### Corrected Layer View

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ ui-react (Shared React Components)                        │ │
│  │ - Reusable React components for all UI modules            │ │
│  │ - Built once, used by multiple pages                      │ │
│  │ - Outputs: lib_[name]-bundle.js                           │ │
│  └───────────────────────────────────────────────────────────┘ │
│                            ↓ (consumed by)                      │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ CCB UI Modules (pk-webui, msb-webui, etc.)                │ │
│  │ - Java-based page containers                              │ │
│  │ - Serve HTML + React bundles                              │ │
│  │ - Provide REST endpoints for React                        │ │
│  │ Example: ccb/ui/pk-webui/kwk/                             │ │
│  │   ├── ui/       (KWKOverviewPage.java)                    │ │
│  │   ├── rest/     (CrcJsonController.java)                  │ │
│  │   └── public/   (Static resources)                        │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               ↓ (calls via REST)
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────┐                   │
│  │  Use Case Clusters (UCC)                │                   │
│  │  - Business process orchestration       │                   │
│  │  - Each UCC = One business application  │                   │
│  └──────────────┬──────────────────────────┘                   │
│                 ↓ depends on                                    │
│  ┌──────────────▼──────────────────────────┐                   │
│  │  Service Clusters (SC)                   │                   │
│  │  - Domain services                       │                   │
│  └──────────────┬──────────────────────────┘                   │
│                 ↓ depends on                                    │
│  ┌──────────────▼──────────────────────────┐                   │
│  │  Shared Business (SB)                    │                   │
│  └──────────────┬──────────────────────────┘                   │
│                 ↓ depends on                                    │
│  ┌──────────────▼──────────────────────────┐                   │
│  │  Core Platform (CCB)                     │                   │
│  └──────────────┬──────────────────────────┘                   │
│                 ↓ depends on                                    │
│  ┌──────────────▼──────────────────────────┐                   │
│  │  Framework (FW)                          │                   │
│  └──────────────────────────────────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## How ui-react Integrates with CCB UI Modules

### Example: KWK Module

**1. ui-react builds KWK React components**
```
ui-react/src/main/webapp/WEB-INF/resources/media/react/
├── parent_comp/
│   ├── kwk-page.js                    ← Entry point
│   ├── kwkconfirmation-page.js        ← Confirmation page entry
│   └── qrkwkconfirmation-page.js      ← QR confirmation entry
│
└── parent_comp/kwk/                   ← KWK components
    ├── kwkpanel.js                    ← Main panel
    ├── confpanel.js                   ← Confirmation panel
    ├── qrconfpanel.js                 ← QR panel
    ├── kwkemailpanel.js               ← Email panel
    └── kwkselection.js                ← Selection component

BUILD PROCESS (Webpack):
  ↓
Output: lib_kwk-page-bundle.js
        lib_kwkconfirmation-page-bundle.js
        lib_qrkwkconfirmation-page-bundle.js
```

**2. CCB UI Module (ccb/ui/pk-webui/kwk) serves the page**
```java
// File: ccb/ui/pk-webui/kwk/ui/.../KWKOverviewPage.java

@Named("kwk.overview")
public class KWKOverviewPage extends BasePage<KWKOverviewPageModel> 
                              implements ReactPage {
    
    @Override
    public void onBeforeRender() {
        // Set up page data, user context, etc.
    }
}
```

**HTML Output (served to browser):**
```html
<!DOCTYPE html>
<html>
<head>
    <title>KWK Overview</title>
    <!-- CSS, meta tags, etc. -->
</head>
<body>
    <!-- Container for React app -->
    <div id="kwkReactContainer"></div>
    
    <!-- Load the React bundle from ui-react -->
    <script src="/portal/media/system/js/lib_kwk-page-bundle.js"></script>
</body>
</html>
```

**3. React bundle executes in browser**
```javascript
// From ui-react/parent_comp/kwk-page.js
import React from 'react';
import ReactDOM from 'react-dom';
import KwKPanel from 'parent/kwk/kwkpanel';

ReactDOM.render(
    <KwKPanel />,
    document.getElementById('kwkReactContainer')
);
```

**4. React component calls REST API**
```javascript
// From ui-react/parent_comp/kwk/kwkpanel.js
class KwKPanel extends React.Component {
    loadData() {
        fetch('/portal/api/kwk/recommendations')
            .then(response => response.json())
            .then(data => this.setState({ recommendations: data }));
    }
}
```

**5. REST Controller handles the request**
```java
// File: ccb/ui/pk-webui/kwk/rest/.../CrcJsonController.java

@RestController
@RequestMapping("/api/kwk")
public class CrcJsonController extends AbstractJsonController {
    
    @Inject
    private KwkRecommendationProcess kwkProcess;
    
    @GetMapping("/recommendations")
    public RecommendationsResponse getRecommendations() {
        // Call UCC process
        return kwkProcess.getRecommendations();
    }
}
```

**6. REST Controller calls UCC Process**
```java
// File: ucc/kwkrecommendation/process/.../KwkRecommendationProcess.java

@CCBProcess
@Named
public class KwkRecommendationProcess extends BaseMultistepProcess {
    
    @Inject
    private CustomerService customerService;  // From SC
    
    public RecommendationsResponse getRecommendations() {
        // Orchestrate business logic
        // Call multiple SC services
        // Return consolidated data
    }
}
```

---

## Why ui-react is Not in UCC Layer

### ui-react is **INFRASTRUCTURE**, not **APPLICATION**

- **UCC** = Business applications (each use case)
- **ui-react** = Shared UI toolkit (used by many use cases)

### Analogy
Think of it like this:

| Layer | Equivalent | Role |
|-------|------------|------|
| **UCC** | Spring Boot microservices | Each is a separate business app |
| **SC** | Domain service libraries | Shared business logic |
| **ui-react** | React component library (like Material-UI) | Shared UI components |
| **CCB UI Modules** | Express.js servers serving HTML | Page containers + REST APIs |

### Different Concerns

**ui-react cares about:**
- ✅ How buttons look
- ✅ How forms validate
- ✅ How modals animate
- ✅ Component reusability

**UCC cares about:**
- ✅ Business workflows
- ✅ Process orchestration
- ✅ Service integration
- ✅ Business rules

---

## Migration Implications

### For Microservice Migration of KWK

When extracting KWK as a standalone microservice, you have **TWO separate concerns**:

#### 1. Backend (UCC Layer)
**What to extract:**
- UCC processes related to KWK
- SC services used by KWK (or create clients)
- REST API endpoints

**Result:**
```
kwk-microservice/
├── src/main/java/
│   ├── process/     ← KWK business logic (from UCC)
│   ├── rest/        ← REST controllers (from ccb/ui/pk-webui/kwk/rest)
│   └── service/     ← Either copy SC or use REST clients
└── pom.xml
```

#### 2. Frontend (ui-react Components)
**What to extract:**
- React components from `ui-react/parent_comp/kwk/`
- Entry points from `ui-react/parent_comp/kwk*.js`
- Shared dependencies from `child_comp`, `shared_comp`

**Result:**
```
kwk-frontend/
├── src/
│   ├── components/
│   │   ├── KwkPanel.jsx        ← From ui-react/parent_comp/kwk/kwkpanel.js
│   │   ├── ConfPanel.jsx       ← From ui-react/parent_comp/kwk/confpanel.js
│   │   └── QrConfPanel.jsx     ← From ui-react/parent_comp/kwk/qrconfpanel.js
│   ├── pages/
│   │   ├── KwkPage.jsx         ← From ui-react/parent_comp/kwk-page.js
│   │   └── Confirmation.jsx    ← From ui-react/parent_comp/kwkconfirmation-page.js
│   └── App.jsx
├── package.json
└── webpack.config.js
```

#### 3. The Challenge: Shared Components
**Problem:** KWK React components likely depend on:
- `child_comp/*` - Shared buttons, forms, modals
- `shared_comp/*` - Utilities, validators, helpers
- `pack/*` - Third-party libraries

**Options:**
1. **Copy everything** (duplicates code)
2. **Create shared NPM package** (maintains monorepo dependency)
3. **Rewrite using modern React** (cleanest break, most work)

---

## Summary

### Where ui-react Fits

```
Frontend Stack:
  Browser
    ↓
  ui-react bundles (JavaScript)
    ↓
  CCB UI Modules (Java pages + REST)
    ↓
  UCC Backend (Business logic)

Backend Stack:
  UCC (Use Cases)
    ↓
  SC (Services)
    ↓
  SB (Shared Business)
    ↓
  CCB (Core Platform)
    ↓
  FW (Framework)
```

### Key Takeaways

1. **ui-react is NOT part of UCC** - It's a separate frontend infrastructure layer
2. **ui-react is shared** - Multiple CCB UI modules consume it
3. **ui-react builds JavaScript bundles** - These are loaded by Java-based pages
4. **CCB UI modules bridge frontend/backend** - They serve React bundles AND provide REST APIs
5. **For migration:** You need to extract BOTH backend (UCC) AND frontend (ui-react components)

### Answer to Your Question

> "If the apps are in UCC folders, what is ui-react layer for?"

**Answer:** ui-react is **NOT the app layer** - it's the **shared UI component library**. 

The **apps** are actually split across TWO locations:
- **Backend app logic** → `ucc/{usecase}/` (Java processes)
- **Frontend UI components** → `ui-react/parent_comp/{usecase}-page.js` (React components)
- **Integration glue** → `ccb/ui/{webui}/{usecase}/` (Java pages + REST controllers)

Think of it as:
- **UCC** = Your business logic (like Spring Boot services)
- **ui-react** = Your UI toolkit (like React component library)
- **CCB UI Modules** = Your frontend servers (like Next.js or Express.js serving the UI)

