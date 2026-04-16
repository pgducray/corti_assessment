# Authentication Troubleshooting

## Context

This document addresses the investigation and resolution of a 401 Unauthorized error encountered when attempting to authenticate with the Corti API using OAuth2 client credentials flow.

## 1. Root Cause Analysis

The 401 Unauthorized error indicates that the authentication server received the request but refused to authorize it. Based on the provided payload, the most likely causes are:

- **Invalid or Expired Credentials**: The `client_id` (testuser) or `client_secret` (testkey) may be placeholders, incorrect, or have been revoked in the copiloteu realm.

- **Unsupported Grant Type or Scope**: While `client_credentials` is standard, the server may require a specific scope beyond `openid`, or the specific client may not have the "Service Account Enabled" setting required for this flow.

- **Expired Access Token**: OAuth2 access tokens expire after 5 minutes and must be refreshed.

## 2. Internal Troubleshooting Approach

To resolve this without compromising security, follow these diagnostic steps:

1. **Verify Credentials**
   - Confirm that the `client_id` and `client_secret` are correctly stored in environment variables
   - Check that the credentials are valid and have not been revoked or rotated

2. **Configuration Audit**
   - Verify in the admin console that the `client_id` exists in the specified realm
   - Confirm that the client's "Access Type" is set to "confidential" with "Service Accounts Enabled"
   - Validate that the client has appropriate scope permissions

3. **Endpoint and Payload Verification**
   - Confirm the authentication endpoint URL is correct for the target realm
   - Validate that all payload keys (`grant_type`, `client_id`, `client_secret`, `scope`) are properly formatted
   - Test the endpoint using a tool like Postman or curl to isolate API vs. code issues

4. **Implement Token Management**
   - Add token expiration checking before making API requests
   - Implement automatic token refresh logic (tokens expire after 5 minutes)
   - Use try-except blocks to handle authentication errors gracefully and trigger re-authentication

## 3. Customer Response (Email Draft)

**Subject**: Technical Support: Resolving your 401 Unauthorized Error

Dear Customer,

Our team has reviewed the authentication error you encountered while connecting to the Corti API. A 401 error typically indicates a credential mismatch or a configuration misalignment.

**What Likely Went Wrong**

Based on the error logs, the authentication server could not validate the request. This is usually due to:

- **Expired Token**: Client credentials produce short-lived tokens (5 minutes) that must be refreshed regularly
- **Insufficient Scope**: The client may not have scope access to use this endpoint action
- **Configuration Issue**: The endpoint URL or payload structure may be incorrect

**Recommended Fixes**

1. **Implement Token Refresh**: Include automatic token refresh logic in your application to avoid using expired tokens
2. **Verify the Endpoint**: Ensure the authentication URL matches the realm specified in your credentials
3. **Check Scope Permissions**: Verify that your client has the necessary scope permissions, or try adjusting the scope parameter as documented in your API guide

**Security Note**

For your protection, never share your Client Secret via email or support tickets. We strongly recommend:
- Store credentials in environment variables rather than hardcoding them in scripts
- Rotate credentials immediately if you suspect they have been exposed
- Follow our security best practices: https://docs.corti.ai/authentication/security_best_practices

If you continue to experience issues after trying these steps, please reply with any error messages you receive (excluding sensitive credentials), and we'll be happy to assist further.

Best regards,

[Your Name]

Technical Support Engineer

## 4. Internal Security Recommendations

The presence of hardcoded credentials in scripts (especially placeholders like `testkey`) suggests a risk of accidental exposure via version control (Git) or shared notebooks.

**Best Practices & Actions:**

1. **Environment Variables**: Enforce the use of `.env` files. Instead of `client_secret='testkey'`, use `os.getenv('CLIENT_SECRET')`.

2. **Secret Scanning**: Implement tools like TruffleHog or GitHub Secret Scanning to catch hardcoded keys before they are pushed to a repository.

3. **Credential Rotation**: If "testkey" was ever a functional credential (not just a placeholder), it should be considered compromised and rotated immediately.

4. **Secret Management**: Use dedicated secret managers (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault) to inject credentials into the application runtime dynamically, eliminating the need to store them in code or configuration files.

5. **Access Control**: Implement least-privilege access principles, ensuring clients only have the minimum scope permissions required for their intended operations.
