# Google OAuth Setup Guide

## Issue: "client_secret is missing"

The OAuth flow is failing because Google requires a client secret for the token exchange, even with PKCE.

## Solution:

### 1. Get Your Google Client Secret

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Navigate to**: APIs & Services → Credentials
3. **Find your OAuth 2.0 Client ID**: `835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com`
4. **Click on it** to view details
5. **Copy the "Client Secret"** (it will look like: `GOCSPX-xxxxxxxxxxxxxxxxxxxx`)

### 2. Update Backend Environment

Create a `.env` file in the backend directory:

```bash
# In agenticone-backend/.env
GOOGLE_CLIENT_SECRET=GOCSPX-your-actual-client-secret-here
GOOGLE_CLIENT_ID=835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com
```

### 3. Restart Backend

```bash
cd agenticone-backend
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Test OAuth Flow

The OAuth flow should now work correctly with the client secret.

## Alternative: Use Public Client Configuration

If you want to avoid using client secrets, you can:

1. **Create a new OAuth client** in Google Cloud Console
2. **Set Application type** to "Public client" (for SPAs)
3. **Update the client ID** in your frontend code

But the current setup with client secret is more secure and recommended.
