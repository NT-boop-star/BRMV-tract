import asyncio
import asyncpg

async def main():
    try:
        conn = await asyncpg.connect('postgresql://brvm_user:brvm_password@127.0.0.1:5432/brvm_tracker')
        res = await conn.fetchval('SELECT 1')
        print("Success:", res)
    except Exception as e:
        print("Error:", repr(e))

asyncio.run(main())
