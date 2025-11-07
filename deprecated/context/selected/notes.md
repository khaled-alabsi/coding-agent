## Legacy vs UCC Pattern Differences only

in legacy the http request will be handled by cbb/ui/[channelName]-webui/[app-name]/rest/controller
in ucc ucc/channelName]/process/rest/          




---



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



----


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


