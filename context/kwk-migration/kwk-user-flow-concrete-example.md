# KWK User Flow: Complete Journey from Browser to Backend

**Date:** November 6, 2025  
**Purpose:** Concrete end-to-end user flow with real file paths, function names, and data flow

---

## Scenario: Customer Sends a Referral via Email

**User Story:** Maria opens the KWK (Kunden Werben Kunden / Customer Refer Customer) page in her browser, selects a product and reward, enters her friend's email address, and clicks "Send". The system generates a unique referral code and redirects her to a confirmation page.

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User Opens Browser                                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: HTTP Request to KWK Page                                │
│ URL: https://banking.commerzbank.de/portal/kwk                  │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Java Page Controller Handles Request                    │
│ File: KWKOverviewPage.java                                      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: HTML Page Rendered with React Container                 │
│ Browser receives HTML with <div id="kwkReactContainer">         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: React Bundle Loads and Executes                         │
│ File: lib_kwk-page-bundle.js                                    │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: User Interacts with React UI                            │
│ Component: KwKPanel.js                                           │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: User Clicks Send → React Makes REST API Call            │
│ POST /banking/rest/sendReference                                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: REST Controller Receives Request                        │
│ File: CrcJsonController.java                                    │
│ Method: sendReference()                                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 9: Process Layer Handles Business Logic                    │
│ File: CustomerReferCustomerProcessImpl.java                     │
│ Method: sendReference()                                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 10: Service Layer Persists Data                            │
│ File: CustomerReferCustomerService.java                         │
│ Method: saveCrcData()                                            │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 11: Response Returns to React                              │
│ JSON: { "result": { "items": [{ "crcCode": "ABC123" }] } }      │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 12: React Redirects to Confirmation Page                   │
│ Component: KwKPanel.redirectToConfirmationPage()                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Step-by-Step Breakdown

### STEP 1: User Opens Browser

**Action:** Maria types the URL or clicks a link  
**URL:** `https://banking.commerzbank.de/portal/kwk`  
**Browser:** Chrome, Firefox, Safari, etc.

---

### STEP 2: HTTP GET Request

**Request:**
```http
GET /portal/kwk HTTP/1.1
Host: banking.commerzbank.de
Cookie: JSESSIONID=ABC123...
Accept: text/html
```

**What Happens:**
- Request hits the application server (likely Tomcat/JBoss)
- Spring MVC routing directs request to Wicket framework
- Wicket page mounting resolves URL to Java page class

---

### STEP 3: Java Page Controller Initializes

**File:** `C:\CCB\sources\portal\ccb\ui\pk-webui\kwk\ui\src\main\java\com\commerzbank\ccb\kwk\KWKOverviewPage.java`

**Class:** `KWKOverviewPage extends BasePage<KWKOverviewPageModel> implements ReactPage`

**Constructor Called:**
```java
public KWKOverviewPage(PageParameters pageParameters) {
    super(pageParameters, PAGE_ID);
    super.setFunctionId(PAGE_ID);
    setModel(Model.of(new KWKOverviewPageModel()));
}
```
- `PAGE_ID = "ccb.kundenwerbenkunden"`
- Creates page model for data binding

**onInitialize() Method Executes:**
```java
@Override
protected void onInitialize() {
    super.onInitialize();
    
    // 1. Load configuration from CMS
    Properties includeProps = getIncludeProperties();
    String kwkJson = includeProps.getProperty("kwk");
    
    // 2. Validate products and check customer eligibility
    this.kwkDispatcher.getValidCrcProductList(this, createsErrorPageURL(ERROR_ID1), kwkJson);
    
    // 3. Check if customer is employee (employees not eligible)
    boolean isEmployee = this.kwkDispatcher.isEmployee();
    if (isEmployee) {
        redirectToErrorPage("ER3");
        return;
    }
    
    // 4. Initialize page model
    getModelObject().init();
    
    // 5. Add React bundle loader
    add(new ReactjsLoaderBehavior("kwk-page"));
    
    // 6. Add CMS content includes (wi1, ci1, ci2, ci3, wi2)
    add(new ContentIncludePanel(W_ID1, PAGE_ID, W_ID1, model));
    add(new ContentIncludePanel(CONTENT_INCLUDE1_ID, ...));
    
    // 7. Add main container panel
    add(new KWKOverviewContainerPanel("kwkContainerPanel", 
        new KWKOverviewContainerModel().bind(getModel())));
}
```

**Key Dependencies Injected:**
```java
@SpringBean
private CrcDispatcher kwkDispatcher;
```

