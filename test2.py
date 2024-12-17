import asyncio
import asyncpg
from asyncpg.exceptions import ConnectionDoesNotExistError

async def test_postgresql_connection():
    conn_str = "postgresql://postgres:123456@localhost:5432/myblog"
    
    try:
        # 尝试建立连接
        conn = await asyncpg.connect(dsn=conn_str)
        print("连接成功！")
        
        # 可选：你可以执行简单的查询来测试连接
        result = await conn.fetch("SELECT 1")
        print(f"查询结果: {result}")

        # 关闭连接
        await conn.close()
    except ConnectionDoesNotExistError as e:
        print(f"数据库连接失败: {e}")
    except Exception as e:
        print(f"发生错误: {e}")

# 运行异步函数
loop = asyncio.get_event_loop()
loop.run_until_complete(test_postgresql_connection())
