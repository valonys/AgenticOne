# Environment Setup Guide for AgenticOne Backend

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp env.example .env
   ```

2. **Edit the .env file with your actual values:**
   ```bash
   nano .env  # or use your preferred editor
   ```

3. **Validate your configuration:**
   ```bash
   python3 validate_env.py
   ```

## Required Environment Variables

### 🔴 CRITICAL - Must be configured

| Variable | Description | Example Value |
|----------|-------------|---------------|
| `GOOGLE_CLOUD_PROJECT` | Your Google Cloud Project ID | `my-project-123` |
| `VERTEX_AI_LOCATION` | Vertex AI region | `us-central1` |
| `VERTEX_AI_MODEL` | Gemini model to use | `gemini-1.5-pro` |
| `VECTOR_SEARCH_INDEX_ID` | Vector search index ID | `my-vector-index` |
| `FIRESTORE_PROJECT_ID` | Firestore project ID | `my-project-123` |
| `CLOUD_STORAGE_BUCKET` | Cloud Storage bucket name | `my-storage-bucket` |
| `SECRET_KEY` | Application secret key | `your-super-secret-key` |

### 🟡 OPTIONAL - Will use defaults if not set

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Service account key file | Not set (auto-detected in Cloud Run) |
| `VECTOR_SEARCH_DIMENSIONS` | Vector dimensions | `768` |
| `FIRESTORE_DATABASE_ID` | Firestore database ID | `(default)` |
| `MAX_ANALYSIS_RETRIES` | Max analysis retries | `3` |
| `ANALYSIS_TIMEOUT` | Analysis timeout (seconds) | `300` |
| `REPORT_TEMPLATE_PATH` | Report template path | `templates/` |
| `REPORT_OUTPUT_PATH` | Report output path | `reports/` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration | `30` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:3000,http://localhost:5173,https://agenticone.vercel.app` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Log level | `INFO` |

## Google Cloud Setup

### 1. Create a Google Cloud Project

```bash
# Create a new project
gcloud projects create your-project-id --name="AgenticOne Project"

# Set the project
gcloud config set project your-project-id
```

### 2. Enable Required APIs

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Firestore API
gcloud services enable firestore.googleapis.com

# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Cloud Run API
gcloud services enable run.googleapis.com
```

### 3. Create Service Account

```bash
# Create service account
gcloud iam service-accounts create agenticone-backend \
  --display-name="AgenticOne Backend Service Account"

# Grant required roles
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:agenticone-backend@your-project-id.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:agenticone-backend@your-project-id.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:agenticone-backend@your-project-id.iam.gserviceaccount.com" \
  --role="roles/storage.admin"
```

### 4. Create and Download Service Account Key

```bash
# Create service account key
gcloud iam service-accounts keys create key.json \
  --iam-account=agenticone-backend@your-project-id.iam.gserviceaccount.com

# Set the path in your .env file
echo "GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/key.json" >> .env
```

### 5. Create Cloud Storage Bucket

```bash
# Create storage bucket
gsutil mb gs://your-storage-bucket-name

# Set the bucket name in your .env file
echo "CLOUD_STORAGE_BUCKET=your-storage-bucket-name" >> .env
```

### 6. Set up Firestore

```bash
# Create Firestore database
gcloud firestore databases create --location=us-central1

# Set the project ID in your .env file
echo "FIRESTORE_PROJECT_ID=your-project-id" >> .env
```

## Vector Search Setup

### 1. Create Vector Search Index

```bash
# Create vector search index (this requires Vertex AI Vector Search)
# You'll need to do this through the Google Cloud Console or API
# For now, use a placeholder value
echo "VECTOR_SEARCH_INDEX_ID=my-vector-index" >> .env
```

## Security Configuration

### 1. Generate Secret Key

```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add the generated key to your .env file:
```
SECRET_KEY=your-generated-secret-key-here
```

## Example .env File

```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=my-project-123
GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro

# Vector Search Configuration
VECTOR_SEARCH_INDEX_ID=my-vector-index
VECTOR_SEARCH_DIMENSIONS=768

# Firestore Configuration
FIRESTORE_PROJECT_ID=my-project-123
FIRESTORE_DATABASE_ID=(default)

# Cloud Storage Configuration
CLOUD_STORAGE_BUCKET=my-storage-bucket

# Security
SECRET_KEY=your-super-secret-key-here

# Optional configurations
MAX_ANALYSIS_RETRIES=3
ANALYSIS_TIMEOUT=300
DEBUG=false
LOG_LEVEL=INFO
```

## Validation

After setting up your .env file, run the validation script:

```bash
python3 validate_env.py
```

This will check:
- ✅ All required variables are set
- ✅ Values are in correct format
- ✅ File paths exist (for service account key)
- ⚠️ Warns about placeholder values
- ⚠️ Warns about security issues

## Troubleshooting

### Common Issues

1. **"No .env file found"**
   - Copy `env.example` to `.env`
   - Edit `.env` with your values

2. **"Service account key not found"**
   - Check the path in `GOOGLE_APPLICATION_CREDENTIALS`
   - Ensure the file exists and is readable

3. **"Project ID not found"**
   - Verify your Google Cloud project exists
   - Check the project ID is correct

4. **"Bucket not found"**
   - Create the Cloud Storage bucket
   - Ensure you have permissions

### Testing Configuration

```bash
# Test Google Cloud authentication
gcloud auth application-default login

# Test Firestore connection
gcloud firestore databases list

# Test Cloud Storage
gsutil ls gs://your-bucket-name
```

## Production Deployment

For production deployment on Cloud Run:

1. **Remove local service account key** (not needed in Cloud Run)
2. **Set environment variables in Cloud Run**
3. **Use Cloud Run's built-in authentication**
4. **Enable proper IAM roles for the service**

The environment variables will be automatically injected by Cloud Run based on your deployment configuration.