**getDataForReact() Method Provides Initial Data:**
```java
@Override
public Serializable getDataForReact() {
    Properties includeProps = getIncludeProperties();
    String kwkJson = includeProps.getProperty("kwk");
    
    // Retrieve dropdown data (products, accounts, rewards)
    JsonResponse jsonResponse = this.kwkDispatcher.retrieveDropdownData(
        this, 
        createsErrorPageURL(ERROR_ID1), 
        kwkJson
    );
    
    // Check for errors
    if (jsonResponse.getError() != null) {
        String errorCode = jsonResponse.getError().getCode();
        if (errorCode.equals("NO_VALID_SETTLEMENT_ACCOUNT")) {
            redirectToErrorPage("ER2");
        }
    }
    
    return jsonResponse; // Serialized to JSON for React
}
```

**getTranslationsForReact() Provides i18n:**
```java
@Override
public Map<String, String> getTranslationsForReact() {
    return getTranslations(this.transactionKeys);
}
```

**Translation Keys:**
```java
private String[] transactionKeys = new String[] {
    "header", 
    "lblProductAndReward", 
    "lblRecommendedProduct", 
    "lblYourReward",
    "lblAccount", 
    "lblEmailAddress", 
    "lblSend", 
    "txtExpiry", 
    "emailInvalid", 
    "emailEmpty", 
    "emailText1", 
    "emailText2",
    // ... more translation keys
};
```

---

### STEP 4: HTML Response Generated

**What the Browser Receives:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Kunden werben Kunden</title>
    <link rel="stylesheet" href="/portal/media/system/css/main.css">
    <!-- Additional CSS, meta tags, etc. -->
</head>
<body>
    <!-- Header, navigation, etc. -->
    
    <!-- React Container -->
    <div id="kwkReactContainer"></div>
    
    <!-- CMS Content Includes -->
    <div id="wi1"><!-- Advertisement slot 1 --></div>
    <div id="ci1"><!-- Content include 1 --></div>
    <div id="ci2"><!-- Content include 2 --></div>
    <div id="ci3"><!-- Content include 3 --></div>
    <div id="wi2"><!-- Advertisement slot 2 --></div>
    
    <!-- React Data (serialized JSON) -->
    <script>
        window.getReactData = function() {
            return {
                "result": {
                    "items": [{
                        "products": [
                            {
                                "id": "1",
                                "productNameDropdown": "Girokonto Plus",
                                "rewards": [
                                    {
                                        "id": "101",
                                        "reward": "50 EUR",
                                        "maxAvailabilityTime": "31.12.2025"
                                    },
                                    {
                                        "id": "102",
                                        "reward": "100 EUR",
                                        "maxAvailabilityTime": "31.12.2025"
                                    }
                                ],
                                "errorPageUrlForGeneralTechnicalError": "/portal/error/ER1"
                            },
                            {
                                "id": "2",
                                "productNameDropdown": "Depot",
                                "rewards": [...]
                            }
                        ],
                        "accounts": [
                            {
                                "iban": "DE89370400440532013000",
                                "accountDisplayName": "Girokonto",
                                "accountOwnerName": "Maria Mustermann"
                            }
                        ]
                    }]
                }
            };
        };
        
        window.getReactTranslations = function() {
            return {
                "header": "Kunden werben Kunden",
                "lblProductAndReward": "Produkt und Prämie",
                "lblRecommendedProduct": "Empfohlenes Produkt",
                "lblYourReward": "Ihre Prämie",
                "lblAccount": "Konto",
                "lblEmailAddress": "E-Mail-Adresse",
                "lblSend": "Absenden",
                // ... more translations
            };
        };
    </script>
    
    <!-- Load React Bundle -->
    <script src="/portal/media/system/js/lib_kwk-page-bundle.js"></script>
</body>
</html>
```

---

### STEP 5: React Bundle Loads and Executes

**File Loaded:** `C:\CCB\sources\portal\ui-react\src\main\webapp\WEB-INF\resources\media\system\js\lib_kwk-page-bundle.js`

**Built From:** `C:\CCB\sources\portal\ui-react\src\main\webapp\WEB-INF\resources\media\react\parent_comp\kwk-page.js`

**kwk-page.js Source Code:**
```javascript
// Import React library
import React from 'react';

// Import main KWK panel component
import KwKPanel from 'parent/kwk/kwkpanel';

