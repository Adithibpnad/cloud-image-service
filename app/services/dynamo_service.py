import boto3
from datetime import datetime
from app.config import AWS_ENDPOINT, AWS_REGION, DYNAMO_TABLE

dynamodb = boto3.resource(
    "dynamodb",
    endpoint_url=AWS_ENDPOINT,
    region_name=AWS_REGION,
)

table = dynamodb.Table(DYNAMO_TABLE)

def save_image_metadata(
    user_id: str,
    image_id: str,
    s3_key: str,
    content_type: str,
    tags: list,
    description: str
):
    table.put_item(
        Item={
            "user_id": user_id,
            "image_id": image_id,
            "s3_key": s3_key,
            "content_type": content_type,
            "upload_time": datetime.utcnow().isoformat(),
            "tags": tags,
            "description": description,
        }
    )
