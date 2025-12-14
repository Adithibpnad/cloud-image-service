# Cloud Image Service

A cloud-based image upload and metadata management service inspired by Instagram’s image module.

The system enables secure image uploads using presigned URLs, stores images in object storage,
and persists metadata in a NoSQL database.

This project demonstrates real-world cloud application design with scalability, security,
and clean API practices.

---

## Architecture Overview

- Client requests an upload URL from the backend.
- Backend generates a presigned S3 URL.
- Client uploads image directly to S3 (no backend file handling).
- Metadata is stored in DynamoDB.
- Images can be listed, downloaded, or deleted via APIs.

Presigned URLs avoid routing large files through the backend, improving scalability.

---

## Tech Stack

- Language: Python 3.10
- Backend Framework: FastAPI
- Object Storage: Amazon S3 (LocalStack for local development)
- NoSQL Database: Amazon DynamoDB (LocalStack)
- API Documentation: OpenAPI / Swagger (FastAPI)
- Containerization: Docker & Docker Compose
- Local Cloud Emulation: LocalStack

---

## Local Setup Instructions

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (or `docker compose` depending on Docker version)
- AWS CLI (v2 recommended)
- (Optional) jq for JSON formatting in CLI examples

### 1. Clone the repository
git clone https://github.com/Adithibpnad/cloud-image-service.git
cd cloud-image-service

### 2. Create and activate a virtual environment

- Linux / macOS (bash/zsh):
  python -m venv venv
  source venv/bin/activate

- Windows PowerShell:
  python -m venv venv
  .\venv\Scripts\Activate.ps1

- Windows CMD:
  python -m venv venv
  .\venv\Scripts\activate.bat

Install dependencies:
pip install -r requirements.txt

(Ensure `requirements.txt` includes uvicorn, fastapi, boto3, python-dotenv as needed.)

### 3. Start LocalStack

Depending on your Docker setup:

- Docker Compose:
  docker compose up -d

- Older Docker Compose:
  docker-compose up -d

LocalStack exposes services on localhost:4566 by default (edge port).

### 4. Configure AWS CLI for LocalStack (use dummy credentials)

You can set credentials either via `aws configure` or environment variables.

- aws configure (interactive)
  - Access Key ID: test
  - Secret Access Key: test
  - Default region name: us-east-1
  - Default output format: json

OR set env vars (preferred for scripts):
- Linux/macOS:
  export AWS_ACCESS_KEY_ID=test
  export AWS_SECRET_ACCESS_KEY=test
  export AWS_DEFAULT_REGION=us-east-1

- Windows PowerShell:
  $env:AWS_ACCESS_KEY_ID="test"
  $env:AWS_SECRET_ACCESS_KEY="test"
  $env:AWS_DEFAULT_REGION="us-east-1"

All CLI calls below use `--endpoint-url=http://localhost:4566` to target LocalStack.

### 5. Create S3 bucket

- Single-line (works across shells):
  aws --endpoint-url=http://localhost:4566 s3 mb s3://cloud-image-bucket

If you need to enable CORS for browser uploads, configure the bucket CORS accordingly (example in S3 console or via aws s3api put-bucket-cors).

### 6. Create DynamoDB table

- Single-line:
  aws --endpoint-url=http://localhost:4566 dynamodb create-table \
    --table-name ImageMetadata \
    --attribute-definitions AttributeName=user_id,AttributeType=S AttributeName=image_id,AttributeType=S \
    --key-schema AttributeName=user_id,KeyType=HASH AttributeName=image_id,KeyType=RANGE \
    --billing-mode PAY_PER_REQUEST

(If your shell has trouble with line continuations, run the command as one long line without `\` or use the platform-appropriate continuation character.)

Example JSON form (explicit):
aws --endpoint-url=http://localhost:4566 dynamodb create-table \
  --table-name ImageMetadata \
  --attribute-definitions '[{"AttributeName":"user_id","AttributeType":"S"},{"AttributeName":"image_id","AttributeType":"S"}]' \
  --key-schema '[{"AttributeName":"user_id","KeyType":"HASH"},{"AttributeName":"image_id","KeyType":"RANGE"}]' \
  --billing-mode PAY_PER_REQUEST

### 7. Start the API server

From the project root (ensure venv is activated and dependencies installed):
uvicorn app.main:app --reload

Swagger UI will be available at:
http://127.0.0.1:8000/docs

---

## API Usage Examples

### 1. Generate upload URL
POST /images/upload

Request body:
{
  "user_id": "user123",
  "content_type": "image/jpeg",
  "tags": ["profile", "test"],
  "description": "Sample image upload"
}

Response:
{
  "image_id": "uuid",
  "upload_url": "https://...presigned S3 URL..."
}

### 2. Upload image using presigned URL
Use the returned upload_url to PUT the file directly to S3:

curl -X PUT "<upload_url>" \
  -H "Content-Type: image/jpeg" \
  --data-binary @"test.jpg"

Important: include the same Content-Type header used when generating the presigned URL.

### 3. Download image (CLI, from LocalStack)
aws --endpoint-url=http://localhost:4566 s3 cp \
  s3://cloud-image-bucket/images/<image_id> downloaded.jpg

### 4. Metadata model (DynamoDB)
- user_id (partition key)
- image_id (sort key)
- s3_key
- content_type
- upload_time
- tags
- description

---

## Security & Operational Notes

- Do not use real AWS credentials with LocalStack in shared or CI environments.
- Presigned URLs should have a short expiration time and should be scoped to the intended content type and key prefix.
- Validate content type and maximum file size on the backend before generating presigned URLs.
- Consider virus/malware scanning and content moderation for production systems.
- Add authentication & authorization to ensure only permitted users can generate/upload/manage images.
- If you support browser-based direct uploads, ensure the bucket has appropriate CORS policy.

---

## Local Development Tips

- Use environment variables (.env) for configurable values (bucket name, region, LocalStack endpoint).
- For browser tests, configure CORS and ensure the presigned PUT supports required headers.
- Use Docker to emulate S3/DynamoDB with LocalStack for deterministic local testing.

---

## Testing

- Add unit tests for metadata logic and integration tests that exercise LocalStack (start LocalStack in CI or with a test fixture).
- Consider pytest and moto/localstack for isolated tests. LocalStack gives good end-to-end coverage.

---

## Future Enhancements

- Image listing with filters (user_id, tags, date range)
- Download and delete APIs (signed GET/DELETE)
- Authentication and authorization (JWT / OAuth)
- Deployment options (ECS/Fargate, EKS, or Lambda + API Gateway)
- Thumbnail generation and storing multiple sizes
- Content moderation and virus scanning pipelines

---

## Commit & Push

When you're ready to commit README changes:

git add README.md
git commit -m "docs: improve README with setup and examples"
git push

---

## License & Contributing

- Add a LICENSE file (e.g., MIT) if you want to open-source.
- Add CONTRIBUTING.md to describe development workflow and tests.

