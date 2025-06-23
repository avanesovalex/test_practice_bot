import asyncpg

from bot.config import DB_DSN


class Database:
    def __init__(self):
        self.pool = None
        self.dsn = DB_DSN

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=1,
                max_size=10,
                command_timeout=30
            )
            return self.pool
        except Exception as e:
            return False
    
    async def close(self):
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def execute(self, query: str, *params):
        async with self.pool.acquire() as conn: # type: ignore
            return await conn.execute(query, *params)
    
    async def fetch(self, query: str, *params):
        async with self.pool.acquire() as conn: # type: ignore
            return await conn.fetch(query, *params)
    
    async def fetchrow(self, query: str, *params):
        async with self.pool.acquire() as conn: # type: ignore
            return await conn.fetchrow(query, *params)
    
    async def fetchval(self, query: str, *params):
        async with self.pool.acquire() as conn: # type: ignore
            return await conn.fetchval(query, *params)
    
db = Database()