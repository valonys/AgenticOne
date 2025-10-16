"""
OAuth 2.0 Token Exchange Handler for Google Authentication
"""
import httpx
import json
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import secrets
import hashlib
import base64

router = APIRouter(prefix="/api/auth", tags=["oauth"])

# OAuth 2.0 Configuration
GOOGLE_CLIENT_ID = "835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "your-client-secret-here"  # Replace with actual secret
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

@router.post("/token")
async def exchange_code_for_tokens(request: Request):
    """Exchange authorization code for access tokens"""
    try:
        body = await request.json()
        code = body.get("code")
        redirect_uri = body.get("redirect_uri")
        client_id = body.get("client_id")
        code_verifier = body.get("code_verifier")
        
        if not all([code, redirect_uri, client_id]):
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        # Exchange code for tokens
        token_data = {
            "client_id": client_id,
            # For PKCE, client_secret is not required for public clients (SPA)
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
            "code_verifier": code_verifier
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Token exchange failed")
            
            token_response = response.json()
            
            # Get user info
            user_info = await get_user_info(token_response["access_token"])
            
            return {
                "access_token": token_response["access_token"],
                "refresh_token": token_response.get("refresh_token"),
                "expires_in": token_response.get("expires_in"),
                "user_info": user_info
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def get_user_info(access_token: str) -> Dict[str, Any]:
    """Get user information from Google"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Failed to get user info")
            
            return response.json()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/callback")
async def oauth_callback(
    code: str = None,
    state: str = None,
    error: str = None
):
    """Handle OAuth callback"""
    if error:
        return RedirectResponse(url=f"/?error={error}")
    
    if not code:
        return RedirectResponse(url="/?error=no_code")
    
    # In a real implementation, you would:
    # 1. Verify the state parameter
    # 2. Exchange the code for tokens
    # 3. Store tokens securely
    # 4. Redirect to the main app
    
    return RedirectResponse(url="/?code=success")

@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh access token using refresh token"""
    try:
        body = await request.json()
        refresh_token = body.get("refresh_token")
        
        if not refresh_token:
            raise HTTPException(status_code=400, detail="Refresh token required")
        
        token_data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
            
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail="Token refresh failed")
            
            return response.json()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/revoke")
async def revoke_token(request: Request):
    """Revoke access token"""
    try:
        body = await request.json()
        token = body.get("token")
        
        if not token:
            raise HTTPException(status_code=400, detail="Token required")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/revoke",
                data={"token": token}
            )
            
            return {"status": "revoked"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
