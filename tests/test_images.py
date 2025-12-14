from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_upload_endpoint():
    response = client.post(
        "/images/upload",
        json={
            "user_id": "test_user",
            "content_type": "image/jpeg",
            "tags": ["test"],
            "description": "test image"
        }
    )

    assert response.status_code == 200
    body = response.json()
    assert "image_id" in body
    assert "upload_url" in body


def test_list_images_requires_user_id():
    response = client.get("/images")
    assert response.status_code in (400, 422)


def test_list_images_with_user_id():
    response = client.get("/images", params={"user_id": "test_user"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
def test_delete_non_existing_image():
    response = client.delete(
        "/images/non-existent-id",
        params={"user_id": "test_user"}
    )

    assert response.status_code in (200, 404)

