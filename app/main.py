from fastapi import FastAPI
from app.routes.images import router as images_router

app = FastAPI(title="Cloud Image Service")

app.include_router(images_router)