// Render React app to DOM
React.render(
    <KwKPanel/>, 
    document.getElementById('kwkReactContainer')
);
```

**What Happens:**
1. Bundle executes immediately when loaded
2. Finds DOM element with id `kwkReactContainer`
3. Renders `<KwKPanel/>` component into that element
4. React component tree is mounted

---

### STEP 6: KwKPanel Component Initializes

**File:** `C:\CCB\sources\portal\ui-react\src\main\webapp\WEB-INF\resources\media\react\parent_comp\kwk\kwkpanel.js`

**Class:** `KwKPanel extends React.Component`

**Constructor Executes:**
```javascript
constructor(props) {
    super(props);
    
    // Initialize state variables
    this.selectionConfiguration = [];
    this.productSelections = [];
    this.accountSelections = [];
    this.productList = [];
    this.accountList = [];
    this.kwkCode = '';
    this.targetApp = 'email';
    this.isMobile = /iPhone|Android/.test(navigator.userAgent) && !window.MSStream;

    this.state = {
        selectedProduct: {},
        selectedAccount: {},
        selectedReward: {},
        maxAvailabilityTime: '',
        showLoadingIndicator: false,
        rewardList: [],
        inputIsValidating: false,
        whatsappMsg: '',
        showWhatsapp: this.isMobile,
    };
    
    // Get data from window object (provided by Java page)
    this.reactData = window.getReactData();
    this.translations = window.getReactTranslations();
}
```

**componentDidMount() Initializes Data:**
```javascript
componentDidMount() {
    // Extract products and accounts from reactData
    const products = this.reactData.result.items[0].products;
    const accounts = this.reactData.result.items[0].accounts;
    
    // Transform data for dropdowns
    this.productList = this.transformToProductList(products);
    this.accountList = this.transformToAccountList(accounts);
    this.productSelections = products;
    this.accountSelections = accounts;
    
    // Check URL parameters for pre-selection
    const selectedData = this.getProductSelectionBasedOnParameters(products);
    
    // Set initial state
    this.setState({
        selectedProduct: selectedData.selectedProduct,
        selectedReward: selectedData.selectedReward,
        selectedAccount: accounts[0],
        maxAvailabilityTime: selectedData.selectedReward.maxAvailabilityTime,
        rewardList: this.transformToRewardList(selectedData.selectedProduct.rewards)
    });
}
```

**UI Renders:**
```javascript
render() {
    return (
        <div className="kwk-panel">
            <PageHeading text={this.translations.header} />
            
            {/* Product Selection Dropdown */}
            <KwKSelection
                label={this.translations.lblRecommendedProduct}
                options={this.productList}
                selectedId={this.state.selectedProduct.id}
                onChange={(id) => this.onProductChange(id)}
            />
            
            {/* Reward Selection Dropdown */}
            <KwKSelection
                label={this.translations.lblYourReward}
                options={this.state.rewardList}
                selectedId={this.state.selectedReward.id}
                onChange={(id) => this.onRewardChange(id)}
            />
            
            {/* Account Selection Dropdown */}
            <KwKSelection
                label={this.translations.lblAccount}
                options={this.accountList}
                selectedId={this.state.selectedAccount.iban}
                onChange={(id) => this.onAccountChange(id)}
            />
            
            {/* Email Input Field */}
            <div className="form-group">
                <label>{this.translations.lblEmailAddress}</label>
                <input 
                    type="email" 
                    id="kwkMail" 
                    className="form-control"
                    placeholder="freund@example.com"
                />
            </div>
            
            {/* Send Button */}
            <Button
                text={this.translations.lblSend}
                onClick={() => this.sendReference('email')}
                disabled={this.state.showLoadingIndicator}
            />
            
            {/* WhatsApp Button (mobile only) */}
            {this.state.showWhatsapp && (
                <WhatsAppButton
                    onClick={() => this.openWhatsapp()}
                />
            )}
            
            {/* Loading Indicator */}
            {this.state.showLoadingIndicator && (
                <LoadingIndicator />
            )}
            
            {/* Expiry Text */}
            <p className="expiry-text">
                {this.translations.txtExpiry}: {this.state.maxAvailabilityTime}
            </p>
        </div>
    );
}
```

**User Interaction - Product Selection:**
```javascript
onProductChange(selectedId) {
    // Find product by ID
    const productSelection = this.fetchSelectionFromId(
        selectedId, 
        this.productSelections
    );

    // Update state with new product and its first reward
    this.setState({
        selectedProduct: productSelection,
        selectedReward: productSelection.rewards[0],
        maxAvailabilityTime: productSelection.rewards[0].maxAvailabilityTime,
        rewardList: this.transformToRewardList(productSelection.rewards),
    });
}
```

**User Interaction - Reward Selection:**
```javascript
onRewardChange(selectedId) {
    // Find reward by ID
    const rewardSelection = this.fetchSelectionFromId(
        selectedId, 
        this.state.selectedProduct.rewards
    );
    
    // Update state
    this.setState({
        selectedReward: rewardSelection,
        maxAvailabilityTime: rewardSelection.maxAvailabilityTime,
    });
}
```

**User Interaction - Account Selection:**
```javascript
onAccountChange(selectedId) {
    // Find account by IBAN
    const accountSelection = this.fetchSelectionFromIban(
        selectedId, 
        this.accountSelections
    );
    
    // Update state
    this.setState({
        selectedAccount: accountSelection,
    });
}
```

---

### STEP 7: User Clicks "Send" Button

**User Actions:**
1. Maria selects "Girokonto Plus" as product
2. Selects "100 EUR" as reward
3. Selects her account "DE89370400440532013000"
4. Enters friend's email: "anna@example.com"
5. Clicks "Absenden" (Send) button

**Click Handler Executes:**
```javascript
// Button onClick={() => this.sendReference('email')}
```

**sendReference() Method:**
```javascript
sendReference(targetApp = 'email') {
    // Set target application type
    this.targetApp = targetApp;
    
    // Get error page URL from config
    const navigateToERROR = this.reactData.result.items[0]['products'][0]['errorPageUrlForGeneralTechnicalError'];
    
    // Get email value from input field
    const kwkMail = $('#kwkMail').val();
    
    // Build request body
    const reqBody = {
        'chosenAccountOwnerName': this.state.selectedAccount.accountDisplayName,
        'chosenBounty': this.state.selectedReward.reward,
        'chosenBountyId': this.state.selectedReward.id,
        'chosenIban': this.state.selectedAccount.iban,
        'chosenProductId': this.state.selectedProduct.id,
        'chosenProductName': this.state.selectedProduct.productNameDropdown,
        'crcEmailAddress': kwkMail ? kwkMail : ''
    };
    
    // API endpoint URL
    const url = '/banking/rest/sendReference';
    
    // Make POST request using internal API utility
    api.post(url, reqBody, (err, response) => {
        if (err) {
            // Handle error - redirect to error page
            window.open(navigateToERROR, '_self');
        } else {
            // Handle success response
            if (response.result === undefined) {
                // XML error response
                window.open(response.firstChild.textContent, '_self');
            } else {
                // Extract generated referral code
                this.kwkCode = response.result.items[0].crcCode;
                
                // Redirect based on target app
                if (this.targetApp === 'qr-code-sms') {
                    this.generateSMSQRCodeToConfirmationPage(this.targetApp);
                } else if (this.targetApp === 'qr-code-whatsapp') {
                    this.generateQRCodeToConfirmationPage(this.targetApp);
                } else {
                    // Email flow
                    this.redirectToConfirmationPage();
                }
            }
        }
    });
}
```

**Request Sent:**
```http
POST /banking/rest/sendReference HTTP/1.1
Host: banking.commerzbank.de
Content-Type: application/json
Cookie: JSESSIONID=ABC123...

