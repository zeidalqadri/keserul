# Google OAuth 2.0 Setup Guide

Follow these steps to set up Google OAuth 2.0 authentication for the CBL Tournament Registration Form.

## Step 1: Create Google OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit [console.cloud.google.com](https://console.cloud.google.com)
   - Select your existing project (or create a new one)

2. **Enable Google+ API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google+ API" and enable it
   - Also enable "Google People API" for profile information

3. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Name: `CBL Tournament Form`

4. **Configure OAuth Settings**
   - **Authorized JavaScript origins:**
     - `http://localhost:3000` (for development)
     - `https://your-domain.com` (for production)
   
   - **Authorized redirect URIs:**
     - `http://localhost:3000/api/auth/callback/google` (for development)
     - `https://your-domain.com/api/auth/callback/google` (for production)

5. **Download Credentials**
   - Click "Create"
   - Copy the Client ID and Client Secret

## Step 2: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - In Google Cloud Console, go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in required information:
     - App name: `CBL 2025 Corporate Edition`
     - User support email: Your email
     - Developer contact information: Your email

2. **Add Scopes**
   - Add these scopes:
     - `../auth/userinfo.email`
     - `../auth/userinfo.profile`
     - `openid`

3. **Add Test Users** (for development)
   - Add your email and any test user emails

## Step 3: Environment Variables

Add these to your `.env.local` file:

\`\`\`env
# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-random-secret-key-here

# Google OAuth Credentials
GOOGLE_CLIENT_ID=123456789-abcdef.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your-client-secret-here

# Existing Google Sheets credentials remain the same
GOOGLE_CLIENT_EMAIL=your-service-account@project.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n
GOOGLE_SHEET_ID=your-google-sheet-id
BLOB_READ_WRITE_TOKEN=your-vercel-blob-token
\`\`\`

## Step 4: Generate NextAuth Secret

Run this command to generate a secure secret:

\`\`\`bash
openssl rand -base64 32
\`\`\`

Use the output as your `NEXTAUTH_SECRET`.

## Step 5: Production Deployment

For production deployment:

1. **Update OAuth Settings**
   - Add your production domain to authorized origins and redirect URIs
   - Update `NEXTAUTH_URL` to your production URL

2. **Publish OAuth App**
   - In Google Cloud Console, go to OAuth consent screen
   - Click "Publish App" to make it available to all users
   - Or keep it in testing mode and add specific user emails

## Features Enabled

✅ **Secure Authentication**: Real Google OAuth 2.0
✅ **User Profile**: Access to user's name, email, and profile picture
✅ **Session Management**: Automatic session handling with NextAuth.js
✅ **Data Persistence**: User form data saved per Google account
✅ **Auto-populate**: Previous form data automatically loaded
✅ **Security**: CSRF protection and secure session tokens

## Testing

1. Start your development server: `npm run dev`
2. Go to `http://localhost:3000`
3. Click "Sign in with Google"
4. Complete the OAuth flow
5. Verify user information is displayed correctly

## Troubleshooting

- **"redirect_uri_mismatch"**: Check your authorized redirect URIs match exactly
- **"invalid_client"**: Verify your Client ID and Secret are correct
- **"access_blocked"**: Make sure your app is published or user is added as test user
