# CODE PATTERNS REFERENCE

This document provides code patterns to help quickly identify data sources in the monolith.

---

## 🔍 Pattern 1: MAINFRAME ACCESS

### File Location Patterns
```
sc/*/host/src/main/java/**/*Hostaccess.java
sc/*/host/src/main/java/**/*HostService.java
ccb/middletier/*/host/**/*Hostaccess.java
```

### Code Signature
```java
// Imports to look for
import com.commerzbank.frame.hostaccess.*;
import com.commerzbank.frame.hostaccess.DataProvider;
import com.commerzbank.frame.hostaccess.RequestTemplate;

// Class pattern
public class PersonKundeVertragsDatenV2Hostaccess extends BasePersonKundeVertragsDatenV2Hostaccess {
    
    @Override
    protected RequestTemplate buildRequestForPersonKundeVertragsDaten(...) {
        // Builds mainframe request
    }
    
    @Override
    protected SomeReply processResponseForPersonKundeVertragsDaten(...) {
        // Parses mainframe response
    }
}

// Usage pattern
@Inject
@Named("personKundeVertragsDatenV2")
private PersonKundeVertragsDatenV2Hostaccess hostaccess;

SomeReply reply = hostaccess.callService(request);
```

### Common Mainframe Service Names
- `PKVD` - PersonKundeVertragsDaten (Customer accounts)
- `TVS90` - Transaction code
- `Kunig` - KundenInformationsGesellschaft
- Any class with "Host" or "Hostaccess" in name

### What This Means
⚠️ **CRITICAL**: This accesses **mainframe (IBM z/OS)**
- Data comes from COBOL/CICS applications
- This is the **system of record**
- Must be replaced with REST API for migration

---

## 🔍 Pattern 2: DATABASE ACCESS (JPA/Hibernate)

### File Location Patterns
```
**/dao/**/*DAO.java
**/dao/**/*DAOImpl.java
**/entity/**/*.java
**/domain/**/*Entity.java
```

### Code Signature - Entity
```java
import javax.persistence.*;

@Entity
@Table(name = "CUSTOMER_REFER_CUSTOMER")
public class CustomerReferCustomer {
    
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "CRC_ID_GENERATOR")
    @SequenceGenerator(name = "CRC_ID_GENERATOR", sequenceName = "SEQ_CRC_ID")
    @Column(name = "CRC_ID")
    private Long id;
    
    @Column(name = "CRC_CODE")
    private String crcCode;
    
    // More fields...
}
```

### Code Signature - DAO
```java
import com.commerzbank.frame.dbaccess.AbstractJpaDAO;

@CCBComponent
public class KwkDAOImpl extends AbstractJpaDAO<CustomerReferCustomer, Long> implements KwkDAO {
    
    @Override
    public void saveCrcData(CustomerReferCustomer entity) {
        EntityManager em = getEntityManager();
        super.insert(entity);
    }
    
    @Override
    public CrcData retrieveData(String code) {
        List<CustomerReferCustomer> list = entityManager
            .createQuery("select c from CustomerReferCustomer c where c.crcCode=:code")
            .setParameter("code", code)
            .getResultList();
        // ...
    }
}
```

### What This Means
✅ **Can Migrate**: This is application-owned data
- Table exists in local Oracle/DB2 database
- Schema can be exported and migrated
- This is NOT system of record for accounts/customers

---

## 🔍 Pattern 3: SC SERVICE CALLS

### File Location Patterns
```
sc/*/api/src/main/java/**/*Service.java (interface)
sc/*/service/src/main/java/**/*ServiceImpl.java (implementation)
```

### Code Signature - Service Interface
```java
package com.commerzbank.ccb.sc.person.api.service;

public interface NaturalPersonAPIV3Service {
    RetrieveNaturalPersonV3ServiceResponse retrieveNaturalPersons(String npKenn);
}
```

