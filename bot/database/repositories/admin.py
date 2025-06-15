from database.db import db

async def get_all_users() -> list:
    users = await db.fetch(
        '''SELECT user_id FROM users'''
    )
    return users