#!/usr/bin/env python3
"""
Environment validation script for AgenticOne Backend
"""
import os
import sys
from typing import List, Dict, Any

def validate_environment() -> Dict[str, Any]:
    """Validate environment configuration"""
    results = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "required_missing": [],
        "optional_missing": []
    }
    
    # Required environment variables
    required_vars = {
        "GOOGLE_CLOUD_PROJECT": "Google Cloud Project ID",
        "VERTEX_AI_LOCATION": "Vertex AI region",
        "VERTEX_AI_MODEL": "Vertex AI model name",
        "VECTOR_SEARCH_INDEX_ID": "Vector search index ID",
        "FIRESTORE_PROJECT_ID": "Firestore project ID",
        "CLOUD_STORAGE_BUCKET": "Cloud Storage bucket name",
        "SECRET_KEY": "Application secret key"
    }
    
    # Optional environment variables with defaults
    optional_vars = {
        "GOOGLE_APPLICATION_CREDENTIALS": "Service account key file path",
        "VECTOR_SEARCH_DIMENSIONS": "Vector dimensions (default: 768)",
        "FIRESTORE_DATABASE_ID": "Firestore database ID (default: (default))",
        "MAX_ANALYSIS_RETRIES": "Max analysis retries (default: 3)",
        "ANALYSIS_TIMEOUT": "Analysis timeout (default: 300)",
        "REPORT_TEMPLATE_PATH": "Report template path (default: templates/)",
        "REPORT_OUTPUT_PATH": "Report output path (default: reports/)",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "Token expiration (default: 30)",
        "ALLOWED_ORIGINS": "CORS allowed origins",
        "DEBUG": "Debug mode (default: false)",
        "LOG_LEVEL": "Log level (default: INFO)"
    }
    
    # Check required variables
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value or value.strip() == "":
            results["required_missing"].append(f"{var}: {description}")
            results["valid"] = False
        elif var == "SECRET_KEY" and value == "your-secret-key-here":
            results["warnings"].append(f"{var}: Using default secret key - change in production!")
        elif var == "GOOGLE_CLOUD_PROJECT" and "your-project-id" in value:
            results["warnings"].append(f"{var}: Using placeholder value - update with actual project ID")
    
    # Check optional variables
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if not value or value.strip() == "":
            results["optional_missing"].append(f"{var}: {description}")
    
    # Special validations
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not os.path.exists(creds_path):
            results["errors"].append(f"GOOGLE_APPLICATION_CREDENTIALS file not found: {creds_path}")
            results["valid"] = False
    
    # Validate numeric values
    try:
        if os.getenv("VECTOR_SEARCH_DIMENSIONS"):
            dims = int(os.getenv("VECTOR_SEARCH_DIMENSIONS"))
            if dims <= 0:
                results["errors"].append("VECTOR_SEARCH_DIMENSIONS must be positive")
                results["valid"] = False
    except ValueError:
        results["errors"].append("VECTOR_SEARCH_DIMENSIONS must be a valid integer")
        results["valid"] = False
    
    try:
        if os.getenv("MAX_ANALYSIS_RETRIES"):
            retries = int(os.getenv("MAX_ANALYSIS_RETRIES"))
            if retries < 0:
                results["errors"].append("MAX_ANALYSIS_RETRIES must be non-negative")
                results["valid"] = False
    except ValueError:
        results["errors"].append("MAX_ANALYSIS_RETRIES must be a valid integer")
        results["valid"] = False
    
    try:
        if os.getenv("ANALYSIS_TIMEOUT"):
            timeout = int(os.getenv("ANALYSIS_TIMEOUT"))
            if timeout <= 0:
                results["errors"].append("ANALYSIS_TIMEOUT must be positive")
                results["valid"] = False
    except ValueError:
        results["errors"].append("ANALYSIS_TIMEOUT must be a valid integer")
        results["valid"] = False
    
    return results

def print_validation_results(results: Dict[str, Any]):
    """Print validation results in a formatted way"""
    print("🔍 AgenticOne Backend Environment Validation")
    print("=" * 50)
    
    if results["valid"]:
        print("✅ Environment configuration is valid!")
    else:
        print("❌ Environment configuration has issues!")
    
    if results["errors"]:
        print("\n🚨 ERRORS:")
        for error in results["errors"]:
            print(f"  • {error}")
    
    if results["required_missing"]:
        print("\n🔴 REQUIRED VARIABLES MISSING:")
        for missing in results["required_missing"]:
            print(f"  • {missing}")
    
    if results["warnings"]:
        print("\n⚠️  WARNINGS:")
        for warning in results["warnings"]:
            print(f"  • {warning}")
    
    if results["optional_missing"]:
        print("\n🟡 OPTIONAL VARIABLES MISSING (will use defaults):")
        for missing in results["optional_missing"]:
            print(f"  • {missing}")
    
    print("\n" + "=" * 50)
    
    if results["valid"]:
        print("🎉 All required environment variables are configured!")
        print("💡 You can now run the backend service.")
    else:
        print("🔧 Please fix the issues above before running the backend.")
        print("📝 Copy env.example to .env and update with your values.")

def main():
    """Main validation function"""
    print("Checking environment configuration...\n")
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  No .env file found!")
        print("📝 Please copy env.example to .env and configure your values:")
        print("   cp env.example .env")
        print("   # Then edit .env with your actual values")
        return 1
    
    # Validate environment
    results = validate_environment()
    print_validation_results(results)
    
    return 0 if results["valid"] else 1

if __name__ == "__main__":
    sys.exit(main())