### Code Signature - Service Usage
```java
// In Process or Service class
@Inject
@Named("naturalPersonAPIV3Service")
private NaturalPersonAPIV3Service naturalPersonService;

// Later in code
RetrieveNaturalPersonV3ServiceResponse response = 
    this.naturalPersonService.retrieveNaturalPersons(participant.getNpKenn());
    
String firstName = response.getNaturalPerson().getPerson().getFirstName();
String lastName = response.getNaturalPerson().getPerson().getLastName();
```

### What This Means
🔄 **Need to Check**: SC service may call:
- Mainframe (trace further)
- Database (trace further)
- External API (good!)
- Another SC service (trace further)

**Action**: Find the `*ServiceImpl.java` and check what IT calls

---

## 🔍 Pattern 4: REST CLIENT CALLS

### File Location Patterns
```
**/remote/**/*RestClient.java
**/remote/**/*Client.java
**/client/**/*RestClient.java
```

### Code Signature
```java
import org.springframework.web.client.RestTemplate;
import com.commerzbank.ccb.fw.mt.api.rest.ApiBankingRestTemplate;

public class DatalakeTransactionsSearchRestClient {
    
    @Inject
    @Named("paymentsApiBankingRestTemplate")
    private ApiBankingRestTemplate restTemplate;
    
    @Value("${apiManagement.baseUrl}")
    private String apiBaseURL;
    
    public SomeResponse callExternalAPI(SomeRequest request) {
        String url = apiBaseURL + "/api/v1/endpoint";
        
        ResponseEntity<SomeResponse> response = restTemplate.exchange(
            url, 
            HttpMethod.POST, 
            request, 
            headers,
            SomeResponse.class, 
            null, 
            null
        );
        
        return response.getBody();
    }
}
```

### What This Means
✅ **Already Good**: This is the target pattern
- Already calling REST API
- Document the endpoint
- May be able to reuse in microservice

---

## 🔍 Pattern 5: PROCESS LAYER

### File Location Patterns
```
ccb/middletier/process/*/src/main/java/**/*ProcessImpl.java
ucc/*/process/src/main/java/**/*ProcessImpl.java
```

### Code Signature
```java
import com.commerzbank.ccb.fw.shared.api.annotation.CCBProcess;
import com.commerzbank.ccb.framework.base.annotations.CCBTransactionalProcess;

@CCBProcess
@CCBTransactionalProcess
public class CustomerReferCustomerProcessImpl extends BaseProcess 
    implements CustomerReferCustomerProcess {
    
    // Injected dependencies (THESE ARE KEY!)
    @Inject
    @Named("kwkService")
    private CustomerReferCustomerService kwkService;  // ← Check this
    
    @Inject
    @Named("participantService")
    private ParticipantService participantService;    // ← Check this
    
    @Inject
    @Named("naturalPersonAPIV3Service")
    private NaturalPersonAPIV3Service personService;  // ← Check this
    
    @Override
    public SendReferenceResponse sendReference(SendReferenceRequest request) {
        // Business logic here
        
        // Calls to services
        Participant participant = participantService.retrieveParticipantData(userId);
        PersonResponse person = personService.retrieveNaturalPersons(npKenn);
        kwkService.saveCrcData(data);
        
        return response;
    }
}
```

### What to Extract
1. **All @Inject @Named fields** - These are dependencies
2. **Method calls** - What operations are performed
3. **Data transformations** - What data is needed/produced

---

## 🔍 Pattern 6: REST CONTROLLERS

### File Location Patterns
```
ccb/ui/*/rest/src/main/java/**/*Controller.java
ccb/ui/*/rest/src/main/java/**/*JsonController.java
ucc/*/process/src/main/java/**/*Controller.java
ucc/*/ui/src/main/java/**/*Controller.java
```

### Code Signature
```java
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.*;

@Controller
@RequestMapping()  // or @RequestMapping("/api")
public class CrcJsonController extends AbstractJsonController {
    
    @Inject
    @Named("customerReferCustomerProcess")
    private CustomerReferCustomerProcess crcProcess;
    
    @RequestMapping(
        value = "/sendReference",    // ← ENDPOINT
        method = RequestMethod.POST,
        produces = "application/json;charset=utf-8"
    )
    @ResponseBody
    public JsonResponse sendReference(@RequestBody SendReferenceRequest request) {
        // Validate
        if (request == null) {
            return new JsonResponse(error);
        }
        
        // Call process
        SendReferenceResponse response = this.crcProcess.sendReference(request);
        
        // Build response
        return new JsonResponse(result);
    }
}
```

