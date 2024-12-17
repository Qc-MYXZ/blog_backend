from tortoise import fields,Tortoise
from tortoise.models import Model
DATABASE_URL = "postgresql://postgres:123456@localhost:5432/myblog"
TORTOISE_ORM = {
    "connections": {
        "default": DATABASE_URL,
    },
    "apps": {
        "models": {
            "models": ["apps.models"],
            "default_connection": "default",
        },
    },
}
# 定义你的模型
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"<User(username={self.username}, email={self.email})>"
