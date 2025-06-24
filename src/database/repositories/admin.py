from src.database.db import db


async def is_user_admin(user_id):
    admin = await db.fetchval(
        '''SELECT is_admin FROM users WHERE user_id = $1''', user_id
    )
    return admin


async def get_all_users() -> list:
    users = await db.fetch(
        '''SELECT user_id, full_name FROM users'''
    )
    return [user['user_id'] for user in users]


async def get_one_user(user_id) -> list:
    user = await db.fetch(
        '''SELECT full_name, birth_date, phone_number, last_activity FROM users
        WHERE user_id = $1''', user_id
    )
    return [user[0]['full_name'],
            user[0]['birth_date'],
            user[0]['phone_number'],
            user[0]['last_activity']]


async def get_recently_active_users() -> list:
    users = await db.fetch(
        """SELECT user_id, full_name, last_activity
        FROM users
        WHERE last_activity >= NOW() - INTERVAL '24 hours'"""
    )
    return users


async def get_all_requests() -> list:
    requests = await db.fetch(
        '''SELECT id, user_id request_date
        FROM requests'''
    )
    return requests


async def get_recently_added_requests() -> list:
    requests = await db.fetch(
        """SELECT id, user_id, request_date
        FROM requests
        WHERE request_date >= NOW() - INTERVAL '168 hours'"""
    )
    return requests