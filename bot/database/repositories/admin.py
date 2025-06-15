from database.db import db

async def is_user_admin(user_id):
    admin = await db.fetchval(
        '''SELECT is_admin FROM users WHERE user_id = $1''', user_id
    )
    return admin

async def get_all_users() -> list:
    users = await db.fetch(
        '''SELECT user_id FROM users'''
    )
    return [user['user_id'] for user in users]