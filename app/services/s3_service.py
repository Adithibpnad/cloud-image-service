import boto3
from app.config import AWS_ENDPOINT, AWS_REGION, S3_BUCKET

s3 = boto3.client(
    "s3",
    endpoint_url=AWS_ENDPOINT,
    region_name=AWS_REGION,
)

def generate_presigned_upload_url(image_id: str, content_type: str):
    key = f"images/{image_id}"

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=300
    )

    return key, url
