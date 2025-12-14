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