{
    "chosenAccountOwnerName": "Girokonto",
    "chosenBounty": "100 EUR",
    "chosenBountyId": "102",
    "chosenIban": "DE89370400440532013000",
    "chosenProductId": "1",
    "chosenProductName": "Girokonto Plus",
    "crcEmailAddress": "anna@example.com"
}
```

---

### STEP 8: REST Controller Receives Request

**File:** `C:\CCB\sources\portal\ccb\ui\pk-webui\kwk\rest\src\main\java\com\commerzbank\ccb\crc\rest\delegate\CrcJsonController.java`

**Class:** `CrcJsonController extends AbstractJsonController`

**Annotations:**
```java
@Controller
@RequestMapping()
public class CrcJsonController extends AbstractJsonController {
```

**Endpoint Method:**
```java
@RequestMapping(
    value = "/sendReference", 
    method = RequestMethod.POST, 
    produces = "application/json;charset=utf-8"
)
@ResponseBody
public JsonResponse sendReference(@RequestBody SendReferenceRequest request) {
    
    // 1. Validate request is not null
    if (request == null) {
        JsonError error = new JsonError("911", "The request is null");
        LOG.warn("Request is null");
        return new JsonResponse(error);
    }
    
    // 2. Handle empty email address
    if (StringUtils.isBlank(request.getCrcEmailAddress())) {
        request.setCrcEmailAddress(null);
    }
    
    // 3. Call process layer
    SendReferenceResponse sendReferenceResponse = 
        this.crcProcess.sendReference(request);
    
    // 4. Extract referral code from response
    String referalCode = sendReferenceResponse.getKwkCode();
    
    // 5. Validate referral code was generated
    if (StringUtils.isBlank(referalCode)) {
        JsonError error = new JsonError("912", "The referal code is null or empty");
        LOG.warn("Generated referal code is null");
        return new JsonResponse(error);
    }
    
    // 6. Build success response
    JsonResult result = new JsonResult();
    result.addItem(new CrcCodeDto(referalCode));
    
    return new JsonResponse(result);
}
```

**Dependencies:**
```java
@Inject
@Named("customerReferCustomerProcess")
private CustomerReferCustomerProcess crcProcess;
```

**Request Object Structure (SendReferenceRequest.java):**
```java
public class SendReferenceRequest {
    private String chosenAccountOwnerName;  // "Girokonto"
    private String chosenBounty;            // "100 EUR"
    private String chosenBountyId;          // "102"
    private String chosenIban;              // "DE89370400440532013000"
    private String chosenProductId;         // "1"
    private String chosenProductName;       // "Girokonto Plus"
    private String crcEmailAddress;         // "anna@example.com"
    
