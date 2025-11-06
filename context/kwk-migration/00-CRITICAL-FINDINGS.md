# KWK Migration - CRITICAL FINDINGS ⚠️

## Date: November 6, 2025

---

## 🔴 MOST CRITICAL DISCOVERY

### Account Data Does NOT Come From Database!

**YOU ASKED**: "Where does this data come from? Who put it in the database?"

**THE ANSWER**: The account data shown in KWK **is NOT in the local database at all!**

### The Real Data Flow

```
┌─────────────────────────────────────────────────────────┐
│ CUSTOMER ACCOUNTS LIVE IN:                             │
│ ⭐ MAINFRAME CORE BANKING SYSTEM ⭐                    │
│ (Not in this application's database)                   │
└─────────────────────────────────────────────────────────┘
                          ↓
              Real-time query via PKVD
                          ↓
┌─────────────────────────────────────────────────────────┐
│ KWK Application                                         │
│ - Calls mainframe service (PKVD)                       │
│ - Gets list of customer's accounts                     │
│ - Filters for accounts with REWARDCREDIT permission    │
│ - Shows to user for selection                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 Data Sources Breakdown

### What KWK OWNS (can migrate)
| Data Type | Source | Migration |
|-----------|--------|-----------|
| Referral records | CUSTOMER_REFER_CUSTOMER table | ✅ Can migrate |
| Referral codes | Generated in app, stored in DB | ✅ Can migrate |
| Email addresses | Stored in CUSTOMER_REFER_CUSTOMER | ✅ Can migrate |
| Reward selections | Stored in CUSTOMER_REFER_CUSTOMER | ✅ Can migrate |

### What KWK READS (cannot migrate, must call)
| Data Type | Real Source | Current Access | Migration Strategy |
|-----------|-------------|----------------|-------------------|
| **Customer Accounts** | **Mainframe** | PKVD host service | ⚠️ Must keep calling or replicate |
| Account balances | Mainframe | PKVD host service | ⚠️ Must keep calling |
| Customer names | Mainframe/API | Natural Person API V3 | Call via API gateway |
| Customer type | Mainframe/API | Customers API V3 | Call via API gateway |
| IBAN format | Service | IBAN Converter | Call via API gateway |
| Authorization | Service | Authorization Service | Call via API gateway |

---

## 🏗️ The Mainframe Connection Explained

### What is PKVD?
- **Full Name**: PersonKundeVertragsDaten (Person-Customer-Contract-Data)
- **Type**: Mainframe CICS transaction
- **Transaction Code**: TVS90
- **Technology**: COBOL copybooks, Host Access Framework, MNC
- **Purpose**: THE system of record for all customer accounts

### What PKVD Returns:
```
For Customer X, PKVD returns:
- Account 1: Girokonto Plus, IBAN: DE89..., Balance: €1,234.56
- Account 2: Sparkonto, IBAN: DE12..., Balance: €5,000.00
- Account 3: Kreditkarte, Card Number: 1234..., Limit: €2,000
- ... all accounts the customer owns
```

### How KWK Uses It:
```java
// This is what happens when user opens KWK page:

1. productService.retrieveProductList(KWK_REWARDCREDIT_FILTER)
   └─→ PkvdProductIdentifierRetrieverService
       └─→ personKundeVertragsDatenV2Hostaccess.callService()
           └─→ **MAINFRAME CALL** 🔴
               └─→ Returns: ALL customer accounts
               
2. Filter to show only accounts with REWARDCREDIT permission

3. Convert account numbers to IBAN format

4. Display to user in dropdown
```

### Caching:
- **Cache Name**: PersonKundeVertragsDatenCache
- **TTL**: 30 minutes
- **Risk**: User may see stale data if account just opened/closed

---

## 🚨 Why This Matters for Migration

### Problem 1: You Can't Just Copy Data
```
❌ WRONG APPROACH:
"Let's export the account data and put it in our microservice database"

WHY IT'S WRONG:
- Accounts are created by OTHER systems (branch, online banking, mobile)
- They change constantly (balances, status, permissions)
- New accounts appear, old accounts close
- The mainframe is THE authoritative source
```

### Problem 2: Real-Time Dependency
```
User opens account at 10:00 AM
└─→ Account created in mainframe at 10:00 AM
    └─→ If you have a copy, it won't have the new account
        └─→ User can't select it for KWK reward
            └─→ Bad user experience
```

### Problem 3: Data Consistency
```
Mainframe: Account balance = €1,000
Your copy:  Account balance = €950 (from yesterday)

