// Firebase-based Google OAuth Authentication (Alternative approach)
interface GoogleUser {
  id: string;
  email: string;
  name: string;
  picture: string;
  access_token: string;
}

class FirebaseGoogleAuth {
  private user: GoogleUser | null = null;
  private listeners: Array<(user: GoogleUser | null) => void> = [];
  private firebaseApp: any = null;
  private auth: any = null;

  constructor() {
    this.initializeFirebase();
  }

  private async initializeFirebase() {
    try {
      // Dynamic import of Firebase
      const { initializeApp } = await import('firebase/app');
      const { getAuth, signInWithPopup, GoogleAuthProvider, signOut } = await import('firebase/auth');
      
      // Firebase configuration
      const firebaseConfig = {
        apiKey: "AIzaSyCY6H_1RQN6j8mp8tRwpO20o54coKPHEKM", // Using Gemini API key as fallback
        authDomain: "agenticone-ed918.firebaseapp.com",
        projectId: "agenticone-ed918",
        storageBucket: "agenticone-ed918.appspot.com",
        messagingSenderId: "835773828317",
        appId: "1:835773828317:web:your-app-id"
      };

      this.firebaseApp = initializeApp(firebaseConfig);
      this.auth = getAuth(this.firebaseApp);
      
      console.log('✅ Firebase initialized successfully');
    } catch (error) {
      console.warn('Firebase initialization failed, using fallback:', error);
      this.setupFallbackAuth();
    }
  }

  private setupFallbackAuth() {
    console.log('Using fallback authentication mode');
    this.listeners.forEach(listener => listener(null));
  }

  // Public methods
  async signIn() {
    try {
      if (!this.auth) {
        throw new Error('Firebase auth not available');
      }

      const { signInWithPopup, GoogleAuthProvider } = await import('firebase/auth');
      const provider = new GoogleAuthProvider();
      
      console.log('Attempting Firebase Google sign-in...');
      const result = await signInWithPopup(this.auth, provider);
      
      // Extract user information
      const user = result.user;
      this.user = {
        id: user.uid,
        email: user.email || '',
        name: user.displayName || '',
        picture: user.photoURL || '',
        access_token: await user.getIdToken()
      };

      // Notify all listeners
      this.listeners.forEach(listener => listener(this.user));
      
      console.log('✅ Firebase Google login successful:', this.user);
    } catch (error) {
      console.error('Firebase sign-in error:', error);
      throw new Error('Google sign-in failed. Please use guest mode instead.');
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

  async signOut() {
    try {
      if (this.auth) {
        const { signOut } = await import('firebase/auth');
        await signOut(this.auth);
      }
    } catch (error) {
      console.error('Firebase sign-out error:', error);
    }
    
    this.user = null;
    this.listeners.forEach(listener => listener(null));
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
export const auth = new FirebaseGoogleAuth();

export type { GoogleUser };
