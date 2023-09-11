# Gramex Plus / Enterprise Edition

Install the [Plus / Enterprise edition of Gramex](https://learn.gramener.com/guide/):

```bash
pip install gramexenterprise
```

[Read the documentation for details](https://learn.gramener.com/guide/)

## Changelog

### 1.93.0

- ENH: Allow DBAuth templates to use `token`, not just `reset_url`
- ENH: EmailAuth supports a `from:` kwarg
- ENH: SAMLAuth should save redirect page

### 1.85.0

- FIX: EmailAuth should not raise an error with OTP

### 1.82.1

- FIX: Do not import unused OTP function

### 1.82.0

- FIX: Allow OTP to use databases
- FIX: Save redirect information for SAMLAuth2
- ENH: Add recaptcha to SMS template

### 1.76.0

- FIX: EmailAuth supports recaptcha: and delay
- FIX: Remove HTTP reason, add ldap dependency

### 1.74.0

- ENH: EmailAuth support html emails and bypasses Outlook safelinks
- ENH: EmailAuth supports direct entry of OTP
- FIX: EmailAuth: if user refreshes OTP page, preserve next page
- ENH: DBAuth forgot-email accepts text/html content/files
- FIX: DBAuth uses 'email' as default email column
- ENH: SAMLAuth2 handler supporting SAML2 @vinay.ranjan
- ENH: Support password policy
- SEC: Slow down username enumeration

### 1.65.0

- DBAuth: remove `table` as an explicit kwarg. It is not required for files, and will fail for
  non-Excel files from Gramex CE 1.65.0 onwards.
- Auth: When Gramex is behind a proxy, use `handler.xredirect_uri` to redirect to the end-user URL,
  not the proxied URL (which would be `localhost:port`).

### 1.56.1

- DBAuth: `reset_url` should be ?forgot key

### 1.56.0

- DBAuth: extend signup to configure email like forgot configuration