User selects account thinking they have €1,000
→ Confusion and support calls
```

---

## ✅ RECOMMENDED MIGRATION STRATEGY

### Phase 1: Extract KWK Logic (Months 1-2)
1. ✅ Migrate CUSTOMER_REFER_CUSTOMER table
2. ✅ Extract business logic (referral code generation, validation)
3. ✅ Extract REST endpoints
4. ✅ Extract React frontend components
5. ✅ Set up new microservice infrastructure

### Phase 2: Handle External Dependencies (Months 3-4)
1. ⚠️ **Create or use existing "Account API"** wrapper around PKVD
   - This is the KEY piece
   - Microservice calls REST API instead of direct PKVD
   - API handles mainframe calls, caching, circuit breakers
   
2. ✅ Connect to existing SC services via API gateway:
   - Natural Person API
   - Customers API
   - IBAN Converter
   - Authorization Service
   - Juridical Logging

### Phase 3: Testing and Deployment (Months 5-6)
1. Integration tests with mock mainframe
2. Load testing (mainframe has capacity limits!)
3. Fallback testing (what if mainframe is down?)
4. Gradual rollout with feature flags

---

## 🎯 Three Migration Options for Account Data

### Option A: API Wrapper (RECOMMENDED) ✅
```
KWK Microservice → Account API → PKVD → Mainframe
```
**Pros**: 
- Always fresh data
- Mainframe stays system of record
- Lowest risk
- Can be implemented quickly

**Cons**:
- Still dependent on mainframe
- Network latency

**Effort**: 2-3 weeks

---

### Option B: Data Replication (COMPLEX) ⚠️
```
Mainframe → CDC → Kafka → KWK Microservice DB
```
**Pros**:
- Local data copy
- Fast queries
- Can work if mainframe briefly down

**Cons**:
- VERY complex to implement
- Eventual consistency issues
- Requires CDC from mainframe (needs mainframe team)
- Sync lag

**Effort**: 3-6 months + mainframe team cooperation

---

### Option C: Hybrid Caching (BALANCED) 🔄
```
KWK Microservice → Redis (5 min cache) → Account API → PKVD
```
**Pros**:
- Reduced mainframe calls
- Better performance
- Still gets fresh data

**Cons**:
- More complex than Option A
- Still depends on mainframe

**Effort**: 3-4 weeks

---

## 📋 Migration Checklist

### Must Understand
- [x] ✅ Account data comes from mainframe (not database)
- [x] ✅ PKVD is the system of record
- [x] ✅ KWK only READS accounts, never creates them
- [x] ✅ Data is cached for 30 minutes currently

### Must Decide
- [ ] ⚠️ Which account data strategy? (A, B, or C?)
- [ ] ⚠️ Keep direct mainframe access or use wrapper?
- [ ] ⚠️ Cache strategy in new microservice?
- [ ] ⚠️ Fallback behavior if mainframe unavailable?

### Must Implement
- [ ] 🔧 CUSTOMER_REFER_CUSTOMER table migration
- [ ] 🔧 Business logic extraction
- [ ] 🔧 Account data access (via API)
- [ ] 🔧 SC service integration (API gateway)
- [ ] 🔧 Frontend migration
- [ ] 🔧 Caching layer (Redis)
- [ ] 🔧 Circuit breakers for external calls
- [ ] 🔧 Logging and monitoring
- [ ] 🔧 Integration tests
- [ ] 🔧 Load tests (mainframe capacity!)

### Must Test
- [ ] 🧪 Mainframe down scenario
- [ ] 🧪 Stale cache scenario
- [ ] 🧪 New account opening flow
- [ ] 🧪 Account closing flow
- [ ] 🧪 Permission changes
- [ ] 🧪 High load (1000+ concurrent users)

---

## 💡 Key Insights

1. **KWK is NOT a self-contained application** - it's heavily dependent on external systems

2. **The mainframe dependency is NOT optional** - you MUST access it somehow

3. **"Migrating to microservice" doesn't mean "becoming independent"** - you'll still need the mainframe

4. **The real work is NOT the code** - it's handling the external dependencies properly

5. **This is common in banking** - core data lives in mainframe, applications just query it

---

## 🎓 What We Learned

### Before Investigation:
```
❌ "Account data is in the database, we'll just migrate the tables"
```

### After Investigation:
```
✅ "Account data lives in mainframe
   PKVD service provides it
   We cache it for 30 minutes
   We must keep calling it or replicate (complex)
   This is the biggest migration challenge"
```

---

## 📞 Who to Talk To

1. **Mainframe Team** - Understand PKVD capacity, SLAs, future plans
2. **Account API Team** - Check if wrapper already exists
3. **Architecture Team** - Decide on migration strategy
4. **Infrastructure Team** - Set up API gateway, Redis cache
5. **Security Team** - Mainframe credentials, certificates, access

---

## 🚀 Next Steps

1. **Review this document** with architecture team
2. **Decide on account data strategy** (A, B, or C)
3. **Check if Account API already exists** (may not need to build)
4. **Create detailed technical design** based on chosen strategy
5. **Prototype the mainframe/API integration** first (de-risk)
6. **Start with frontend extraction** (can be done in parallel)

---

## ⚠️ RISKS

| Risk | Impact | Mitigation |
|------|--------|------------|
| Mainframe unavailable | 🔴 HIGH | Circuit breakers, graceful degradation |
| Stale cache data | 🟡 MEDIUM | Shorter TTL, cache invalidation |
| Performance degradation | 🟡 MEDIUM | Aggressive caching, load testing |
| Missing new accounts | 🟡 MEDIUM | Shorter cache TTL, real-time sync |
| Migration takes too long | 🟠 HIGH | Start with Option A (simplest) |
| Mainframe team unresponsive | 🔴 HIGH | Get buy-in early, escalate if needed |

---

## 📚 Related Documents

- `07-kwk-business-flow-and-data-sources.md` - Complete technical flow
- `03-dependency-map.md` - All KWK dependencies
- `04-frontend-build-flow.md` - Frontend bundle creation
- `02-migration-plan.md` - Overall migration plan

---

## Final Recommendation

**Start Simple, Iterate:**
1. Month 1-2: Migrate database + business logic + frontend
2. Month 2-3: Connect to existing Account API (or create wrapper)
3. Month 3-4: Add Redis caching for performance
4. Month 4-6: Testing, optimization, gradual rollout
5. Future: Consider data replication if needed (complex!)

**Don't try to solve the mainframe problem perfectly on day 1.**  
**Get it working with API wrapper first, optimize later.**

---

*This document answers your critical question: "Where does the data come from? Who put it in the database?"*

*Answer: The account data comes from the **mainframe**, put there by **account opening systems**, accessed by **PKVD service**, and **KWK just reads it**.*

