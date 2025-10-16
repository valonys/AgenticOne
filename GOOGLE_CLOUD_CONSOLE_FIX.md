# 🔧 Google Cloud Console OAuth Configuration Fix

## 🚨 **Error: redirect_uri_mismatch**

The error "Error 400: redirect_uri_mismatch" occurs when the redirect URI in the OAuth request doesn't match what's configured in Google Cloud Console.

## 🛠️ **Step-by-Step Fix:**

### 1. **Go to Google Cloud Console**
- Visit: https://console.cloud.google.com/
- Select your project (or create one if needed)

### 2. **Navigate to OAuth Configuration**
- Go to "APIs & Services" → "Credentials"
- Find your OAuth 2.0 Client ID
- Click the edit (pencil) icon

### 3. **Configure Authorized JavaScript Origins**
Add these URLs:
```
http://localhost:3000
http://localhost:8080
http://127.0.0.1:3000
http://127.0.0.1:8080
```

### 4. **Configure Authorized Redirect URIs**
Add these URLs:
```
http://localhost:3000
http://localhost:8080
http://127.0.0.1:3000
http://127.0.0.1:8080
```

### 5. **Save Changes**
- Click "Save" at the bottom
- Wait a few minutes for changes to propagate

## 🔍 **Current OAuth Implementation:**

The OAuth implementation now uses:
- **Redirect URI**: `window.location.origin` (e.g., `http://localhost:3000`)
- **Client ID**: `835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com`
- **Scopes**: `openid profile email`

## 📋 **Configuration Checklist:**

### ✅ **Google Cloud Console Settings:**
- [ ] OAuth consent screen configured
- [ ] Authorized JavaScript origins added
- [ ] Authorized redirect URIs added
- [ ] Client ID and secret available
- [ ] Scopes configured (openid, profile, email)

### ✅ **Local Development:**
- [ ] Frontend running on http://localhost:3000
- [ ] Backend running on http://localhost:8000
- [ ] Environment variables set
- [ ] OAuth flow tested

## 🧪 **Test the Fix:**

1. **Update Google Cloud Console** with the URLs above
2. **Wait 2-3 minutes** for changes to propagate
3. **Test OAuth flow:**
   - Go to http://localhost:3000
   - Click "Continue with Google"
   - Should redirect to Google's consent screen
   - Complete authentication
   - Should return to app

## 🚨 **Common Issues:**

### Issue 1: "redirect_uri_mismatch"
**Solution**: Add the exact redirect URI to Google Cloud Console
- Current: `http://localhost:3000`
- Add to Authorized Redirect URIs

### Issue 2: "invalid_client"
**Solution**: Check Client ID configuration
- Verify Client ID is correct
- Check if OAuth consent screen is configured

### Issue 3: "access_denied"
**Solution**: Check OAuth consent screen
- Configure OAuth consent screen
- Add test users if needed

## 🔧 **Alternative: Use Different Redirect URI**

If the above doesn't work, you can modify the OAuth implementation to use a specific redirect URI:

```typescript
// In auth-oauth2.ts, change:
this.redirectUri = window.location.origin;

// To:
this.redirectUri = 'http://localhost:3000';
```

## 📞 **Need Help?**

If you're still having issues:

1. **Check Google Cloud Console** - Make sure all URLs are added
2. **Wait for propagation** - Changes can take 2-3 minutes
3. **Clear browser cache** - Sometimes cached OAuth settings cause issues
4. **Check browser console** - Look for any JavaScript errors
5. **Test with different browser** - Rule out browser-specific issues

## 🎯 **Expected Result:**

After fixing the configuration:
- ✅ Click "Continue with Google"
- ✅ Redirects to Google's consent screen
- ✅ User authenticates with Google
- ✅ Returns to app with user info
- ✅ No "redirect_uri_mismatch" error

The OAuth flow should now work properly! 🚀
