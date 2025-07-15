# Deployment Secrets Configuration

This document provides the exact secret names and value formats required for the production deployment workflow. Repository owners must add these secrets to the GitHub repository settings before the automated deployment pipeline can function.

## Required GitHub Secrets

Navigate to your GitHub repository → Settings → Secrets and variables → Actions, then add the following secrets:

### Google Cloud Platform (GCP) Secrets

#### `GCP_PROJECT_ID`
- **Description**: Your Google Cloud project ID
- **Format**: String (project identifier)
- **Example**: `my-business-automation-prod`
- **How to find**: Visit [Google Cloud Console](https://console.cloud.google.com/) → Select your project → Copy the Project ID

#### `GCP_SA_KEY`
- **Description**: Service Account JSON key for GitHub Actions authentication
- **Format**: Complete JSON object (as string)
- **Example**:
```json
{
  "type": "service_account",
  "project_id": "my-business-automation-prod",
  "private_key_id": "abcd1234...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBg...\n-----END PRIVATE KEY-----\n",
  "client_email": "github-actions@my-business-automation-prod.iam.gserviceaccount.com",
  "client_id": "123456789012345678901",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs/github-actions%40my-business-automation-prod.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
```
- **Required Permissions**: 
  - Cloud Run Admin
  - Artifact Registry Writer
  - Service Account User

### Cloudflare Secrets

#### `CLOUDFLARE_API_TOKEN`
- **Description**: Cloudflare API token with Pages:Edit permissions
- **Format**: String (40-character token)
- **Example**: `abcdef1234567890abcdef1234567890abcdef12`
- **How to create**: 
  1. Visit [Cloudflare Dashboard](https://dash.cloudflare.com/profile/api-tokens)
  2. Create Token → Custom token
  3. Permissions: `Zone:Zone:Read`, `Zone:Page Rule:Edit`, `Account:Cloudflare Pages:Edit`
  4. Account Resources: `Include - All accounts` (or specific account)
  5. Zone Resources: `Include - All zones` (or specific zone)

#### `CLOUDFLARE_ACCOUNT_ID`
- **Description**: Your Cloudflare account identifier
- **Format**: String (32-character hex)
- **Example**: `1234567890abcdef1234567890abcdef`
- **How to find**: Cloudflare Dashboard → Right sidebar → Account ID

### Frontend Environment Variables

#### `VITE_API_BASE_URL`
- **Description**: Backend API base URL for frontend calls
- **Format**: HTTPS URL (no trailing slash)
- **Example**: `https://optimizer-api-xyz123-uc.a.run.app`
- **Note**: This will be the Cloud Run service URL once backend is deployed

#### `VITE_GRAFANA_URL`
- **Description**: Grafana dashboard URL for embedded metrics
- **Format**: HTTPS URL (no trailing slash)
- **Example**: `https://your-grafana-instance.grafana.net`
- **Alternative**: `http://localhost:3001` for local development

### Backend Authentication (OIDC)

#### `OIDC_ISSUER_URL`
- **Description**: OAuth2/OIDC provider issuer URL
- **Format**: HTTPS URL
- **Example**: `https://accounts.google.com` (Google)
- **Example**: `https://your-domain.auth0.com/` (Auth0)
- **Example**: `https://login.microsoftonline.com/{tenant-id}/v2.0` (Azure AD)

#### `OIDC_CLIENT_ID`
- **Description**: OAuth2 client identifier
- **Format**: String (varies by provider)
- **Example**: `123456789012-abcdefghijklmnopqrstuvwxyz.apps.googleusercontent.com` (Google)
- **Example**: `AbCdEfGhIjKlMnOpQrStUvWxYz123456` (Auth0)

#### `OIDC_CLIENT_SECRET`
- **Description**: OAuth2 client secret
- **Format**: String (varies by provider)
- **Example**: `GOCSPX-abcdefghijklmnopqrstuvwxyz123456` (Google)
- **Example**: `AbCdEfGhIjKlMnOpQrStUvWxYz123456AbCdEfGhIjKlMnOpQrStUvWxYz123456` (Auth0)
- **Security**: Keep this secret! Never commit to version control.

### Optional Secrets (Development/Testing)

#### `OPENAI_API_KEY`
- **Description**: OpenAI API key for LLM calls (if not using Google Secret Manager)
- **Format**: String starting with `sk-`
- **Example**: `sk-1234567890abcdef1234567890abcdef12345678901234567890`

#### `ANTHROPIC_API_KEY`
- **Description**: Anthropic Claude API key (if using Claude models)
- **Format**: String starting with `sk-ant-`
- **Example**: `sk-ant-api03-1234567890abcdef1234567890abcdef12345678901234567890`

## Verification Checklist

Before pushing code that triggers deployment:

- [ ] All 7 required secrets are added to GitHub repository
- [ ] GCP Service Account has necessary permissions (Cloud Run, Artifact Registry)
- [ ] Cloudflare API token has Pages:Edit permissions for target account
- [ ] OIDC application is configured with correct redirect URIs
- [ ] Frontend environment variables point to correct backend URLs
- [ ] Test deployment workflow runs successfully

## Security Notes

1. **Service Account**: Use principle of least privilege - only grant permissions needed for deployment
2. **API Tokens**: Rotate regularly and monitor usage in provider dashboards
3. **Client Secrets**: Store in GitHub Secrets only, never in code or environment files
4. **Access Review**: Regularly audit who has access to modify these secrets

## Troubleshooting

### Common Issues:

**"Authentication failed" in GCP deployment:**
- Verify `GCP_SA_KEY` is valid JSON and service account exists
- Check service account has Cloud Run Admin + Artifact Registry Writer roles

**"Cloudflare Pages deployment failed":**
- Verify `CLOUDFLARE_API_TOKEN` has Pages:Edit permission
- Confirm `CLOUDFLARE_ACCOUNT_ID` matches the account owning the target domain

**"Frontend can't reach backend":**
- Ensure `VITE_API_BASE_URL` matches deployed Cloud Run service URL
- Check CORS settings in backend allow frontend domain

**"OIDC authentication fails":**
- Verify redirect URIs in OIDC provider include both local and production URLs
- Confirm `OIDC_CLIENT_ID` and `OIDC_CLIENT_SECRET` match provider configuration

For additional support, check the deployment logs in GitHub Actions or refer to `DEPLOYMENT_ROLLBACK.md` for emergency procedures. 