### What to Extract
1. **Endpoint path**: `value = "/sendReference"`
2. **HTTP method**: `POST`, `GET`, `PUT`, `DELETE`
3. **Request DTO**: `SendReferenceRequest` class
4. **Response DTO**: `SendReferenceResponse` class
5. **Process called**: `crcProcess.sendReference()`

---

## 🔍 Pattern 7: REQUEST/RESPONSE DTOs

### File Location Patterns
```
**/processinterface/request/**/*.java
**/processinterface/response/**/*.java
**/dto/**/*.java
**/domain/**/*.java (if not entity)
```

### Code Signature - Request
```java
public class SendReferenceRequest implements Serializable {
    
    @IbanDE
    private String chosenIban;           // ← Field needed
    
    @GenericDescription(max = 256)
    private String chosenAccountOwnerName;  // ← Field needed
    
    @EmailAddress
    private String crcEmailAddress;      // ← Field needed
    
    // Getters and setters...
}
```

### What to Extract
- **Field names**: `chosenIban`, `chosenAccountOwnerName`
- **Validation annotations**: `@IbanDE`, `@EmailAddress`
- **Data types**: `String`, `Integer`, `Boolean`
- **These are the data requirements!**

---

## 🎯 QUICK IDENTIFICATION CHECKLIST

When you see this code pattern → Data source is:

| Code Pattern | Data Source | Action |
|--------------|-------------|--------|
| `extends ...Hostaccess` | ⚠️ MAINFRAME | Need REST API |
| `@Entity @Table` | ✅ DATABASE | Can migrate |
| `AbstractJpaDAO` | ✅ DATABASE | Can migrate |
| `EntityManager` | ✅ DATABASE | Can migrate |
| `RestTemplate.exchange()` | ✅ REST API | Already good |
| `@Named("...Service")` | 🔄 SC SERVICE | Trace further |
| `@Inject @Named` | 🔄 DEPENDENCY | Check type |

---

## 📊 DATA FLOW TRACING EXAMPLE

```
Controller
  ↓ calls
Process
  ↓ calls
Service (check name pattern)
  ↓
  ├─→ Ends in "DAO" → DATABASE ✅
  ├─→ Ends in "Hostaccess" → MAINFRAME ⚠️
  ├─→ Ends in "RestClient" → REST API ✅
  └─→ Ends in "Service" → 🔄 Trace further
          ↓ Check implementation
          Service Impl
              ↓ calls
              [Repeat pattern matching]
```

---

## 🔑 KEY FILES TO ALWAYS CHECK

### 1. For UCC Apps:
```
ucc/[app]/process/src/main/java/**/*ProcessImpl.java     ← Start here
ucc/[app]/process-interface/src/main/java/**/request/*.java  ← Data in
ucc/[app]/process-interface/src/main/java/**/response/*.java ← Data out
```

### 2. For Legacy Apps:
```
ccb/ui/[bank]-webui/[app]/rest/**/*Controller.java       ← Start here
ccb/middletier/process/[app]/**/*ProcessImpl.java        ← Business logic
ccb/middletier/service/[app]/**/*ServiceImpl.java        ← Data access
ccb/middletier/service/[app]/**/dao/**/*DAOImpl.java     ← Database
```

### 3. For SC Services (when tracing):
```
sc/[service]/api/src/main/java/**/*Service.java          ← Interface
sc/[service]/service/src/main/java/**/*ServiceImpl.java  ← Implementation
sc/[service]/remote/src/main/java/**/*RestClient.java    ← External calls
sc/[service]/host/src/main/java/**/*Hostaccess.java      ← Mainframe calls
```

---

*Use these patterns to quickly identify data sources without reading every line of code.*

