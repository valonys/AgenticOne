// Google OAuth Authentication - No Firebase needed!
interface GoogleUser {
  id: string;
  email: string;
  name: string;
  picture: string;
  access_token: string;
}

class GoogleAuth {
  private user: GoogleUser | null = null;
  private listeners: Array<(user: GoogleUser | null) => void> = [];

  constructor() {
    this.initializeGoogleAuth();
  }

  private initializeGoogleAuth() {
    // Check if Google Identity Services is already loaded
    if (window.google?.accounts?.id) {
      this.setupGoogleAuth();
    } else {
      // Wait for the script to load with timeout
      let attempts = 0;
      const maxAttempts = 50; // 5 seconds max wait
      
      const checkGoogle = () => {
        attempts++;
        if (window.google?.accounts?.id) {
          this.setupGoogleAuth();
        } else if (attempts >= maxAttempts) {
          console.warn('Google OAuth script failed to load, using fallback');
          this.setupFallbackAuth();
        } else {
          setTimeout(checkGoogle, 100);
        }
      };
      checkGoogle();
    }
  }

  private setupFallbackAuth() {
    // Fallback when Google OAuth fails to load
    console.log('Using fallback authentication mode');
    // Notify listeners that auth is ready (but not authenticated)
    this.listeners.forEach(listener => listener(null));
  }

  private setupGoogleAuth() {
    if (!window.google?.accounts?.id) {
      console.error('Google OAuth not available');
      return;
    }

    const clientId = process.env.GOOGLE_CLIENT_ID || '835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com';
    console.log('🔧 Initializing Google OAuth with Client ID:', clientId);

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response: any) => this.handleCredentialResponse(response),
        auto_select: false,
        cancel_on_tap_outside: true,
        ux_mode: 'popup',
        context: 'signin'
      });
      console.log('✅ Google OAuth initialized successfully');
    } catch (error) {
      console.error('❌ Google OAuth initialization failed:', error);
    }
  }

  private handleCredentialResponse(response: any) {
    try {
      console.log('Received Google OAuth response:', response);
      
      if (!response.credential) {
        console.error('No credential in response');
        return;
      }
      
      // Decode the JWT token to get user info
      const payload = JSON.parse(atob(response.credential.split('.')[1]));
      console.log('Decoded JWT payload:', payload);
      
      this.user = {
        id: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
        access_token: response.credential
      };

      // Notify all listeners
      this.listeners.forEach(listener => listener(this.user));
      
      console.log('✅ Google OAuth login successful:', this.user);
    } catch (error) {
      console.error('❌ Google OAuth error:', error);
      // Show user-friendly error
      alert('Google sign-in failed. Please try again or use guest mode.');
    }
  }

  // Public methods
  signIn() {
    try {
      if (window.google?.accounts?.id) {
        console.log('Attempting Google OAuth sign-in...');
        
        // Try the one-tap prompt first
        window.google.accounts.id.prompt((notification: any) => {
          console.log('OAuth notification:', notification);
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            console.log('Google OAuth prompt not displayed or skipped, trying alternative...');
            this.showAlternativeSignIn();
          }
        });
      } else {
        console.error('Google OAuth not available');
        throw new Error('Google OAuth is not available. Please check your internet connection and refresh the page.');
      }
    } catch (error) {
      console.error('Sign-in error:', error);
      throw error;
    }
  }

  private showAlternativeSignIn() {
    // Create a temporary button for sign-in
    const button = document.createElement('div');
    button.id = 'google-signin-button';
    button.style.position = 'fixed';
    button.style.top = '50%';
    button.style.left = '50%';
    button.style.transform = 'translate(-50%, -50%)';
    button.style.zIndex = '9999';
    button.style.backgroundColor = 'white';
    button.style.padding = '20px';
    button.style.borderRadius = '8px';
    button.style.boxShadow = '0 4px 12px rgba(0,0,0,0.3)';
    
    document.body.appendChild(button);
    
    try {
      window.google.accounts.id.renderButton(button, {
        theme: 'outline',
        size: 'large',
        type: 'standard',
        shape: 'rectangular',
        text: 'signin_with',
        width: 300
      });
    } catch (error) {
      console.error('Failed to render Google sign-in button:', error);
      document.body.removeChild(button);
      alert('Google sign-in is not available. Please use guest mode or try refreshing the page.');
    }
  }

  // Guest sign-in method
  signInAsGuest(customName?: string) {
    console.log('Signing in as guest...');
    const guestName = customName || 'Guest User';
    this.user = {
      id: 'guest-' + Date.now(),
      email: 'guest@agenticone.com',
      name: guestName,
      picture: 'https://via.placeholder.com/150/4F46E5/FFFFFF?text=' + guestName.charAt(0).toUpperCase(),
      access_token: 'guest-token-' + Date.now()
    };

    // Notify all listeners
    this.listeners.forEach(listener => listener(this.user));
    console.log('✅ Guest login successful:', this.user);
  }

  signOut() {
    this.user = null;
    this.listeners.forEach(listener => listener(null));
    
    if (window.google) {
      window.google.accounts.id.disableAutoSelect();
    }
  }

  getCurrentUser(): GoogleUser | null {
    return this.user;
  }

  onAuthStateChanged(callback: (user: GoogleUser | null) => void) {
    this.listeners.push(callback);
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  // Get authorization header for API calls
  getAuthHeader(): string | null {
    return this.user ? `Bearer ${this.user.access_token}` : null;
  }
}

// Create singleton instance
export const auth = new GoogleAuth();

// Type definitions
declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          prompt: () => void;
          disableAutoSelect: () => void;
        };
      };
    };
  }
}

export type { GoogleUser };
