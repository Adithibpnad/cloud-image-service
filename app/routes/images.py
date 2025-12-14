from fastapi import APIRouter
from pydantic import BaseModel
import uuid

from app.services.s3_service import generate_presigned_upload_url
from app.services.dynamo_service import save_image_metadata

router = APIRouter()


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
@router.get("/images")
def list_images(user_id: str = None, tag: str = None):
    table = dynamodb.Table(TABLE_NAME)

    if not user_id:
        return {"error": "user_id is required"}

    response = table.query(
        KeyConditionExpression=Key("user_id").eq(user_id)
    )

    items = response.get("Items", [])

    if tag:
        items = [item for item in items if tag in item.get("tags", [])]

    return items

@router.get("/images/{image_id}/download")
def download_image(image_id: str, user_id: str):
    table = dynamodb.Table(TABLE_NAME)

    response = table.get_item(
        Key={"user_id": user_id, "image_id": image_id}
    )

    item = response.get("Item")
    if not item:
        return {"error": "Image not found"}

    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": BUCKET_NAME,
            "Key": item["s3_key"]
        },
        ExpiresIn=3600
    )

    return {"download_url": url}


@router.delete("/images/{image_id}")
def delete_image(image_id: str, user_id: str):
    table = dynamodb.Table(TABLE_NAME)

    table.delete_item(
        Key={"user_id": user_id, "image_id": image_id}
    )

    s3.delete_object(
        Bucket=BUCKET_NAME,
        Key=f"images/{image_id}"
    )

    return {"status": "deleted"}
