from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
from boto3.dynamodb.conditions import Key

from app.services.s3_service import generate_presigned_upload_url, s3
from app.services.dynamo_service import save_image_metadata, dynamodb
from app.config import S3_BUCKET, DYNAMO_TABLE

router = APIRouter(prefix="/images")


class UploadRequest(BaseModel):
    user_id: str
    content_type: str
    tags: list[str]
    description: str


@router.post("/upload")
def upload_image(data: UploadRequest):
    image_id = str(uuid.uuid4())

    s3_key, upload_url = generate_presigned_upload_url(
        image_id=image_id,
        content_type=data.content_type
    )

    save_image_metadata(
        user_id=data.user_id,
        image_id=image_id,
        s3_key=s3_key,
        content_type=data.content_type,
        tags=data.tags,
        description=data.description
    )

    return {
        "image_id": image_id,
        "upload_url": upload_url
    }


@router.get("/")
def list_images(user_id: str, tag: str | None = None):
    table = dynamodb.Table(DYNAMO_TABLE)

    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )

    items = response.get("Items", [])

    if tag:
        items = [item for item in items if tag in item.get("tags", [])]

    return items


@router.get("/{image_id}/download")
def download_image(image_id: str, user_id: str):
    table = dynamodb.Table(DYNAMO_TABLE)

    response = table.get_item(
        Key={"user_id": user_id, "image_id": image_id}
    )

    item = response.get("Item")
    if not item:
        raise HTTPException(status_code=404, detail="Image not found")

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": item["s3_key"]
        },
        ExpiresIn=3600
    )

    return {"download_url": url}


@router.delete("/{image_id}")
def delete_image(image_id: str, user_id: str):
    table = dynamodb.Table(DYNAMO_TABLE)

    table.delete_item(
        Key={"user_id": user_id, "image_id": image_id}
    )

    s3.delete_object(
        Bucket=S3_BUCKET,
        Key=f"images/{image_id}"
    )

    return {"status": "deleted"}
@router.get("")
def list_images(
    user_id: str,
    tag: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    table = dynamodb.Table(DYNAMO_TABLE)

    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )

    items = response.get("Items", [])

    if tag:
        items = [i for i in items if tag in i.get("tags", [])]

    if start_date:
        start = datetime.fromisoformat(start_date)
        items = [
            i for i in items
            if datetime.fromisoformat(i["upload_time"]) >= start
        ]

    if end_date:
        end = datetime.fromisoformat(end_date)
        items = [
            i for i in items
            if datetime.fromisoformat(i["upload_time"]) <= end
        ]

    return items