from fastapi import FastAPI
from app.routes.images import router

app = FastAPI(title="Cloud Image Service")

app.include_router(router, prefix="/images")
