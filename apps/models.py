from tortoise import fields
from tortoise.models import Model

TORTOISE_ORM = {
        "connections": {
            "default": "postgres://postgres:123456@localhost:5432/postgres",  # 你的数据库连接字符串
        },
        "apps": {
            "models": {
                "models": ["apps.models"],  # 指定模型所在模块
                "default_connection": "default",  # 默认数据库连接
            }
        }
    }
class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)
    email = fields.CharField(max_length=100)
    
    class Meta:
        table = "users"
        
    def __str__(self):
        return self.username
