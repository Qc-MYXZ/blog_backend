"""create app
"""
import time
from fastapi import FastAPI
from fastapi.logger import logger
from tortoise import Tortoise

def create_app_test() -> FastAPI:
    app = FastAPI(
        title="blog_backend",
        description="FastAPI",
        version="v1",
    )
        # 在 FastAPI 的启动事件中初始化数据库
    @app.on_event("startup")
    async def startup():
        # 初始化数据库连接并生成数据库模式
        await Tortoise.init(config=get_tortoise_config())  # 使用字典配置
        await Tortoise.generate_schemas()

    @app.on_event("shutdown")
    async def shutdown():
        # 关闭数据库连接
        await Tortoise.close_connections()

    return app