    // Getters and setters...
}
```

---

### STEP 9: Process Layer Executes Business Logic

**File:** `C:\CCB\sources\portal\ccb\middletier\process\kwk\src\main\java\com\commerzbank\ccb\kwk\process\CustomerReferCustomerProcessImpl.java`

**Class:** `CustomerReferCustomerProcessImpl extends BaseProcess implements CustomerReferCustomerProcess`

**Annotations:**
```java
@CCBProcess
@CCBTransactionalProcess
public class CustomerReferCustomerProcessImpl extends BaseProcess 
    implements CustomerReferCustomerProcess {
```

**Main Method:**
```java
@PreAuthorize("protect('REWARDCREDIT')")
@Override
@PermissionsCheckedInternal
public SendReferenceResponse sendReference(SendReferenceRequest sendReferenceRequest) {
    
    String errorText = HYPHEN;
    String kwkCode = generateUniqueReferrallCode();
    CrcData kwkData = new CrcData();
    
    try {
        // 1. Check authorization for selected IBAN
        checkAuthorizationForSelectedIban(sendReferenceRequest.getChosenIban());
        
        // 2. Build CRC data object
        kwkData.setAccountOwnerName(sendReferenceRequest.getChosenAccountOwnerName());
        kwkData.setBounty(sendReferenceRequest.getChosenBounty());
        kwkData.setBountyId(sendReferenceRequest.getChosenBountyId());
        kwkData.setAccountOwnerIban(sendReferenceRequest.getChosenIban());
        kwkData.setKwkCode(kwkCode);
        kwkData.setKwkEmailAddress(sendReferenceRequest.getCrcEmailAddress());
        kwkData.setProductName(sendReferenceRequest.getChosenProductName());
        kwkData.setProductId(sendReferenceRequest.getChosenProductId());
        kwkData.setDateOfCreation(new Date());
        
        // 3. Retrieve participant (customer) data
        Participant participant = this.participantService.retrieveParticipantData(
            getUserIdForFo()
        );
        
        if (participant != null) {
            kwkData.setNpkenn(participant.getNpKenn());
            
            // 4. Retrieve natural person data (name)
            RetrieveNaturalPersonV3ServiceResponse naturalPersonResponse = 
                this.naturalPersonAPIV3Service.retrieveNaturalPersons(
                    participant.getNpKenn()
                );
            
            if (naturalPersonResponse != null && 
                naturalPersonResponse.getNaturalPerson() != null) {
                
                kwkData.setProposerFirstname(
                    naturalPersonResponse.getNaturalPerson()
                        .getPerson().getFirstName()
                );
                kwkData.setProposerLastname(
                    naturalPersonResponse.getNaturalPerson()
                        .getPerson().getLastName()
                );
                
                LOG.debug("First and last name: {} and {}",
                    naturalPersonResponse.getNaturalPerson()
                        .getPerson().getFirstName(),
                    naturalPersonResponse.getNaturalPerson()
                        .getPerson().getLastName()
                );
            }
        }
        
        // 5. Save CRC data to database
        this.kwkService.saveCrcData(kwkData);
        
    } catch (Exception e) {
        errorText = CrcJuristicalLoggingErrorMessages.TECHNICAL_ERROR
            .getErrorMessage();
        LOG.debug(errorText + "{}", e);
    }
    
    // 6. Log transaction for juridical/compliance purposes
    logSelectedInformation(kwkData, errorText);
    
    // 7. Build and return response
    SendReferenceResponse sendReferenceResponse = new SendReferenceResponse();
    sendReferenceResponse.setKwkCode(kwkCode);
    
    return sendReferenceResponse;
}
```

**Authorization Check:**
```java
@InCodePermissionCheck
private void checkAuthorizationForSelectedIban(String chosenIban) {
    LOG.debug("start of checkAuthorizationForSelectedIban");
    
    // 1. Define product filter for KWK reward credit
    final List<ProductFilter> filter = new ArrayList<>();
    filter.add(ProductFilter.KWK_REWARDCREDIT_FILTER);
    
    // 2. Retrieve authorized products for current user
    final ProductList productList = this.productService.retrieveProductList(filter);
    
    if (productList != null && productList.getListOfProducts() != null) {
        final List<TnvProductEnvelope> allProducts = productList.getListOfProducts();
        
        if (CollectionUtils.isNotEmpty(allProducts)) {
            // 3. Check if chosen IBAN is in authorized list
            for (TnvProductEnvelope tnvProduct : allProducts) {
                String selectedIban = getIban(tnvProduct.getTechnicalAccountNumber());
                
                if (null != selectedIban && 
                    selectedIban.replaceAll(" ", "").equals(chosenIban)) {
                    // Authorization successful
                    return;
                }
            }
        }
    }
    
    // 4. Throw exception if IBAN not authorized
    throw new AccessDeniedException(
        "Selected Iban number " + chosenIban + " doesn't have access"
    );
}
```

**Generate Unique Referral Code:**
```java
private String generateUniqueReferrallCode() {
    boolean isUnique;
    StringBuilder kwkCode;
    
    do {
        // Generate random code
        kwkCode = generateReferralCode();
        
        // Check if code already exists in database
        isUnique = isKwkCodeIsUnique(kwkCode.toString());
        
    } while (!isUnique);
    
    return kwkCode.toString();
}

private static StringBuilder generateReferralCode() {
    // Allowed characters (no I, O, 0 to avoid confusion)
    String[] strAllowedCharacters = { 
        "1", "2", "3", "4", "5", "6", "7", "8", "9", 
        "A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "L", "M", 
        "N", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z" 
    };
    
    StringBuilder referralCode = new StringBuilder();
    
    // Generate 6-character code
    for (int i = 0; i < 6; i++) {
        referralCode.append(strAllowedCharacters[random.nextInt(32)]);
    }
    
    // Validate no character appears more than 3 times
    for (int i = 0; i < referralCode.length(); i++) {
        char currentCharacter = referralCode.charAt(i);
        int occurrences = countOccurrences(currentCharacter, referralCode.toString());
        
        if (occurrences > 3) {
            // Regenerate if validation fails
            return generateReferralCode();
        }
    }
    
    return referralCode;
}

private boolean isKwkCodeIsUnique(String kwkCode) {
    CrcData kwkData = this.kwkService.retrieveKwkData(kwkCode);
    return (kwkData == null);
}
```

**Dependencies Used:**
```java
@Inject
@Named("customerReferCustomerService")
private CustomerReferCustomerService kwkService;

@Inject
@Named("participantService")
private ParticipantService participantService;

@Inject
@Named("naturalPersonAPIV3Service")
private NaturalPersonAPIV3Service naturalPersonAPIV3Service;

@Inject
@Named("productService")
private ProductService productService;

@Inject
@Named("juristicalLoggingService")
private JuristicalLoggingService juristicalLoggingService;
```

**Service Layer Calls:**
- **ParticipantService** (from SC layer) - Gets customer participant data
- **NaturalPersonAPIV3Service** (from SC layer) - Gets customer name
- **ProductService** (from SC layer) - Validates authorized accounts
- **CustomerReferCustomerService** (from SC layer) - Persists CRC data to database

---

### STEP 10: Service Layer Persists Data

**File:** `C:\CCB\sources\portal\sc\[service-module]\src\main\java\com\commerzbank\ccb\kwk\service\CustomerReferCustomerService.java`

**Method Called:**
```java
public void saveCrcData(CrcData kwkData) {
    // 1. Map domain object to entity
    CrcEntity entity = mapper.toEntity(kwkData);
    
    // 2. Set additional fields
    entity.setCreatedBy(getCurrentUser());
    entity.setCreatedDate(new Date());
    entity.setStatus("ACTIVE");
    
    // 3. Persist to database
    crcRepository.save(entity);
    
    LOG.info("KWK referral code {} saved successfully", kwkData.getKwkCode());
}
```

**Database Table (Conceptual):**
```sql
CREATE TABLE CRC_DATA (
    ID                  BIGINT PRIMARY KEY,
    KWK_CODE            VARCHAR(6) UNIQUE NOT NULL,
    NPKENN              VARCHAR(20),
    PROPOSER_FIRSTNAME  VARCHAR(100),
    PROPOSER_LASTNAME   VARCHAR(100),
    ACCOUNT_OWNER_NAME  VARCHAR(200),
    ACCOUNT_OWNER_IBAN  VARCHAR(34),
    PRODUCT_ID          VARCHAR(10),
    PRODUCT_NAME        VARCHAR(200),
    BOUNTY_ID           VARCHAR(10),
    BOUNTY              VARCHAR(50),
    EMAIL_ADDRESS       VARCHAR(255),
    DATE_OF_CREATION    TIMESTAMP,
    STATUS              VARCHAR(20),
    CREATED_BY          VARCHAR(50),
    CREATED_DATE        TIMESTAMP
);
```

**Record Inserted:**
```sql
INSERT INTO CRC_DATA VALUES (
    12345,                          -- ID
    'AB3C7K',                       -- KWK_CODE
    '1000001234567',                -- NPKENN
    'Maria',                        -- PROPOSER_FIRSTNAME
    'Mustermann',                   -- PROPOSER_LASTNAME
    'Girokonto',                    -- ACCOUNT_OWNER_NAME
    'DE89370400440532013000',       -- ACCOUNT_OWNER_IBAN
    '1',                            -- PRODUCT_ID
    'Girokonto Plus',               -- PRODUCT_NAME
    '102',                          -- BOUNTY_ID
    '100 EUR',                      -- BOUNTY
    'anna@example.com',             -- EMAIL_ADDRESS
    '2025-11-06 14:32:15',          -- DATE_OF_CREATION
    'ACTIVE',                       -- STATUS
    'MARIA.MUSTERMANN',             -- CREATED_BY
    '2025-11-06 14:32:15'           -- CREATED_DATE
);
```

---

### STEP 11: Response Returns Through Layers

**Service Layer Returns:**
```java
// CustomerReferCustomerService.saveCrcData() completes
// Returns control to CustomerReferCustomerProcessImpl
```

**Process Layer Returns:**
```java
SendReferenceResponse sendReferenceResponse = new SendReferenceResponse();
sendReferenceResponse.setKwkCode("AB3C7K");
return sendReferenceResponse;
```

**REST Controller Returns:**
```java
JsonResult result = new JsonResult();
result.addItem(new CrcCodeDto("AB3C7K"));
return new JsonResponse(result);
```

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json;charset=utf-8

{
    "result": {
        "items": [
            {
                "crcCode": "AB3C7K"
            }
        ]
    }
}
```

---

### STEP 12: React Handles Response and Redirects

**Success Callback in KwKPanel:**
```javascript
api.post(url, reqBody, (err, response) => {
    if (!err && response.result) {
        // Extract referral code
        this.kwkCode = response.result.items[0].crcCode;  // "AB3C7K"
        
        // Redirect to confirmation page
        this.redirectToConfirmationPage();
    }
});
```

**Redirect Method:**
```javascript
redirectToConfirmationPage() {
    // 1. Build base URL
    let origin = '';
    if (!window.location.origin) {
        origin = window.location.protocol + '//' + 
                 window.location.hostname + 
                 (window.location.port ? ':' + window.location.port : '');
    } else {
        origin = window.location.origin;
    }
    
    // 2. Build confirmation page URL
    const navigateToURL = origin + window.location.pathname + '/confirmationpage';
    // Result: "https://banking.commerzbank.de/portal/kwk/confirmationpage"
    
    // 3. Store data in session storage
    sessionStorage.setItem('productId', this.state.selectedProduct['id']);
    sessionStorage.setItem('kwkCode', this.kwkCode);
    sessionStorage.setItem('targetApp', this.targetApp);
    
    // 4. Redirect with POST data
    Redirector.redirectWithData(
        navigateToURL, 
        {
            productId: this.state.selectedProduct['id'],  // "1"
            kwkCode: this.kwkCode,                        // "AB3C7K"
            targetApp: this.targetApp                     // "email"
        },
        'POST'
    );
}
```

**Browser Redirects:**
```http
POST /portal/kwk/confirmationpage HTTP/1.1
Host: banking.commerzbank.de
Content-Type: application/x-www-form-urlencoded

productId=1&kwkCode=AB3C7K&targetApp=email
```

---

### STEP 13: Confirmation Page Loads

**New Java Page Handles Request:**
- **File:** `C:\CCB\sources\portal\ccb\ui\pk-webui\kwk\ui\src\main\java\com\commerzbank\ccb\kwk\confirmationpage\KWKConfirmationPage.java`
- Loads new React bundle: `lib_kwkconfirmation-page-bundle.js`
- Displays confirmation message with referral code
- Shows sharing options (email template, copy link, etc.)

**Confirmation Page Shows:**
```
┌─────────────────────────────────────────────────────┐
│  ✓ Ihre Empfehlung wurde erfolgreich versendet!    │
│                                                     │
│  Ihr Empfehlungscode: AB3C7K                        │
│                                                     │
│  Eine E-Mail mit dem Empfehlungslink wurde an       │
│  anna@example.com gesendet.                         │
│                                                     │
│  [Weiteren Freund empfehlen]  [Zurück zur Übersicht]│
└─────────────────────────────────────────────────────┘
```

---

## Summary: Complete Data Flow

### Request Flow
```
User Browser
    → GET /portal/kwk
    → KWKOverviewPage.java (Java)
    → HTML with React container
    → lib_kwk-page-bundle.js loads
    → KwKPanel.js renders
    → User fills form and clicks Send
    → POST /banking/rest/sendReference
    → CrcJsonController.sendReference()
    → CustomerReferCustomerProcessImpl.sendReference()
    → ParticipantService (SC layer)
    → NaturalPersonAPIV3Service (SC layer)
    → ProductService (SC layer)
    → CustomerReferCustomerService.saveCrcData()
    → Database INSERT
    ← Returns referral code
    ← JSON response to React
    → React redirects to confirmation page
    → KWKConfirmationPage.java
    → Success message shown
```

### Key Files Involved

| Layer | File Path | Purpose |
|-------|-----------|---------|
| **UI Page** | `ccb/ui/pk-webui/kwk/ui/.../KWKOverviewPage.java` | Initial page controller |
| **React Entry** | `ui-react/.../parent_comp/kwk-page.js` | React app entry point |
| **React Component** | `ui-react/.../parent_comp/kwk/kwkpanel.js` | Main UI component |
| **REST Controller** | `ccb/ui/pk-webui/kwk/rest/.../CrcJsonController.java` | API endpoint |
| **Process Interface** | `ccb/process-interface/kwk/.../CustomerReferCustomerProcess.java` | Process contract |
| **Process Impl** | `ccb/middletier/process/kwk/.../CustomerReferCustomerProcessImpl.java` | Business logic |
| **Service** | `sc/[module]/.../CustomerReferCustomerService.java` | Data persistence |
| **Confirmation** | `ccb/ui/pk-webui/kwk/ui/.../KWKConfirmationPage.java` | Confirmation page |

### Technologies Used
- **Frontend:** React (old version), jQuery, Webpack
- **Backend:** Java, Spring Framework, Wicket
- **Security:** Spring Security, @PreAuthorize annotations
- **Data:** JPA/Hibernate (implied)
- **Build:** Maven, NPM, Webpack

---

## Migration Considerations

To extract KWK as a standalone microservice, you need to migrate:

### Backend Components
1. **Process Layer:** `CustomerReferCustomerProcessImpl.java`
2. **REST API:** `CrcJsonController.java`
3. **Service Layer:** `CustomerReferCustomerService.java`
4. **Dependencies:** Participant, NaturalPerson, Product services (create REST clients)

### Frontend Components
1. **React Components:** All files in `parent_comp/kwk/`
2. **Entry Points:** `kwk-page.js`, `kwkconfirmation-page.js`
3. **Shared Dependencies:** Extract from `child_comp/`, `shared_comp/`
4. **Build System:** Create standalone webpack configuration

### Integration Points to Replace
1. **Spring Security:** Implement OAuth2/JWT
2. **Wicket Pages:** Replace with React SPA or Next.js
3. **Service Calls:** Convert to REST/GraphQL clients
4. **Database:** Extract CRC_DATA table schema

