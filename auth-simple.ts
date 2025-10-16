// Simplified Google OAuth Authentication
interface GoogleUser {
  id: string;
  email: string;
  name: string;
  picture: string;
  access_token: string;
}

class SimpleGoogleAuth {
  private user: GoogleUser | null = null;
  private listeners: Array<(user: GoogleUser | null) => void> = [];

  constructor() {
    this.initializeAuth();
  }

  private initializeAuth() {
    // Load Google OAuth script dynamically
    if (!document.querySelector('script[src*="accounts.google.com"]')) {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = () => this.setupGoogleAuth();
      document.head.appendChild(script);
    } else {
      // Script already loaded, wait a bit and setup
      setTimeout(() => this.setupGoogleAuth(), 1000);
    }
  }

  private setupGoogleAuth() {
    if (!window.google?.accounts?.id) {
      console.warn('Google OAuth not available, using fallback');
      this.setupFallbackAuth();
      return;
    }

    const clientId = process.env.GOOGLE_CLIENT_ID || '835773828317-v3ce03jcca5o7nq09vs2tuc1tejke8du.apps.googleusercontent.com';
    console.log('🔧 Setting up Google OAuth with Client ID:', clientId);

    try {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (response: any) => this.handleCredentialResponse(response),
        auto_select: false,
        cancel_on_tap_outside: true,
        ux_mode: 'popup'
      });
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
    try {
      if (window.google?.accounts?.id) {
        console.log('Attempting Google OAuth sign-in...');
        window.google.accounts.id.prompt();
      } else {
        console.error('Google OAuth not available');
        throw new Error('Google OAuth is not available. Please use guest mode.');
      }
    } catch (error) {
      console.error('Sign-in error:', error);
      throw error;
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
export const auth = new SimpleGoogleAuth();

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
