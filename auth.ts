// New Google OAuth Authentication with better error handling
interface GoogleUser {
  id: string;
  email: string;
  name: string;
  picture: string;
  access_token: string;
}

class NewGoogleAuth {
  private user: GoogleUser | null = null;
  private listeners: Array<(user: GoogleUser | null) => void> = [];
  private isInitialized = false;

  constructor() {
    this.initializeAuth();
  }

  private async initializeAuth() {
    try {
      // Wait for Google script to load
      await this.waitForGoogleScript();
      this.setupGoogleAuth();
    } catch (error) {
      console.warn('Google OAuth initialization failed, using fallback:', error);
      this.setupFallbackAuth();
    }
  }

  private waitForGoogleScript(): Promise<void> {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      const maxAttempts = 50; // 5 seconds max wait
      
      const checkGoogle = () => {
        attempts++;
        if (window.google?.accounts?.id) {
          resolve();
        } else if (attempts >= maxAttempts) {
          reject(new Error('Google OAuth script failed to load'));
        } else {
          setTimeout(checkGoogle, 100);
        }
      };
      checkGoogle();
    });
  }

  private setupGoogleAuth() {
    if (!window.google?.accounts?.id) {
      console.error('Google OAuth not available');
      this.setupFallbackAuth();
      return;
    }

    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com';
    console.log('🔧 Initializing Google OAuth with Client ID:', clientId);

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response: any) => this.handleCredentialResponse(response),
        auto_select: false,
        cancel_on_tap_outside: true,
        ux_mode: 'popup',
        context: 'signin',
        state_cookie_domain: 'localhost'
      });
      
      this.isInitialized = true;
      console.log('✅ Google OAuth initialized successfully');
    } catch (error) {
      console.error('❌ Google OAuth initialization failed:', error);
      this.setupFallbackAuth();
    }
  }

  private setupFallbackAuth() {
    console.log('Using fallback authentication mode');
    this.listeners.forEach(listener => listener(null));
  }

  private handleCredentialResponse(response: any) {
    try {
      console.log('Received Google OAuth response:', response);
      
      if (!response.credential) {
        console.error('No credential in response');
        alert('Google sign-in failed. Please try guest mode instead.');
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
      alert('Google sign-in failed. Please try guest mode instead.');
    }
  }

  // Public methods
  signIn() {
    if (!this.isInitialized) {
      console.error('Google OAuth not initialized');
      throw new Error('Google OAuth is not available. Please use guest mode.');
    }

    try {
      console.log('Attempting Google OAuth sign-in...');
      window.google.accounts.id.prompt((notification: any) => {
        console.log('OAuth notification:', notification);
        if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
          console.log('Google OAuth prompt not displayed, trying alternative...');
          this.showAlternativeSignIn();
        }
      });
    } catch (error) {
      console.error('Sign-in error:', error);
      throw error;
    }
  }

  private showAlternativeSignIn() {
    // Create a modal with Google sign-in button
    const modal = document.createElement('div');
    modal.id = 'google-signin-modal';
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      display: flex;
      justify-content: center;
      align-items: center;
      z-index: 10000;
    `;
    
    const content = document.createElement('div');
    content.style.cssText = `
      background: white;
      padding: 30px;
      border-radius: 8px;
      text-align: center;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    `;
    
    content.innerHTML = `
      <h3 style="margin-bottom: 20px; color: #333;">Sign in with Google</h3>
      <div id="google-signin-button"></div>
      <button id="close-modal" style="margin-top: 20px; padding: 10px 20px; background: #f0f0f0; border: none; border-radius: 4px; cursor: pointer;">Cancel</button>
    `;
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // Add close button functionality
    document.getElementById('close-modal')?.addEventListener('click', () => {
      document.body.removeChild(modal);
    });
    
    // Render Google sign-in button
    try {
      window.google.accounts.id.renderButton(
        document.getElementById('google-signin-button'),
        {
          theme: 'outline',
          size: 'large',
          type: 'standard',
          shape: 'rectangular',
          text: 'signin_with',
          width: 300
        }
      );
    } catch (error) {
      console.error('Failed to render Google sign-in button:', error);
      document.body.removeChild(modal);
      alert('Google sign-in is not available. Please use guest mode.');
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
export const auth = new NewGoogleAuth();

// Type definitions
declare global {
  interface Window {
    google: {
      accounts: {
        id: {
          initialize: (config: any) => void;
          prompt: (callback?: (notification: any) => void) => void;
          disableAutoSelect: () => void;
          renderButton: (element: HTMLElement, config: any) => void;
        };
      };
    };
  }
}

export type { GoogleUser };
