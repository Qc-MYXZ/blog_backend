"""create app
"""
import time
from fastapi import FastAPI
from fastapi.logger import logger
print('11111')

def create_app_test() -> FastAPI:
    app = FastAPI(
        title="blog_backend",
        description="FastAPI",
        version="v1",
    )
    return app
