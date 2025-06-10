from database.db import db

async def add_request(user_id, category, request_text, photo_id=None):
    request_id = await db.fetchval(
        '''INSERT INTO requests(user_id, category, request_text, photo_id) VALUES($1, $2, $3, $4)
        RETURNING id''',
        user_id, category, request_text, photo_id
    )
    return request_id

async def get_request(request_id):
    request = await db.fetchrow(
        '''SELECT r.id, u.full_name, u.phone_number, r.request_text, r.category, r.photo_id
        FROM requests r
        JOIN users u ON r.user_id = u.user_id
        WHERE r.id = $1''',
        request_id
    )
    return request