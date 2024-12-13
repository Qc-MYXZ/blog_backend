from fastapi import APIRouter
from apps.views import user

v1 = APIRouter()
v1.include_router(user.router, prefix="/users", tags=["user_info"])