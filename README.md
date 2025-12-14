# Cloud Image Service

A cloud-native image upload and metadata management service inspired by social-media image modules.  
This backend issues pre-signed object storage URLs for direct uploads, persists metadata in a NoSQL store, and exposes a small, testable API for listing, downloading and deleting images.

[![license](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![python](https://img.shields.io/badge/python-3.10-blue.svg)](#)
[![docs](https://img.shields.io/badge/docs-Swagger-brightgreen.svg)](#)

Table of contents
- Quick start
- Architecture
- Tech stack
- Local development (LocalStack)
- Configuration (.env)
- API (endpoints & examples)
- Testing
- Operational notes & security
- Deployments & CI recommendations
- Contributing & license

Quick start (minutes)
1. Clone
   git clone https://github.com/Adithibpnad/cloud-image-service.git
   cd cloud-image-service

2. Local (recommended): bring up LocalStack and the app
   - Start LocalStack:
     docker compose up -d
   - Create a virtualenv and install deps:
     python -m venv venv
     source venv/bin/activate
     pip install -r requirements.txt
   - Start the API:
     uvicorn app.main:app --reload
   - Open the API docs (Swagger): http://127.0.0.1:8000/docs

Architecture (high level)
- Client requests an upload URL from the API.
- Backend returns a presigned S3 PUT URL scoped to content-type and key.
- Client uploads directly to S3 (no backend file streaming).
- Backend stores metadata (user_id, image_id, s3_key, content_type, upload_time, tags, description) in DynamoDB.
- API provides listing, signed-download, and deletion operations.

Tech stack
- Language: Python 3.10
- Framework: FastAPI (OpenAPI / Swagger)
- Object storage: Amazon S3 (LocalStack for local dev)
- NoSQL: Amazon DynamoDB (LocalStack)
- Containerization: Docker & Docker Compose

Local development using LocalStack
LocalStack exposes AWS-compatible endpoints on http://localhost:4566 (edge port).

1) Configure dummy AWS credentials (for local-only development)
   export AWS_ACCESS_KEY_ID=test
   export AWS_SECRET_ACCESS_KEY=test
   export AWS_DEFAULT_REGION=us-east-1

2) Create the S3 bucket
   aws --endpoint-url=http://localhost:4566 s3 mb s3://cloud-image-bucket

3) Create the DynamoDB table
   aws --endpoint-url=http://localhost:4566 dynamodb create-table \
     --table-name ImageMetadata \
     --attribute-definitions '[{"AttributeName":"user_id","AttributeType":"S"},{"AttributeName":"image_id","AttributeType":"S"}]' \
     --key-schema '[{"AttributeName":"user_id","KeyType":"HASH"},{"AttributeName":"image_id","KeyType":"RANGE"}]' \
     --billing-mode PAY_PER_REQUEST

Environment variables (.env example)
Create a .env in project root or export environment variables in your shell.

Example .env:
AWS_ENDPOINT_URL=http://localhost:4566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=test
AWS_SECRET_ACCESS_KEY=test
S3_BUCKET=cloud-image-bucket
DYNAMO_TABLE=ImageMetadata
PRESIGNED_EXPIRATION=300  # seconds

API: endpoints & usage
Base: GET http://127.0.0.1:8000/docs for interactive docs.

1) Generate upload URL
   POST /images/upload
   Body (JSON):
   {
     "user_id": "user123",
     "content_type": "image/jpeg",
     "tags": ["profile","mobile"],
     "description": "Sample image"
   }

   Response:
   {
     "image_id": "uuid",
     "upload_url": "https://...presigned S3 URL..."
   }

2) Upload image (client)
   Use the returned upload_url to PUT the file directly to S3:
   curl -X PUT "<upload_url>" \
     -H "Content-Type: image/jpeg" \
     --data-binary @test.jpg

   Important: the Content-Type header must match the content_type used when generating the presigned URL.

3) List images
   GET /images?user_id=user123&tag=profile

4) Download (get presigned GET URL)
   GET /images/{image_id}/download

   Response:
   {
     "download_url": "https://...presigned GET URL..."
   }

5) Delete image + metadata
   DELETE /images/{image_id}?user_id=user123

Metadata schema (DynamoDB)
- user_id (partition key)
- image_id (sort key)
- s3_key
- content_type
- upload_time (ISO8601)
- tags (list)
- description

Testing
- Unit tests: pytest (run from repo root)
  pytest tests/unit
- Integration tests: start LocalStack and run integration suite
  pytest tests/integration
- CI: run unit tests on pushes; run integration tests in an isolated environment (LocalStack in CI or via service mocks)

Operational notes & security
- Always scope presigned URLs to the intended key prefix and content-type, and keep short expiration times.
- Validate content-type and file size server-side before issuing presigned URLs.
- Consider virus scanning and content moderation (e.g. AWS Lambda + S3 event, or a scanning service) before marking uploads as approved.
- Add authentication & authorization (JWT / OAuth) to ensure users only manage their images.
- For browser uploads, configure S3 CORS and ensure preflight headers are allowed for the PUT operation.

Deployment & scaling
- This service is simple to deploy to container platforms (ECS/Fargate, EKS) or serverless (Lambda + API Gateway) with small adjustments (e.g., ephemeral localstack is for dev only).
- DynamoDB schema supports high-concurrency access patterns when partition keys are chosen correctly (avoid hot partitions).
- Offload heavy tasks (thumbnail generation, moderation) to async workers or event-driven pipelines.

CI / infra recommendations
- Use IaC (Terraform / CloudFormation) to create S3 buckets, DynamoDB tables, and policies.
- Add a GitHub Actions workflow to run linting, unit tests, and a limited integration job with LocalStack.
- Use automated security scanning and dependabot for dependency updates.

Future enhancements (roadmap)
- Authentication & authorization (OAuth2, JWT)
- Date-range filtering and advanced search by tags
- Thumbnail generation & multiple sizes
- Virus and content moderation pipelines
- Production-ready AWS deployment scripts and CI pipelines

Contributing
- Please open issues for bugs and feature requests.
- For code changes, please create feature branches, add tests, and open a pull request with a clear description and test coverage.
- See CONTRIBUTING for further clarifications.

License
- MIT License — see LICENSE

Credits & contact
- Maintainer: Adithibpnad
- Repo: https://github.com/Adithibpnad/cloud-image-service
