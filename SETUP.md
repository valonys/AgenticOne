# AgenticOne Setup Guide

This guide will walk you through the necessary steps to configure the AgenticOne application.

## Prerequisites

To run this application, you need a hosting environment that can serve static files (`index.html`, `index.tsx`, etc.) and inject environment variables into the JavaScript context.

## Configuration

The application requires API keys for both Google Gemini and Firebase. These keys must be available in the execution environment as `process.env.API_KEY` and `process.env.FIREBASE_API_KEY`.

### 1. Get Google Gemini API Key

1.  Visit [Google AI Studio](https://aistudio.google.com/).
2.  Click on "**Get API key**" and then "**Create API key**".
3.  Copy the generated API key.
4.  Make this key available to the application as the environment variable `API_KEY`.

### 2. Get Firebase API Key & Project Setup

1.  Go to the [Firebase Console](https://console.firebase.google.com/).
2.  Click "**Add project**" and follow the steps to create a new Firebase project.
3.  Once inside your project dashboard, navigate to **Authentication** from the left-hand menu and click "**Get started**".
4.  Under the "Sign-in method" tab, select "**Email/Password**" and enable it.
5.  Go to your **Project Settings** (click the gear icon ⚙️ next to "Project Overview").
6.  In the "General" tab, scroll down to "Your apps" and click the web icon (`</>`) to register a new web app.
7.  Give your app a nickname and click "**Register app**". You do not need to set up Firebase Hosting.
8.  Firebase will display a configuration object (`firebaseConfig`). Copy the `apiKey` value from this object.
9.  Make this key available to the application as the environment variable `FIREBASE_API_KEY`.

### Summary of Environment Variables

Your execution environment must provide the following variables:

-   `API_KEY`: Your API key for the Google Gemini service.
-   `FIREBASE_API_KEY`: Your API key for the Firebase project.

## Troubleshooting

-   **`Firebase: Error (auth/invalid-api-key)`**: This error means the Firebase API key is incorrect or not being loaded properly.
    -   Verify that the `FIREBASE_API_KEY` environment variable is correctly set and accessible by the application.
    -   Double-check that the key value matches the one in your Firebase project settings.

-   **`[GoogleGenerativeAI Error]: API key not valid`**: This indicates an issue with your Gemini API key.
    -   Verify that the `API_KEY` environment variable is correctly set.
    -   Ensure the Gemini API is enabled for your Google Cloud project.

-   **`auth/configuration-not-found`**: This can happen if the Firebase Auth Domain in `firebase.ts` does not match your project. Ensure the `authDomain` field is correct.
