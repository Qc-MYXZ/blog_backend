"""create app
"""
import time
from fastapi import FastAPI
from fastapi.logger import logger

def create_app() -> FastAPI:
    app = FastAPI(
        title="blog_backend",
        description="FastAPI",
        version="v1",
    )
    return app